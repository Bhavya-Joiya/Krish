"""Validate and resize crop photos with Pillow."""

from __future__ import annotations

import io
import logging

from PIL import Image, UnidentifiedImageError

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class ImageValidationError(ValueError):
    """Raised when inbound bytes are not a usable image."""


def prepare_image_jpeg(
    raw: bytes,
    *,
    settings: Settings | None = None,
) -> bytes:
    """
    Validate image bytes, convert to RGB JPEG, and cap dimensions.

    Returns JPEG bytes suitable for vision APIs.
    """
    settings = settings or get_settings()

    if not raw:
        raise ImageValidationError("empty image")
    if len(raw) > settings.max_image_bytes:
        raise ImageValidationError(
            f"image too large ({len(raw)} bytes > {settings.max_image_bytes})"
        )

    try:
        with Image.open(io.BytesIO(raw)) as img:
            img.load()
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            elif img.mode == "L":
                img = img.convert("RGB")

            max_dim = settings.max_image_dimension
            w, h = img.size
            if max(w, h) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                logger.info("Resized image from %sx%s to %sx%s", w, h, *img.size)

            out = io.BytesIO()
            img.save(out, format="JPEG", quality=85, optimize=True)
            jpeg = out.getvalue()
            logger.info("Prepared JPEG bytes=%s", len(jpeg))
            return jpeg
    except UnidentifiedImageError as exc:
        raise ImageValidationError("not a valid image file") from exc
    except OSError as exc:
        raise ImageValidationError(f"could not process image: {exc}") from exc
