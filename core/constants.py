"""Application constants.

Purpose: centralize stable infrastructure names.
Responsibilities: avoid duplicated magic strings.
Dependencies: none.
Extension Notes: add only cross-cutting constants used by multiple layers.
"""

DEFAULT_APP_NAME = "Personal AI Agent"
APP_VERSION = "0.1.0"
DEFAULT_TIMEZONE = "UTC"
REQUEST_ID_HEADER = "X-Request-ID"
LOG_DIRECTORY = "logs"
HEALTH_OK = "healthy"
HEALTH_DEGRADED = "degraded"
STATUS_RUNNING = "running"
