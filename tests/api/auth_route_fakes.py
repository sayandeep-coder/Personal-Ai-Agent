"""Auth API route fakes.

Purpose: provide fake services and containers for route tests.
Responsibilities: avoid real database, Redis, or Google calls.
Dependencies: auth DTOs and FastAPI route factory monkeypatching.
Extension Notes: replace with fixture factories if API tests grow.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from apps.api.routes.auth import google as routes
from apps.api.routes.auth.google import router
from services.auth.dtos import AuthResult, AuthStatus, LoginResult


class Service:
    """Fake auth service."""

    def login(self, redirect_uri: str) -> LoginResult:
        """Return login result."""
        return LoginResult("https://google.test/login", "state")

    def callback(self, code: str, state: str) -> AuthResult:
        """Return auth result."""
        from uuid import uuid4

        return AuthResult(uuid4(), uuid4(), "user@example.com", True)

    def status(self, email: str | None) -> AuthStatus:
        """Return auth status."""
        return AuthStatus(True, ("google",), email or "user@example.com", "connected")

    def logout(self, email: str) -> AuthStatus:
        """Return logged-out status."""
        return AuthStatus(False, (), email, "disconnected")

    def refresh(self, email: str) -> AuthResult:
        """Return refreshed auth result."""
        from uuid import uuid4

        return AuthResult(uuid4(), uuid4(), email, True)


class Factory:
    """Fake session factory."""

    def __call__(self) -> "Factory":
        """Return context manager."""
        return self

    def __enter__(self) -> object:
        """Enter context."""
        return object()

    def __exit__(self, *args: object) -> None:
        """Exit context."""


class Container:
    """Fake container."""

    class Database:
        """Fake database."""

        def get_session_factory(self) -> Factory:
            """Return session factory."""
            return Factory()

    database = Database()


def client(monkeypatch: MonkeyPatch) -> TestClient:
    """Return auth API test client."""
    monkeypatch.setattr(routes, "create_auth_service", lambda *_: Service())
    app = FastAPI()
    app.state.container = Container()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)
