"""OpenWeather 5-day / 3-hour forecast helpers for proactive rain checks.

Rain rule (any forecast point in the lookahead window):
  pop >= PROACTIVE_RAIN_POP_THRESHOLD
  OR rain volume (3h) >= PROACTIVE_RAIN_MM_THRESHOLD
  OR weather main/description indicates Rain / Drizzle / Thunderstorm
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


@dataclass
class ForecastPoint:
    dt: int
    pop: float
    rain_mm: float
    weather_main: str
    weather_description: str


@dataclass
class RainEvaluation:
    rain_expected: bool
    lookahead_hours: int
    points_checked: int
    matching_points: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""
    raw_error: str | None = None


async def fetch_forecast_5day(
    latitude: float,
    longitude: float,
    *,
    settings: Settings | None = None,
    timeout: float = 25.0,
) -> dict[str, Any]:
    """Fetch OpenWeather 5-day / 3-hour forecast JSON."""
    settings = settings or get_settings()
    if not settings.openweather_configured:
        raise RuntimeError("OPENWEATHER_API_KEY is not configured")

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": settings.openweather_api_key.strip(),
        "units": "metric",
        "lang": "hi",
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        return resp.json()


def _parse_points(data: dict[str, Any]) -> list[ForecastPoint]:
    points: list[ForecastPoint] = []
    for item in data.get("list") or []:
        weather = (item.get("weather") or [{}])[0]
        rain = item.get("rain") or {}
        rain_mm = float(rain.get("3h") or rain.get("1h") or 0.0)
        points.append(
            ForecastPoint(
                dt=int(item.get("dt") or 0),
                pop=float(item.get("pop") or 0.0),
                rain_mm=rain_mm,
                weather_main=str(weather.get("main") or ""),
                weather_description=str(weather.get("description") or ""),
            )
        )
    return points


def evaluate_rain_next_hours(
    forecast_data: dict[str, Any],
    *,
    settings: Settings | None = None,
    now_ts: int | None = None,
) -> RainEvaluation:
    """
    Inspect forecast points in [now, now + lookahead_hours].

    Rain is expected if ANY point matches:
      - pop >= proactive_rain_pop_threshold, OR
      - rain_mm >= proactive_rain_mm_threshold, OR
      - weather main in {Rain, Drizzle, Thunderstorm}
        (or description contains rain / drizzle / thunderstorm / बारिश)
    """
    settings = settings or get_settings()
    lookahead = int(settings.proactive_lookahead_hours)
    pop_th = float(settings.proactive_rain_pop_threshold)
    mm_th = float(settings.proactive_rain_mm_threshold)
    now = int(now_ts if now_ts is not None else time.time())
    end = now + lookahead * 3600

    points = _parse_points(forecast_data)
    window = [p for p in points if now <= p.dt <= end]
    matching: list[dict[str, Any]] = []

    rain_mains = {"rain", "drizzle", "thunderstorm"}
    for p in window:
        main_l = p.weather_main.lower()
        desc_l = p.weather_description.lower()
        by_pop = p.pop >= pop_th
        by_mm = p.rain_mm >= mm_th
        by_label = main_l in rain_mains or any(
            token in desc_l for token in ("rain", "drizzle", "thunderstorm", "बारिश")
        )
        if by_pop or by_mm or by_label:
            matching.append(
                {
                    "dt": p.dt,
                    "pop": p.pop,
                    "rain_mm": p.rain_mm,
                    "weather_main": p.weather_main,
                    "weather_description": p.weather_description,
                    "matched_by": [
                        name
                        for name, ok in (
                            ("pop", by_pop),
                            ("rain_mm", by_mm),
                            ("weather_label", by_label),
                        )
                        if ok
                    ],
                }
            )

    expected = bool(matching)
    if expected:
        reason = (
            f"{len(matching)} forecast period(s) in next {lookahead}h "
            f"met rain rule (pop>={pop_th} OR mm>={mm_th} OR rain label)"
        )
    else:
        reason = (
            f"No forecast period in next {lookahead}h met rain rule "
            f"(pop>={pop_th} OR mm>={mm_th} OR rain label); checked {len(window)} points"
        )

    return RainEvaluation(
        rain_expected=expected,
        lookahead_hours=lookahead,
        points_checked=len(window),
        matching_points=matching,
        reason=reason,
    )


async def check_rain_next_24h(
    latitude: float,
    longitude: float,
    *,
    settings: Settings | None = None,
) -> RainEvaluation:
    """Fetch forecast and evaluate the configured rain rule."""
    settings = settings or get_settings()
    try:
        data = await fetch_forecast_5day(latitude, longitude, settings=settings)
        return evaluate_rain_next_hours(data, settings=settings)
    except Exception as exc:
        logger.exception("Forecast rain check failed lat=%s lon=%s", latitude, longitude)
        return RainEvaluation(
            rain_expected=False,
            lookahead_hours=int(settings.proactive_lookahead_hours),
            points_checked=0,
            matching_points=[],
            reason="forecast_error",
            raw_error=str(exc),
        )
