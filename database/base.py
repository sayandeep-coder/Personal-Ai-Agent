"""SQLAlchemy declarative base.

Purpose: define the shared ORM metadata root.
Responsibilities: provide a base class for future ORM models.
Dependencies: SQLAlchemy ORM.
Extension Notes: add naming conventions here if migrations need them.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

