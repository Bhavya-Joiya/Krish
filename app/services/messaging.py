"""Outbound messaging via Twilio WhatsApp API."""

from __future__ import annotations

import logging

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _client(settings: Settings | None = None) -> Client:
    settings = settings or get_settings()
    if not settings.twilio_configured:
        raise RuntimeError(
            "Twilio is not configured. Set TWILIO_ACCOUNT_SID and "
            "TWILIO_AUTH_TOKEN in your .env file."
        )
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


def _normalize_to(to: str) -> str:
    if not to.startswith("whatsapp:"):
        return f"whatsapp:{to}"
    return to


def send_whatsapp_text(
    to: str,
    body: str,
    *,
    settings: Settings | None = None,
) -> str | None:
    """Send a WhatsApp text message via Twilio. Returns message SID."""
    settings = settings or get_settings()

    if not settings.twilio_configured:
        logger.warning("Twilio not configured — skipping send to %s: %s", to, body)
        return None

    to = _normalize_to(to)

    try:
        client = _client(settings)
        message = client.messages.create(
            from_=settings.twilio_whatsapp_from,
            to=to,
            body=body,
        )
        logger.info("Sent WhatsApp text sid=%s to=%s", message.sid, to)
        return message.sid
    except TwilioRestException as exc:
        logger.error("Twilio text send failed: %s", exc)
        raise


def send_whatsapp_audio(
    to: str,
    media_url: str,
    *,
    body: str | None = None,
    settings: Settings | None = None,
) -> str | None:
    """
    Send a WhatsApp audio/voice media message.
    `media_url` must be publicly reachable by Twilio (ngrok /media/...).
    """
    settings = settings or get_settings()

    if not settings.twilio_configured:
        logger.warning("Twilio not configured — skipping audio to %s", to)
        return None

    to = _normalize_to(to)

    try:
        client = _client(settings)
        kwargs: dict = {
            "from_": settings.twilio_whatsapp_from,
            "to": to,
            "media_url": [media_url],
        }
        if body:
            kwargs["body"] = body
        message = client.messages.create(**kwargs)
        logger.info("Sent WhatsApp audio sid=%s to=%s url=%s", message.sid, to, media_url)
        return message.sid
    except TwilioRestException as exc:
        logger.error("Twilio audio send failed: %s", exc)
        raise
