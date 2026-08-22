"""Audio format helpers using bundled imageio-ffmpeg (no system ffmpeg required)."""

from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def get_ffmpeg_exe() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def convert_to_wav(audio_bytes: bytes, *, suffix: str = ".ogg") -> bytes:
    """
    Convert arbitrary audio bytes to 16kHz mono WAV for STT fallbacks.
    Primary Groq Whisper usually accepts ogg/opus directly — use this if needed.
    """
    ffmpeg = get_ffmpeg_exe()
    with tempfile.TemporaryDirectory(prefix="scb_audio_") as tmp:
        src = Path(tmp) / f"in{suffix}"
        dst = Path(tmp) / "out.wav"
        src.write_bytes(audio_bytes)
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(src),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            str(dst),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0 or not dst.exists():
            logger.error("ffmpeg failed: %s", proc.stderr[-500:] if proc.stderr else "")
            raise RuntimeError("audio conversion failed")
        return dst.read_bytes()


def guess_audio_suffix(content_type: str | None) -> str:
    ctype = (content_type or "").lower()
    if "mpeg" in ctype or "mp3" in ctype:
        return ".mp3"
    if "wav" in ctype:
        return ".wav"
    if "mp4" in ctype or "m4a" in ctype:
        return ".m4a"
    if "webm" in ctype:
        return ".webm"
    return ".ogg"
