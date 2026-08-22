"""APScheduler wiring for the proactive nudge loop.

Starts with FastAPI lifespan. Uses a module singleton + replace_existing job id
so uvicorn --reload does not register duplicate jobs.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.services.proactive import run_proactive_check

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None
_JOB_ID = "proactive_rain_advisory_nudge"


def scheduler_running() -> bool:
    return bool(_scheduler is not None and _scheduler.running)


def get_scheduler_status() -> dict[str, Any]:
    settings = get_settings()
    return {
        "scheduler_running": scheduler_running(),
        "proactive_enabled": bool(settings.proactive_enabled),
        "proactive_interval_minutes": int(settings.proactive_check_interval_minutes),
        "proactive_demo_mode": bool(settings.proactive_demo_mode),
        "job_id": _JOB_ID if scheduler_running() else None,
    }


async def _scheduled_job() -> None:
    settings = get_settings()
    if not settings.proactive_enabled:
        logger.info("[PROACTIVE] Job tick skipped — PROACTIVE_ENABLED=false")
        return
    try:
        await run_proactive_check(settings=settings)
    except Exception:
        logger.exception("[PROACTIVE] Unhandled scheduler job error")


def start_scheduler() -> AsyncIOScheduler | None:
    """Start the singleton AsyncIOScheduler if proactive is enabled."""
    global _scheduler
    settings = get_settings()

    # Under uvicorn --reload, only the worker child should start the scheduler.
    # WatchFiles sets this in some setups; also guard with existing singleton.
    if os.environ.get("UVICORN_RELOAD_PARENT") == "1":
        return None

    if _scheduler is not None and _scheduler.running:
        logger.info("[PROACTIVE] Scheduler already running — skip start")
        return _scheduler

    if not settings.proactive_enabled:
        logger.info("[PROACTIVE] Scheduler not started (PROACTIVE_ENABLED=false)")
        return None

    interval = max(1, int(settings.proactive_check_interval_minutes))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _scheduled_job,
        trigger="interval",
        minutes=interval,
        id=_JOB_ID,
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "[PROACTIVE] Scheduler started (interval=%s minutes, job_id=%s)",
        interval,
        _JOB_ID,
    )
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    try:
        if _scheduler.running:
            _scheduler.shutdown(wait=False)
            logger.info("[PROACTIVE] Scheduler stopped")
    except Exception:
        logger.exception("[PROACTIVE] Scheduler shutdown error")
    finally:
        _scheduler = None


def run_proactive_check_sync(**kwargs: Any) -> Any:
    """Sync wrapper for CLI scripts."""
    return asyncio.run(run_proactive_check(**kwargs))
