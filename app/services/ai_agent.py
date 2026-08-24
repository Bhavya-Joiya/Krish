"""Kisan Mitra — WhatsApp agriculture agent with mandi tool calling."""

from __future__ import annotations

import logging
import re

from google import genai
from google.genai import types

from app.config import Settings, get_settings
from app.services.groq_client import groq_chat
from app.services.mandi_tool import fetch_mandi_prices, fetch_mandi_prices_sync

logger = logging.getLogger(__name__)

KISAN_MITRA_SYSTEM = """You are Kisan Mitra, a warm, respectful, expert agriculture assistant for Indian farmers.

Language: reply in conversational Hindi or Hinglish (example: "Namaste kisan bhai!").
Keep every message short and easy to read on WhatsApp. Use line breaks. Use emojis 🌾 💰 📍 when they help.

Mandi prices:
- Whenever the farmer asks for crop prices, mandi bhav, or market rates, you MUST call the fetch_mandi_prices tool.
- Never invent prices. Quote only what the tool returns, then add one practical line of advice.
- If the tool has no data, say so honestly and ask them to try another crop or district.

Other questions (pests, fertilizer, sowing, irrigation): give practical, cautious advice. Do not claim you have a live weather reading unless the farmer shared a place. Suggest Telegram for leaf photos and voice notes.

Sign-off: you may use a short "Kisan Mitra 🌾" once, not on every line.
"""

_MANDI_HINT = re.compile(
    r"मंडी|mandi|bhav|भाव|price|rate|भाव\s*क्या|kitna.*bik|bik.*kitna|quintal|क्विंटल",
    re.IGNORECASE,
)

_FALLBACK = (
    "Namaste kisan bhai! 🌾 Main Kisan Mitra hoon. "
    "Abhi jawaab nahi de paya — kripya phir se likhein, "
    "ya mandi bhav ke liye crop ka naam bhejein (jaise tamatar, pyaz)."
)


def _looks_like_mandi(text: str) -> bool:
    return bool(_MANDI_HINT.search(text or ""))


def _extract_text(response) -> str:
    text = (getattr(response, "text", None) or "").strip()
    if text:
        return text
    parts = getattr(response, "parts", None) or []
    chunks: list[str] = []
    for part in parts:
        if getattr(part, "thought", None):
            continue
        if isinstance(getattr(part, "text", None), str) and part.text.strip():
            chunks.append(part.text.strip())
    return "\n".join(chunks).strip()


class AIAgent:
    """Gemini agent with Agmarknet tool calling; Groq + mandi fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def process_message(self, text: str) -> str:
        user_text = (text or "").strip()
        if not user_text:
            return (
                "Namaste kisan bhai! 🌾 Main Kisan Mitra hoon. "
                "Aap crop ka naam, mandi bhav, ya kheti ka sawaal bhej sakte hain."
            )

        if self.settings.gemini_configured:
            try:
                reply = await self._gemini_with_tools(user_text)
                if reply:
                    return reply
            except Exception as exc:
                logger.warning("Kisan Mitra Gemini path failed (%s) — using fallback", exc)

        return await self._fallback(user_text)

    async def _gemini_with_tools(self, user_text: str) -> str:
        client = genai.Client(api_key=self.settings.gemini_api_key)
        chat = client.chats.create(
            model=self.settings.gemini_model,
            config=types.GenerateContentConfig(
                system_instruction=KISAN_MITRA_SYSTEM,
                temperature=0.4,
                max_output_tokens=min(self.settings.chat_max_output_tokens, 2048),
                tools=[fetch_mandi_prices_sync],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
            ),
        )
        response = chat.send_message(user_text)
        text = _extract_text(response)
        if not text:
            raise RuntimeError("Gemini returned empty Kisan Mitra reply")
        logger.info("Kisan Mitra Gemini ok chars=%s", len(text))
        return text

    async def _fallback(self, user_text: str) -> str:
        if _looks_like_mandi(user_text):
            from app.handlers.mandi_handler import parse_state

            return await fetch_mandi_prices(user_text, parse_state(user_text), None)

        if self.settings.groq_configured:
            try:
                prefixed = (
                    "You are Kisan Mitra. Reply in short Hindi/Hinglish for WhatsApp. "
                    f"Farmer: {user_text}"
                )
                return await groq_chat(prefixed, settings=self.settings)
            except Exception:
                logger.exception("Kisan Mitra Groq fallback failed")
        return _FALLBACK


_agent: AIAgent | None = None


def get_ai_agent() -> AIAgent:
    global _agent
    if _agent is None:
        _agent = AIAgent()
    return _agent
