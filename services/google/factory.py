"""Google service factory.

Purpose: create Google API services with shared dependencies.
Responsibilities: wire credentials, OAuth refresh, and REST client.
Dependencies: settings, SQLAlchemy session, service classes.
Extension Notes: add caching or quota managers here later.
"""

from sqlalchemy.orm import Session

from core.config import Settings
from core.security.cipher import TokenCipher
from database.repositories.oauth_token import OAuthTokenRepository
from integrations.google.auth.client import GoogleOAuthClient
from integrations.google.common.http import GoogleApiClient
from services.google.credentials import GoogleCredentialResolver
from services.oauth.service import OAuthTokenService


def credential_resolver(settings: Settings, session: Session) -> GoogleCredentialResolver:
    """Create a Google credential resolver."""
    cipher = TokenCipher(settings.oauth_token_encryption_key)
    tokens = OAuthTokenService(OAuthTokenRepository(session), cipher)
    return GoogleCredentialResolver(session, tokens, GoogleOAuthClient(settings))


def google_client() -> GoogleApiClient:
    """Create the Google REST client."""
    return GoogleApiClient()
