"""Celery configuration.

Purpose: build Celery settings from application configuration.
Responsibilities: keep broker/backend options centralized.
Dependencies: application settings.
Extension Notes: split queue routing here when worker topology grows.
"""

from dataclasses import dataclass

from core.config import Settings


@dataclass(frozen=True)
class CeleryConfig:
    """Immutable Celery configuration derived from settings."""

    broker_url: str
    result_backend: str
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: tuple[str, ...] = ("json",)
    timezone: str = "UTC"
    enable_utc: bool = True
    task_track_started: bool = True
    broker_connection_retry_on_startup: bool = True

    @classmethod
    def from_settings(cls, settings: Settings) -> "CeleryConfig":
        """Create Celery configuration from application settings."""
        return cls(
            broker_url=settings.redis_url,
            result_backend=settings.redis_url,
            timezone=settings.timezone,
        )

