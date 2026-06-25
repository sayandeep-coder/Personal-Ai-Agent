"""Health check interfaces.

Purpose: define a common contract for infrastructure health probes.
Responsibilities: represent component health without binding to frameworks.
Dependencies: dataclasses and protocols.
Extension Notes: add readiness/liveness separation when deployment needs it.
"""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class HealthReport:
    """Immutable health status returned by a component."""

    name: str
    healthy: bool
    detail: str = "ok"
    latency_ms: float = 0.0
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def status(self) -> str:
        """Return a stable status string for API responses."""
        return "healthy" if self.healthy else "unhealthy"


class HealthCheck(Protocol):
    """Protocol implemented by health-checkable infrastructure services."""

    def check(self) -> HealthReport:
        """Return the current health status."""
        ...
