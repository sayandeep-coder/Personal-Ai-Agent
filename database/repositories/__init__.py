"""Repository package.

Purpose: expose persistence adapter base classes.
Responsibilities: keep repositories grouped by database concern.
Dependencies: SQLAlchemy repository base.
Extension Notes: add concrete repositories per aggregate later.
"""

from database.repositories.base import RepositoryBase
from database.repositories.integration import IntegrationRepository
from database.repositories.oauth_token import OAuthTokenRepository
from database.repositories.user import UserRepository

__all__ = [
    "IntegrationRepository",
    "OAuthTokenRepository",
    "RepositoryBase",
    "UserRepository",
]
