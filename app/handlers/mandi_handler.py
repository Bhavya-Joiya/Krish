"""Chatbot handler: Agmarknet mandi prices in Hindi for Telegram / Web Chat."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

from app.db_sa import get_session_factory, init_sqlalchemy
from app.services.mandi_client import MandiClient, MandiQueryResult

logger = logging.getLogger(__name__)

HINDI_UNAVAILABLE = (
    "Mandi ke bhav abhi uplabdh nahi hain, kuch samay baad try karein."
)

# Query language → Agmarknet English commodity names
_COMMODITY_MAP: tuple[tuple[tuple[str, ...], str], ...] = (
    (("टमाटर", "tamatar", "tomato"), "Tomato"),
    (("प्याज", "pyaz", "onion"), "Onion"),
    (("आलू", "aloo", "potato"), "Potato"),
    (("गेहूं", "गेहूँ", "gehun", "wheat"), "Wheat"),
    (("चावल", "धान", "chawal", "rice", "paddy"), "Rice"),
    (("कपास", "kapas", "cotton"), "Cotton"),
    (("सोयाबीन", "soyabean", "soybean", "soya"), "Soyabean"),
    (("मक्का", "makka", "maize", "corn"), "Maize"),
    (("अंगूर", "angoor", "grape"), "Grapes"),
)

_STATE_MAP: tuple[tuple[tuple[str, ...], str], ...] = (
    (("उत्तर प्रदेश", "uttar pradesh", "up"), "Uttar Pradesh"),
    (("महाराष्ट्र", "maharashtra"), "Maharashtra"),
    (("पंजाब", "punjab"), "Punjab"),
    (("मध्य प्रदेश", "madhya pradesh", "mp"), "Madhya Pradesh"),
    (("दिल्ली", "delhi"), "NCT of Delhi"),
    (("हरियाणा", "haryana"), "Haryana"),
    (("गुजरात", "gujarat"), "Gujarat"),
    (("राजस्थान", "rajasthan"), "Rajasthan"),
    (("कर्नाटक", "karnataka"), "Karnataka"),
    (("तमिलनाडु", "tamil nadu"), "Tamil Nadu"),
    (("आंध्र", "andhra"), "Andhra Pradesh"),
)


def parse_commodity(text: str) -> str:
    """Map a farmer query to an Agmarknet commodity; default Tomato."""
    lowered = (text or "").lower()
    for keys, official in _COMMODITY_MAP:
        if any(k.lower() in lowered for k in keys):
            return official
    return "Tomato"


def parse_state(text: str) -> str | None:
    """Optional state filter from the farmer's message."""
    lowered = (text or "").lower()
    for keys, official in _STATE_MAP:
        if any(k.lower() in lowered for k in keys):
            return official
    return None


def _format_rupees(value: float | None) -> str:
    if value is None:
        return "—"
    if value >= 100:
        return f"₹{int(round(value))}"
    return f"₹{value:g}"


def _freshness_footer(result: MandiQueryResult) -> str:
    if result.source == "live":
        return "Updated: just now (Agmarknet / data.gov.in)"
    if result.source == "cache" and result.records:
        stamps = [r.get("updated_at") for r in result.records if r.get("updated_at")]
        latest = max(stamps) if stamps else None
        if isinstance(latest, datetime):
            return f"Updated: {latest.strftime('%d-%m-%Y %H:%M')} UTC (cache)"
        return "Updated: last 24h cache (Agmarknet)"
    return ""


def format_mandi_message(result: MandiQueryResult, commodity: str) -> str:
    """Build the farmer-facing Hindi/English mix reply (top 3 markets)."""
    if not result.records:
        return HINDI_UNAVAILABLE

    ranked = sorted(
        result.records,
        key=lambda r: float(r.get("modal_price") or 0),
        reverse=True,
    )
    top = ranked[:3]
    crop = commodity or str(top[0].get("commodity") or "फसल")
    lines = [f"🏷 {crop} मंडी भाव (Agmarknet)", ""]
    for row in top:
        market = row.get("market") or "Mandi"
        district = row.get("district") or ""
        state = row.get("state") or ""
        place = ", ".join(p for p in (district, state) if p)
        label = f"{market}" + (f" ({place})" if place else "")
        modal = _format_rupees(row.get("modal_price"))
        variety = row.get("variety") or ""
        extra = f" · {variety}" if variety and variety.lower() not in {"nr", "other", "n/a"} else ""
        lines.append(f"📍 {label}: {modal}/quintal{extra}")
    footer = _freshness_footer(result)
    if footer:
        lines.extend(["", footer])
    lines.append("बेचने से पहले स्थानीय मंडी में भाव ज़रूर कन्फर्म करें।")
    return "\n".join(lines)


async def handle_mandi_query(farmer: Any, commodity: str | None = None) -> str:
    """
    Resolve mandi prices for a farmer query.

    ``farmer`` may be a phone/chat id, a dict with optional ``query``/``state``,
    or the raw user message. ``commodity`` may be an official crop name or the
    full chat text.
    """
    query_text = ""
    state = None
    if isinstance(farmer, dict):
        query_text = str(farmer.get("query") or farmer.get("message") or "")
        state = farmer.get("state")
    elif isinstance(farmer, str) and not commodity:
        query_text = farmer

    blob = " ".join(
        part for part in (query_text, commodity if commodity and " " in str(commodity) else "")
        if part
    ).strip()
    if not blob:
        blob = str(commodity or "")

    crop = commodity if commodity and " " not in str(commodity) else parse_commodity(blob or str(commodity or ""))
    if commodity and re.match(r"^[A-Za-z]+$", str(commodity).strip()):
        crop = str(commodity).strip().title()
        if crop.lower() == "soybean":
            crop = "Soyabean"
    if not crop:
        crop = parse_commodity(blob)

    if state is None:
        state = parse_state(blob)

    init_sqlalchemy()
    session = get_session_factory()()
    try:
        client = MandiClient(session)
        result = await client.get_prices(crop, state, None)
        logger.info(
            "Mandi query farmer=%s crop=%s state=%s source=%s n=%s",
            farmer if not isinstance(farmer, dict) else farmer.get("id"),
            crop,
            state,
            result.source,
            len(result.records),
        )
        return format_mandi_message(result, crop)
    except Exception:
        logger.exception("handle_mandi_query failed")
        return HINDI_UNAVAILABLE
    finally:
        session.close()
