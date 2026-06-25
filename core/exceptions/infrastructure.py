"""Infrastructure exceptions.

Purpose: model failures from foundational services.
Responsibilities: keep error categories explicit and catchable.
Dependencies: base application exception.
Extension Notes: add narrower exceptions only when callers branch on them.
"""

from core.exceptions.base import ApplicationException


class ConfigurationException(ApplicationException):
    """Raised when configuration cannot be loaded or validated."""


class DatabaseException(ApplicationException):
    """Raised when database infrastructure fails."""


class RedisException(ApplicationException):
    """Raised when Redis infrastructure fails."""


class WorkerException(ApplicationException):
    """Raised when worker infrastructure fails."""


class ValidationException(ApplicationException):
    """Raised when infrastructure input validation fails."""


class LoggingException(ApplicationException):
    """Raised when logging cannot be configured."""
