"""API process bootstrap.

Purpose: expose the ASGI application for servers.
Responsibilities: create the FastAPI app through the app factory.
Dependencies: FastAPI app module.
Extension Notes: keep server-specific options outside application code.
"""

from apps.api.app import create_app

app = create_app()

__all__ = ["app"]
