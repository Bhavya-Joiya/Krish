"""Offline unit checks for proactive rain rule + message builder (no network)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.services.forecast import evaluate_rain_next_hours
from app.services.proactive import build_nudge_message


def _fake_forecast(points: list[dict]) -> dict:
    return {"list": points}


def main() -> int:
    now = int(time.time())
    settings = Settings(
        proactive_lookahead_hours=24,
        proactive_rain_pop_threshold=0.40,
        proactive_rain_mm_threshold=1.0,
    )

    # No rain
    no_rain = evaluate_rain_next_hours(
        _fake_forecast(
            [
                {
                    "dt": now + 3600,
                    "pop": 0.1,
                    "rain": {},
                    "weather": [{"main": "Clear", "description": "clear sky"}],
                }
            ]
        ),
        settings=settings,
        now_ts=now,
    )
    assert no_rain.rain_expected is False, no_rain

    # Rain by pop
    by_pop = evaluate_rain_next_hours(
        _fake_forecast(
            [
                {
                    "dt": now + 7200,
                    "pop": 0.55,
                    "rain": {},
                    "weather": [{"main": "Clouds", "description": "clouds"}],
                }
            ]
        ),
        settings=settings,
        now_ts=now,
    )
    assert by_pop.rain_expected is True, by_pop

    # Rain by mm
    by_mm = evaluate_rain_next_hours(
        _fake_forecast(
            [
                {
                    "dt": now + 10800,
                    "pop": 0.1,
                    "rain": {"3h": 2.5},
                    "weather": [{"main": "Clouds", "description": "clouds"}],
                }
            ]
        ),
        settings=settings,
        now_ts=now,
    )
    assert by_mm.rain_expected is True, by_mm

    # Rain by label
    by_label = evaluate_rain_next_hours(
        _fake_forecast(
            [
                {
                    "dt": now + 14400,
                    "pop": 0.0,
                    "rain": {},
                    "weather": [{"main": "Rain", "description": "light rain"}],
                }
            ]
        ),
        settings=settings,
        now_ts=now,
    )
    assert by_label.rain_expected is True, by_label

    # Outside window ignored
    outside = evaluate_rain_next_hours(
        _fake_forecast(
            [
                {
                    "dt": now + 40 * 3600,
                    "pop": 0.9,
                    "rain": {"3h": 5},
                    "weather": [{"main": "Rain", "description": "rain"}],
                }
            ]
        ),
        settings=settings,
        now_ts=now,
    )
    assert outside.rain_expected is False, outside

    msg = build_nudge_message(
        [
            {
                "id": 1,
                "title": "टमाटर सिंचाई सलाह",
                "crop": "टमाटर",
                "message": "test",
            }
        ],
        lookahead_hours=24,
        demo_mode=True,
    )
    assert "DEMO MODE" in msg
    assert "बारिश" in msg
    assert "टमाटर" in msg

    # Boolean matrix documentation in assert form
    cases = [
        (False, False, False),
        (False, True, False),
        (True, False, False),
        (True, True, True),
    ]
    for rain, open_adv, expect_nudge in cases:
        assert (rain and open_adv) is expect_nudge

    print("OK: proactive offline rule tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
