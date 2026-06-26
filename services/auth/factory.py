"""Authentication service factory.

Purpose: create AuthenticationService from infrastructure dependencies.
Responsibilities: wire Google client, state store, token cipher, and repositories.
Dependencies: settings, SQLAlchemy session, Redis-like client, auth services.
Extension Notes: add provider selection here only when multiple providers exist.
"""

from sqlalchemy.orm import Session

from core.config import Settings
from core.security.cipher import TokenCipher
from database.repositories.oauth_token import OAuthTokenRepository
from integrations.google.auth.client import GoogleOAuthClient
from services.auth.service import AuthenticationService
from services.auth.state import RedisOAuthStateStore, RedisStateClient
from services.oauth.service import OAuthTokenService


def create_auth_service(
    settings: Settings,
    session: Session,
    redis_client: RedisStateClient,
) -> AuthenticationService:
    """Create an authentication service."""
    cipher = TokenCipher(settings.oauth_token_encryption_key)
    token_service = OAuthTokenService(OAuthTokenRepository(session), cipher)
    state_store = RedisOAuthStateStore(redis_client)
    google = GoogleOAuthClient(settings)
    return AuthenticationService(session, google, state_store, token_service)
