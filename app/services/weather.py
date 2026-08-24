"""OpenWeather current-conditions helper (free Current Weather API 2.5)."""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

WEATHER_UNAVAILABLE_HI = "मौसम की जानकारी अभी उपलब्ध नहीं है। थोड़ी देर बाद फिर पूछें।"


async def fetch_weather_hindi(
    latitude: float,
    longitude: float,
    *,
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    if not settings.openweather_configured:
        return (
            "OpenWeather API key सेट नहीं है। "
            ".env में OPENWEATHER_API_KEY डालें "
            "(https://openweathermap.org/api से मुफ़्त कुंजी लें)।"
        )

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": settings.openweather_api_key,
        "units": "metric",
        "lang": "hi",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        logger.exception("OpenWeather request failed")
        return WEATHER_UNAVAILABLE_HI

    try:
        name = data.get("name") or "आपके इलाके"
        weather = (data.get("weather") or [{}])[0]
        desc = weather.get("description") or "जानकारी सीमित"
        main = data.get("main") or {}
        wind = data.get("wind") or {}
        temp = main.get("temp")
        feels = main.get("feels_like")
        humidity = main.get("humidity")
        wind_speed = wind.get("speed")

        lines = [f"🌤 {name} का मौसम"]
        lines.append(f"हाल: {desc}")
        if temp is not None:
            lines.append(f"तापमान: {temp:.0f}°C")
        if feels is not None:
            lines.append(f"महसूस: {feels:.0f}°C")
        if humidity is not None:
            lines.append(f"नमी: {humidity}%")
        if wind_speed is not None:
            lines.append(f"हवा: {wind_speed} m/s")

        # Simple farm tip
        if temp is not None and temp >= 35:
            lines.append("सुझाव: दोपहर में छिड़काव/सिंचाई से बचें।")
        elif "बारिश" in desc or "rain" in desc.lower():
            lines.append("सुझाव: आज छिड़काव टाल सकते हैं।")
        else:
            lines.append("सुझाव: खेत का काम मौसम देखकर तय करें।")

        return "\n".join(lines)
    except Exception:
        logger.exception("OpenWeather parse failed")
        return WEATHER_UNAVAILABLE_HI
