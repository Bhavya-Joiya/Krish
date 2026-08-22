"""Twilio WhatsApp webhook — Phase 5 hardened replies (TwiML delivery)."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Form, Header, HTTPException, Request, Response, status
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.config import get_settings
from app.services.message_types import IncomingMessage, MessageType, detect_message_type
from app.services.messaging import send_whatsapp_audio, send_whatsapp_text
from app.services.orchestrator import BotReply, handle_incoming
from app.services.resilience import (
    RATE_LIMIT_REPLY_HI,
    is_duplicate_message,
    is_rate_limited,
)
from app.services.tts import public_media_url, synthesize_hindi_mp3

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/twilio", tags=["twilio"])

# Debug: last webhook hit (so you can verify Twilio is reaching the server)
_LAST_HIT: dict[str, Any] = {"at": None, "from": None, "type": None, "sid": None, "body": None}


def _twiml_message(text: str) -> Response:
    """Return a WhatsApp reply inside the webhook response (most reliable for Sandbox)."""
    resp = MessagingResponse()
    # WhatsApp / Twilio practical limit — keep under ~1500 chars
    body = (text or "").strip()
    if len(body) > 1400:
        body = body[:1400].rsplit(" ", 1)[0] + "…"
    resp.message(body)
    xml = str(resp)
    logger.info("TwiML reply chars=%s preview=%r", len(body), body[:80])
    return Response(content=xml, media_type="application/xml")


def _validate_twilio_signature(
    request: Request,
    form_dict: dict[str, str],
    signature: str | None,
) -> None:
    settings = get_settings()
    if not settings.twilio_validate_signature:
        return
    if not settings.twilio_auth_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signature validation enabled but TWILIO_AUTH_TOKEN is missing",
        )
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-Twilio-Signature header",
        )

    public = settings.app_public_url.rstrip("/") if settings.app_public_url else ""
    url = f"{public}{request.url.path}" if public else str(request.url)

    validator = RequestValidator(settings.twilio_auth_token)
    if not validator.validate(url, form_dict, signature):
        logger.warning("Invalid Twilio signature for url=%s", url)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Twilio signature",
        )


async def _maybe_send_voice(to: str, reply: BotReply) -> None:
    settings = get_settings()
    if not reply.send_voice or not settings.tts_enabled:
        return
    if not settings.public_base_url:
        logger.warning("Skipping TTS — APP_PUBLIC_URL not set")
        return
    try:
        speak = reply.text
        if reply.transcript and "\n\n" in reply.text:
            speak = reply.text.split("\n\n", 1)[1]
        path = await synthesize_hindi_mp3(speak, settings=settings)
        media_url = public_media_url(path.name, settings=settings)
        send_whatsapp_audio(to, media_url, settings=settings)
    except Exception:
        logger.exception("TTS / voice send failed — text reply already sent via TwiML")


async def _process_and_reply_rest(incoming: IncomingMessage) -> None:
    """Fallback path: send via REST when we already returned a quick TwiML ack."""
    settings = get_settings()
    try:
        reply = await handle_incoming(incoming, settings=settings)
    except Exception:
        logger.exception("Orchestrator failed (REST path)")
        reply = BotReply(
            "माफ़ कीजिए, अभी जवाब नहीं दे पाए। "
            "कृपया फिर से फोटो, टेक्स्ट, या वॉइस भेजें।"
        )

    if settings.twilio_configured and incoming.from_number:
        try:
            send_whatsapp_text(incoming.from_number, reply.text, settings=settings)
            logger.info("REST follow-up sent to %s", incoming.from_number)
        except Exception:
            logger.exception("Failed to send WhatsApp REST follow-up")
            return
        await _maybe_send_voice(incoming.from_number, reply)


@router.get("/whatsapp/debug")
async def twilio_webhook_debug():
    """Open in browser to see if Twilio has hit this server recently."""
    settings = get_settings()
    return {
        "ok": True,
        "public_url": settings.public_base_url,
        "expected_webhook": f"{settings.public_base_url}/webhooks/twilio/whatsapp"
        if settings.public_base_url
        else "(set APP_PUBLIC_URL)",
        "last_hit": _LAST_HIT,
        "hint": "Send a WhatsApp message, then refresh this page. last_hit.at should update.",
    }


@router.post("/whatsapp")
async def twilio_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    From: Annotated[str, Form()] = "",
    Body: Annotated[str, Form()] = "",
    NumMedia: Annotated[str, Form()] = "0",
    MediaUrl0: Annotated[str, Form()] = "",
    MediaContentType0: Annotated[str, Form()] = "",
    Latitude: Annotated[str, Form()] = "",
    Longitude: Annotated[str, Form()] = "",
    MessageSid: Annotated[str, Form()] = "",
    x_twilio_signature: Annotated[str | None, Header(alias="X-Twilio-Signature")] = None,
) -> Response:
    """
    Receives inbound WhatsApp messages from Twilio Sandbox.

    Primary delivery: TwiML <Message> in this HTTP response (reliable on Sandbox).
    Voice notes (TTS) still go out via REST in a background task.
    """
    form = await request.form()
    form_dict = {k: str(v) for k, v in form.items()}
    logger.info(
        "Webhook POST received keys=%s from=%s sid=%s",
        list(form_dict.keys()),
        form_dict.get("From"),
        form_dict.get("MessageSid"),
    )
    _validate_twilio_signature(request, form_dict, x_twilio_signature)

    if is_duplicate_message(MessageSid or None):
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml",
        )

    if is_rate_limited(From or None):
        return _twiml_message(RATE_LIMIT_REPLY_HI)

    try:
        num_media = int(NumMedia or "0")
    except ValueError:
        num_media = 0

    message_type = detect_message_type(
        body=Body or "",
        num_media=num_media,
        media_content_type=MediaContentType0 or None,
        latitude=Latitude or None,
        longitude=Longitude or None,
    )

    incoming = IncomingMessage(
        from_number=From,
        body=Body or "",
        message_type=message_type,
        media_url=MediaUrl0 or None,
        media_content_type=MediaContentType0 or None,
        latitude=float(Latitude) if Latitude else None,
        longitude=float(Longitude) if Longitude else None,
        raw={
            "MessageSid": MessageSid,
            "NumMedia": num_media,
        },
    )

    _LAST_HIT.update(
        {
            "at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "from": From,
            "type": message_type.value,
            "sid": MessageSid,
            "body": (Body or "")[:120],
        }
    )

    logger.info(
        "Inbound WhatsApp type=%s from=%s body=%r media_url=%s sid=%s",
        incoming.message_type.value,
        incoming.from_number,
        (incoming.body[:120] + "…") if len(incoming.body) > 120 else incoming.body,
        incoming.media_url,
        MessageSid,
    )

    # Heavy media: ack quickly, finish via REST (avoids Twilio 15s webhook timeout)
    if message_type in {MessageType.IMAGE, MessageType.AUDIO}:
        background_tasks.add_task(_process_and_reply_rest, incoming)
        if message_type == MessageType.IMAGE:
            return _twiml_message(
                "📸 फोटो मिल गई। फसल जांच रहा हूँ — कुछ सेकंड में पूरा जवाब भेजूँगा।"
            )
        return _twiml_message(
            "🎙️ वॉइस नोट मिल गया। सुन/समझ रहा हूँ — कुछ सेकंड में जवाब भेजूँगा।"
        )

    # Text / location: answer inside TwiML (most reliable)
    try:
        reply = await asyncio.wait_for(handle_incoming(incoming), timeout=12.0)
    except asyncio.TimeoutError:
        logger.warning("AI timed out — falling back to REST follow-up")
        background_tasks.add_task(_process_and_reply_rest, incoming)
        return _twiml_message("⏳ जवाब तैयार हो रहा है, एक पल में भेज रहा हूँ…")
    except Exception:
        logger.exception("Orchestrator failed in webhook")
        return _twiml_message(
            "माफ़ कीजिए, अभी जवाब नहीं दे पाए। कृपया फिर से लिखें।"
        )

    if reply.send_voice and incoming.from_number:
        background_tasks.add_task(_maybe_send_voice, incoming.from_number, reply)

    return _twiml_message(reply.text)
