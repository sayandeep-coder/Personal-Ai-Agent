"""Base application exception.

Purpose: define the common exception contract.
Responsibilities: carry stable error codes and safe details.
Dependencies: standard library.
Extension Notes: add telemetry hooks outside this class, not inside it.
"""

from dataclasses import dataclass, field

from core.types import JsonValue


@dataclass(eq=False)
class BaseException(Exception):
    """Common parent for all application-specific exceptions."""

    message: str
    code: str = "application_error"
    details: dict[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize the Python exception message."""
        super().__init__(self.message)


class ApplicationException(BaseException):
    """Base exception for application infrastructure failures."""
