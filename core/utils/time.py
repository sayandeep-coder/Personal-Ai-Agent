"""Time utilities.

Purpose: centralize timezone-aware time helpers.
Responsibilities: provide UTC now and timezone validation.
Dependencies: datetime and zoneinfo.
Extension Notes: add clock abstractions for deterministic tests later.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def validate_timezone(value: str) -> str:
    """Return a valid IANA timezone or raise ValueError."""
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Invalid timezone: {value}") from exc
    return value

