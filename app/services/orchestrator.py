"""Phase 4 orchestrator — voice/photo/text + weather/mandi + persistence hooks."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.config import Settings, get_settings
from app.services.gemini_client import gemini_chat, gemini_diagnose_image
from app.services.groq_client import groq_chat, groq_diagnose_image
from app.services.image_pipeline import ImageValidationError, prepare_image_jpeg
from app.services.intent import Intent, detect_intent
from app.services.mandi import format_mandi_reply
from app.services.media import download_media
from app.services.message_types import IncomingMessage, MessageType, ack_for
from app.services.prompts import (
    FRIENDLY_ERROR_HI,
    LOCATION_SAVED_HI,
    NEED_CLEAR_PHOTO_HI,
    STT_EMPTY_HI,
    STT_FAILED_HI,
)
from app.services.reply_format import format_diagnosis_reply
from app.services.repository import (
    get_farmer_location,
    log_diagnosis,
    log_message,
    upsert_farmer_location,
)
from app.services.stt import transcribe_audio
from app.services.weather import ASK_LOCATION_HI, fetch_weather_hindi

logger = logging.getLogger(__name__)


@dataclass
class BotReply:
    text: str
    send_voice: bool = False
    transcript: str | None = None
    is_diagnosis: bool = False
    meta: dict = field(default_factory=dict)


async def _diagnose(jpeg: bytes, caption: str, settings: Settings) -> str:
    errors: list[str] = []

    if settings.gemini_configured:
        try:
            raw = await gemini_diagnose_image(jpeg, caption=caption, settings=settings)
            return format_diagnosis_reply(raw)
        except Exception as exc:
            errors.append(f"gemini:{exc}")
            logger.warning("Gemini diagnosis failed: %s", exc)

    if settings.groq_configured:
        try:
            raw = await groq_diagnose_image(jpeg, caption=caption, settings=settings)
            return format_diagnosis_reply(raw)
        except Exception as exc:
            errors.append(f"groq:{exc}")
            logger.warning("Groq diagnosis failed: %s", exc)

    if not settings.gemini_configured and not settings.groq_configured:
        return (
            "AI कुंजी सेट नहीं है। कृपया .env में GEMINI_API_KEY "
            "(और वैकल्पिक GROQ_API_KEY) डालें, फिर सर्वर रीस्टार्ट करें।"
        )

    logger.error("All diagnosis providers failed: %s", errors)
    return FRIENDLY_ERROR_HI


async def _general_chat(text: str, settings: Settings) -> str:
    errors: list[str] = []

    if settings.gemini_configured:
        try:
            return await gemini_chat(text, settings=settings)
        except Exception as exc:
            errors.append(f"gemini:{exc}")
            logger.warning("Gemini chat failed: %s", exc)

    if settings.groq_configured:
        try:
            return await groq_chat(text, settings=settings)
        except Exception as exc:
            errors.append(f"groq:{exc}")
            logger.warning("Groq chat failed: %s", exc)

    if not settings.gemini_configured and not settings.groq_configured:
        return (
            "AI कुंजी सेट नहीं है। कृपया .env में GEMINI_API_KEY डालें।\n"
            f"(आपने लिखा: {text[:80]})"
        )

    logger.error("All chat providers failed: %s", errors)
    return FRIENDLY_ERROR_HI


async def _handle_textish(
    text: str,
    *,
    phone: str,
    settings: Settings,
    prefer_voice: bool,
    transcript: str | None = None,
) -> BotReply:
    intent = detect_intent(text)
    logger.info("Intent=%s for phone=%s text=%r", intent.value, phone, text[:80])

    if intent == Intent.WEATHER:
        loc = get_farmer_location(phone) if phone else None
        if not loc:
            return BotReply(ASK_LOCATION_HI, send_voice=prefer_voice, transcript=transcript)
        reply = await fetch_weather_hindi(loc[0], loc[1], settings=settings)
        return BotReply(reply, send_voice=prefer_voice, transcript=transcript)

    if intent == Intent.MANDI:
        return BotReply(
            format_mandi_reply(text),
            send_voice=prefer_voice,
            transcript=transcript,
        )

    answer = await _general_chat(text, settings)
    if transcript:
        return BotReply(
            f"आपने कहा: {transcript}\n\n{answer}",
            send_voice=prefer_voice,
            transcript=transcript,
        )
    return BotReply(answer, send_voice=False)


def _safe_log_inbound(message: IncomingMessage, summary: str) -> None:
    try:
        log_message(
            message.from_number or "unknown",
            direction="inbound",
            message_type=message.message_type.value,
            content_summary=summary,
        )
    except Exception:
        logger.exception("Failed to log inbound message")


def _safe_log_outbound(phone: str, message_type: str, summary: str) -> None:
    try:
        log_message(
            phone or "unknown",
            direction="outbound",
            message_type=message_type,
            content_summary=summary,
        )
    except Exception:
        logger.exception("Failed to log outbound message")


async def handle_incoming(
    message: IncomingMessage,
    *,
    settings: Settings | None = None,
) -> BotReply:
    """
    Produce a farmer-facing reply and persist conversation breadcrumbs.
    """
    settings = settings or get_settings()
    phone = message.from_number or "unknown"

    if message.message_type == MessageType.IMAGE:
        _safe_log_inbound(message, f"image:{message.media_url or ''}"[:200])
        if not message.media_url:
            reply = BotReply(NEED_CLEAR_PHOTO_HI)
            _safe_log_outbound(phone, "text", reply.text)
            return reply
        try:
            raw = await download_media(message.media_url, settings=settings)
            jpeg = prepare_image_jpeg(raw, settings=settings)
        except ImageValidationError:
            logger.warning("Invalid image from %s", phone)
            reply = BotReply(NEED_CLEAR_PHOTO_HI)
            _safe_log_outbound(phone, "text", reply.text)
            return reply
        except Exception:
            logger.exception("Media download failed")
            reply = BotReply(FRIENDLY_ERROR_HI)
            _safe_log_outbound(phone, "text", reply.text)
            return reply

        text = await _diagnose(jpeg, message.body or "", settings)
        try:
            log_diagnosis(phone, text)
        except Exception:
            logger.exception("Failed to log diagnosis")
        reply = BotReply(
            text=text,
            send_voice=bool(settings.tts_enabled and settings.tts_on_diagnosis),
            is_diagnosis=True,
        )
        _safe_log_outbound(phone, "text", reply.text)
        return reply

    if message.message_type == MessageType.AUDIO:
        _safe_log_inbound(message, f"audio:{message.media_url or ''}"[:200])
        if not message.media_url:
            reply = BotReply(STT_FAILED_HI)
            _safe_log_outbound(phone, "text", reply.text)
            return reply
        try:
            audio = await download_media(message.media_url, settings=settings)
            transcript = await transcribe_audio(
                audio,
                content_type=message.media_content_type,
                settings=settings,
            )
        except Exception:
            logger.exception("STT failed")
            reply = BotReply(STT_FAILED_HI)
            _safe_log_outbound(phone, "text", reply.text)
            return reply

        if not transcript:
            reply = BotReply(STT_EMPTY_HI)
            _safe_log_outbound(phone, "text", reply.text)
            return reply

        logger.info("Voice transcript: %r", transcript[:200])
        reply = await _handle_textish(
            transcript,
            phone=phone,
            settings=settings,
            prefer_voice=bool(settings.tts_enabled),
            transcript=transcript,
        )
        _safe_log_outbound(phone, "text", reply.text)
        return reply

    if message.message_type == MessageType.TEXT:
        body = (message.body or "").strip()
        _safe_log_inbound(message, body[:200])
        if not body:
            reply = BotReply(ack_for(MessageType.UNKNOWN))
            _safe_log_outbound(phone, "text", reply.text)
            return reply
        reply = await _handle_textish(
            body,
            phone=phone,
            settings=settings,
            prefer_voice=False,
        )
        _safe_log_outbound(phone, "text", reply.text)
        return reply

    if message.message_type == MessageType.LOCATION:
        _safe_log_inbound(
            message,
            f"loc:{message.latitude},{message.longitude}",
        )
        if message.latitude is None or message.longitude is None:
            reply = BotReply(ASK_LOCATION_HI)
            _safe_log_outbound(phone, "text", reply.text)
            return reply
        try:
            upsert_farmer_location(phone, message.latitude, message.longitude)
        except Exception:
            logger.exception("Failed to save location")
            reply = BotReply(FRIENDLY_ERROR_HI)
            _safe_log_outbound(phone, "text", reply.text)
            return reply
        reply = BotReply(LOCATION_SAVED_HI)
        _safe_log_outbound(phone, "text", reply.text)
        return reply

    reply = BotReply(ack_for(MessageType.UNKNOWN))
    _safe_log_inbound(message, "unknown")
    _safe_log_outbound(phone, "text", reply.text)
    return reply
