"""Repository interfaces.

Purpose: define the minimum repository contract.
Responsibilities: decouple application services from persistence details.
Dependencies: typing protocols.
Extension Notes: add specialized repository protocols per bounded context.
"""

from typing import Protocol
from uuid import UUID


class Repository(Protocol):
    """Protocol for persistence adapters with identity-based access."""

    def get(self, entity_id: UUID) -> object | None:
        """Return an entity by id when present."""
        ...

