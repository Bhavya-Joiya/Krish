"""Hardcoded / demo mandi price samples for Phase 4."""

from __future__ import annotations

from datetime import date

# Demo sample prices (₹/quintal) — hackathon MVP, not live AGMARKNET
_MANDI_SAMPLES: dict[str, list[dict[str, str | int]]] = {
    "azadpur": [
        {"crop": "टमाटर (Tomato)", "price": 1800},
        {"crop": "प्याज (Onion)", "price": 2200},
        {"crop": "आलू (Potato)", "price": 1400},
        {"crop": "गेहूँ (Wheat)", "price": 2450},
    ],
    "nashik": [
        {"crop": "प्याज (Onion)", "price": 2100},
        {"crop": "टमाटर (Tomato)", "price": 1600},
        {"crop": "अंगूर (Grapes)", "price": 4500},
    ],
}


def format_mandi_reply(query: str = "") -> str:
    today = date.today().strftime("%d-%m-%Y")
    q = (query or "").lower()

    crop_hints: list[str] = []
    mapping = [
        (("टमाटर", "tomato"), "टमाटर"),
        (("प्याज", "onion"), "प्याज"),
        (("आलू", "potato"), "आलू"),
        (("गेहूं", "गेहूँ", "wheat"), "गेहूँ"),
        (("अंगूर", "grape"), "अंगूर"),
    ]
    for keys, label in mapping:
        if any(k in q for k in keys):
            crop_hints.append(label)

    def build(filter_crops: bool) -> str:
        lines = [
            f"🏷 मंडी भाव (डेमो सैंपल) — {today}",
            "नोट: लाइव AGMARKNET नहीं — हैकथॉन डेमो डेटा।",
            "",
        ]
        price_count = 0
        for mandi_key, title in (("azadpur", "आज़ादपुर (दिल्ली)"), ("nashik", "नाशिक")):
            lines.append(f"• {title}")
            for row in _MANDI_SAMPLES[mandi_key]:
                crop = str(row["crop"])
                if filter_crops and crop_hints and not any(h in crop for h in crop_hints):
                    continue
                lines.append(f"  - {crop}: ₹{row['price']}/क्विंटल")
                price_count += 1
            lines.append("")
        lines.append("बेचने से पहले स्थानीय मंडी भाव ज़रूर चेक करें।")
        return "\n".join(lines).strip(), price_count

    text, count = build(filter_crops=True)
    if count == 0:
        text, _ = build(filter_crops=False)
    return text
