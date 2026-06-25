"""Celery application factory.

Purpose: create the Celery app used by worker processes.
Responsibilities: apply infrastructure configuration and base task class.
Dependencies: Celery, settings, and worker configuration.
Extension Notes: register task modules here after workflows are introduced.
"""

from celery import Celery

from core.config import Settings, settings
from worker.config import CeleryConfig
from worker.task import BaseTask


def create_celery_app(app_settings: Settings = settings) -> Celery:
    """Create and configure the Celery application."""
    config = CeleryConfig.from_settings(app_settings)
    celery_app = Celery(
        main=app_settings.app_name,
        broker=config.broker_url,
        backend=config.result_backend,
        task_cls=BaseTask,
    )
    celery_app.conf.update(
        task_serializer=config.task_serializer,
        result_serializer=config.result_serializer,
        accept_content=list(config.accept_content),
        timezone=config.timezone,
        enable_utc=config.enable_utc,
        task_track_started=config.task_track_started,
        broker_connection_retry_on_startup=config.broker_connection_retry_on_startup,
    )
    return celery_app

