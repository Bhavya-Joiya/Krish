"""Format AI diagnosis JSON into a short WhatsApp-friendly Hindi reply."""

from __future__ import annotations

import json
import re
from typing import Any

from app.services.prompts import NEED_CLEAR_PHOTO_HI


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def format_diagnosis_reply(raw_model_text: str) -> str:
    """Turn model output (JSON or free text) into a farmer-facing reply."""
    data = _extract_json(raw_model_text)
    if not data:
        # Model returned plain text — use it if non-empty
        cleaned = raw_model_text.strip()
        return cleaned[:900] if cleaned else NEED_CLEAR_PHOTO_HI

    if data.get("is_crop") is False:
        return str(data.get("explanation_hi") or NEED_CLEAR_PHOTO_HI).strip()

    disease = str(data.get("disease_or_pest") or "अस्पष्ट समस्या").strip()
    crop = str(data.get("crop_guess") or "").strip()
    confidence = str(data.get("confidence") or "").strip()
    explanation = str(data.get("explanation_hi") or "").strip()
    actions = data.get("actions_hi") or []
    caution = str(data.get("caution_hi") or "").strip()

    lines: list[str] = []
    header = f"🌱 निदान: {disease}"
    if crop and crop.lower() not in {"unknown", "अज्ञात"}:
        header += f"\nफसल: {crop}"
    if confidence:
        conf_map = {"high": "उच्च", "medium": "मध्यम", "low": "कम"}
        header += f"\nविश्वास: {conf_map.get(confidence.lower(), confidence)}"
    lines.append(header)

    if explanation:
        lines.append(explanation)

    if isinstance(actions, list) and actions:
        lines.append("क्या करें:")
        for i, step in enumerate(actions[:4], start=1):
            lines.append(f"{i}. {str(step).strip()}")

    if caution:
        lines.append(f"⚠️ {caution}")

    reply = "\n".join(lines).strip()
    return reply[:1200] if reply else NEED_CLEAR_PHOTO_HI
