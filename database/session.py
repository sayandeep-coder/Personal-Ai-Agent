"""Database session factory.

Purpose: create SQLAlchemy session factories.
Responsibilities: provide typed session construction for repositories.
Dependencies: SQLAlchemy ORM.
Extension Notes: add async sessions in a sibling module if needed.
"""

from collections.abc import Iterator

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings
from database.engine import create_database_engine


engine = create_database_engine(settings)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
session_factory = SessionLocal


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory bound to the provided engine."""
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Yield a database session and always close it."""
    session = factory()
    try:
        yield session
    finally:
        session.close()
