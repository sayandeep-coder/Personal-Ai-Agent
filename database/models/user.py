"""User ORM model.

Purpose: map the existing users table.
Responsibilities: represent user identity and preferences.
Dependencies: SQLAlchemy ORM and PostgreSQL JSONB/UUID types.
Extension Notes: keep authentication behavior in services, not the model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from database.models.integration import Integration


class User(TimestampMixin, Base):
    """ORM mapping for an application user."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default=text("'Asia/Kolkata'"),
    )
    preferences: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )

    integrations: Mapped[list["Integration"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
