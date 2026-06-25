"""Repository package.

Purpose: expose persistence adapter base classes.
Responsibilities: keep repositories grouped by database concern.
Dependencies: SQLAlchemy repository base.
Extension Notes: add concrete repositories per aggregate later.
"""

from database.repositories.base import RepositoryBase

__all__ = ["RepositoryBase"]
