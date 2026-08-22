"""Incoming message models and type detection (Phase 1)."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    LOCATION = "location"
    UNKNOWN = "unknown"


class IncomingMessage(BaseModel):
    """Normalized inbound message from WhatsApp or Web Chat."""

    from_number: str = Field(..., description="Sender id, e.g. whatsapp:+91...")
    body: str = ""
    message_type: MessageType = MessageType.UNKNOWN
    media_url: str | None = None
    media_content_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


def detect_message_type(
    *,
    body: str,
    num_media: int,
    media_content_type: str | None,
    latitude: str | None,
    longitude: str | None,
) -> MessageType:
    if latitude and longitude:
        return MessageType.LOCATION

    if num_media > 0 and media_content_type:
        ctype = media_content_type.lower()
        if ctype.startswith("image/"):
            return MessageType.IMAGE
        if ctype.startswith("audio/") or ctype in {"audio/ogg", "audio/opus"}:
            return MessageType.AUDIO
        # Some WhatsApp voice notes arrive as application/ogg
        if "ogg" in ctype or "opus" in ctype:
            return MessageType.AUDIO

    if body and body.strip():
        return MessageType.TEXT

    return MessageType.UNKNOWN


PHASE1_ACK_BY_TYPE: dict[MessageType, str] = {
    MessageType.TEXT: (
        "नमस्ते किसान भाई! 👋\n"
        "आपका संदेश मिल गया। Smart Crop Bot जल्द फसल सलाह देना शुरू करेगा।\n"
        "(Phase 1 — चैनल टेस्ट सफल ✅)"
    ),
    MessageType.IMAGE: (
        "फसल की फोटो मिल गई! 📸\n"
        "Phase 2 में AI बीमारी पहचान करेगा। अभी सिर्फ चैनल टेस्ट है।\n"
        "धन्यवाद!"
    ),
    MessageType.AUDIO: (
        "आपका वॉइस नोट मिल गया! 🎙️\n"
        "Phase 3 में हम इसे सुनकर जवाब देंगे। अभी सिर्फ चैनल टेस्ट है।"
    ),
    MessageType.LOCATION: (
        "लोकेशन मिल गई! 📍\n"
        "Phase 4 में इससे मौसम की जानकारी देंगे। अभी सिर्फ चैनल टेस्ट है।"
    ),
    MessageType.UNKNOWN: (
        "संदेश मिल गया, पर प्रकार समझ नहीं आया।\n"
        "कृपया टेक्स्ट, फोटो, या वॉइस नोट भेजें।"
    ),
}


def ack_for(message_type: MessageType) -> str:
    return PHASE1_ACK_BY_TYPE.get(
        message_type, PHASE1_ACK_BY_TYPE[MessageType.UNKNOWN]
    )
