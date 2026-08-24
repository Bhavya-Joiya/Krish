"""Live Agmarknet (data.gov.in) client with a 24-hour SQL cache.

Primary: GET https://api.data.gov.in/resource/{DATA_GOV_IN_RESOURCE_ID}
Fallback: mandi_prices rows updated in the last 24 hours.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings, get_settings
from app.models.mandi_price import MandiPrice

logger = logging.getLogger(__name__)

_NR_TOKENS = {"", "NR", "NA", "N/A", "NIL", "-", "--", "NULL", "NONE"}


def parse_price(value: Any) -> float | None:
    """Parse a mandi price; skip Agmarknet 'NR' / non-numeric placeholders."""
    if value is None:
        return None
    text = str(value).strip().upper().replace(",", "")
    if text in _NR_TOKENS:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if number < 0:
        return None
    return number


def _field(record: dict[str, Any], *keys: str) -> str:
    for key in keys:
        raw = record.get(key)
        if raw is not None and str(raw).strip():
            return str(raw).strip()
    return ""


@dataclass
class MandiQueryResult:
    """Normalized prices plus whether they came from the live API or cache."""

    records: list[dict[str, Any]] = field(default_factory=list)
    source: str = "none"  # live | cache | none
    fetched_at: datetime = field(default_factory=datetime.utcnow)


class MandiClient:
    """Fetch Agmarknet prices, cache them, and fall back to cache on API failure."""

    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    def _api_url(self) -> str:
        resource = (self.settings.data_gov_in_resource_id or "").strip()
        return f"https://api.data.gov.in/resource/{resource}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _request_json(self, params: dict[str, str | int]) -> dict[str, Any]:
        """One GET to data.gov.in with retries (timeouts are common on this API)."""
        headers = {"Accept": "application/json", "User-Agent": "KrishMandi/1.0"}
        timeout = httpx.Timeout(connect=10.0, read=35.0, write=10.0, pool=10.0)
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            response = await client.get(self._api_url(), params=params)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Agmarknet returned a non-JSON object")
        return payload

    async def _fetch_live(
        self,
        commodity: str,
        state: str | None = None,
        district: str | None = None,
        *,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Hit data.gov.in and return sanitized price rows (NR skipped)."""
        if not self.settings.data_gov_configured:
            raise RuntimeError("DATA_GOV_IN_API_KEY is not configured")

        params: dict[str, str | int] = {
            "api-key": self.settings.data_gov_in_api_key.strip(),
            "format": "json",
            "offset": 0,
            "limit": max(1, min(int(limit), 50)),
            "filters[commodity]": commodity,
        }
        if state:
            params["filters[state]"] = state
        if district:
            params["filters[district]"] = district

        try:
            payload = await self._request_json(params)
        except Exception:
            if state or district:
                logger.warning(
                    "Agmarknet filtered request failed; retrying commodity-only commodity=%s",
                    commodity,
                )
                params.pop("filters[state]", None)
                params.pop("filters[district]", None)
                payload = await self._request_json(params)
            else:
                raise

        raw_records = payload.get("records") or []
        cleaned: list[dict[str, Any]] = []
        for row in raw_records:
            if not isinstance(row, dict):
                continue
            modal = parse_price(row.get("modal_price"))
            if modal is None:
                continue
            cleaned.append(
                {
                    "state": _field(row, "state"),
                    "district": _field(row, "district"),
                    "market": _field(row, "market"),
                    "commodity": _field(row, "commodity") or commodity,
                    "variety": _field(row, "variety"),
                    "min_price": parse_price(row.get("min_price")),
                    "max_price": parse_price(row.get("max_price")),
                    "modal_price": modal,
                    "arrival_date": _field(row, "arrival_date"),
                }
            )
        if state:
            narrowed = [r for r in cleaned if r["state"].lower() == state.lower()]
            if narrowed:
                cleaned = narrowed
        if district:
            narrowed = [r for r in cleaned if r["district"].lower() == district.lower()]
            if narrowed:
                cleaned = narrowed
        logger.info(
            "Agmarknet live commodity=%s state=%s district=%s raw=%s kept=%s",
            commodity,
            state,
            district,
            len(raw_records),
            len(cleaned),
        )
        return cleaned

    def _upsert_cache(self, records: list[dict[str, Any]]) -> None:
        """Insert or update cache rows keyed by market + commodity + variety + date."""
        now = datetime.utcnow()
        for row in records:
            stmt = select(MandiPrice).where(
                MandiPrice.state == row["state"],
                MandiPrice.district == row["district"],
                MandiPrice.market == row["market"],
                MandiPrice.commodity == row["commodity"],
                MandiPrice.variety == (row.get("variety") or ""),
                MandiPrice.arrival_date == (row.get("arrival_date") or ""),
            )
            existing = self.session.scalars(stmt).first()
            if existing is None:
                existing = MandiPrice(
                    state=row["state"],
                    district=row["district"],
                    market=row["market"],
                    commodity=row["commodity"],
                    variety=row.get("variety") or "",
                    arrival_date=row.get("arrival_date") or "",
                )
                self.session.add(existing)
            existing.min_price = row.get("min_price")
            existing.max_price = row.get("max_price")
            existing.modal_price = row.get("modal_price")
            existing.updated_at = now
        self.session.commit()

    def _get_cached(
        self,
        commodity: str,
        state: str | None = None,
        district: str | None = None,
        *,
        max_age_hours: int = 24,
    ) -> list[dict[str, Any]]:
        """Return cache rows newer than max_age_hours."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        stmt = select(MandiPrice).where(
            MandiPrice.commodity.ilike(commodity),
            MandiPrice.updated_at >= cutoff,
            MandiPrice.modal_price.is_not(None),
        )
        if state:
            stmt = stmt.where(MandiPrice.state.ilike(state))
        if district:
            stmt = stmt.where(MandiPrice.district.ilike(district))
        stmt = stmt.order_by(MandiPrice.updated_at.desc())
        rows = list(self.session.scalars(stmt).all())
        return [
            {
                "state": r.state,
                "district": r.district,
                "market": r.market,
                "commodity": r.commodity,
                "variety": r.variety,
                "min_price": r.min_price,
                "max_price": r.max_price,
                "modal_price": r.modal_price,
                "arrival_date": r.arrival_date,
                "updated_at": r.updated_at,
            }
            for r in rows
        ]

    async def get_prices(
        self,
        commodity: str,
        state: str | None = None,
        district: str | None = None,
    ) -> MandiQueryResult:
        """Live fetch first; on failure or empty live result, use 24h cache."""
        try:
            live = await self._fetch_live(commodity, state, district)
            if live:
                self._upsert_cache(live)
                return MandiQueryResult(records=live, source="live")
            logger.warning(
                "Agmarknet returned no usable rows commodity=%s state=%s",
                commodity,
                state,
            )
        except Exception:
            logger.exception(
                "Agmarknet live fetch failed commodity=%s state=%s — using cache",
                commodity,
                state,
            )

        cached = self._get_cached(commodity, state, district)
        if cached:
            return MandiQueryResult(records=cached, source="cache")
        return MandiQueryResult(records=[], source="none")
