"""ORM models package.

Purpose: reserve the bounded package for SQLAlchemy ORM models.
Responsibilities: expose model classes to Alembic once implemented.
Dependencies: database declarative base.
Extension Notes: import concrete models here after they are created.
"""

from database.base import Base

__all__ = ["Base"]
