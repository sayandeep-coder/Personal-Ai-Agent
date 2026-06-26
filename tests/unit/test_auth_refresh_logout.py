"""Auth refresh and logout unit tests.

Purpose: verify token refresh and logout orchestration.
Responsibilities: cover existing login, refresh token, and logout flows.
Dependencies: auth service fakes and repository monkeypatching.
Extension Notes: add expiry-specific policy tests when policy is introduced.
"""

import pytest

from database.models.enums import IntegrationStatus
from database.repositories import integration, user
from services.auth.service import AuthenticationService
from tests.unit.auth_fakes import Store
from tests.unit.test_auth_service import service


def make_existing(monkeypatch: pytest.MonkeyPatch) -> AuthenticationService:
    """Create authenticated fake state and return service."""
    auth = service(monkeypatch)
    auth.callback("ok", "state")
    monkeypatch.setattr(user.UserRepository, "get_by_email", lambda *_: Store.user)
    monkeypatch.setattr(
        integration.IntegrationRepository,
        "get_by_user_provider",
        lambda *_: Store.integration,
    )
    return auth


def test_existing_user_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """Existing connected Google user is authenticated."""
    auth = make_existing(monkeypatch)
    status = auth.status("user@example.com")
    assert status.authenticated is True
    assert status.connected_services == ("google",)


def test_refresh_token_updates_stored_access(monkeypatch: pytest.MonkeyPatch) -> None:
    """Refresh uses stored refresh token and updates access token."""
    auth = make_existing(monkeypatch)
    assert Store.token is not None
    old_token = Store.token.access_token
    auth.refresh("user@example.com")
    assert Store.token.access_token != old_token


def test_logout_disconnects_integration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Logout revokes token and disconnects integration."""
    auth = make_existing(monkeypatch)
    status = auth.logout("user@example.com")
    assert status.authenticated is False
    assert Store.integration.status == IntegrationStatus.DISCONNECTED.value
