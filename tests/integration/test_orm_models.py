"""ORM integration tests.

Purpose: verify SQLAlchemy model metadata and relationships.
Responsibilities: ensure models, foreign keys, and repositories import cleanly.
Dependencies: SQLAlchemy ORM configuration.
Extension Notes: add live database tests when test Postgres is available.
"""

from sqlalchemy.orm import configure_mappers

from database.base import Base
from database.models import Integration, OAuthToken, User
from database.repositories import IntegrationRepository, OAuthTokenRepository, UserRepository
from database.session import SessionLocal, engine, session_factory


def test_metadata_tables_and_session_exports() -> None:
    """Metadata and session exports are available."""
    assert sorted(Base.metadata.tables.keys()) == [
        "integrations",
        "jobs",
        "oauth_tokens",
        "users",
    ]
    assert engine.name == "postgresql"
    assert SessionLocal is session_factory


def test_mappers_relationships_and_repositories() -> None:
    """Mapper configuration and relationships are valid."""
    configure_mappers()
    assert User.integrations.property.mapper.class_ is Integration
    assert Integration.user.property.mapper.class_ is User
    assert Integration.oauth_token.property.mapper.class_ is OAuthToken
    assert OAuthToken.integration.property.mapper.class_ is Integration
    assert UserRepository.__name__ == "UserRepository"
    assert IntegrationRepository.__name__ == "IntegrationRepository"
    assert OAuthTokenRepository.__name__ == "OAuthTokenRepository"
