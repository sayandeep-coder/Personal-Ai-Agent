"""Database transaction helper.

Purpose: provide explicit transaction boundaries.
Responsibilities: commit successful units of work and rollback failures.
Dependencies: SQLAlchemy sessions.
Extension Notes: expose nested transactions only when use cases require them.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker


@contextmanager
def transaction(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Run work inside a managed transaction."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

