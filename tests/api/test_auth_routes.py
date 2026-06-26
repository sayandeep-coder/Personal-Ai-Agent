"""Auth API route tests.

Purpose: verify auth routes call service layer and hide tokens.
Responsibilities: cover login, callback, status, logout, and refresh endpoints.
Dependencies: FastAPI TestClient and route fakes.
Extension Notes: add full-stack tests with test Postgres/Redis later.
"""

from tests.api.auth_route_fakes import client
from pytest import MonkeyPatch


def test_google_login_redirects(monkeypatch: MonkeyPatch) -> None:
    """Login endpoint redirects to Google."""
    response = client(monkeypatch).get(
        "/api/v1/auth/google/login",
        params={"redirect_uri": "http://localhost/callback"},
        follow_redirects=False,
    )
    assert response.status_code == 307
    assert response.headers["location"] == "https://google.test/login"


def test_google_callback_returns_no_tokens(monkeypatch: MonkeyPatch) -> None:
    """Callback returns auth result without token data."""
    response = client(monkeypatch).get(
        "/api/v1/auth/google/callback",
        params={"code": "ok", "state": "state", "redirect_uri": "http://localhost/callback"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
    assert "access_token" not in response.text


def test_status_logout_and_refresh(monkeypatch: MonkeyPatch) -> None:
    """Status, logout, and refresh endpoints call service layer."""
    api = client(monkeypatch)
    status = api.get("/api/v1/auth/status", params={"email": "user@example.com"})
    logout = api.post("/api/v1/auth/logout", json={"email": "user@example.com"})
    refresh = api.post("/api/v1/auth/refresh", json={"email": "user@example.com"})
    assert status.json()["authenticated"] is True
    assert logout.json()["authenticated"] is False
    assert refresh.json()["connected"] is True
