"""Celery tasks for background mandi cache refresh."""

from __future__ import annotations

import asyncio
import logging

from celery import shared_task

from app.db_sa import get_session_factory, init_sqlalchemy
from app.services.mandi_client import MandiClient
from app.workers.schedules import COMMON_CROPS, COMMON_STATES

logger = logging.getLogger(__name__)


async def refresh_mandi_prices_async() -> dict[str, int]:
    """Fetch common crop × state pairs and upsert the SQL cache."""
    init_sqlalchemy()
    session = get_session_factory()()
    client = MandiClient(session)
    ok = 0
    failed = 0
    try:
        for crop in COMMON_CROPS:
            for state in COMMON_STATES:
                try:
                    result = await client.get_prices(crop, state, None)
                    if result.records:
                        ok += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1
                    logger.exception("Mandi refresh failed crop=%s state=%s", crop, state)
                await asyncio.sleep(0.35)
    finally:
        session.close()
    logger.info("Mandi refresh done ok=%s empty_or_fail=%s", ok, failed)
    return {"ok": ok, "failed": failed}


@shared_task(name="app.workers.tasks.refresh_mandi_prices")
def refresh_mandi_prices() -> dict[str, int]:
    """Celery Beat entry: run the async client inside a sync worker."""
    return asyncio.run(refresh_mandi_prices_async())
