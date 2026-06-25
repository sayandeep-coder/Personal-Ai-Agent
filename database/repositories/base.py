"""Base repository implementation.

Purpose: provide shared repository construction.
Responsibilities: hold a SQLAlchemy session dependency.
Dependencies: SQLAlchemy ORM sessions.
Extension Notes: add generic CRUD helpers only when multiple repositories need them.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


@dataclass
class RepositoryBase(Generic[ModelT]):
    """Base class for SQLAlchemy-backed repositories."""

    session: Session

    def get(self, entity_id: UUID) -> ModelT | None:
        """Return an entity by id.

        Subclasses must implement this once models exist.
        """
        raise NotImplementedError

