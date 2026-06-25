"""Configuration enumerations.

Purpose: constrain environment and logging values.
Responsibilities: keep configuration values explicit and typed.
Dependencies: standard library enum.
Extension Notes: add enums only for stable infrastructure choices.
"""

from enum import StrEnum


class AppEnvironment(StrEnum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    """Supported application log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

