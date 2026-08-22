"""Manual / CI-friendly runner for the proactive nudge loop.

Examples (from c:\\Krishi):

  .venv\\Scripts\\python.exe scripts\\test_proactive.py --dry-run
  .venv\\Scripts\\python.exe scripts\\test_proactive.py --force-rain --dry-run
  .venv\\Scripts\\python.exe scripts\\test_proactive.py --farmer-id telegram:123456789
  .venv\\Scripts\\python.exe scripts\\test_proactive.py --force-rain
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import init_db
from app.services.proactive import run_proactive_check


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Run proactive rain+advisory nudge check")
    parser.add_argument(
        "--farmer-id",
        default=None,
        help="Only process this farmer id (e.g. telegram:123456789)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate rules and print message; do NOT send Telegram",
    )
    parser.add_argument(
        "--force-rain",
        action="store_true",
        help="Treat rain as true (demo). Still logs real OpenWeather result when available.",
    )
    args = parser.parse_args()

    init_db()
    result = asyncio.run(
        run_proactive_check(
            dry_run=args.dry_run,
            force_rain=args.force_rain,
            farmer_id=args.farmer_id,
        )
    )
    print(
        json.dumps(
            {
                "farmers_checked": result.farmers_checked,
                "rain_detected_count": result.rain_detected_count,
                "nudges_sent": result.nudges_sent,
                "failures": result.failures,
                "skipped": result.skipped,
                "demo_mode": result.demo_mode,
                "dry_run": result.dry_run,
                "details": result.details,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
