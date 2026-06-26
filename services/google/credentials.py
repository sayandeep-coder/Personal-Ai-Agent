"""Google credential resolver.

Purpose: resolve decrypted Google access tokens for service wrappers.
Responsibilities: reuse OAuth token storage and refresh expired credentials.
Dependencies: repositories, token service, and Google OAuth client.
Extension Notes: pass required_scopes from callers that need specific permissions.
"""

from sqlalchemy.orm import Session

from core.exceptions import ValidationException
from core.logging import get_logger
from core.types import JsonValue
from database.models.enums import IntegrationProvider, IntegrationStatus
from database.models.oauth_token import OAuthToken
from database.repositories.integration import IntegrationRepository
from database.repositories.oauth_token import OAuthTokenRepository
from database.repositories.user import UserRepository
from integrations.google.auth.protocols import GoogleOAuthPort
from services.oauth.service import OAuthTokenService
from core.utils import utc_now

_logger = get_logger(__name__)

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"


class GoogleCredentialResolver:
    """Resolves Google access tokens for authenticated users."""

    def __init__(
        self,
        session: Session,
        token_service: OAuthTokenService,
        google_oauth: GoogleOAuthPort,
    ) -> None:
        """Create a credential resolver."""
        self._session = session
        self._tokens = token_service
        self._google_oauth = google_oauth

    def access_token(self, email: str, required_scopes: list[str] | None = None) -> str:
        """Return a valid decrypted Google access token.

        Raises ValidationException if required OAuth scopes are missing.
        """
        user = UserRepository(self._session).get_by_email(email)
        if user is None:
            raise ValidationException("User not found", code="google.user_missing")
        integration = IntegrationRepository(self._session).get_by_user_provider(
            user.id,
            IntegrationProvider.GOOGLE,
        )
        if integration is None or integration.status != IntegrationStatus.CONNECTED.value:
            raise ValidationException("Google not connected", code="google.not_connected")
        token = OAuthTokenRepository(self._session).get_by_integration(integration.id)
        if token is None:
            raise ValidationException("Google token missing", code="google.token_missing")

        if required_scopes:
            _verify_scopes(token, required_scopes, email)

        if token.expires_at is not None and token.expires_at <= utc_now():
            refresh_tok = self._tokens.refresh_token(token)
            if refresh_tok is None:
                raise ValidationException(
                    "Refresh token missing — re-authorize the Google integration.",
                    code="google.refresh_missing",
                )
            _logger.warning("google_token_expired_refreshing", email=email)
            try:
                self._tokens.store(integration, self._google_oauth.refresh_token(refresh_tok))
                self._session.commit()
                token = OAuthTokenRepository(self._session).get_by_integration(integration.id)
                if token is None:
                    raise ValidationException("Token missing after refresh", code="google.token_missing")
            except ValidationException:
                raise
            except Exception as exc:
                raise ValidationException(
                    f"Token refresh failed: {exc}",
                    code="google.refresh_failed",
                ) from exc

        return self._tokens.access_token(token)


def _verify_scopes(token: OAuthToken, required_scopes: list[str], email: str) -> None:
    """Raise if any required_scopes are absent from the stored token scope string."""
    granted_raw = token.scope or ""
    granted = set(granted_raw.split())
    missing = [s for s in required_scopes if s not in granted]
    if missing:
        _logger.warning(
            "google_missing_oauth_scopes",
            email=email,
            granted=granted_raw,
            missing=missing,
        )
        missing_val: list[JsonValue] = list(missing)
        granted_val: list[JsonValue] = list(granted)
        raise ValidationException(
            f"Missing required Google OAuth scope(s): {', '.join(missing)}. "
            "Re-authorize the Google integration to grant the required permissions.",
            code="google.missing_scope",
            details={"missing_scopes": missing_val, "granted_scopes": granted_val},
        )

