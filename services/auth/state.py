"""OAuth state management.

Purpose: protect OAuth callbacks from CSRF.
Responsibilities: generate, store, and consume one-time state values.
Dependencies: secrets and Redis-compatible clients.
Extension Notes: add signed state payloads if multi-client redirects expand.
"""

from secrets import token_urlsafe
from typing import Protocol


class OAuthStateStore(Protocol):
    """Protocol for OAuth state storage."""

    def create(self, redirect_uri: str) -> str:
        """Create and persist a new state value."""
        ...

    def consume(self, state: str) -> str | None:
        """Consume a state value once and return its redirect URI."""
        ...


class RedisStateClient(Protocol):
    """Protocol for Redis operations required by OAuth state storage."""

    def setex(self, name: str, time: int, value: str) -> object:
        """Set a value with expiration."""
        ...

    def get(self, name: str) -> object:
        """Return a value by key."""
        ...

    def getdel(self, name: str) -> object:
        """Return and delete a value by key."""
        ...

    def delete(self, *names: str) -> object:
        """Delete one or more keys."""
        ...


class RedisOAuthStateStore:
    """Redis-backed OAuth state store."""

    def __init__(self, redis_client: RedisStateClient, ttl_seconds: int = 600) -> None:
        """Create a state store from a Redis-compatible client."""
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds

    def create(self, redirect_uri: str) -> str:
        """Create and persist a new state value."""
        state = token_urlsafe(32)
        self._redis.setex(self._key(state), self._ttl_seconds, redirect_uri)
        return state

    def consume(self, state: str) -> str | None:
        """Consume a state value once and return its redirect URI."""
        key = self._key(state)
        if hasattr(self._redis, "getdel"):
            return self._decode(self._redis.getdel(key))
        value = self._redis.get(key)
        if value:
            self._redis.delete(key)
        return self._decode(value)

    def _key(self, state: str) -> str:
        """Return the Redis key for an OAuth state."""
        return f"oauth:state:{state}"

    def _decode(self, value: object) -> str | None:
        """Decode a Redis value into text."""
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode()
        return str(value)
