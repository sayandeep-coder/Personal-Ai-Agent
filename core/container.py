"""Dependency injection container.

Purpose: compose infrastructure services without hidden dependencies.
Responsibilities: own service construction and lifecycle coordination.
Dependencies: configuration, database, Redis, and health services.
Extension Notes: add providers here only for infrastructure boundaries.
"""

from dataclasses import dataclass

from cache.manager import RedisManager
from core.config import Settings
from core.metadata import ApplicationMetadata
from core.metrics import MetricsManager
from database.manager import DatabaseManager
from health.service import HealthService


@dataclass(frozen=True)
class ServiceContainer:
    """Immutable container for application infrastructure services."""

    settings: Settings
    database: DatabaseManager
    redis: RedisManager
    health: HealthService
    metadata: ApplicationMetadata
    metrics: MetricsManager

    def start(self) -> None:
        """Start services that require eager initialization."""
        self.database.start()
        self.redis.start()

    def stop(self) -> None:
        """Release resources owned by the container."""
        self.redis.stop()
        self.database.stop()
