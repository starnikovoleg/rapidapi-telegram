# rapidapi-telegram

A small Python client for the Telegram metadata API on
[RapidAPI](https://rapidapi.com).

- Sync only, single dependency (`requests`)
- Twelve read-only endpoints exposed as plain methods
- Four convenience helpers that chain a username lookup with a follow-up call
- Pluggable HTTP transport — swap `requests` for `httpx`, a mock, or anything
  else that satisfies the `Transport` protocol

## Install

```sh
pip install rapidapi-telegram
```

Python ≥ 3.9.

## Quick start

```python
from rapidapi_telegram import TelegramClient

client = TelegramClient(api_key="YOUR_RAPIDAPI_KEY")

# Direct call.
profile = client.resolve_username("durov")

# Chained call: resolve the username and fetch the full channel in one go.
channel = client.get_channel_by_username("telegram")
print(channel)
```

The client sends `X-RapidAPI-Key` and `X-RapidAPI-Host` on every request and
defaults to `telegram-public-api.p.rapidapi.com`. Subscribe to the API on
RapidAPI Hub and grab your key from the dashboard. Override the host with
`TelegramClient(api_key=..., api_host="...")` if you're pointing at a
different listing.

## Methods

### Direct endpoints

| Method                                                  | What it does                                      |
|---------------------------------------------------------|---------------------------------------------------|
| `resolve_username(username)`                            | Resolve a public `@username`                      |
| `resolve_phone(phone)`                                  | Resolve a phone number (international format)     |
| `search_contacts(q, limit=None)`                        | Hybrid contact + global directory search          |
| `search_messages(q, limit=None, offset_id=None)`        | Global message search                             |
| `get_user(peer_id)`                                     | Full user profile                                 |
| `get_channel(peer_id)`                                  | Full channel info                                 |
| `get_channels(ids)`                                     | Batch fetch channels by id                        |
| `get_channel_recommendations(peer_id=None)`             | Recommendations for a channel (or generic)        |
| `get_channel_messages(peer_id, ids)`                    | Fetch specific messages from a channel            |
| `get_history(peer_id, **kw)`                            | Message history for a peer                        |
| `get_replies(peer_id, msg_id, **kw)`                    | Replies thread for a channel post                 |
| `get_discussion_message(peer_id, msg_id)`               | Resolve a channel post to its discussion root     |

### Chained helpers

| Method                                              | Equivalent to                                    |
|-----------------------------------------------------|--------------------------------------------------|
| `get_channel_by_username(username)`                 | `resolve_username` → `get_channel`               |
| `get_user_by_username(username)`                    | `resolve_username` → `get_user`                  |
| `get_history_by_username(username, **kw)`           | `resolve_username` → `get_history`               |
| `get_channel_messages_by_username(username, ids)`   | `resolve_username` → `get_channel_messages`      |

## Errors

| Class                          | HTTP |
|--------------------------------|------|
| `BadRequestError`              | 400  |
| `NotFoundError`                | 404  |
| `RateLimitError`               | 429  |
| `ServiceUnavailableError`      | 503  |
| `GatewayTimeoutError`          | 504  |
| `TransportError`               | —    |
| `TelegramAPIError` (base)      | —    |

```python
from rapidapi_telegram import TelegramClient, NotFoundError

client = TelegramClient(api_key="...")
try:
    client.get_channel_by_username("does-not-exist")
except NotFoundError as exc:
    print("nothing here:", exc.message)
```

## Custom HTTP transport

The default transport uses `requests`. To override it — for `httpx`, retries,
mocking, or any other reason — pass any object that implements `Transport`:

```python
from rapidapi_telegram import TelegramClient, Response

class MyTransport:
    def request(self, method, url, *, params=None, headers=None, timeout=None):
        # ...do whatever you want, then return a Response
        return Response(status_code=200, json={"peers": []})

client = TelegramClient(api_key="...", transport=MyTransport())
```

See [`examples/custom_transport.py`](examples/custom_transport.py) for a
working `httpx` adapter.

## Examples

See the [`examples/`](examples/) folder:

- `resolve_username.py` — single endpoint call
- `get_channel_by_username.py` — chained call
- `search_messages.py` — paginated search loop
- `custom_transport.py` — pluggable transport with `httpx`

Run any of them after exporting your key:

```sh
export RAPIDAPI_KEY=your-key
python examples/get_channel_by_username.py telegram
```

## License

MIT. See [LICENSE](LICENSE).
