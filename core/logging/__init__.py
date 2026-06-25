"""Logging package.

Purpose: expose structured application logging helpers.
Responsibilities: configure Loguru and provide contextual loggers.
Dependencies: Loguru and request context.
Extension Notes: add external log sinks through configuration functions.
"""

from core.logging.logger import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]

