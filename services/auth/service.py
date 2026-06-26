"""Authentication orchestration service.

Purpose: coordinate Google OAuth authentication workflows.
Responsibilities: login URL, callback, status, refresh, and logout.
Dependencies: repositories, Google OAuth port, state store, token cipher.
Extension Notes: add session management when a sessions table exists.
"""

from sqlalchemy.orm import Session

from core.exceptions import ValidationException
from database.models.enums import IntegrationStatus
from database.repositories.integration import IntegrationRepository
from database.repositories.user import UserRepository
from integrations.google.auth.protocols import GoogleOAuthPort
from services.auth.dtos import AuthResult, AuthStatus, LoginResult
from services.auth.lookup import AuthLookup
from services.auth.state import OAuthStateStore
from services.integration.service import IntegrationService
from services.oauth.service import OAuthTokenService
from services.user.service import UserService


class AuthenticationService:
    """Coordinates Google OAuth authentication use cases."""

    def __init__(
        self,
        session: Session,
        google: GoogleOAuthPort,
        state_store: OAuthStateStore,
        token_service: OAuthTokenService,
    ) -> None:
        """Create an authentication service."""
        self._session = session
        self._google = google
        self._state_store = state_store
        self._tokens = token_service
        self._users = UserService(UserRepository(session))
        self._integrations = IntegrationService(IntegrationRepository(session))
        self._lookup = AuthLookup(session)

    def login(self, redirect_uri: str) -> LoginResult:
        """Create an OAuth authorization URL."""
        state = self._state_store.create(redirect_uri)
        url = self._google.authorization_url(state, redirect_uri)
        return LoginResult(authorization_url=url, state=state)

    def callback(self, code: str, state: str) -> AuthResult:
        """Handle a Google OAuth callback."""
        redirect_uri = self._state_store.consume(state)
        if redirect_uri is None:
            raise ValidationException("Invalid OAuth state", code="auth.invalid_state")
        token_set = self._google.exchange_code(code, redirect_uri)
        profile = self._google.profile(token_set.access_token)
        if not profile.email_verified:
            raise ValidationException("Google email is not verified", code="auth.email")
        user = self._users.get_or_create_from_google(profile)
        self._session.flush()
        integration = self._integrations.connect_google(user, profile.email)
        self._session.flush()
        self._tokens.store(integration, token_set)
        self._session.commit()
        return AuthResult(user.id, integration.id, profile.email, True)

    def status(self, email: str | None) -> AuthStatus:
        """Return Google authentication status."""
        if email is None:
            return AuthStatus(False, (), None, None)
        user = self._users.find_by_email(email)
        if user is None:
            return AuthStatus(False, (), None, None)
        integration = self._integrations.get_google(user)
        if integration is None:
            return AuthStatus(False, (), None, None)
        connected = integration.status == IntegrationStatus.CONNECTED.value
        services = ("google",) if connected else ()
        return AuthStatus(connected, services, integration.account_email, integration.status)

    def refresh(self, email: str) -> AuthResult:
        """Refresh a user's Google access token."""
        user = self._lookup.user(email)
        integration = self._lookup.google_integration(user)
        token = self._lookup.token(integration.id)
        refresh_token = self._tokens.refresh_token(token)
        if refresh_token is None:
            raise ValidationException("Refresh token missing", code="auth.refresh_missing")
        self._tokens.store(integration, self._google.refresh_token(refresh_token))
        self._session.commit()
        return AuthResult(user.id, integration.id, email, True)

    def logout(self, email: str) -> AuthStatus:
        """Revoke token and disconnect Google integration."""
        user = self._lookup.user(email)
        integration = self._lookup.google_integration(user)
        token = self._lookup.token(integration.id)
        self._google.revoke(self._tokens.access_token(token))
        self._integrations.disconnect(integration)
        self._session.commit()
        return self.status(email)
