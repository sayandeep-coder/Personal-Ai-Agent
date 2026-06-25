"""Infrastructure API routes.

Purpose: define infrastructure HTTP endpoints.
Responsibilities: expose root, health, readiness, version, metrics, and config.
Dependencies: FastAPI and container dependency.
Extension Notes: keep feature routers in separate modules later.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.dependencies import get_container
from core.config.enums import AppEnvironment
from core.container import ServiceContainer
from core.constants import HEALTH_OK, STATUS_RUNNING

router = APIRouter()


@router.get("/")
def root(container: ServiceContainer = Depends(get_container)) -> dict[str, str]:
    """Return the basic application health response."""
    return {
        "application": container.settings.app_name,
        "version": container.metadata.version,
        "environment": container.settings.app_env.value,
        "status": STATUS_RUNNING,
    }


@router.get("/health")
def health(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return aggregate infrastructure health summary."""
    return container.health.summary()


@router.get("/health/live")
def liveness() -> dict[str, str]:
    """Return liveness without dependency calls."""
    return {"status": "alive"}


@router.get("/health/ready")
def readiness(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return readiness based on infrastructure checks."""
    return container.health.summary()


@router.get("/version")
def version(container: ServiceContainer = Depends(get_container)) -> dict[str, str]:
    """Return application and runtime version metadata."""
    return container.metadata.as_dict()


@router.get("/metrics")
def metrics(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return infrastructure metrics for future Prometheus integration."""
    return {
        "status": HEALTH_OK,
        "format": "json",
        "metrics": container.metrics.snapshot(),
    }


@router.get("/config")
def config(container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return non-sensitive development configuration."""
    if container.settings.app_env == AppEnvironment.PRODUCTION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return {"configuration": container.settings.safe_dict()}
