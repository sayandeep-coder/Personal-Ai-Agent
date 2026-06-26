"""ORM model mixins.

Purpose: share common timestamp columns across mapped tables.
Responsibilities: define created_at and updated_at columns.
Dependencies: SQLAlchemy ORM.
Extension Notes: add soft-delete mixins only when schema supports them.
"""

from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

_LOCAL_TIMESTAMP = text("(CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')")


class TimestampMixin:
    """Mixin for tables with created and updated timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=_LOCAL_TIMESTAMP,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=_LOCAL_TIMESTAMP,
        nullable=False,
    )

