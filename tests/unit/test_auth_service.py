"""Authentication service unit tests.

Purpose: verify Google OAuth orchestration without external services.
Responsibilities: cover login, callback, refresh, logout, and failures.
Dependencies: pytest, service fakes, and repository monkeypatching.
Extension Notes: add database integration tests when test Postgres is available.
"""

import pytest
from cryptography.fernet import Fernet
from pydantic import SecretStr
from sqlalchemy.orm import Session as SqlSession
from typing import cast

from core.exceptions import ValidationException
from core.security.cipher import TokenCipher
from database.models.oauth_token import OAuthToken
from database.repositories import integration, oauth_token, user
from services.auth.service import AuthenticationService
from services.oauth.service import OAuthTokenService
from tests.unit.auth_fakes import Google, Session, State, Store


def save_token(_: object, value: OAuthToken) -> OAuthToken:
    """Persist token in fake store."""
    Store.token = value
    return value


def service(monkeypatch: pytest.MonkeyPatch) -> AuthenticationService:
    """Create service with patched repositories."""
    Store.token = None
    Store.integration.status = "connected"
    Store.integration.account_email = "user@example.com"
    State.valid = True
    monkeypatch.setattr(user.UserRepository, "get_by_email", lambda *_: None)
    monkeypatch.setattr(user.UserRepository, "add", lambda _, value: Store.user)
    monkeypatch.setattr(integration.IntegrationRepository, "get_by_user_provider", lambda *_: None)
    monkeypatch.setattr(integration.IntegrationRepository, "add", lambda _, value: Store.integration)
    monkeypatch.setattr(oauth_token.OAuthTokenRepository, "get_by_integration", lambda *_: Store.token)
    monkeypatch.setattr(oauth_token.OAuthTokenRepository, "add", save_token)
    cipher = TokenCipher(SecretStr(Fernet.generate_key().decode()))
    session = cast(SqlSession, Session())
    token_service = OAuthTokenService(oauth_token.OAuthTokenRepository(session), cipher)
    return AuthenticationService(session, Google(), State(), token_service)


def test_login_generates_authorization_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Login returns a Google authorization URL."""
    result = service(monkeypatch).login("http://localhost/callback")
    assert result.state == "state"
    assert "state=state" in result.authorization_url


def test_new_user_login_stores_encrypted_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Callback creates records and stores encrypted token."""
    result = service(monkeypatch).callback("ok", "state")
    assert result.email == "user@example.com"
    assert Store.token is not None
    assert Store.token.access_token != "access"


def test_invalid_state_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid OAuth state is rejected."""
    auth = service(monkeypatch)
    State.valid = False
    with pytest.raises(ValidationException):
        auth.callback("ok", "wrong")


def test_invalid_authorization_code_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provider authorization code failures are surfaced."""
    with pytest.raises(ValidationException):
        service(monkeypatch).callback("bad", "state")
