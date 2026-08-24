"""Outbound messaging via Telegram Bot API."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

TELEGRAM_TEXT_LIMIT = 4096


def _normalize_chat_id(to: str) -> str:
    if to.startswith("telegram:"):
        return to.split(":", 1)[1]
    return to


def _truncate_text(text: str, limit: int = TELEGRAM_TEXT_LIMIT) -> str:
    body = (text or "").strip()
    if len(body) <= limit:
        return body
    return body[: limit - 1].rsplit(" ", 1)[0] + "…"


def send_telegram_text(
    to: str,
    body: str,
    *,
    settings: Settings | None = None,
    request_location: bool = False,
    remove_keyboard: bool = False,
) -> str | None:
    """Send a Telegram text message. Returns Telegram message_id."""
    settings = settings or get_settings()

    if not settings.telegram_configured:
        logger.warning("Telegram not configured — skipping send to %s: %s", to, body)
        return None

    chat_id = _normalize_chat_id(to)
    text = _truncate_text(body)
    url = f"{settings.telegram_api_base}/sendMessage"
    payload: dict[str, object] = {"chat_id": chat_id, "text": text}
    if request_location:
        payload["reply_markup"] = {
            "keyboard": [
                [{"text": "📍 खेत की लोकेशन भेजें", "request_location": True}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
    elif remove_keyboard:
        payload["reply_markup"] = {"remove_keyboard": True}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            message_id = str(response.json()["result"]["message_id"])
        logger.info("Sent Telegram text message_id=%s to=%s", message_id, chat_id)
        return message_id
    except httpx.HTTPError as exc:
        logger.error("Telegram text send failed: %s", exc)
        raise


def send_telegram_audio(
    to: str,
    audio_path: Path | str,
    *,
    caption: str | None = None,
    settings: Settings | None = None,
) -> str | None:
    """Send a Telegram audio file (uploads MP3 directly — no public URL needed)."""
    settings = settings or get_settings()

    if not settings.telegram_configured:
        logger.warning("Telegram not configured — skipping audio to %s", to)
        return None

    chat_id = _normalize_chat_id(to)
    path = Path(audio_path)
    url = f"{settings.telegram_api_base}/sendAudio"
    data: dict[str, str] = {"chat_id": chat_id}
    if caption:
        data["caption"] = _truncate_text(caption, limit=1024)

    try:
        with httpx.Client(timeout=60.0) as client:
            with path.open("rb") as handle:
                response = client.post(
                    url,
                    data=data,
                    files={"audio": (path.name, handle, "audio/mpeg")},
                )
            response.raise_for_status()
            message_id = str(response.json()["result"]["message_id"])
        logger.info("Sent Telegram audio message_id=%s to=%s path=%s", message_id, chat_id, path.name)
        return message_id
    except httpx.HTTPError as exc:
        logger.error("Telegram audio send failed: %s", exc)
        raise
