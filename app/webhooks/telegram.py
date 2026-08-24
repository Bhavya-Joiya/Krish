"""Telegram Bot webhook — inbound updates and outbound replies."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status

from app.config import get_settings
from app.services.media import TELEGRAM_URL_PREFIX
from app.services.message_types import IncomingMessage, MessageType
from app.services.messaging import send_telegram_audio, send_telegram_text
from app.services.orchestrator import BotReply, handle_incoming
from app.services.resilience import (
    RATE_LIMIT_REPLY_HI,
    is_duplicate_message,
    is_rate_limited,
)
from app.services.tts import synthesize_hindi_mp3

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/telegram", tags=["telegram"])

_LAST_HIT: dict[str, Any] = {"at": None, "from": None, "type": None, "id": None, "body": None}


def _validate_webhook_secret(secret: str | None) -> None:
    settings = get_settings()
    expected = (settings.telegram_webhook_secret or "").strip()
    if not expected:
        return
    if secret != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram webhook secret",
        )


def _parse_telegram_message(message: dict[str, Any]) -> IncomingMessage | None:
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat_id is None:
        return None

    from_number = f"telegram:{chat_id}"
    message_id = str(message.get("message_id", ""))
    body = message.get("text") or message.get("caption") or ""

    if location := message.get("location"):
        return IncomingMessage(
            from_number=from_number,
            body=body,
            message_type=MessageType.LOCATION,
            latitude=float(location["latitude"]),
            longitude=float(location["longitude"]),
            raw={"message_id": message_id},
        )

    if photos := message.get("photo"):
        photo = photos[-1]
        return IncomingMessage(
            from_number=from_number,
            body=body,
            message_type=MessageType.IMAGE,
            media_url=f"{TELEGRAM_URL_PREFIX}{photo['file_id']}",
            media_content_type="image/jpeg",
            raw={"message_id": message_id},
        )

    if voice := message.get("voice"):
        return IncomingMessage(
            from_number=from_number,
            body=body,
            message_type=MessageType.AUDIO,
            media_url=f"{TELEGRAM_URL_PREFIX}{voice['file_id']}",
            media_content_type="audio/ogg",
            raw={"message_id": message_id},
        )

    if audio := message.get("audio"):
        return IncomingMessage(
            from_number=from_number,
            body=body,
            message_type=MessageType.AUDIO,
            media_url=f"{TELEGRAM_URL_PREFIX}{audio['file_id']}",
            media_content_type=audio.get("mime_type") or "audio/mpeg",
            raw={"message_id": message_id},
        )

    if document := message.get("document"):
        mime = (document.get("mime_type") or "").lower()
        if mime.startswith("image/"):
            return IncomingMessage(
                from_number=from_number,
                body=body,
                message_type=MessageType.IMAGE,
                media_url=f"{TELEGRAM_URL_PREFIX}{document['file_id']}",
                media_content_type=mime,
                raw={"message_id": message_id},
            )

    if body.strip():
        return IncomingMessage(
            from_number=from_number,
            body=body,
            message_type=MessageType.TEXT,
            raw={"message_id": message_id},
        )

    return IncomingMessage(
        from_number=from_number,
        body=body,
        message_type=MessageType.UNKNOWN,
        raw={"message_id": message_id},
    )


async def _maybe_send_voice(to: str, reply: BotReply) -> None:
    settings = get_settings()
    if not reply.send_voice or not settings.tts_enabled:
        return
    try:
        speak = reply.text
        if reply.transcript and "\n\n" in reply.text:
            speak = reply.text.split("\n\n", 1)[1]
        path = await synthesize_hindi_mp3(speak, settings=settings)
        send_telegram_audio(to, path, settings=settings)
    except Exception:
        logger.exception("TTS / voice send failed — text reply already sent")


async def _process_and_reply(incoming: IncomingMessage) -> None:
    settings = get_settings()
    try:
        reply = await handle_incoming(incoming, settings=settings)
    except Exception:
        logger.exception("Orchestrator failed")
        reply = BotReply(
            "माफ़ कीजिए, अभी जवाब नहीं दे पाए। "
            "कृपया फिर से फोटो, टेक्स्ट, या वॉइस भेजें।"
        )

    if settings.telegram_configured and incoming.from_number:
        try:
            send_telegram_text(
                incoming.from_number,
                reply.text,
                settings=settings,
                request_location=reply.request_location,
                remove_keyboard=reply.remove_keyboard,
            )
            await _maybe_send_voice(incoming.from_number, reply)
        except Exception:
            logger.exception("Failed to send Telegram reply")


@router.get("/debug")
async def telegram_webhook_debug():
    """Open in browser to see if Telegram has hit this server recently."""
    settings = get_settings()
    return {
        "ok": True,
        "public_url": settings.public_base_url,
        "expected_webhook": f"{settings.public_base_url}/webhooks/telegram"
        if settings.public_base_url
        else "(set APP_PUBLIC_URL)",
        "set_webhook_url": f"{settings.public_base_url}/webhooks/telegram/set-webhook"
        if settings.public_base_url
        else "(set APP_PUBLIC_URL first)",
        "last_hit": _LAST_HIT,
        "hint": "Send a Telegram message to your bot, then refresh this page.",
    }


@router.post("/set-webhook")
async def set_telegram_webhook():
    """Register APP_PUBLIC_URL/webhooks/telegram with Telegram (call once after deploy)."""
    settings = get_settings()
    if not settings.telegram_configured:
        raise HTTPException(status_code=400, detail="TELEGRAM_BOT_TOKEN not configured")
    if not settings.public_base_url:
        raise HTTPException(status_code=400, detail="APP_PUBLIC_URL not configured")

    webhook_url = f"{settings.public_base_url}/webhooks/telegram"
    payload: dict[str, str] = {"url": webhook_url}
    secret = (settings.telegram_webhook_secret or "").strip()
    if secret:
        payload["secret_token"] = secret

    with httpx.Client(timeout=30.0) as client:
        response = client.post(f"{settings.telegram_api_base}/setWebhook", json=payload)
        response.raise_for_status()
        result = response.json()

    if not result.get("ok"):
        raise HTTPException(status_code=502, detail=result)

    return {"ok": True, "webhook_url": webhook_url, "telegram": result}


@router.post("")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(
        default=None, alias="X-Telegram-Bot-Api-Secret-Token"
    ),
) -> dict[str, bool]:
    """Receives inbound Telegram updates."""
    _validate_webhook_secret(x_telegram_bot_api_secret_token)

    update = await request.json()
    message = update.get("message") or update.get("edited_message")
    if not message:
        return {"ok": True}

    incoming = _parse_telegram_message(message)
    if incoming is None:
        return {"ok": True}

    message_id = incoming.raw.get("message_id")
    logger.info(
        "Telegram update type=%s from=%s id=%s body=%r",
        incoming.message_type.value,
        incoming.from_number,
        message_id,
        (incoming.body[:120] + "…") if len(incoming.body) > 120 else incoming.body,
    )

    if is_duplicate_message(str(message_id) if message_id else None):
        return {"ok": True}

    if is_rate_limited(incoming.from_number):
        send_telegram_text(incoming.from_number, RATE_LIMIT_REPLY_HI)
        return {"ok": True}

    _LAST_HIT.update(
        {
            "at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "from": incoming.from_number,
            "type": incoming.message_type.value,
            "id": message_id,
            "body": (incoming.body or "")[:120],
        }
    )

    if incoming.message_type in {MessageType.IMAGE, MessageType.AUDIO}:
        if incoming.message_type == MessageType.IMAGE:
            send_telegram_text(
                incoming.from_number,
                "📸 फोटो मिल गई। फसल जांच रहा हूँ — कुछ सेकंड में पूरा जवाब भेजूँगा।",
            )
        else:
            send_telegram_text(
                incoming.from_number,
                "🎙️ वॉइस नोट मिल गया। सुन/समझ रहा हूँ — कुछ सेकंड में जवाब भेजूँगा।",
            )
        background_tasks.add_task(_process_and_reply, incoming)
        return {"ok": True}

    try:
        reply = await asyncio.wait_for(handle_incoming(incoming), timeout=12.0)
    except asyncio.TimeoutError:
        logger.warning("AI timed out — falling back to background reply")
        send_telegram_text(incoming.from_number, "⏳ जवाब तैयार हो रहा है, एक पल में भेज रहा हूँ…")
        background_tasks.add_task(_process_and_reply, incoming)
        return {"ok": True}
    except Exception:
        logger.exception("Orchestrator failed in webhook")
        send_telegram_text(
            incoming.from_number,
            "माफ़ कीजिए, अभी जवाब नहीं दे पाए। कृपया फिर से लिखें।",
        )
        return {"ok": True}

    send_telegram_text(
        incoming.from_number,
        reply.text,
        request_location=reply.request_location,
        remove_keyboard=reply.remove_keyboard,
    )
    if reply.send_voice:
        background_tasks.add_task(_maybe_send_voice, incoming.from_number, reply)
    return {"ok": True}
