"""Application logging configuration.

Purpose: configure Loguru sinks for console and file logging.
Responsibilities: structured logs, rotation, request ids, environment levels.
Dependencies: Loguru, settings, and request context.
Extension Notes: add OpenTelemetry/export sinks here when needed.
"""

from pathlib import Path
import sys
from typing import Final

from loguru import logger

from core.config.settings import Settings
from core.constants import LOG_DIRECTORY
from core.context.request import get_request_id

_LOG_FILE: Final[str] = "application.log"


def _record_patcher(record: dict[str, object]) -> None:
    """Attach request context to every emitted log record."""
    extra = record.setdefault("extra", {})
    if isinstance(extra, dict):
        extra.setdefault("request_id", get_request_id() or "-")


def configure_logging(settings: Settings) -> None:
    """Configure process-wide application logging."""
    from core.logging.formatter import console_format

    logger.remove()
    logger.configure(patcher=_record_patcher)
    log_dir = Path(LOG_DIRECTORY)
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        sink=sys.stderr,
        level=settings.log_level.value,
        format=console_format(settings.app_env),
        serialize=settings.is_production,
        backtrace=not settings.is_production,
        diagnose=not settings.is_production,
    )
    logger.add(
        log_dir / _LOG_FILE,
        level=settings.log_level.value,
        rotation="10 MB",
        retention="14 days",
        compression="gz",
        serialize=True,
    )


def get_logger(name: str):
    """Return a module-bound structured logger."""
    return logger.bind(module=name)
