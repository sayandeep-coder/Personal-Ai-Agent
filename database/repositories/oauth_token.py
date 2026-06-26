"""OAuth token repository.

Purpose: provide persistence operations for OAuth tokens.
Responsibilities: lookup and persist token rows.
Dependencies: SQLAlchemy sessions and OAuthToken model.
Extension Notes: encryption and refresh logic belong in services.
"""

from uuid import UUID

from sqlalchemy import select

from database.models.oauth_token import OAuthToken
from database.repositories.base import RepositoryBase


class OAuthTokenRepository(RepositoryBase[OAuthToken]):
    """Repository for OAuth token persistence."""

    def get(self, entity_id: UUID) -> OAuthToken | None:
        """Return an OAuth token row by id."""
        return self.session.get(OAuthToken, entity_id)

    def get_by_integration(self, integration_id: UUID) -> OAuthToken | None:
        """Return OAuth token data for an integration."""
        statement = select(OAuthToken).where(
            OAuthToken.integration_id == integration_id,
        )
        return self.session.scalar(statement)

    def add(self, token: OAuthToken) -> OAuthToken:
        """Persist a new OAuth token row in the current transaction."""
        self.session.add(token)
        return token

