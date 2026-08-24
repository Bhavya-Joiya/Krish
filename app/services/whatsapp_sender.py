"""Green-API WhatsApp sender (Kisan Mitra)."""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class WhatsAppSender:
    """Send text messages through a Green-API instance."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def _send_url(self) -> str:
        return self.settings.green_api_url("sendMessage")

    async def send_message(self, chat_id: str, text: str) -> bool:
        """POST `{host}/waInstance{id}/sendMessage/{token}` with chatId + message."""
        if not self.settings.green_api_configured:
            logger.error("Green-API is not configured — cannot send WhatsApp message")
            return False
        target = (chat_id or "").strip()
        body = (text or "").strip()
        if not target or not body:
            logger.warning("WhatsApp send skipped — empty chat_id or text")
            return False

        timeout = httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=10.0)
        payload = {"chatId": target, "message": body}
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self._send_url(), json=payload)
                response.raise_for_status()
                data = response.json() if response.content else {}
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Green-API sendMessage HTTP %s chat=%s body=%s",
                exc.response.status_code,
                target,
                (exc.response.text or "")[:300],
            )
            return False
        except httpx.HTTPError:
            logger.exception("Green-API sendMessage network error chat=%s", target)
            return False
        except Exception:
            logger.exception("Green-API sendMessage unexpected error chat=%s", target)
            return False

        message_id = ""
        if isinstance(data, dict):
            message_id = str(data.get("idMessage") or data.get("id") or "")
        logger.info("WhatsApp sent chat=%s idMessage=%s chars=%s", target, message_id, len(body))
        return True


_sender: WhatsAppSender | None = None


def get_whatsapp_sender() -> WhatsAppSender:
    global _sender
    if _sender is None:
        _sender = WhatsAppSender()
    return _sender
