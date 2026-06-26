"""FastAPI app factory.

Purpose: construct the HTTP application.
Responsibilities: configure lifecycle, middleware, routes, and logging.
Dependencies: FastAPI, settings, and service container factory.
Extension Notes: add versioned API routers as independent modules.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.api.errors import register_error_handlers
from apps.api.middleware import RequestContextMiddleware
from apps.api.routes.auth.google import router as auth_router
from apps.api.routes.base import router
from apps.api.routes.google.calendar import router as calendar_router
from apps.api.routes.google.docs import router as docs_router
from apps.api.routes.google.drive import router as drive_router
from apps.api.routes.google.gmail import router as gmail_router
from apps.api.routes.github.router import router as github_router
from apps.api.routes.google.sheets import router as sheets_router
from apps.api.routes.maps import router as maps_router
from apps.api.routes.weather import router as weather_router
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
    register_error_handlers(app)
    app.include_router(router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(gmail_router, prefix="/api/v1")
    app.include_router(calendar_router, prefix="/api/v1")
    app.include_router(drive_router, prefix="/api/v1")
    app.include_router(docs_router, prefix="/api/v1")
    app.include_router(sheets_router, prefix="/api/v1")
    app.include_router(github_router, prefix="/api/v1")
    app.include_router(weather_router, prefix="/api/v1")
    app.include_router(maps_router, prefix="/api/v1")
    return app
