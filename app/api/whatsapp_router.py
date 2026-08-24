"""Green-API WhatsApp webhook — Kisan Mitra."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from app.config import get_settings
from app.services.ai_agent import get_ai_agent
from app.services.whatsapp_sender import get_whatsapp_sender

logger = logging.getLogger(__name__)

router = APIRouter(tags=["whatsapp"])

_FALLBACK_REPLY = (
    "Namaste kisan bhai! 🌾 Abhi jawaab nahi de paya. "
    "Kripya thodi der baad phir se likhein."
)


def _unwrap_payload(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    body = raw.get("body")
    if isinstance(body, dict) and ("typeWebhook" in body or "senderData" in body):
        return body
    return raw


def extract_chat_id(payload: dict[str, Any]) -> str:
    sender = payload.get("senderData") if isinstance(payload.get("senderData"), dict) else {}
    for key in ("chatId", "sender"):
        value = str(sender.get(key) or "").strip()
        if value:
            return value
    return str(payload.get("chatId") or "").strip()


def extract_message_text(payload: dict[str, Any]) -> str:
    """Support textMessageData.textMessage and extendedTextMessageData.text."""
    message = payload.get("messageData") if isinstance(payload.get("messageData"), dict) else {}
    text_block = message.get("textMessageData") if isinstance(message.get("textMessageData"), dict) else {}
    extended = (
        message.get("extendedTextMessageData")
        if isinstance(message.get("extendedTextMessageData"), dict)
        else {}
    )
    candidates = [
        text_block.get("textMessage"),
        extended.get("text"),
        extended.get("textMessage"),
        message.get("textMessage"),
        payload.get("message"),
    ]
    for item in candidates:
        if isinstance(item, str) and item.strip():
            return item.strip()
    return ""


async def _process_and_reply(chat_id: str, text: str) -> None:
    try:
        reply = await get_ai_agent().process_message(text)
    except Exception:
        logger.exception("Kisan Mitra agent failed chat=%s", chat_id)
        reply = _FALLBACK_REPLY
    if not (reply or "").strip():
        reply = _FALLBACK_REPLY
    try:
        ok = await get_whatsapp_sender().send_message(chat_id, reply)
        if not ok:
            logger.error("WhatsApp reply not delivered chat=%s", chat_id)
    except Exception:
        logger.exception("WhatsApp send failed chat=%s", chat_id)


@router.post("/webhook/green-api/set-webhook")
async def set_green_api_webhook():
    """Point this Green-API instance at APP_PUBLIC_URL/webhook/green-api."""
    settings = get_settings()
    if not settings.green_api_configured:
        raise HTTPException(status_code=400, detail="Green-API credentials are not configured")
    if not settings.public_base_url:
        raise HTTPException(status_code=400, detail="APP_PUBLIC_URL is not configured")

    webhook_url = f"{settings.public_base_url}/webhook/green-api"
    payload = {
        "webhookUrl": webhook_url,
        "incomingWebhook": "yes",
        "outgoingWebhook": "no",
        "outgoingAPIMessageWebhook": "no",
        "stateWebhook": "no",
        "incomingBlockWebhook": "no",
        "incomingCallWebhook": "no",
    }
    timeout = httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=10.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(settings.green_api_url("setSettings"), json=payload)
            response.raise_for_status()
            result = response.json() if response.content else {}
    except httpx.HTTPError as exc:
        logger.exception("Green-API setSettings failed")
        raise HTTPException(status_code=502, detail=f"Green-API setSettings failed: {exc}") from exc

    return {"ok": True, "webhook_url": webhook_url, "green_api": result}


@router.post("/webhook/green-api")
async def green_api_webhook(request: Request, background_tasks: BackgroundTasks) -> dict[str, str]:
    """Inbound Green-API notifications. Always 200 so Green-API does not retry."""
    try:
        raw = await request.json()
    except Exception:
        logger.warning("Green-API webhook with non-JSON body")
        return {"status": "ok"}

    payload = _unwrap_payload(raw)
    type_webhook = str(payload.get("typeWebhook") or "").strip()
    if type_webhook != "incomingMessageReceived":
        return {"status": "ignored"}

    chat_id = extract_chat_id(payload)
    if not chat_id or chat_id.endswith("@g.us"):
        logger.info("Green-API ignored — missing chatId or group chat")
        return {"status": "ignored"}

    text = extract_message_text(payload)
    if not text:
        logger.info("Green-API ignored — no text chat=%s", chat_id)
        return {"status": "ignored"}

    logger.info(
        "WhatsApp inbound chat=%s body=%r",
        chat_id,
        (text[:120] + "…") if len(text) > 120 else text,
    )
    background_tasks.add_task(_process_and_reply, chat_id, text)
    return {"status": "ok"}
