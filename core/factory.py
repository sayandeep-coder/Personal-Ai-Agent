"""Service factory.

Purpose: construct the dependency injection container.
Responsibilities: wire infrastructure services from settings.
Dependencies: core, database, Redis, and health modules.
Extension Notes: keep application-specific providers out of this factory.
"""

from cache.manager import RedisManager
from core.config import Settings, settings
from core.container import ServiceContainer
from core.metadata import ApplicationMetadata
from core.metrics import MetricsManager
from database.manager import DatabaseManager
from health.service import HealthService


def create_container(app_settings: Settings = settings) -> ServiceContainer:
    """Create a dependency container for the application process."""
    database = DatabaseManager(app_settings)
    redis = RedisManager(app_settings)
    metadata = ApplicationMetadata(settings=app_settings)
    metrics = MetricsManager()
    health = HealthService(
        settings=app_settings,
        checks=(database, redis),
        metrics=metrics,
    )
    return ServiceContainer(
        settings=app_settings,
        database=database,
        redis=redis,
        health=health,
        metadata=metadata,
        metrics=metrics,
    )
