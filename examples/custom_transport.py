"""Swap the default ``requests``-based transport for an ``httpx`` adapter.

The client only depends on a small ``Transport`` protocol — anything with a
``.request(method, url, *, params, headers, timeout) -> Response`` method
will do. Below is a 20-line httpx adapter.

Usage:
    pip install httpx
    export RAPIDAPI_KEY=your-key
    python examples/custom_transport.py durov
"""

from __future__ import annotations

import json
import os
import sys

import httpx

from rapidapi_telegram import Response, TelegramClient


class HttpxTransport:
    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client()

    def request(self, method, url, *, params=None, headers=None, timeout=None):
        resp = self._client.request(
            method, url, params=params, headers=headers, timeout=timeout
        )
        try:
            body = resp.json() if resp.content else None
        except ValueError:
            body = None
        return Response(status_code=resp.status_code, json=body)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python examples/custom_transport.py <username>")
        return 2

    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        print("set RAPIDAPI_KEY first")
        return 2

    client = TelegramClient(api_key=api_key, transport=HttpxTransport())
    print(json.dumps(client.resolve_username(sys.argv[1]), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
