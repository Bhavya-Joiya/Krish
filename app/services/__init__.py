"""Service package — import submodules directly to avoid heavy side effects."""

from __future__ import annotations

from typing import Any

__all__ = [
    "IncomingMessage",
    "MessageType",
    "BotReply",
    "send_telegram_text",
    "send_telegram_audio",
    "handle_incoming",
]


def __getattr__(name: str) -> Any:
    if name in {"IncomingMessage", "MessageType"}:
        from app.services.message_types import IncomingMessage, MessageType

        return IncomingMessage if name == "IncomingMessage" else MessageType
    if name in {"send_telegram_text", "send_telegram_audio"}:
        from app.services.messaging import send_telegram_audio, send_telegram_text

        return send_telegram_text if name == "send_telegram_text" else send_telegram_audio
    if name in {"BotReply", "handle_incoming"}:
        from app.services.orchestrator import BotReply, handle_incoming

        return BotReply if name == "BotReply" else handle_incoming
    raise AttributeError(name)
