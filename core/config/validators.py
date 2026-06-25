"""Configuration validators.

Purpose: keep settings validation helpers reusable and testable.
Responsibilities: validate environment URLs and timezone names.
Dependencies: shared time utilities.
Extension Notes: add provider-specific validation without exposing secrets.
"""

from core.utils import validate_timezone


def validate_required_url(value: str, field_name: str) -> str:
    """Validate that a required URL-like setting is present."""
    if value.strip() == "":
        raise ValueError(f"{field_name} must not be empty")
    return value


def validate_iana_timezone(value: str) -> str:
    """Validate that a timezone name is an IANA timezone."""
    return validate_timezone(value)

