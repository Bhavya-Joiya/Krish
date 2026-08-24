"""Celery application for optional Redis + Beat workers.

On Render we do not require Redis: FastAPI's APScheduler runs the same
refresh function every 6 hours. Start a worker only when you have Redis:

    celery -A app.workers.celery_app worker -B -l info
"""

from __future__ import annotations

from celery import Celery

from app.config import get_settings
from app.workers.schedules import MANDI_BEAT_SCHEDULE

settings = get_settings()

celery_app = Celery("krish")
celery_app.conf.broker_url = settings.celery_broker_url
celery_app.conf.result_backend = settings.celery_broker_url
celery_app.conf.timezone = "Asia/Kolkata"
celery_app.conf.enable_utc = False
celery_app.conf.beat_schedule = MANDI_BEAT_SCHEDULE
celery_app.conf.imports = ("app.workers.tasks",)
