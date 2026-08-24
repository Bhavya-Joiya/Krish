"""Offline checks for Agmarknet NR sanitization (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.mandi_client import parse_price


def test_parse_price_skips_nr() -> None:
    assert parse_price("NR") is None
    assert parse_price("nr") is None
    assert parse_price("NA") is None
    assert parse_price("-") is None
    assert parse_price("") is None
    assert parse_price(None) is None


def test_parse_price_numbers() -> None:
    assert parse_price("1800") == 1800.0
    assert parse_price("1,800") == 1800.0
    assert parse_price(2200) == 2200.0


if __name__ == "__main__":
    test_parse_price_skips_nr()
    test_parse_price_numbers()
    print("OK: NR sanitization")
