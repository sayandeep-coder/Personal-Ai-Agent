"""OAuth token ORM model.

Purpose: map the existing oauth_tokens table.
Responsibilities: represent encrypted OAuth credential storage.
Dependencies: SQLAlchemy ORM and PostgreSQL UUID types.
Extension Notes: encryption/decryption belongs in OAuth services.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from database.models.integration import Integration


class OAuthToken(TimestampMixin, Base):
    """ORM mapping for provider OAuth tokens."""

    __tablename__ = "oauth_tokens"
    __table_args__ = (UniqueConstraint("integration_id", name="uq_oauth_integration"),)

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    integration_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("integrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    token_type: Mapped[str | None] = mapped_column(
        String(50),
        server_default=text("'Bearer'"),
    )
    scope: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    integration: Mapped["Integration"] = relationship(back_populates="oauth_token")
