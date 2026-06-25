"""Health service.

Purpose: aggregate infrastructure health checks.
Responsibilities: produce API and CLI friendly health payloads.
Dependencies: health check protocols and settings.
Extension Notes: add component weighting or readiness gates here.
"""

from dataclasses import dataclass

from core.config import Settings
from core.constants import HEALTH_DEGRADED, HEALTH_OK
from core.interfaces.health import HealthCheck, HealthReport
from core.metrics import MetricsManager


@dataclass(frozen=True)
class HealthService:
    """Application service for infrastructure health aggregation."""

    settings: Settings
    checks: tuple[HealthCheck, ...]
    metrics: MetricsManager

    def check(self) -> dict[str, object]:
        """Return aggregate health for configuration and dependencies."""
        reports = self.reports()
        healthy = all(report.healthy for report in reports)
        return {
            "status": HEALTH_OK if healthy else HEALTH_DEGRADED,
            "application": self.settings.app_name,
            "environment": self.settings.app_env.value,
            "checks": {
                report.name: {
                    "healthy": report.healthy,
                    "status": report.status,
                    "detail": report.detail,
                    "latency_ms": report.latency_ms,
                    "metadata": report.metadata,
                }
                for report in reports
            },
        }

    def summary(self) -> dict[str, object]:
        """Return a compact API health summary."""
        reports = self.reports()
        healthy = all(report.healthy for report in reports)
        return {
            "status": HEALTH_OK if healthy else HEALTH_DEGRADED,
            "uptime": self.metrics.uptime_human(),
            "checks": {
                report.name: {
                    "status": report.status,
                    "latency_ms": report.latency_ms,
                    "detail": report.detail,
                }
                for report in reports
            },
        }

    def reports(self) -> list[HealthReport]:
        """Return health reports for configuration and dependencies."""
        reports = [HealthReport(name="configuration", healthy=True)]
        reports.extend(check.check() for check in self.checks)
        return reports
