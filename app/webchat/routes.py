"""Web Chat fallback — text, image URL, and demo location (no voice upload)."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.services.message_types import IncomingMessage, MessageType, detect_message_type
from app.services.orchestrator import handle_incoming

logger = logging.getLogger(__name__)

WEBCHAT_NO_AUDIO_HI = (
    "वॉइस नोट Web Chat backup में उपलब्ध नहीं है। "
    "कृपया सवाल टेक्स्ट में लिखें, या WhatsApp sandbox पर वॉइस भेजें।"
)

router = APIRouter(tags=["webchat"])
templates = Jinja2Templates(directory="app/templates")


class WebChatRequest(BaseModel):
    from_number: str = Field(default="web:+910000000000")
    body: str = ""
    message_type: str = "text"
    media_url: str | None = None
    media_content_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class WebChatResponse(BaseModel):
    ok: bool
    detected_type: str
    reply: str
    send_voice: bool = False
    transcript: str | None = None


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(
        request,
        "chat.html",
        {"title": "Smart Crop Bot — Web Chat"},
    )


@router.post("/api/webchat", response_model=WebChatResponse)
async def webchat_api(payload: WebChatRequest) -> WebChatResponse:
    """JSON API used by the browser chat fallback."""
    explicit = payload.message_type.lower().strip()
    if explicit in {t.value for t in MessageType}:
        message_type = MessageType(explicit)
    else:
        message_type = detect_message_type(
            body=payload.body,
            num_media=1 if payload.media_url else 0,
            media_content_type=payload.media_content_type,
            latitude=str(payload.latitude) if payload.latitude is not None else None,
            longitude=str(payload.longitude) if payload.longitude is not None else None,
        )

    if message_type == MessageType.AUDIO:
        logger.info("WebChat rejected audio from=%s", payload.from_number)
        return WebChatResponse(
            ok=True,
            detected_type=MessageType.TEXT.value,
            reply=WEBCHAT_NO_AUDIO_HI,
        )

    incoming = IncomingMessage(
        from_number=payload.from_number,
        body=payload.body,
        message_type=message_type,
        media_url=payload.media_url,
        media_content_type=payload.media_content_type,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )

    reply = await handle_incoming(incoming)
    logger.info(
        "WebChat type=%s from=%s → reply chars=%s voice=%s",
        incoming.message_type.value,
        incoming.from_number,
        len(reply.text),
        reply.send_voice,
    )
    return WebChatResponse(
        ok=True,
        detected_type=incoming.message_type.value,
        reply=reply.text,
        send_voice=reply.send_voice,
        transcript=reply.transcript,
    )


@router.post("/api/webchat/form", response_model=WebChatResponse)
async def webchat_form(
    body: Annotated[str, Form()] = "",
    message_type: Annotated[str, Form()] = "text",
    from_number: Annotated[str, Form()] = "web:+910000000000",
) -> WebChatResponse:
    return await webchat_api(
        WebChatRequest(from_number=from_number, body=body, message_type=message_type)
    )
