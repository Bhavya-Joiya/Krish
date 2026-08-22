"""Seed an OPEN advisory for a demo farmer (Telegram chat id / phone key).

Examples:

  .venv\\Scripts\\python.exe scripts\\seed_advisory.py --farmer-id telegram:123456789
  .venv\\Scripts\\python.exe scripts\\seed_advisory.py --farmer-id telegram:123 --crop टमाटर --title "सिंचाई सलाह"
  .venv\\Scripts\\python.exe scripts\\seed_advisory.py --list
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import init_db
from app.services.repository import create_advisory, list_advisories, list_farmers_with_locations


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed or list OPEN advisories")
    parser.add_argument("--farmer-id", default=None, help="Farmer id, e.g. telegram:123456789")
    parser.add_argument("--title", default="टमाटर सिंचाई सलाह")
    parser.add_argument(
        "--message",
        default="मिट्टी की नमी देखकर सिंचाई करें। अधिक पानी से जड़ सड़न हो सकती है।",
    )
    parser.add_argument("--crop", default="टमाटर")
    parser.add_argument("--type", dest="advisory_type", default="irrigation")
    parser.add_argument("--list", action="store_true", help="List recent advisories and exit")
    parser.add_argument("--list-farmers", action="store_true", help="List farmers with locations")
    args = parser.parse_args()

    init_db()

    if args.list_farmers:
        print(json.dumps(list_farmers_with_locations(), ensure_ascii=False, indent=2))
        return 0

    if args.list:
        print(json.dumps(list_advisories(limit=50), ensure_ascii=False, indent=2))
        return 0

    if not args.farmer_id:
        parser.error("--farmer-id is required unless --list / --list-farmers")

    advisory_id = create_advisory(
        args.farmer_id,
        title=args.title,
        message=args.message,
        crop=args.crop,
        advisory_type=args.advisory_type,
        status="OPEN",
    )
    print(json.dumps({"ok": True, "advisory_id": advisory_id, "farmer_id": args.farmer_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
