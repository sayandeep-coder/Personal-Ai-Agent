"""Exception framework.

Purpose: provide a typed hierarchy for infrastructure failures.
Responsibilities: normalize error codes and operational context.
Dependencies: local exception modules.
Extension Notes: domain exceptions should live near domain packages later.
"""

from core.exceptions.base import ApplicationException, BaseException
from core.exceptions.infrastructure import (
    ConfigurationException,
    DatabaseException,
    LoggingException,
    RedisException,
    ValidationException,
    WorkerException,
)

__all__ = [
    "BaseException",
    "ApplicationException",
    "ConfigurationException",
    "DatabaseException",
    "LoggingException",
    "RedisException",
    "ValidationException",
    "WorkerException",
]
