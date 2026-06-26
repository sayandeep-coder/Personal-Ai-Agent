"""Infrastructure API routes.

Purpose: define infrastructure HTTP endpoints.
Responsibilities: expose root, health, readiness, version, metrics, and config.
Dependencies: FastAPI and container dependency.
Extension Notes: keep feature routers in separate modules later.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.dependencies import get_container
from core.config.enums import AppEnvironment
from core.constants import HEALTH_OK, STATUS_RUNNING
from core.container import ServiceContainer

router = APIRouter()


def root(container: ServiceContainer = Depends(get_container)) -> dict[str, str]:
    """Return the basic application health response."""
    return {
        "application": container.settings.app_name,
        "version": container.metadata.version,
        "environment": container.settings.app_env.value,
        "status": STATUS_RUNNING,
    }


def health(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return aggregate infrastructure health summary."""
    return container.health.summary()


def liveness() -> dict[str, str]:
    """Return liveness without dependency calls."""
    return {"status": "alive"}


def readiness(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return readiness based on infrastructure checks."""
    return container.health.summary()


def version(container: ServiceContainer = Depends(get_container)) -> dict[str, str]:
    """Return application and runtime version metadata."""
    return container.metadata.as_dict()


def metrics(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return infrastructure metrics for future Prometheus integration."""
    return {"status": HEALTH_OK, "format": "json", "metrics": container.metrics.snapshot()}


def config(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return non-sensitive development configuration."""
    if container.settings.app_env == AppEnvironment.PRODUCTION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return {"configuration": container.settings.safe_dict()}


router.add_api_route("/", root, methods=["GET"])
router.add_api_route("/health", health, methods=["GET"])
router.add_api_route("/health/live", liveness, methods=["GET"])
router.add_api_route("/health/ready", readiness, methods=["GET"])
router.add_api_route("/version", version, methods=["GET"])
router.add_api_route("/metrics", metrics, methods=["GET"])
router.add_api_route("/config", config, methods=["GET"])

