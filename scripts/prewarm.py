"""
One-shot demo prewarm helper.

Usage (with server already running):
  .venv\\Scripts\\python.exe scripts\\prewarm.py
  .venv\\Scripts\\python.exe scripts\\prewarm.py --base http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import sys

import httpx


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-warm Smart Crop Bot before demo")
    parser.add_argument("--base", default="http://127.0.0.1:8000", help="API base URL")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    with httpx.Client(timeout=90.0) as client:
        health = client.get(f"{base}/health")
        print("HEALTH:", health.status_code, health.text)
        checklist = client.get(f"{base}/demo/checklist")
        print("CHECKLIST:", json.dumps(checklist.json(), indent=2, ensure_ascii=False))
        prewarm = client.post(f"{base}/demo/prewarm")
        print("PREWARM:", json.dumps(prewarm.json(), indent=2, ensure_ascii=False))

    return 0 if health.is_success else 1


if __name__ == "__main__":
    sys.exit(main())
