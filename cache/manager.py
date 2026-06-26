"""Redis manager.

Purpose: own Redis client lifecycle.
Responsibilities: create a singleton connection and expose health checks.
Dependencies: redis-py, settings, and health interfaces.
Extension Notes: add logical clients for cache, broker, and locks if needed.
"""

from dataclasses import dataclass, field
from time import perf_counter
from typing import Protocol, cast

from redis import Redis

from cache.factory import create_redis_client
from core.config import Settings
from core.interfaces.health import HealthReport


class ClosableRedis(Protocol):
    """Protocol for Redis clients that can close connection pools."""

    def close(self) -> None:
        """Close Redis client resources."""
        ...


@dataclass
class RedisManager:
    """Lifecycle owner for the Redis client."""

    settings: Settings
    client: Redis | None = field(default=None, init=False)

    def start(self) -> None:
        """Initialize the Redis client if needed."""
        if self.client is None:
            self.client = create_redis_client(self.settings)

    def stop(self) -> None:
        """Close the Redis client connection pool."""
        if self.client is not None:
            cast(ClosableRedis, self.client).close()
        self.client = None

    def get_client(self) -> Redis:
        """Return an initialized Redis client."""
        self.start()
        if self.client is None:
            raise RuntimeError("Redis client is not initialized")
        return self.client

    def check(self) -> HealthReport:
        """Verify Redis connectivity with PING."""
        started = perf_counter()
        try:
            client = self.get_client()
            pong = client.ping()
            latency_ms = round((perf_counter() - started) * 1000, 2)
            return HealthReport(name="redis", healthy=bool(pong), latency_ms=latency_ms)
        except Exception as exc:
            latency_ms = round((perf_counter() - started) * 1000, 2)
            return HealthReport(
                name="redis",
                healthy=False,
                detail=exc.__class__.__name__,
                latency_ms=latency_ms,
            )
