"""Google Maps integration errors.

Purpose: create safe Google Maps exceptions.
Responsibilities: attach stable codes and HTTP status hints.
Dependencies: application validation exception.
Extension Notes: add provider status metadata only when safe.
"""

from core.exceptions import ValidationException


def maps_error(code: str, message: str, status_code: int) -> ValidationException:
    """Return a Maps exception with an HTTP status hint."""
    return ValidationException(message, code=f"maps.{code}", details={"status_code": status_code})
