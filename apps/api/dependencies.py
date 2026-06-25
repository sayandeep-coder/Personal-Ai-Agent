"""FastAPI dependencies.

Purpose: provide typed access to application services.
Responsibilities: retrieve the DI container from app state.
Dependencies: FastAPI and core container.
Extension Notes: add request-scoped dependencies here.
"""

from typing import cast

from fastapi import Request

from core.container import ServiceContainer


def get_container(request: Request) -> ServiceContainer:
    """Return the dependency container attached to the FastAPI app."""
    return cast(ServiceContainer, request.app.state.container)

