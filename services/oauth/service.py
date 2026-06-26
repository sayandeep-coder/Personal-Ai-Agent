"""OAuth token service.

Purpose: manage encrypted OAuth token persistence.
Responsibilities: encrypt, decrypt, create, update, and inspect token expiry.
Dependencies: token repository, models, cipher, and Google token DTOs.
Extension Notes: never expose encrypted or plaintext tokens through APIs.
"""

from core.security.cipher import TokenCipher
from database.models.integration import Integration
from database.models.oauth_token import OAuthToken
from database.repositories.oauth_token import OAuthTokenRepository
from integrations.google.auth.types import GoogleTokenSet


class OAuthTokenService:
    """Service for encrypted OAuth token storage."""

    def __init__(self, repository: OAuthTokenRepository, cipher: TokenCipher) -> None:
        """Create an OAuth token service."""
        self._repository = repository
        self._cipher = cipher

    def store(self, integration: Integration, token_set: GoogleTokenSet) -> OAuthToken:
        """Create or update encrypted tokens for an integration."""
        token = self._repository.get_by_integration(integration.id)
        if token is None:
            token = OAuthToken(
                integration_id=integration.id,
                access_token=self._cipher.encrypt(token_set.access_token),
            )
            self._repository.add(token)
        else:
            token.access_token = self._cipher.encrypt(token_set.access_token)
        if token_set.refresh_token:
            token.refresh_token = self._cipher.encrypt(token_set.refresh_token)
        token.token_type = token_set.token_type
        token.scope = token_set.scope
        token.expires_at = token_set.expires_at
        return token

    def access_token(self, token: OAuthToken) -> str:
        """Return the decrypted access token."""
        return self._cipher.decrypt(token.access_token)

    def refresh_token(self, token: OAuthToken) -> str | None:
        """Return the decrypted refresh token when stored."""
        return self._cipher.decrypt(token.refresh_token) if token.refresh_token else None
