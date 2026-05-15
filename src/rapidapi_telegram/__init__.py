"""Python client for the Telegram metadata API on RapidAPI."""

from ._version import __version__
from .client import DEFAULT_API_HOST, TelegramClient
from .errors import (
    BadRequestError,
    GatewayTimeoutError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    TelegramAPIError,
    TransportError,
)
from .transport import RequestsTransport, Response, Transport

__all__ = [
    "__version__",
    "DEFAULT_API_HOST",
    "TelegramClient",
    "Transport",
    "Response",
    "RequestsTransport",
    "TelegramAPIError",
    "BadRequestError",
    "NotFoundError",
    "RateLimitError",
    "ServiceUnavailableError",
    "GatewayTimeoutError",
    "TransportError",
]
