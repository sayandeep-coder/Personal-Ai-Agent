"""Integration repository.

Purpose: provide persistence operations for integrations.
Responsibilities: lookup and persist provider connection rows.
Dependencies: SQLAlchemy sessions and Integration model.
Extension Notes: provider behavior belongs in integration services.
"""

from uuid import UUID

from sqlalchemy import select

from database.models.enums import IntegrationProvider
from database.models.integration import Integration
from database.repositories.base import RepositoryBase


class IntegrationRepository(RepositoryBase[Integration]):
    """Repository for integration persistence."""

    def get(self, entity_id: UUID) -> Integration | None:
        """Return an integration by id."""
        return self.session.get(Integration, entity_id)

    def get_by_user_provider(
        self,
        user_id: UUID,
        provider: IntegrationProvider,
    ) -> Integration | None:
        """Return a user's integration for a provider."""
        statement = select(Integration).where(
            Integration.user_id == user_id,
            Integration.provider == provider.value,
        )
        return self.session.scalar(statement)

    def list_for_user(self, user_id: UUID) -> list[Integration]:
        """Return all integrations for a user."""
        statement = select(Integration).where(Integration.user_id == user_id)
        return list(self.session.scalars(statement))

    def add(self, integration: Integration) -> Integration:
        """Persist a new integration in the current transaction."""
        self.session.add(integration)
        return integration

