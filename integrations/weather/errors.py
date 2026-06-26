"""Weather integration exceptions.

Purpose: create safe Weather provider exceptions.
Responsibilities: attach stable codes and HTTP status hints.
Dependencies: application validation exception.
Extension Notes: add provider-specific error metadata only when safe.
"""

from core.exceptions import ValidationException


def weather_error(code: str, message: str, status_code: int) -> ValidationException:
    """Return a weather exception with an HTTP status hint."""
    return ValidationException(message, code=f"weather.{code}", details={"status_code": status_code})
