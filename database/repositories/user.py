"""User repository.

Purpose: provide persistence operations for users.
Responsibilities: lookup and persist user rows.
Dependencies: SQLAlchemy sessions and User model.
Extension Notes: keep onboarding/authentication logic in services.
"""

from uuid import UUID

from sqlalchemy import select

from database.models.user import User
from database.repositories.base import RepositoryBase


class UserRepository(RepositoryBase[User]):
    """Repository for user persistence."""

    def get(self, entity_id: UUID) -> User | None:
        """Return a user by id."""
        return self.session.get(User, entity_id)

    def get_by_email(self, email: str) -> User | None:
        """Return a user by unique email."""
        statement = select(User).where(User.email == email)
        return self.session.scalar(statement)

    def add(self, user: User) -> User:
        """Persist a new user in the current transaction."""
        self.session.add(user)
        return user

