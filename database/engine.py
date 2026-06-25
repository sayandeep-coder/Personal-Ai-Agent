"""Database engine factory.

Purpose: create configured SQLAlchemy engines.
Responsibilities: isolate engine options from callers.
Dependencies: SQLAlchemy and settings.
Extension Notes: add read-replica factories without changing repositories.
"""

from sqlalchemy import Engine, create_engine

from core.config import Settings


def create_database_engine(settings: Settings) -> Engine:
    """Create the primary SQLAlchemy engine."""
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        future=True,
    )

