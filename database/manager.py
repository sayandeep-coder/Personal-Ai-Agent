"""Database manager.

Purpose: own PostgreSQL engine and session factory lifecycle.
Responsibilities: create sessions, check health, and dispose resources.
Dependencies: settings, SQLAlchemy factories, and health interfaces.
Extension Notes: add replica/session routing behind this manager.
"""

from dataclasses import dataclass, field
from time import perf_counter

from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from core.config import Settings, settings as default_settings
from core.interfaces.health import HealthReport
from database.engine import create_database_engine
from database.session import create_session_factory
from database.session import engine as default_engine
from database.session import session_factory as default_session_factory


@dataclass
class DatabaseManager:
    """Lifecycle owner for SQLAlchemy database infrastructure."""

    settings: Settings
    engine: Engine | None = field(default=None, init=False)
    session_factory: sessionmaker[Session] | None = field(default=None, init=False)

    def start(self) -> None:
        """Initialize the engine and session factory if needed."""
        if self.engine is None:
            if self.settings == default_settings:
                self.engine = default_engine
                self.session_factory = default_session_factory
            else:
                self.engine = create_database_engine(self.settings)
                self.session_factory = create_session_factory(self.engine)

    def stop(self) -> None:
        """Dispose the database engine."""
        if self.engine is not None:
            self.engine.dispose()
        self.engine = None
        self.session_factory = None

    def get_session_factory(self) -> sessionmaker[Session]:
        """Return an initialized session factory."""
        self.start()
        if self.session_factory is None:
            raise RuntimeError("Database session factory is not initialized")
        return self.session_factory

    def check(self) -> HealthReport:
        """Verify database connectivity with a lightweight query."""
        started = perf_counter()
        try:
            self.start()
            if self.engine is None:
                raise RuntimeError("Database engine is not initialized")
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            latency_ms = round((perf_counter() - started) * 1000, 2)
            return HealthReport(name="database", healthy=True, latency_ms=latency_ms)
        except Exception as exc:
            latency_ms = round((perf_counter() - started) * 1000, 2)
            return HealthReport(
                name="database",
                healthy=False,
                detail=exc.__class__.__name__,
                latency_ms=latency_ms,
            )
