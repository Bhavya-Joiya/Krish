"""Gemini / agent tool: live Agmarknet mandi prices as a short farmer-facing summary."""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import re

from app.db_sa import get_session_factory, init_sqlalchemy
from app.handlers.mandi_handler import parse_commodity, parse_state
from app.services.mandi_client import MandiClient, MandiQueryResult, parse_price

logger = logging.getLogger(__name__)

_UNAVAILABLE = (
    "🌾 Mandi ke bhav abhi uplabdh nahi hain. Kuch samay baad try karein, "
    "ya crop ka naam clearly likhein (jaise tamatar, pyaz, gehun)."
)

_KNOWN = (
    "tomato",
    "tamatar",
    "onion",
    "pyaz",
    "potato",
    "aloo",
    "wheat",
    "gehun",
    "rice",
    "paddy",
    "chawal",
    "cotton",
    "kapas",
    "soyabean",
    "soybean",
    "maize",
    "makka",
    "corn",
    "grapes",
    "angoor",
    "टमाटर",
    "प्याज",
    "आलू",
    "गेहूं",
    "गेहूँ",
    "चावल",
    "कपास",
    "सोयाबीन",
    "मक्का",
    "अंगूर",
)


def _normalize_commodity(commodity: str) -> str:
    raw = (commodity or "").strip()
    if not raw:
        return "Tomato"
    lowered = raw.lower()
    if any(token in lowered or token in raw for token in _KNOWN):
        return parse_commodity(raw)
    if re.match(r"^[A-Za-z][A-Za-z\s]+$", raw):
        title = raw.title()
        return "Soyabean" if title.lower() in {"soybean", "soya"} else title
    return parse_commodity(raw)


def _normalize_place(value: str | None, *, kind: str) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if kind == "state":
        mapped = parse_state(text)
        return mapped or text.title()
    return text.title()


def _format_rupees(value: float | None) -> str:
    if value is None:
        return "—"
    if value >= 100:
        return f"₹{int(round(value))}"
    return f"₹{value:g}"


def _format_summary(result: MandiQueryResult, commodity: str) -> str:
    if not result.records:
        return _UNAVAILABLE

    ranked = sorted(
        result.records,
        key=lambda row: float(row.get("modal_price") or 0),
        reverse=True,
    )
    top = ranked[:5]
    crop = commodity or str(top[0].get("commodity") or "फसल")
    lines = [f"🌾 {crop} मंडी भाव", ""]
    for row in top:
        market = row.get("market") or "Mandi"
        district = row.get("district") or ""
        state = row.get("state") or ""
        place = ", ".join(part for part in (district, state) if part)
        modal = _format_rupees(parse_price(row.get("modal_price")) or row.get("modal_price"))
        variety = row.get("variety") or ""
        extra = ""
        if variety and variety.lower() not in {"nr", "other", "n/a", "na"}:
            extra = f" · {variety}"
        where = f"{market}" + (f" ({place})" if place else "")
        lines.append(f"📍 {where}: 💰 {modal}/quintal{extra}")

    if result.source == "live":
        lines.extend(["", "Updated: just now (Agmarknet)"])
    elif result.source == "cache":
        lines.extend(["", "Updated: last 24h cache (Agmarknet)"])
    lines.append("Bechne se pehle local mandi mein bhav confirm kar lein.")
    return "\n".join(lines)


async def fetch_mandi_prices(
    commodity: str,
    state: str | None = None,
    district: str | None = None,
) -> str:
    """
    Query Agmarknet (data.gov.in), skip NR prices, fall back to 24h SQL cache.

    Returns a short WhatsApp-ready summary of modal prices and markets.
    """
    crop = _normalize_commodity(commodity)
    state_name = _normalize_place(state, kind="state")
    district_name = _normalize_place(district, kind="district")

    init_sqlalchemy()
    session = get_session_factory()()
    try:
        client = MandiClient(session)
        result = await client.get_prices(crop, state_name, district_name)
        logger.info(
            "mandi_tool crop=%s state=%s district=%s source=%s n=%s",
            crop,
            state_name,
            district_name,
            result.source,
            len(result.records),
        )
        return _format_summary(result, crop)
    except Exception:
        logger.exception("fetch_mandi_prices failed crop=%s", crop)
        return _UNAVAILABLE
    finally:
        session.close()


def fetch_mandi_prices_sync(
    commodity: str,
    state: str | None = None,
    district: str | None = None,
) -> str:
    """Sync adapter for Gemini automatic function calling (must not deadlock the event loop)."""

    def _run() -> str:
        return asyncio.run(fetch_mandi_prices(commodity, state, district))

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(_run).result(timeout=50)
    except Exception:
        logger.exception("fetch_mandi_prices_sync failed")
        return _UNAVAILABLE


# Gemini reads __name__ + docstring to decide when to call the tool.
fetch_mandi_prices_sync.__name__ = "fetch_mandi_prices"
fetch_mandi_prices_sync.__doc__ = (
    "Fetch live wholesale mandi (market) prices from Agmarknet / data.gov.in. "
    "Call this whenever the farmer asks for crop rates, mandi bhav, or market prices. "
    "commodity: crop name in English or Hindi (Tomato, Onion, Wheat, टमाटर, प्याज). "
    "state: optional Indian state (Maharashtra, Uttar Pradesh). "
    "district: optional district name."
)
