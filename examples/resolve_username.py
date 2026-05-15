"""Resolve a public Telegram @username.

Usage:
    export RAPIDAPI_KEY=your-key
    python examples/resolve_username.py durov
"""

from __future__ import annotations

import json
import os
import sys

from rapidapi_telegram import TelegramClient


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python examples/resolve_username.py <username>")
        return 2

    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        print("set RAPIDAPI_KEY first")
        return 2

    client = TelegramClient(api_key=api_key)
    envelope = client.resolve_username(sys.argv[1])
    print(json.dumps(envelope, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
