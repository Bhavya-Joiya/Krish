"""Groq fallback — vision + chat when Gemini fails."""

from __future__ import annotations

import base64
import logging

from groq import Groq

from app.config import Settings, get_settings
from app.services.prompts import CHAT_SYSTEM, DIAGNOSIS_SYSTEM

logger = logging.getLogger(__name__)


def _client(settings: Settings) -> Groq:
    return Groq(api_key=settings.groq_api_key)


async def groq_diagnose_image(
    jpeg_bytes: bytes,
    *,
    caption: str = "",
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    if not settings.groq_configured:
        raise RuntimeError("GROQ_API_KEY is not configured")

    b64 = base64.b64encode(jpeg_bytes).decode("ascii")
    data_url = f"data:image/jpeg;base64,{b64}"
    prompt = DIAGNOSIS_SYSTEM + "\nAnalyze this crop photo and respond with JSON only."
    if caption.strip():
        prompt += f"\nFarmer caption: {caption.strip()}"

    client = _client(settings)
    completion = client.chat.completions.create(
        model=settings.groq_vision_model,
        temperature=0.2,
        max_tokens=settings.diagnosis_max_output_tokens,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    )
    text = (completion.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("Groq vision returned empty diagnosis")
    logger.info("Groq diagnosis ok chars=%s", len(text))
    return text


async def groq_chat(
    user_text: str,
    *,
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    if not settings.groq_configured:
        raise RuntimeError("GROQ_API_KEY is not configured")

    client = _client(settings)
    completion = client.chat.completions.create(
        model=settings.groq_chat_model,
        temperature=0.4,
        max_tokens=settings.chat_max_output_tokens,
        messages=[
            {"role": "system", "content": CHAT_SYSTEM},
            {"role": "user", "content": user_text.strip()},
        ],
    )
    choice = completion.choices[0]
    text = (choice.message.content or "").strip()
    if not text:
        raise RuntimeError("Groq chat returned empty reply")
    finish = getattr(choice, "finish_reason", None)
    logger.info("Groq chat ok chars=%s finish=%s", len(text), finish)
    return text
