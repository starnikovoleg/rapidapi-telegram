# Telegram API — Python Client

> **Read public Telegram data via REST or MCP.** Channels, messages, members, search — no bot token, no phone number, no Telegram app required.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![RapidAPI](https://img.shields.io/badge/RapidAPI-Telegram%20API-blue)](https://rapidapi.com/starnikovoleg/api/telegram155)

A lightweight Python client for **Telegram** on [RapidAPI](https://rapidapi.com/starnikovoleg/api/telegram155). Access real-time Telegram channel info, message history, user profiles, global search, and channel members — all through a simple REST API powered by MTProto (not the limited Bot API).

**Perfect for:** AI agents, n8n workflows, OSINT research, Telegram monitoring, channel analytics, and automation pipelines.

---

## Why This API?

- **Real-time MTProto data** — not the Bot API, not web scraping. Direct access to public Telegram data in milliseconds.
- **12 read-only endpoints** — channels, users, messages, history, search, members, recommendations, and more.
- **MCP support** — native [Model Context Protocol](https://modelcontextprotocol.io/) endpoint for AI agents (Claude, LangChain, CrewAI, n8n).
- **No bot token needed** — no Telegram app setup, no phone number. Just a RapidAPI key.
- **Generous free tier** — 2,500 requests/month free. Start building immediately.
- **Pluggable transport** — swap `requests` for `httpx`, add retries, or inject mocks for testing.

---

## Installation

```bash
pip install rapidapi-telegram
```

Requires **Python 3.9+**. The only runtime dependency is [`requests`](https://pypi.org/project/requests/).

---

## Quick Start

```python
from rapidapi_telegram import TelegramClient

client = TelegramClient(api_key="YOUR_RAPIDAPI_KEY")

# Resolve a public @username
profile = client.resolve_username("durov")

# Get full channel info by username (chained: resolve → fetch)
channel = client.get_channel_by_username("telegram")
print(channel)

# Read the last 20 messages from a channel
history = client.get_history_by_username("telegram", limit=20)
for msg in history.get("messages", []):
    print(msg.get("message", ""))
```

Get your API key: subscribe to the API on [RapidAPI](https://rapidapi.com/starnikovoleg/api/telegram155) and copy the key from your dashboard.

---

## All Endpoints

### 12 Direct Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| `resolve_username(username)` | Resolve a public `@username` to a peer ID | Find any Telegram user or channel by username |
| `resolve_phone(phone)` | Resolve a phone number (international format) | Look up users by phone |
| `search_contacts(q, limit=None)` | Hybrid contact + global directory search | Search for Telegram channels and users by keyword |
| `search_messages(q, limit=None, offset_id=None)` | Global message search across public channels | Find messages mentioning a topic across Telegram |
| `get_user(peer_id)` | Full user profile (bio, birthday, premium status) | Get detailed info about a Telegram user |
| `get_channel(peer_id)` | Full channel info (description, member count) | Get detailed info about a Telegram channel |
| `get_channels(ids)` | Batch-fetch multiple channels by ID | Fetch several channels in one request |
| `get_channel_recommendations(peer_id=None)` | Similar channel recommendations | Discover related Telegram channels |
| `get_channel_messages(peer_id, ids)` | Fetch specific messages from a channel by ID | Get exact messages you need |
| `get_history(peer_id, **kw)` | Message history for a channel or chat | Read Telegram channel messages, paginate through history |
| `get_replies(peer_id, msg_id, **kw)` | Replies/comments thread for a channel post | Read comments on a Telegram channel post |
| `get_discussion_message(peer_id, msg_id)` | Resolve a post to its discussion thread root | Navigate from post to discussion group |

### `get_history` Parameters

The `get_history` method supports fine-grained pagination:

```python
history = client.get_history(
    peer_id=1005640892,
    limit=50,           # Max messages to return (1–100)
    offset_id=None,     # Start from this message ID (None = latest)
    offset_date=None,   # Unix timestamp cutoff
    add_offset=None,    # Additional offset (negative = newer)
    max_id=None,        # Upper bound message ID
    min_id=None,        # Lower bound message ID
    hash=None,          # Cache hash from previous response
)
```

### `get_replies` Parameters

```python
replies = client.get_replies(
    peer_id=1005640892,
    msg_id=42,
    limit=50,           # Max replies to return
    offset_id=None,     # Paginate within the thread
    add_offset=None,    # Additional offset
    max_id=None,        # Upper bound
    min_id=None,        # Lower bound
    hash=None,          # Cache hash
)
```

### 4 Chained Helpers

These combine a `resolve_username` call with a follow-up request — so you can work with `@usernames` directly instead of numeric IDs:

| Method | What It Does |
|--------|-------------|
| `get_channel_by_username(username)` | Resolve `@username` → fetch full channel info |
| `get_user_by_username(username)` | Resolve `@username` → fetch full user profile |
| `get_history_by_username(username, **kw)` | Resolve `@username` → fetch message history |
| `get_channel_messages_by_username(username, ids)` | Resolve `@username` → fetch specific messages |

```python
# Instead of two separate calls:
resolved = client.resolve_username("telegram")
channel_id = resolved["peer"]["channel_id"]
channel = client.get_channel(channel_id)

# Just do:
channel = client.get_channel_by_username("telegram")
```

---

## Pagination Example — Search Messages

Paginate through global message search results using `offset_id`:

```python
from rapidapi_telegram import TelegramClient

client = TelegramClient(api_key="YOUR_RAPIDAPI_KEY")

offset_id = None
for page in range(3):
    result = client.search_messages("bitcoin", limit=20, offset_id=offset_id)
    messages = result.get("messages", [])
    print(f"Page {page + 1}: {len(messages)} messages")

    for msg in messages:
        print(msg.get("message", "")[:100])

    if not messages:
        break
    offset_id = messages[-1].get("id")
```

---

## Error Handling

Every non-2xx HTTP response raises a typed exception. Catch specific errors or the base class:

| Exception | HTTP Status | When |
|-----------|-------------|------|
| `BadRequestError` | 400 | Malformed request parameters |
| `NotFoundError` | 404 | Username or peer not found |
| `RateLimitError` | 429 | Quota exceeded — upgrade your plan or wait |
| `ServiceUnavailableError` | 503 | Temporary service issue |
| `GatewayTimeoutError` | 504 | Request timed out |
| `TransportError` | — | Network/connection failure before response |
| `TelegramAPIError` | — | Base class for all API errors |

```python
from rapidapi_telegram import TelegramClient, NotFoundError, RateLimitError

client = TelegramClient(api_key="YOUR_RAPIDAPI_KEY")

try:
    channel = client.get_channel_by_username("this-does-not-exist")
except NotFoundError as exc:
    print(f"Not found: {exc.message}")
except RateLimitError:
    print("Rate limit hit — wait or upgrade your plan")
```

Every exception has `.status_code` and `.message` attributes for programmatic handling.

---

## Custom HTTP Transport

The default transport uses `requests`. You can swap it for `httpx`, add retries, or inject a mock — anything that implements the `Transport` protocol:

```python
import httpx
from rapidapi_telegram import TelegramClient, Response

class HttpxTransport:
    def __init__(self):
        self._client = httpx.Client()

    def request(self, method, url, *, params=None, headers=None, timeout=None):
        resp = self._client.request(
            method, url, params=params, headers=headers, timeout=timeout
        )
        try:
            body = resp.json() if resp.content else None
        except ValueError:
            body = None
        return Response(status_code=resp.status_code, json=body)

client = TelegramClient(api_key="YOUR_KEY", transport=HttpxTransport())
```

You can also pass a pre-configured `requests.Session` for connection pooling or custom adapters:

```python
import requests
from rapidapi_telegram import TelegramClient, RequestsTransport

session = requests.Session()
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

client = TelegramClient(
    api_key="YOUR_KEY",
    transport=RequestsTransport(session=session),
)
```

---

## Client Configuration

```python
client = TelegramClient(
    api_key="YOUR_RAPIDAPI_KEY",       # Required — your RapidAPI key
    api_host="telegram-public-api.p.rapidapi.com",  # RapidAPI host (default)
    base_url=None,                      # Override full URL (for local dev)
    timeout=30.0,                       # Per-request timeout in seconds
    transport=None,                     # Custom Transport implementation
    extra_headers=None,                 # Additional headers for every request
)
```

---

## MCP Support — For AI Agents

This API natively supports the **Model Context Protocol (MCP)** — the open standard for connecting AI agents to external tools. All 12 endpoints are available as MCP tools (`tg_resolve_username`, `tg_get_history`, `tg_search_global`, etc.).

Use it with **Claude**, **LangChain**, **CrewAI**, **n8n**, or any MCP-compatible agent framework.

MCP endpoint: `POST /v1/mcp` (Streamable HTTP, protocol `2025-06-18`)

See the [API documentation](https://rapidapi.com/starnikovoleg/api/telegram155) for MCP setup details.

---

## Use Cases

- **AI Agents & n8n Workflows** — feed real-time Telegram data into automation pipelines, monitor channels, trigger actions on new messages.
- **OSINT & Research** — search across public Telegram channels, analyze message history, track channel members and growth.
- **Telegram Channel Analytics** — subscriber counts, message frequency, engagement patterns, channel recommendations.
- **Telegram Monitoring** — track keywords across public channels, monitor specific channels for new posts.
- **Content Aggregation** — pull messages from multiple channels into a dashboard or database.

---

## Examples

See the [`examples/`](examples/) folder for runnable scripts:

| File | What It Does |
|------|-------------|
| [`resolve_username.py`](examples/resolve_username.py) | Resolve a `@username` to a peer profile |
| [`get_channel_by_username.py`](examples/get_channel_by_username.py) | Fetch full channel info by username |
| [`search_messages.py`](examples/search_messages.py) | Paginated global message search |
| [`custom_transport.py`](examples/custom_transport.py) | Plug in `httpx` as the HTTP backend |

Run any example:

```bash
export RAPIDAPI_KEY=your-key
python examples/get_channel_by_username.py telegram
```

---

## API Reference

### Constructor

**`TelegramClient(api_key, *, api_host, base_url, timeout, transport, extra_headers)`**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | *required* | Your RapidAPI key |
| `api_host` | `str` | `"telegram-public-api.p.rapidapi.com"` | RapidAPI host header |
| `base_url` | `str \| None` | `None` | Override request URL (for local dev/testing) |
| `timeout` | `float` | `30.0` | Per-request timeout in seconds |
| `transport` | `Transport \| None` | `None` | Custom HTTP transport (defaults to `RequestsTransport`) |
| `extra_headers` | `dict \| None` | `None` | Extra headers merged into every request |

### Response Format

All methods return the parsed JSON response as a Python `dict`. The shape depends on the endpoint — see the [API documentation](https://rapidapi.com/starnikovoleg/api/telegram155) for response schemas.

### Transport Protocol

Any object with this method signature works as a transport:

```python
def request(
    self,
    method: str,
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float | None = None,
) -> Response:
    ...
```

Where `Response` is a dataclass with `status_code: int` and `json: Any`.

---

## Comparison: MTProto API vs Bot API vs Scraping

| Feature | This API (MTProto) | Telegram Bot API | Web Scraping |
|---------|--------------------|------------------|-------------|
| Read channel messages | Yes | Limited (bot must be admin) | Fragile, breaks often |
| Search across channels | Yes (global search) | No | No |
| Channel members list | Yes | No | No |
| User profiles | Yes (full) | Limited | Limited |
| No bot token needed | Yes | No | Yes |
| Real-time data | Yes | Yes | Depends |
| MCP support | Yes | No | No |
| Rate limits | Predictable (plan-based) | Telegram-enforced | IP-based bans |
| Setup time | 2 minutes | 10+ minutes | Hours |

---

## License

MIT. See [LICENSE](LICENSE).
