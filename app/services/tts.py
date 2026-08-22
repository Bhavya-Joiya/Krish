"""Text-to-speech via edge-tts (free Hindi neural voices)."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

import edge_tts

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def media_directory(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    path = Path(settings.media_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def synthesize_hindi_mp3(
    text: str,
    *,
    settings: Settings | None = None,
) -> Path:
    """
    Convert reply text to an MP3 file under media/.
    Returns the filesystem path to the generated file.
    """
    settings = settings or get_settings()
    cleaned = " ".join((text or "").split())
    if not cleaned:
        raise ValueError("empty text for TTS")

    # Keep WhatsApp voice notes reasonably short
    if len(cleaned) > 600:
        cleaned = cleaned[:600].rsplit(" ", 1)[0] + "…"

    out = media_directory(settings) / f"tts_{uuid.uuid4().hex}.mp3"
    communicate = edge_tts.Communicate(cleaned, settings.tts_voice)
    await communicate.save(str(out))
    logger.info("TTS saved path=%s bytes=%s", out.name, out.stat().st_size)
    return out


def public_media_url(filename: str, *, settings: Settings | None = None) -> str:
    """Build a publicly reachable URL for Twilio to fetch (requires APP_PUBLIC_URL / ngrok)."""
    settings = settings or get_settings()
    base = settings.public_base_url
    if not base:
        raise RuntimeError(
            "APP_PUBLIC_URL is empty — set your ngrok HTTPS URL so Twilio can fetch voice media"
        )
    return f"{base}/media/{filename}"
