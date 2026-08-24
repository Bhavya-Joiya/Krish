"""Simple intent detection for weather / mandi / general chat."""

from __future__ import annotations

from enum import Enum


class Intent(str, Enum):
    WEATHER = "weather"
    MANDI = "mandi"
    GENERAL = "general"


_WEATHER_KEYWORDS = (
    "मौसम",
    "बारिश",
    "तापमान",
    "गर्मी",
    "सर्दी",
    "humidity",
    "weather",
    "rain",
    "temperature",
    "forecast",
    "बादल",
    "धूप",
    "हवा",
)

_MANDI_KEYWORDS = (
    "मंडी",
    "मन्डी",
    "भाव",
    "बाजार",
    "बाज़ार",
    "रेट",
    "price",
    "mandi",
    "rate",
    "गेहूं",
    "गेहूँ",
    "wheat",
    "टमाटर",
    "tomato",
    "प्याज",
    "onion",
    "आलू",
    "potato",
    "चावल",
    "धान",
    "rice",
    "कपास",
    "cotton",
    "सोयाबीन",
    "soybean",
    "soyabean",
    "मक्का",
    "maize",
    "बिक्री",
    "बेच",
)


def detect_intent(text: str) -> Intent:
    lowered = (text or "").lower()
    # Check mandi before weather if both present — price questions often mention weather? rare.
    if any(k.lower() in lowered for k in _MANDI_KEYWORDS):
        return Intent.MANDI
    if any(k.lower() in lowered for k in _WEATHER_KEYWORDS):
        return Intent.WEATHER
    return Intent.GENERAL
