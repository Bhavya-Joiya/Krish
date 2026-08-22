"""Pre-warm external AI clients before a live demo."""

from __future__ import annotations

import logging
from typing import Any

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


async def prewarm_services(settings: Settings | None = None) -> dict[str, Any]:
    """
    Hit Gemini / Groq lightly so cold starts don't delay the first demo message.
    Never raises — returns a status map.
    """
    settings = settings or get_settings()
    status: dict[str, Any] = {
        "gemini": "skipped",
        "groq": "skipped",
        "tts": "skipped",
    }

    if settings.gemini_configured:
        try:
            from app.services.gemini_client import gemini_chat

            text = await gemini_chat("नमस्ते — सिर्फ टेस्ट। एक शब्द में जवाब दो।", settings=settings)
            status["gemini"] = "ok" if text else "empty"
        except Exception as exc:
            logger.warning("Gemini prewarm failed: %s", exc)
            status["gemini"] = f"fail:{type(exc).__name__}"

    if settings.groq_configured:
        try:
            from app.services.groq_client import groq_chat

            text = await groq_chat("hello — reply with one word ok", settings=settings)
            status["groq"] = "ok" if text else "empty"
        except Exception as exc:
            logger.warning("Groq prewarm failed: %s", exc)
            status["groq"] = f"fail:{type(exc).__name__}"

    if settings.tts_enabled:
        try:
            from app.services.tts import synthesize_hindi_mp3

            path = await synthesize_hindi_mp3("स्मार्ट क्रॉप बॉट तैयार है।", settings=settings)
            status["tts"] = "ok" if path.exists() else "missing"
        except Exception as exc:
            logger.warning("TTS prewarm failed: %s", exc)
            status["tts"] = f"fail:{type(exc).__name__}"

    return status
