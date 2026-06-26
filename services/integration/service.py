"""Integration service.

Purpose: coordinate integration persistence.
Responsibilities: create, update, disconnect, and inspect integration status.
Dependencies: integration repository and models.
Extension Notes: sync provider metadata in dedicated use cases later.
"""

from database.models.enums import IntegrationProvider, IntegrationStatus
from database.models.integration import Integration
from database.models.user import User
from database.repositories.integration import IntegrationRepository


class IntegrationService:
    """Service for external provider integration state."""

    def __init__(self, repository: IntegrationRepository) -> None:
        """Create an integration service."""
        self._repository = repository

    def get_google(self, user: User) -> Integration | None:
        """Return a user's Google integration."""
        return self._repository.get_by_user_provider(user.id, IntegrationProvider.GOOGLE)

    def connect_google(self, user: User, account_email: str) -> Integration:
        """Create or update a connected Google integration."""
        integration = self.get_google(user)
        if integration is None:
            integration = Integration(user_id=user.id, provider=IntegrationProvider.GOOGLE)
            self._repository.add(integration)
        integration.account_email = account_email
        integration.status = IntegrationStatus.CONNECTED.value
        return integration

    def disconnect(self, integration: Integration) -> None:
        """Mark an integration as disconnected."""
        integration.status = IntegrationStatus.DISCONNECTED.value

