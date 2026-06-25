"""Log formatting helpers.

Purpose: keep development and production formatting separate.
Responsibilities: build Loguru format strings.
Dependencies: core settings.
Extension Notes: add JSON sink configuration without changing callers.
"""

from core.config.enums import AppEnvironment


def console_format(environment: AppEnvironment) -> str:
    """Return the console format for the current environment."""
    if environment == AppEnvironment.PRODUCTION:
        return "{time:YYYY-MM-DDTHH:mm:ss.SSSZ} | {level} | {extra} | {message}"
    return (
        "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | {extra} | <level>{message}</level>"
    )

