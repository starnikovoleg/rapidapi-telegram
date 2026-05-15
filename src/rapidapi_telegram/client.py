"""Public client for the Telegram metadata API on RapidAPI.

All twelve endpoints are exposed as plain methods on :class:`TelegramClient`.
Four convenience helpers chain ``resolve_username`` with a follow-up call so
the common "look up by username" path is a single method.

Responses are returned as the parsed JSON dictionary. Non-2xx responses
raise a typed exception from :mod:`rapidapi_telegram.errors`.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional
from urllib.parse import quote

from . import errors
from .transport import RequestsTransport, Response, Transport

DEFAULT_API_HOST = "telegram-public-api.p.rapidapi.com"
DEFAULT_TIMEOUT = 30.0


class TelegramClient:
    """Client for the Telegram metadata API on RapidAPI.

    Parameters
    ----------
    api_key:
        Your RapidAPI key. Sent in the ``X-RapidAPI-Key`` header.
    api_host:
        The RapidAPI host for this API. Sent in the ``X-RapidAPI-Host`` header.
        Defaults to :data:`DEFAULT_API_HOST`.
    base_url:
        If set, fully overrides the request URL's scheme and host (e.g. for
        pointing at a local server during development). When unset, requests
        go to ``https://{api_host}``.
    timeout:
        Per-request timeout in seconds.
    transport:
        Any object that implements :class:`~rapidapi_telegram.transport.Transport`.
        Defaults to :class:`~rapidapi_telegram.transport.RequestsTransport`.
    extra_headers:
        Additional headers merged into every request. Useful when fronting
        the API with a different gateway during testing.
    """

    def __init__(
        self,
        api_key: str,
        *,
        api_host: str = DEFAULT_API_HOST,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: Optional[Transport] = None,
        extra_headers: Optional[dict] = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._api_host = api_host
        self._base_url = (base_url or f"https://{api_host}").rstrip("/")
        self._timeout = timeout
        self._transport: Transport = transport or RequestsTransport()
        self._extra_headers = dict(extra_headers or {})

    # ------------------------------------------------------------------
    # 12 direct endpoint methods
    # ------------------------------------------------------------------

    def resolve_username(self, username: str) -> dict:
        """Look up a public ``@username`` and return its profile envelope."""
        username = username.lstrip("@")
        return self._get(f"/v1/usernames/{quote(username, safe='')}")

    def resolve_phone(self, phone: str) -> dict:
        """Look up a phone number (international format)."""
        return self._get(f"/v1/phones/{quote(phone, safe='')}")

    def search_contacts(self, q: str, *, limit: Optional[int] = None) -> dict:
        """Hybrid contact + global directory search."""
        return self._get("/v1/contacts/search", params=_drop_none(q=q, limit=limit))

    def search_messages(
        self,
        q: str,
        *,
        limit: Optional[int] = None,
        offset_id: Optional[int] = None,
    ) -> dict:
        """Global message search."""
        return self._get(
            "/v1/messages/search",
            params=_drop_none(q=q, limit=limit, offset_id=offset_id),
        )

    def get_user(self, peer_id: int) -> dict:
        """Full user profile for ``peer_id``."""
        return self._get(f"/v1/users/{int(peer_id)}")

    def get_channel(self, peer_id: int) -> dict:
        """Full channel info for ``peer_id``."""
        return self._get(f"/v1/channels/{int(peer_id)}")

    def get_channels(self, ids: Iterable[int]) -> dict:
        """Batch-fetch channels by id."""
        joined = ",".join(str(int(i)) for i in ids)
        if not joined:
            raise ValueError("ids must be a non-empty iterable")
        return self._get("/v1/channels", params={"ids": joined})

    def get_channel_recommendations(self, peer_id: Optional[int] = None) -> dict:
        """Recommendations for a specific channel (or generic when omitted)."""
        params = {"peer_id": int(peer_id)} if peer_id is not None else None
        return self._get("/v1/channels/recommendations", params=params)

    def get_channel_messages(self, peer_id: int, ids: Iterable[int]) -> dict:
        """Fetch the listed message IDs from a channel."""
        joined = ",".join(str(int(i)) for i in ids)
        if not joined:
            raise ValueError("ids must be a non-empty iterable")
        return self._get(
            f"/v1/channels/{int(peer_id)}/messages",
            params={"ids": joined},
        )

    def get_history(
        self,
        peer_id: int,
        *,
        limit: Optional[int] = None,
        offset_id: Optional[int] = None,
        offset_date: Optional[int] = None,
        add_offset: Optional[int] = None,
        max_id: Optional[int] = None,
        min_id: Optional[int] = None,
        hash: Optional[int] = None,
    ) -> dict:
        """Message history for a peer."""
        return self._get(
            f"/v1/peers/{int(peer_id)}/history",
            params=_drop_none(
                limit=limit,
                offset_id=offset_id,
                offset_date=offset_date,
                add_offset=add_offset,
                max_id=max_id,
                min_id=min_id,
                hash=hash,
            ),
        )

    def get_replies(
        self,
        peer_id: int,
        msg_id: int,
        *,
        limit: Optional[int] = None,
        offset_id: Optional[int] = None,
        add_offset: Optional[int] = None,
        max_id: Optional[int] = None,
        min_id: Optional[int] = None,
        hash: Optional[int] = None,
    ) -> dict:
        """Replies thread for a channel post."""
        return self._get(
            f"/v1/peers/{int(peer_id)}/messages/{int(msg_id)}/replies",
            params=_drop_none(
                limit=limit,
                offset_id=offset_id,
                add_offset=add_offset,
                max_id=max_id,
                min_id=min_id,
                hash=hash,
            ),
        )

    def get_discussion_message(self, peer_id: int, msg_id: int) -> dict:
        """Resolve a channel post to its discussion thread root."""
        return self._get(
            f"/v1/peers/{int(peer_id)}/messages/{int(msg_id)}/discussion"
        )

    # ------------------------------------------------------------------
    # Chained convenience helpers
    # ------------------------------------------------------------------

    def get_channel_by_username(self, username: str) -> dict:
        """Resolve ``username`` and fetch the full channel in one call."""
        channel_id = _channel_id(self.resolve_username(username))
        if channel_id is None:
            raise errors.NotFoundError(
                f"no channel found for username {username!r}", status_code=404
            )
        return self.get_channel(channel_id)

    def get_user_by_username(self, username: str) -> dict:
        """Resolve ``username`` and fetch the full user profile in one call."""
        user_id = _user_id(self.resolve_username(username))
        if user_id is None:
            raise errors.NotFoundError(
                f"no user found for username {username!r}", status_code=404
            )
        return self.get_user(user_id)

    def get_history_by_username(self, username: str, **kwargs: Any) -> dict:
        """Resolve ``username`` and fetch its message history in one call."""
        peer_id = _any_peer_id(self.resolve_username(username))
        if peer_id is None:
            raise errors.NotFoundError(
                f"no peer found for username {username!r}", status_code=404
            )
        return self.get_history(peer_id, **kwargs)

    def get_channel_messages_by_username(
        self, username: str, ids: Iterable[int]
    ) -> dict:
        """Resolve a channel ``username`` and fetch specific messages from it."""
        channel_id = _channel_id(self.resolve_username(username))
        if channel_id is None:
            raise errors.NotFoundError(
                f"no channel found for username {username!r}", status_code=404
            )
        return self.get_channel_messages(channel_id, ids)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get(self, path: str, *, params: Optional[dict] = None) -> Any:
        url = self._base_url + path
        headers = {
            "X-RapidAPI-Key": self._api_key,
            "X-RapidAPI-Host": self._api_host,
            "Accept": "application/json",
        }
        if self._extra_headers:
            headers.update(self._extra_headers)
        resp: Response = self._transport.request(
            "GET",
            url,
            params=params,
            headers=headers,
            timeout=self._timeout,
        )
        return _unwrap(resp)


def _drop_none(**kwargs: Any) -> dict:
    """Return ``kwargs`` minus any entries whose value is None."""
    return {k: v for k, v in kwargs.items() if v is not None}


def _unwrap(resp: Response) -> Any:
    if 200 <= resp.status_code < 300:
        return resp.json
    msg = ""
    if isinstance(resp.json, dict):
        msg = str(resp.json.get("error") or "")
    if not msg:
        msg = f"HTTP {resp.status_code}"
    raise errors.from_status(resp.status_code, msg)


def _channel_id(env: Any) -> Optional[int]:
    """Extract a channel id from a resolve_username envelope, if any."""
    return _peer_field(env, "channel_id")


def _user_id(env: Any) -> Optional[int]:
    """Extract a user id from a resolve_username envelope, if any."""
    return _peer_field(env, "user_id")


def _any_peer_id(env: Any) -> Optional[int]:
    """Extract whichever peer id is present (channel / user / chat)."""
    for key in ("channel_id", "user_id", "chat_id"):
        pid = _peer_field(env, key)
        if pid is not None:
            return pid
    return None


def _peer_field(env: Any, key: str) -> Optional[int]:
    if not isinstance(env, dict):
        return None
    peer = env.get("peer")
    if not isinstance(peer, dict):
        return None
    val = peer.get(key)
    if val in (None, 0):
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
