"""Resolve a channel by @username and fetch its full info in one call.

Usage:
    export RAPIDAPI_KEY=your-key
    python examples/get_channel_by_username.py telegram
"""

from __future__ import annotations

import json
import os
import sys

from rapidapi_telegram import NotFoundError, TelegramClient


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python examples/get_channel_by_username.py <username>")
        return 2

    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        print("set RAPIDAPI_KEY first")
        return 2

    client = TelegramClient(api_key=api_key)
    try:
        full = client.get_channel_by_username(sys.argv[1])
    except NotFoundError as exc:
        print(f"not found: {exc.message}")
        return 1

    print(json.dumps(full, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
