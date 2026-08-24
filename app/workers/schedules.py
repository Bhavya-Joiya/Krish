"""Celery Beat schedule and shared crop/state lists for mandi refresh."""

from __future__ import annotations

COMMON_CROPS: tuple[str, ...] = (
    "Wheat",
    "Rice",
    "Cotton",
    "Soyabean",
    "Maize",
    "Onion",
    "Tomato",
    "Potato",
)

COMMON_STATES: tuple[str, ...] = (
    "Uttar Pradesh",
    "Maharashtra",
    "Punjab",
    "Madhya Pradesh",
)

# Celery Beat: every 6 hours.
MANDI_BEAT_SCHEDULE = {
    "refresh-mandi-prices": {
        "task": "app.workers.tasks.refresh_mandi_prices",
        "schedule": 6 * 60 * 60,
    }
}
