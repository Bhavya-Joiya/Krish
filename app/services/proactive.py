"""Proactive Agricultural Nudge Loop.

Central rule (visible and explicit):

    Nudge = Rain-in-next-lookahead-hours  AND  Open-Advisory

Channel: existing Telegram outbound messaging (`send_telegram_text`).
This project previously used Twilio WhatsApp; outbound now goes through Telegram.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.config import Settings, get_settings
from app.services.forecast import RainEvaluation, check_rain_next_24h
from app.services.messaging import send_telegram_text
from app.services.repository import (
    finish_proactive_run,
    get_open_advisories,
    list_farmers_with_locations,
    log_message,
    log_nudge_event,
    recently_nudged,
    start_proactive_run,
)

logger = logging.getLogger(__name__)

NUDGE_TYPE = "rain_open_advisory"


@dataclass
class ProactiveRunResult:
    farmers_checked: int = 0
    rain_detected_count: int = 0
    nudges_sent: int = 0
    failures: int = 0
    skipped: int = 0
    details: list[dict[str, Any]] = field(default_factory=list)
    demo_mode: bool = False
    dry_run: bool = False


def build_nudge_message(
    advisories: list[dict[str, Any]],
    *,
    lookahead_hours: int,
    demo_mode: bool = False,
) -> str:
    """Build one consolidated Hindi nudge from open advisories + rain expectation."""
    crops = sorted(
        {
            (a.get("crop") or "").strip()
            for a in advisories
            if (a.get("crop") or "").strip()
        }
    )
    titles = [str(a.get("title") or "").strip() for a in advisories if a.get("title")]
    crop_bit = ""
    if crops:
        crop_bit = f"आपकी फसल ({', '.join(crops)}) के लिए "

    if len(titles) == 1:
        advisory_line = (
            f"{crop_bit}सलाह अभी सक्रिय है: {titles[0]}।"
            if crop_bit
            else f"आपकी सलाह अभी सक्रिय है: {titles[0]}।"
        )
    else:
        joined = "; ".join(titles[:3])
        more = f" (+{len(titles) - 3} और)" if len(titles) > 3 else ""
        advisory_line = (
            f"{crop_bit}{len(titles)} सक्रिय सलाहें हैं: {joined}{more}।"
            if crop_bit
            else f"आपकी {len(titles)} सक्रिय सलाहें हैं: {joined}{more}।"
        )

    tip = (
        "बारिश की संभावना को देखते हुए सिंचाई/छिड़काव को थोड़ी देर रोकने पर विचार करें।"
    )

    lines = [
        "🌧 मौसम अपडेट:",
        f"आपके क्षेत्र में अगले {lookahead_hours} घंटे में बारिश की संभावना है।",
        "",
        advisory_line,
        tip,
        "",
        "यह एक advisory है — अंतिम निर्णय स्थानीय परिस्थितियों के अनुसार लें।",
    ]
    if demo_mode:
        lines.insert(0, "[DEMO MODE]")
        lines.insert(1, "")
    return "\n".join(lines)


def _primary_advisory_id(advisories: list[dict[str, Any]]) -> int | None:
    if not advisories:
        return None
    return int(advisories[0]["id"])


async def _process_farmer(
    farmer: dict[str, Any],
    *,
    settings: Settings,
    dry_run: bool,
    force_rain: bool,
    result: ProactiveRunResult,
) -> None:
    farmer_id = str(farmer["farmer_id"])
    lat = float(farmer["latitude"])
    lon = float(farmer["longitude"])
    detail: dict[str, Any] = {
        "farmer_id": farmer_id,
        "latitude": lat,
        "longitude": lon,
    }

    try:
        open_advisories = get_open_advisories(farmer_id)
        if not open_advisories:
            logger.info("[PROACTIVE] Farmer %s: no OPEN advisory — skip", farmer_id)
            detail["action"] = "skip_no_open_advisory"
            result.skipped += 1
            result.details.append(detail)
            return

        logger.info(
            "[PROACTIVE] Farmer %s: open advisory found (count=%s)",
            farmer_id,
            len(open_advisories),
        )
        detail["open_advisory_ids"] = [a["id"] for a in open_advisories]

        evaluation: RainEvaluation = await check_rain_next_24h(
            lat, lon, settings=settings
        )
        detail["forecast_reason"] = evaluation.reason
        detail["points_checked"] = evaluation.points_checked
        if evaluation.raw_error:
            detail["forecast_error"] = evaluation.raw_error
            logger.warning(
                "[PROACTIVE] Farmer %s: OpenWeather failed: %s",
                farmer_id,
                evaluation.raw_error,
            )

        rain_expected = bool(evaluation.rain_expected)
        if force_rain or settings.proactive_demo_mode:
            logger.info(
                "[PROACTIVE] Farmer %s: DEMO/force rain override "
                "(real rain_expected=%s, reason=%s)",
                farmer_id,
                evaluation.rain_expected,
                evaluation.reason,
            )
            rain_expected = True
            detail["demo_or_force_rain"] = True
            detail["real_rain_expected"] = evaluation.rain_expected

        detail["rain_expected"] = rain_expected
        if rain_expected:
            result.rain_detected_count += 1
            logger.info(
                "[PROACTIVE] Farmer %s: rain detected in next %sh",
                farmer_id,
                settings.proactive_lookahead_hours,
            )
        else:
            logger.info("[PROACTIVE] Farmer %s: no rain — skip", farmer_id)
            detail["action"] = "skip_no_rain"
            result.skipped += 1
            result.details.append(detail)
            return

        # Rule: RAIN_IN_NEXT_24H AND OPEN_ADVISORY  (both true here)
        advisory_id = _primary_advisory_id(open_advisories)
        if recently_nudged(
            farmer_id,
            nudge_type=NUDGE_TYPE,
            advisory_id=None,  # farmer-level cooldown for this nudge type
            cooldown_hours=settings.proactive_nudge_cooldown_hours,
        ):
            logger.info(
                "[PROACTIVE] Farmer %s: cooldown active, skipping", farmer_id
            )
            detail["action"] = "skip_cooldown"
            result.skipped += 1
            result.details.append(detail)
            return

        message = build_nudge_message(
            open_advisories,
            lookahead_hours=settings.proactive_lookahead_hours,
            demo_mode=bool(settings.proactive_demo_mode or force_rain),
        )
        detail["message"] = message

        if dry_run:
            logger.info(
                "[PROACTIVE] Farmer %s: DRY-RUN — would send nudge", farmer_id
            )
            log_nudge_event(
                farmer_id,
                advisory_id=advisory_id,
                nudge_type=NUDGE_TYPE,
                rain_detected=True,
                forecast_window_hours=settings.proactive_lookahead_hours,
                delivery_status="dry_run",
                message_text=message,
                demo_mode=bool(settings.proactive_demo_mode or force_rain),
            )
            detail["action"] = "dry_run"
            result.details.append(detail)
            return

        logger.info("[PROACTIVE] Farmer %s: sending nudge", farmer_id)
        try:
            message_id = send_telegram_text(farmer_id, message, settings=settings)
            log_nudge_event(
                farmer_id,
                advisory_id=advisory_id,
                nudge_type=NUDGE_TYPE,
                rain_detected=True,
                forecast_window_hours=settings.proactive_lookahead_hours,
                delivery_status="sent",
                message_text=message,
                message_id=message_id,
                demo_mode=bool(settings.proactive_demo_mode or force_rain),
            )
            try:
                log_message(
                    farmer_id,
                    direction="outbound",
                    message_type="proactive_nudge",
                    content_summary=message,
                )
            except Exception:
                logger.exception("Failed to log proactive message row")
            result.nudges_sent += 1
            detail["action"] = "sent"
            detail["message_id"] = message_id
            logger.info("[PROACTIVE] Farmer %s: nudge sent", farmer_id)
        except Exception as exc:
            logger.exception("[PROACTIVE] Farmer %s: messaging failed", farmer_id)
            log_nudge_event(
                farmer_id,
                advisory_id=advisory_id,
                nudge_type=NUDGE_TYPE,
                rain_detected=True,
                forecast_window_hours=settings.proactive_lookahead_hours,
                delivery_status="failed",
                message_text=message,
                error=str(exc),
                demo_mode=bool(settings.proactive_demo_mode or force_rain),
            )
            result.failures += 1
            detail["action"] = "failed"
            detail["error"] = str(exc)

        result.details.append(detail)
    except Exception as exc:
        logger.exception("[PROACTIVE] Farmer %s: unexpected error", farmer_id)
        result.failures += 1
        detail["action"] = "error"
        detail["error"] = str(exc)
        result.details.append(detail)


async def run_proactive_check(
    *,
    settings: Settings | None = None,
    dry_run: bool = False,
    force_rain: bool = False,
    farmer_id: str | None = None,
) -> ProactiveRunResult:
    """
    Run one proactive pass.

    force_rain: CLI/demo override — treats rain as true while still logging
    the real OpenWeather evaluation when available.
    """
    settings = settings or get_settings()
    result = ProactiveRunResult(
        demo_mode=bool(settings.proactive_demo_mode or force_rain),
        dry_run=dry_run,
    )

    if not settings.proactive_enabled and not dry_run and not force_rain:
        logger.info("[PROACTIVE] Disabled (PROACTIVE_ENABLED=false) — skip")
        return result

    logger.info("[PROACTIVE] Checking farmers (dry_run=%s demo=%s)", dry_run, result.demo_mode)
    run_id = start_proactive_run(
        demo_mode=result.demo_mode,
        notes="dry_run" if dry_run else None,
    )

    farmers = list_farmers_with_locations()
    if farmer_id:
        fid = farmer_id.strip()
        farmers = [f for f in farmers if str(f["farmer_id"]) == fid]
        if not farmers:
            logger.info(
                "[PROACTIVE] Farmer %s: no location — skip / not found", fid
            )
            result.details.append(
                {"farmer_id": fid, "action": "skip_no_location"}
            )

    # Cache forecast by rounded lat/lon to avoid duplicate OpenWeather calls
    # (handled inside per-farmer path; farmers rarely share exact coords)

    for farmer in farmers:
        result.farmers_checked += 1
        await _process_farmer(
            farmer,
            settings=settings,
            dry_run=dry_run,
            force_rain=force_rain,
            result=result,
        )

    finish_proactive_run(
        run_id,
        farmers_checked=result.farmers_checked,
        rain_detected_count=result.rain_detected_count,
        nudges_sent=result.nudges_sent,
        failures=result.failures,
    )
    logger.info(
        "[PROACTIVE] Scheduler completed checked=%s rain=%s sent=%s failures=%s",
        result.farmers_checked,
        result.rain_detected_count,
        result.nudges_sent,
        result.failures,
    )
    return result
