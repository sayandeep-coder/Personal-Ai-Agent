"""Celery worker bootstrap.

Purpose: expose the Celery app for worker processes.
Responsibilities: configure logging and create the worker application.
Dependencies: core settings, logging, and worker app factory.
Extension Notes: import task modules here when real tasks are added.
"""

from core.config import settings
from core.logging import configure_logging
from worker.app import create_celery_app
from worker.broker import verify_broker_connection

configure_logging(settings)
verify_broker_connection(settings)

celery_app = create_celery_app(settings)

__all__ = ["celery_app"]
