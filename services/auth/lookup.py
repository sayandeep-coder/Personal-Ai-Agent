"""Authentication lookup helpers.

Purpose: centralize required auth entity lookups.
Responsibilities: fetch users, integrations, and token rows or raise.
Dependencies: repositories and validation exceptions.
Extension Notes: keep orchestration decisions in AuthenticationService.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ValidationException
from database.models.integration import Integration
from database.models.oauth_token import OAuthToken
from database.models.user import User
from database.repositories.integration import IntegrationRepository
from database.repositories.oauth_token import OAuthTokenRepository
from database.repositories.user import UserRepository
from services.integration.service import IntegrationService


class AuthLookup:
    """Required entity lookup helper for authentication workflows."""

    def __init__(self, session: Session) -> None:
        """Create lookup helper from a database session."""
        self._session = session
        self._users = UserRepository(session)
        self._integrations = IntegrationService(IntegrationRepository(session))
        self._tokens = OAuthTokenRepository(session)

    def user(self, email: str) -> User:
        """Return a user by email or raise."""
        user = self._users.get_by_email(email)
        if user is None:
            raise ValidationException("User not found", code="auth.user_not_found")
        return user

    def google_integration(self, user: User) -> Integration:
        """Return a user's Google integration or raise."""
        integration = self._integrations.get_google(user)
        if integration is None:
            raise ValidationException("Google integration not found", code="auth.no_google")
        return integration

    def token(self, integration_id: UUID) -> OAuthToken:
        """Return OAuth token row or raise."""
        token = self._tokens.get_by_integration(integration_id)
        if token is None:
            raise ValidationException("OAuth token not found", code="auth.no_token")
        return token

