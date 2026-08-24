"""Quick live check: Agmarknet fetch + Hindi formatter.

  python -m scripts.test_mandi
  python -m scripts.test_mandi --commodity Onion --state Maharashtra
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

from app.config import get_settings
from app.db_sa import get_session_factory, init_sqlalchemy
from app.handlers.mandi_handler import handle_mandi_query
from app.services.mandi_client import MandiClient


async def _run(commodity: str, state: str | None) -> int:
    settings = get_settings()
    print("data_gov_configured:", settings.data_gov_configured)
    if not settings.data_gov_configured:
        print("Set DATA_GOV_IN_API_KEY in .env")
        return 1
    init_sqlalchemy()
    session = get_session_factory()()
    try:
        client = MandiClient(session)
        result = await client.get_prices(commodity, state, None)
        print("source:", result.source)
        print("n:", len(result.records))
        print(json.dumps(result.records[:3], default=str, ensure_ascii=False, indent=2))
    finally:
        session.close()
    query = f"{commodity} mandi bhav"
    if state:
        query = f"{state} {query}"
    print("--- handler ---")
    print(await handle_mandi_query("cli", query))
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = argparse.ArgumentParser()
    parser.add_argument("--commodity", default="Tomato")
    parser.add_argument("--state", default=None)
    args = parser.parse_args()
    return asyncio.run(_run(args.commodity, args.state or None))


if __name__ == "__main__":
    raise SystemExit(main())
