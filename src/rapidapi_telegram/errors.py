"""Exceptions raised by ``rapidapi_telegram``.

Every non-2xx HTTP response is mapped to a subclass of :class:`TelegramAPIError`.
Connection / IO failures become :class:`TransportError`.
"""

from __future__ import annotations


class TelegramAPIError(Exception):
    """Base class for all errors raised by the client."""

    def __init__(self, message: str, *, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code}, message={self.message!r})"


class BadRequestError(TelegramAPIError):
    """HTTP 400 — the request was malformed."""


class NotFoundError(TelegramAPIError):
    """HTTP 404 — the requested resource does not exist."""


class RateLimitError(TelegramAPIError):
    """HTTP 429 — quota exceeded."""


class ServiceUnavailableError(TelegramAPIError):
    """HTTP 503 — service temporarily unavailable."""


class GatewayTimeoutError(TelegramAPIError):
    """HTTP 504 — the service timed out before responding."""


class TransportError(TelegramAPIError):
    """The HTTP transport failed before a response was received."""


_STATUS_TO_EXC: dict[int, type[TelegramAPIError]] = {
    400: BadRequestError,
    404: NotFoundError,
    429: RateLimitError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}


def from_status(status_code: int, message: str) -> TelegramAPIError:
    """Build the appropriate exception for ``status_code``."""
    cls = _STATUS_TO_EXC.get(status_code, TelegramAPIError)
    return cls(message, status_code=status_code)
