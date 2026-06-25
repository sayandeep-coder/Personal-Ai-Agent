"""Infrastructure interfaces.

Purpose: expose contracts used across adapter layers.
Responsibilities: keep high-level code independent of concrete services.
Dependencies: local protocol modules.
Extension Notes: add protocols before adding concrete cross-layer imports.
"""

from core.interfaces.health import HealthCheck, HealthReport
from core.interfaces.lifecycle import Lifecycle
from core.interfaces.repository import Repository

__all__ = ["HealthCheck", "HealthReport", "Lifecycle", "Repository"]

