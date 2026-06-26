"""Integration ORM model.

Purpose: map the existing integrations table.
Responsibilities: represent provider account linkage state.
Dependencies: SQLAlchemy ORM and PostgreSQL JSONB/UUID types.
Extension Notes: provider-specific behavior belongs in services/adapters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.models.enums import IntegrationStatus
from database.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from database.models.oauth_token import OAuthToken
    from database.models.user import User


class Integration(TimestampMixin, Base):
    """ORM mapping for a connected external provider."""

    __tablename__ = "integrations"
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_provider"),)

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    account_email: Mapped[str | None] = mapped_column(String(320))
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text(f"'{IntegrationStatus.CONNECTED.value}'"),
    )
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    user: Mapped["User"] = relationship(back_populates="integrations")
    oauth_token: Mapped["OAuthToken | None"] = relationship(
        back_populates="integration",
        cascade="all, delete-orphan",
        uselist=False,
    )
