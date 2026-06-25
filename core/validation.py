"""Validation helpers.

Purpose: centralize small reusable infrastructure validators.
Responsibilities: validate required strings and identifiers.
Dependencies: application validation exception.
Extension Notes: prefer Pydantic models for complex validation.
"""

from core.exceptions import ValidationException


def require_non_empty(value: str | None, field_name: str) -> str:
    """Return a non-empty string or raise a validation exception."""
    if value is None or value.strip() == "":
        raise ValidationException(
            message=f"{field_name} must not be empty",
            code="validation.required",
            details={"field": field_name},
        )
    return value

