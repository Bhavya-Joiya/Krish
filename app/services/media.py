"""Download media from Twilio or public URLs."""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


async def download_media(
    url: str,
    *,
    settings: Settings | None = None,
    timeout: float = 45.0,
) -> bytes:
    """
    Download bytes from a media URL.

    Twilio media URLs require HTTP Basic auth (Account SID + Auth Token).
    Public URLs (web chat demos) are fetched without auth.
    """
    settings = settings or get_settings()
    auth: httpx.Auth | tuple[str, str] | None = None

    if "api.twilio.com" in url or "twilio.com" in url:
        if not settings.twilio_configured:
            raise RuntimeError("Twilio credentials required to download WhatsApp media")
        auth = (settings.twilio_account_sid, settings.twilio_auth_token)

    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        response = await client.get(url, auth=auth)
        response.raise_for_status()
        data = response.content
        logger.info("Downloaded media url=%s bytes=%s", url[:80], len(data))
        return data
