"""Authentication service factory for API routes.

Purpose: build AuthenticationService from request-scoped dependencies.
Responsibilities: wire session, Google client, state store, and token service.
Dependencies: service container and auth infrastructure.
Extension Notes: move to central DI if route factories grow.
"""

from core.container import ServiceContainer
from services.auth.service import AuthenticationService
from sqlalchemy.orm import Session
from services.auth.factory import create_auth_service as create_service


def create_auth_service(
    container: ServiceContainer,
    session: Session,
) -> AuthenticationService:
    """Create an authentication service for an API request."""
    return create_service(container.settings, session, container.redis.get_client())
