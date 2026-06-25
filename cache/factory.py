"""Redis client factory.

Purpose: create Redis clients from configuration.
Responsibilities: isolate client options from callers.
Dependencies: redis-py and settings.
Extension Notes: add sentinel/cluster support through this factory.
"""

from redis import Redis

from core.config import Settings


def create_redis_client(settings: Settings) -> Redis:
    """Create a Redis client for the configured URL."""
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )

