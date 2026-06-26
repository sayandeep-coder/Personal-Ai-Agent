"""Job ORM model.

Purpose: map the existing jobs table.
Responsibilities: represent background job state.
Dependencies: SQLAlchemy ORM and PostgreSQL JSONB/UUID types.
Extension Notes: Celery orchestration belongs in worker services.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from database.models.enums import JobStatus
from database.models.mixins import TimestampMixin


class Job(TimestampMixin, Base):
    """ORM mapping for an asynchronous job record."""

    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text(f"'{JobStatus.PENDING.value}'"),
    )
    payload: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    result: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
