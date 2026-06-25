"""Worker application package.

Purpose: expose Celery worker process bootstrap.
Responsibilities: provide the Celery app object for worker runtimes.
Dependencies: worker infrastructure package.
Extension Notes: add task imports only when real workflows exist.
"""
