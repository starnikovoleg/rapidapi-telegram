"""Paginate through global message search.

Usage:
    export RAPIDAPI_KEY=your-key
    python examples/search_messages.py "bitcoin"
"""

from __future__ import annotations

import json
import os
import sys

from rapidapi_telegram import TelegramClient


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: python examples/search_messages.py "<query>"')
        return 2

    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        print("set RAPIDAPI_KEY first")
        return 2

    client = TelegramClient(api_key=api_key)
    offset_id = None
    for page in range(3):
        envelope = client.search_messages(sys.argv[1], limit=20, offset_id=offset_id)
        messages = envelope.get("messages") or []
        print(f"--- page {page + 1}: {len(messages)} messages ---")
        for m in messages:
            print(json.dumps(m, ensure_ascii=False)[:200])

        if not messages:
            break
        offset_id = messages[-1].get("id")
        if offset_id is None:
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
