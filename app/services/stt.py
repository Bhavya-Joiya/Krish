"""Speech-to-text: Groq Whisper primary, optional faster-whisper local fallback."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from groq import Groq

from app.config import Settings, get_settings
from app.services.audio_convert import convert_to_wav, guess_audio_suffix

logger = logging.getLogger(__name__)

_local_model = None


def _groq_transcribe(
    audio_bytes: bytes,
    *,
    filename: str,
    settings: Settings,
) -> str:
    client = Groq(api_key=settings.groq_api_key)
    transcription = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model=settings.groq_whisper_model,
        language="hi",  # Hindi primary; still handles Hinglish/English well
        response_format="text",
        temperature=0.0,
    )
    # SDK may return str or object with .text
    if isinstance(transcription, str):
        text = transcription
    else:
        text = getattr(transcription, "text", str(transcription))
    return (text or "").strip()


def _local_transcribe(audio_bytes: bytes, *, suffix: str) -> str:
    """Optional local fallback — skipped if faster-whisper is not installed."""
    global _local_model
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError as exc:
        raise RuntimeError("faster-whisper is not installed") from exc

    wav = convert_to_wav(audio_bytes, suffix=suffix)
    if _local_model is None:
        logger.info("Loading local faster-whisper model (base)…")
        _local_model = WhisperModel("base", device="cpu", compute_type="int8")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(wav)
        path = tmp.name
    try:
        segments, _info = _local_model.transcribe(path, language="hi")
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text
    finally:
        Path(path).unlink(missing_ok=True)


async def transcribe_audio(
    audio_bytes: bytes,
    *,
    content_type: str | None = None,
    settings: Settings | None = None,
) -> str:
    """
    Transcribe farmer voice note to text.
    Tries Groq Whisper first (raw bytes), then WAV reconvert, then local faster-whisper.
    """
    settings = settings or get_settings()
    if len(audio_bytes) > settings.max_audio_bytes:
        raise RuntimeError("audio too large")

    suffix = guess_audio_suffix(content_type)
    filename = f"voice{suffix}"
    errors: list[str] = []

    if settings.groq_configured:
        try:
            text = _groq_transcribe(audio_bytes, filename=filename, settings=settings)
            if text:
                logger.info("Groq Whisper ok chars=%s", len(text))
                return text
            errors.append("groq:empty")
        except Exception as exc:
            errors.append(f"groq_raw:{exc}")
            logger.warning("Groq Whisper (raw) failed: %s", exc)

        # Retry after converting to wav
        try:
            wav = convert_to_wav(audio_bytes, suffix=suffix)
            text = _groq_transcribe(wav, filename="voice.wav", settings=settings)
            if text:
                logger.info("Groq Whisper (wav) ok chars=%s", len(text))
                return text
            errors.append("groq_wav:empty")
        except Exception as exc:
            errors.append(f"groq_wav:{exc}")
            logger.warning("Groq Whisper (wav) failed: %s", exc)

    try:
        text = _local_transcribe(audio_bytes, suffix=suffix)
        if text:
            logger.info("Local Whisper ok chars=%s", len(text))
            return text
        errors.append("local:empty")
    except Exception as exc:
        errors.append(f"local:{exc}")
        logger.warning("Local Whisper unavailable/failed: %s", exc)

    logger.error("All STT providers failed: %s", errors)
    raise RuntimeError("speech-to-text failed")
