"""Unit tests for :mod:`rapidapi_telegram`.

These exercise the client through a fake transport — no network, no
``requests`` involvement. The fake records every call so the tests can
assert on URL, headers, params, and method.
"""

from __future__ import annotations

import pytest

from rapidapi_telegram import (
    DEFAULT_API_HOST,
    NotFoundError,
    RateLimitError,
    Response,
    TelegramAPIError,
    TelegramClient,
)


class FakeTransport:
    """Programmable transport that records calls and returns canned responses."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def request(self, method, url, *, params=None, headers=None, timeout=None):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "params": params,
                "headers": headers,
                "timeout": timeout,
            }
        )
        return self._responses.pop(0)


def _ok(body):
    return Response(status_code=200, json=body)


def _err(status, message="boom"):
    return Response(status_code=status, json={"error": message})


def test_resolve_username_sends_expected_request():
    transport = FakeTransport([_ok({"peer": {}, "chats": [], "users": None})])
    client = TelegramClient(api_key="k", transport=transport)

    client.resolve_username("@durov")

    call = transport.calls[0]
    assert call["method"] == "GET"
    assert call["url"] == f"https://{DEFAULT_API_HOST}/v1/usernames/durov"
    assert call["headers"]["X-RapidAPI-Key"] == "k"
    assert call["headers"]["X-RapidAPI-Host"] == DEFAULT_API_HOST
    assert call["headers"]["Accept"] == "application/json"
    assert call["params"] is None


def test_base_url_overrides_host():
    transport = FakeTransport([_ok({"peer": {}})])
    client = TelegramClient(
        api_key="k", base_url="http://localhost:9090", transport=transport
    )
    client.resolve_username("durov")
    assert transport.calls[0]["url"] == "http://localhost:9090/v1/usernames/durov"


def test_extra_headers_are_merged():
    transport = FakeTransport([_ok({})])
    client = TelegramClient(
        api_key="k", transport=transport, extra_headers={"X-Trace": "abc"}
    )
    client.resolve_username("durov")
    assert transport.calls[0]["headers"]["X-Trace"] == "abc"


def test_search_messages_drops_none_params():
    transport = FakeTransport([_ok({"messages": []})])
    client = TelegramClient(api_key="k", transport=transport)
    client.search_messages("q", limit=10)
    assert transport.calls[0]["params"] == {"q": "q", "limit": 10}


def test_get_channels_joins_ids():
    transport = FakeTransport([_ok({"channels": []})])
    client = TelegramClient(api_key="k", transport=transport)
    client.get_channels([1, 2, 3])
    assert transport.calls[0]["params"] == {"ids": "1,2,3"}


def test_get_channels_rejects_empty_ids():
    client = TelegramClient(api_key="k", transport=FakeTransport([]))
    with pytest.raises(ValueError):
        client.get_channels([])


def test_404_maps_to_not_found_error():
    transport = FakeTransport([_err(404, "not found")])
    client = TelegramClient(api_key="k", transport=transport)
    with pytest.raises(NotFoundError) as ei:
        client.get_user(123)
    assert ei.value.status_code == 404
    assert ei.value.message == "not found"


def test_429_maps_to_rate_limit_error():
    transport = FakeTransport([_err(429)])
    client = TelegramClient(api_key="k", transport=transport)
    with pytest.raises(RateLimitError):
        client.get_user(123)


def test_unknown_status_maps_to_base_error():
    transport = FakeTransport([Response(status_code=418, json=None)])
    client = TelegramClient(api_key="k", transport=transport)
    with pytest.raises(TelegramAPIError) as ei:
        client.get_user(123)
    assert ei.value.status_code == 418


def test_get_channel_by_username_chains_correctly():
    resolve_envelope = {"peer": {"channel_id": 1006503122}}
    channel_body = {"full_chat": {"id": 1006503122}, "chats": [], "users": None}
    transport = FakeTransport([_ok(resolve_envelope), _ok(channel_body)])
    client = TelegramClient(api_key="k", transport=transport)

    result = client.get_channel_by_username("telegram")

    assert result == channel_body
    assert transport.calls[0]["url"].endswith("/v1/usernames/telegram")
    assert transport.calls[1]["url"].endswith("/v1/channels/1006503122")


def test_get_channel_by_username_raises_when_peer_is_a_user():
    """If the resolved peer is a user, the channel helper must raise NotFound."""
    envelope = {"peer": {"user_id": 42}}
    transport = FakeTransport([_ok(envelope)])
    client = TelegramClient(api_key="k", transport=transport)
    with pytest.raises(NotFoundError):
        client.get_channel_by_username("alice")


def test_get_user_by_username_chains_correctly():
    envelope = {"peer": {"user_id": 7}}
    user_body = {"users": [{"id": 7, "first_name": "Alice"}]}
    transport = FakeTransport([_ok(envelope), _ok(user_body)])
    client = TelegramClient(api_key="k", transport=transport)
    assert client.get_user_by_username("alice") == user_body
    assert transport.calls[1]["url"].endswith("/v1/users/7")


def test_get_history_by_username_passes_kwargs():
    envelope = {"peer": {"channel_id": 99}}
    transport = FakeTransport([_ok(envelope), _ok({"messages": []})])
    client = TelegramClient(api_key="k", transport=transport)
    client.get_history_by_username("news", limit=50, offset_id=100)
    assert transport.calls[1]["url"].endswith("/v1/peers/99/history")
    assert transport.calls[1]["params"] == {"limit": 50, "offset_id": 100}


def test_empty_api_key_rejected():
    with pytest.raises(ValueError):
        TelegramClient(api_key="")
