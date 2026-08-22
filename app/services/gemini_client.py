"""Google Gemini client — primary vision + text for Phase 2."""

from __future__ import annotations

import logging

from google import genai
from google.genai import types

from app.config import Settings, get_settings
from app.services.prompts import CHAT_SYSTEM, DIAGNOSIS_SYSTEM

logger = logging.getLogger(__name__)


def _client(settings: Settings) -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def _extract_text(response) -> str:
    """Concatenate visible (non-thought) text parts from a Gemini response."""
    text = (response.text or "").strip()
    if text:
        return text
    parts = response.parts or []
    chunks: list[str] = []
    for part in parts:
        if getattr(part, "thought", None):
            continue
        if isinstance(part.text, str) and part.text.strip():
            chunks.append(part.text.strip())
    return "\n".join(chunks).strip()


def _log_usage(response, *, kind: str) -> None:
    usage = getattr(response, "usage_metadata", None)
    finish = None
    if response.candidates:
        finish = getattr(response.candidates[0], "finish_reason", None)
    if usage or finish:
        logger.info(
            "Gemini %s finish=%s output_tokens=%s thoughts_tokens=%s",
            kind,
            finish,
            getattr(usage, "candidates_token_count", None),
            getattr(usage, "thoughts_token_count", None),
        )


async def gemini_diagnose_image(
    jpeg_bytes: bytes,
    *,
    caption: str = "",
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    if not settings.gemini_configured:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = _client(settings)
    user_bits = [DIAGNOSIS_SYSTEM, "Analyze this crop photo and respond with JSON only."]
    if caption.strip():
        user_bits.append(f"Farmer caption: {caption.strip()}")

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="\n\n".join(user_bits)),
                    types.Part.from_bytes(data=jpeg_bytes, mime_type="image/jpeg"),
                ],
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=settings.diagnosis_max_output_tokens,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )
    text = _extract_text(response)
    if not text:
        raise RuntimeError("Gemini returned empty diagnosis")
    _log_usage(response, kind="diagnosis")
    logger.info("Gemini diagnosis ok chars=%s", len(text))
    return text


async def gemini_chat(
    user_text: str,
    *,
    settings: Settings | None = None,
) -> str:
    settings = settings or get_settings()
    if not settings.gemini_configured:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = _client(settings)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"{CHAT_SYSTEM}\n\nFarmer: {user_text.strip()}"
                    )
                ],
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=settings.chat_max_output_tokens,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )
    text = _extract_text(response)
    if not text:
        raise RuntimeError("Gemini returned empty chat reply")
    _log_usage(response, kind="chat")
    logger.info("Gemini chat ok chars=%s", len(text))
    return text
