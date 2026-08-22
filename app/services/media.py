"""Download media from Telegram or public URLs."""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

TELEGRAM_URL_PREFIX = "telegram:"


async def download_telegram_file(
    file_id: str,
    *,
    settings: Settings | None = None,
    timeout: float = 45.0,
) -> bytes:
    """Download a file from Telegram using Bot API getFile."""
    settings = settings or get_settings()
    if not settings.telegram_configured:
        raise RuntimeError("Telegram bot token required to download Telegram media")

    base = settings.telegram_api_base
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        meta = await client.get(f"{base}/getFile", params={"file_id": file_id})
        meta.raise_for_status()
        file_path = meta.json()["result"]["file_path"]
        response = await client.get(
            f"https://api.telegram.org/file/bot{settings.telegram_bot_token.strip()}/{file_path}"
        )
        response.raise_for_status()
        data = response.content
        logger.info("Downloaded Telegram file_id=%s bytes=%s", file_id[:24], len(data))
        return data


async def download_media(
    url: str,
    *,
    settings: Settings | None = None,
    timeout: float = 45.0,
) -> bytes:
    """
    Download bytes from a media URL.

    Telegram file ids use the `telegram:{file_id}` scheme.
    Public URLs (web chat demos) are fetched without auth.
    """
    settings = settings or get_settings()

    if url.startswith(TELEGRAM_URL_PREFIX):
        file_id = url[len(TELEGRAM_URL_PREFIX) :]
        return await download_telegram_file(file_id, settings=settings, timeout=timeout)

    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.content
        logger.info("Downloaded media url=%s bytes=%s", url[:80], len(data))
        return data
