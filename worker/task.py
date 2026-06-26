"""Celery task base.

Purpose: provide shared behavior for future worker tasks.
Responsibilities: log task failures with structured context.
Dependencies: Celery and application logging.
Extension Notes: add retry helpers here only when reused by real tasks.
"""

from typing import TYPE_CHECKING

from core.logging import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:

    class TaskBase:
        """Typing shim for Celery Task."""

        name: str

        def on_failure(
            self,
            exc: BaseException,
            task_id: str,
            args: tuple[object, ...],
            kwargs: dict[str, object],
            einfo: object,
        ) -> None:
            """Handle task failure."""
            ...

else:
    from celery import Task as TaskBase


class BaseTask(TaskBase):
    """Base class for infrastructure-aware Celery tasks."""

    abstract = True

    def on_failure(
        self,
        exc: BaseException,
        task_id: str,
        args: tuple[object, ...],
        kwargs: dict[str, object],
        einfo: object,
    ) -> None:
        """Log task failures with task metadata."""
        logger.bind(task_id=task_id, task_name=self.name).exception(str(exc))
        super().on_failure(exc, task_id, args, kwargs, einfo)
