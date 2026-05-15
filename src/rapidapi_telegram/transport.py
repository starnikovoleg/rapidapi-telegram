"""HTTP transport layer.

The client never calls ``requests`` directly. It calls :class:`Transport`,
which is a tiny protocol with one method. The default implementation is
:class:`RequestsTransport`, but users can pass any object that satisfies the
protocol — e.g. an ``httpx``-backed adapter, a record/replay mock, or a
closure-based stub for tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol, runtime_checkable

from .errors import TransportError


@dataclass
class Response:
    """A minimal response envelope.

    ``json`` is the parsed JSON body, or ``None`` for an empty / non-JSON
    response.
    """

    status_code: int
    json: Any


@runtime_checkable
class Transport(Protocol):
    """Protocol every HTTP backend must satisfy."""

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Response: ...


class RequestsTransport:
    """Default transport, backed by the ``requests`` library.

    Pass a pre-configured ``requests.Session`` if you need connection pooling,
    custom adapters, or retries.
    """

    def __init__(self, session: Any = None) -> None:
        try:
            import requests
        except ImportError as exc:
            raise ImportError(
                "rapidapi_telegram's default transport requires the 'requests' "
                "package. Install it with `pip install requests`, or pass a "
                "custom transport= argument to TelegramClient."
            ) from exc
        self._requests = requests
        self._session = session or requests.Session()

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Response:
        try:
            resp = self._session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=timeout,
            )
        except self._requests.RequestException as exc:
            raise TransportError(str(exc)) from exc

        body: Any
        try:
            body = resp.json() if resp.content else None
        except ValueError:
            body = None
        return Response(status_code=resp.status_code, json=body)
