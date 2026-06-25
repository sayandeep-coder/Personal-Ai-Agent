"""Worker broker verification.

Purpose: verify Celery broker connectivity during worker bootstrap.
Responsibilities: fail fast when Redis is unavailable.
Dependencies: Redis manager and worker exceptions.
Extension Notes: support alternate brokers by adding broker-specific probes.
"""

from cache.manager import RedisManager
from core.config import Settings
from core.exceptions import WorkerException


def verify_broker_connection(settings: Settings) -> None:
    """Verify that the configured Redis broker is reachable."""
    redis = RedisManager(settings)
    redis.start()
    try:
        report = redis.check()
        if not report.healthy:
            raise WorkerException(
                message=report.detail,
                code="worker.broker_unavailable",
            )
    finally:
        redis.stop()

