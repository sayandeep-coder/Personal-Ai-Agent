"""Worker infrastructure package.

Purpose: expose Celery application construction.
Responsibilities: configure broker, backend, and task base classes.
Dependencies: Celery, Redis URL settings, and logging.
Extension Notes: add task modules only after domain workflows exist.
"""
