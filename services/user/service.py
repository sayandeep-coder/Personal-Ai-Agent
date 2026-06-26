"""User service.

Purpose: coordinate user account persistence.
Responsibilities: find existing users and create new users from profiles.
Dependencies: user repository and User model.
Extension Notes: add last-login only when schema includes a column.
"""

from integrations.google.auth.types import GoogleProfile
from database.models.user import User
from database.repositories.user import UserRepository


class UserService:
    """Service for user account operations."""

    def __init__(self, repository: UserRepository) -> None:
        """Create a user service."""
        self._repository = repository

    def find_by_email(self, email: str) -> User | None:
        """Return a user by email."""
        return self._repository.get_by_email(email)

    def get_or_create_from_google(self, profile: GoogleProfile) -> User:
        """Return an existing user or create one from Google profile."""
        existing = self.find_by_email(profile.email)
        if existing is not None:
            return existing
        return self._repository.add(
            User(full_name=profile.full_name, email=profile.email),
        )

