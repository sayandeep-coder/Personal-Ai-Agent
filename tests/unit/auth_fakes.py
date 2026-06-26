"""Authentication test fakes.

Purpose: provide reusable fakes for auth service tests.
Responsibilities: simulate session, state, Google, and persistence stores.
Dependencies: ORM models and Google OAuth DTOs.
Extension Notes: keep fakes minimal and behavior-oriented.
"""

from datetime import timedelta
from uuid import uuid4

from database.models.integration import Integration
from database.models.oauth_token import OAuthToken
from database.models.user import User
from integrations.google.auth.types import GoogleProfile, GoogleTokenSet


class Session:
    """Minimal session fake."""

    def flush(self) -> None:
        """Pretend to flush."""

    def commit(self) -> None:
        """Pretend to commit."""


class State:
    """OAuth state fake."""

    valid = True
    redirect_uri = "http://localhost/callback"

    def create(self, redirect_uri: str) -> str:
        """Return a state."""
        self.redirect_uri = redirect_uri
        return "state"

    def consume(self, state: str) -> str | None:
        """Return the redirect URI when state is valid."""
        if self.valid and state == "state":
            return self.redirect_uri
        return None


class Google:
    """Google OAuth fake."""

    revoked = False

    def authorization_url(self, state: str, redirect_uri: str) -> str:
        """Return fake auth URL."""
        return f"https://google.test?state={state}&redirect_uri={redirect_uri}"

    def exchange_code(self, code: str, redirect_uri: str) -> GoogleTokenSet:
        """Return fake tokens."""
        if code == "bad":
            from core.exceptions import ValidationException

            raise ValidationException("bad code", code="auth.bad_code")
        return token_set("access", "refresh")

    def refresh_token(self, refresh_token: str) -> GoogleTokenSet:
        """Return refreshed token."""
        return token_set("new-access", None)

    def profile(self, access_token: str) -> GoogleProfile:
        """Return fake profile."""
        return GoogleProfile("user@example.com", "User Example", True)

    def revoke(self, token: str) -> None:
        """Record revocation."""
        self.revoked = token == "access"


class Store:
    """In-memory persistence fake."""

    user = User(id=uuid4(), full_name="User Example", email="user@example.com")
    integration = Integration(id=uuid4(), user_id=user.id, provider="google")
    token: OAuthToken | None = None


def token_set(access: str, refresh: str | None) -> GoogleTokenSet:
    """Return a token set."""
    from core.utils import utc_now

    return GoogleTokenSet(access, refresh, "Bearer", "email", utc_now() + timedelta(hours=1))
