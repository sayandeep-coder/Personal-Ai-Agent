"""Database enum values.

Purpose: centralize table-constrained string values.
Responsibilities: avoid magic strings in repositories and services.
Dependencies: standard library enum.
Extension Notes: keep enum values aligned with database CHECK constraints.
"""

from enum import StrEnum


class IntegrationProvider(StrEnum):
    """Supported integration providers."""

    GOOGLE = "google"
    GITHUB = "github"
    WEATHER = "weather"
    MAPS = "maps"


class IntegrationStatus(StrEnum):
    """Supported integration connection states."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    ERROR = "error"


class JobStatus(StrEnum):
    """Supported background job states."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

