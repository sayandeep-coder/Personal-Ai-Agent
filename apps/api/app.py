"""FastAPI app factory.

Purpose: construct the HTTP application.
Responsibilities: configure lifecycle, middleware, routes, and logging.
Dependencies: FastAPI, settings, and service container factory.
Extension Notes: add versioned API routers as independent modules.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.api.middleware import RequestContextMiddleware
from apps.api.routes import router
from core.config import settings
from core.container import ServiceContainer
from core.factory import create_container
from core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage FastAPI process lifecycle."""
    container: ServiceContainer = app.state.container
    container.start()
    try:
        yield
    finally:
        container.stop()


def create_app(container: ServiceContainer | None = None) -> FastAPI:
    """Create the FastAPI application."""
    app_container = container or create_container(settings)
    configure_logging(app_container.settings)
    app = FastAPI(title=app_container.settings.app_name, lifespan=lifespan)
    app.state.container = app_container
    app.add_middleware(RequestContextMiddleware)
    app.include_router(router, prefix="/api/v1")
    return app
