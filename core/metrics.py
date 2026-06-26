"""Infrastructure metrics.

Purpose: expose lightweight runtime metrics.
Responsibilities: track uptime, request count, memory, CPU, workers, threads.
Dependencies: psutil when installed, standard library fallback otherwise.
Extension Notes: replace internals with Prometheus collectors without API changes.
"""

import os
import platform
import resource
import threading
from dataclasses import dataclass, field
from datetime import datetime
from importlib import import_module
from typing import cast

from core.utils import utc_now


@dataclass
class MetricsManager:
    """Collects process-local infrastructure metrics."""

    started_at: datetime = field(default_factory=utc_now)
    request_count: int = 0

    def record_request(self) -> None:
        """Increment the process-local HTTP request counter."""
        self.request_count += 1

    def snapshot(self) -> dict[str, object]:
        """Return a Prometheus-compatible future metrics payload."""
        uptime = self.uptime_seconds()
        requests_per_minute = (self.request_count / uptime) * 60 if uptime else 0.0
        return {
            "uptime_seconds": round(uptime, 3),
            "uptime": self.uptime_human(),
            "memory": self._memory(),
            "cpu_usage": self._cpu_usage(),
            "worker_count": 0,
            "thread_count": threading.active_count(),
            "requests_total": self.request_count,
            "requests_per_minute": round(requests_per_minute, 2),
        }

    def uptime_seconds(self) -> float:
        """Return process uptime in seconds."""
        return (utc_now() - self.started_at).total_seconds()

    def uptime_human(self) -> str:
        """Return process uptime in a compact human-readable form."""
        seconds = int(self.uptime_seconds())
        minutes, second = divmod(seconds, 60)
        hours, minute = divmod(minutes, 60)
        if hours:
            return f"{hours}h {minute}m {second}s"
        if minute:
            return f"{minute}m {second}s"
        return f"{second}s"

    def _memory(self) -> dict[str, float]:
        """Return RSS and VMS memory in megabytes."""
        try:
            psutil = import_module("psutil")
            memory = psutil.Process(os.getpid()).memory_info()
            return {
                "rss_mb": round(memory.rss / 1024 / 1024, 2),
                "vms_mb": round(memory.vms / 1024 / 1024, 2),
            }
        except Exception:
            usage = resource.getrusage(resource.RUSAGE_SELF)
            divisor = 1024 * 1024 if platform.system() == "Darwin" else 1024
            return {"rss_mb": round(usage.ru_maxrss / divisor, 2), "vms_mb": 0.0}

    def _cpu_usage(self) -> float:
        """Return rounded process CPU/load signal."""
        try:
            psutil = import_module("psutil")
            cpu_percent = cast(float, psutil.Process(os.getpid()).cpu_percent(interval=None))
            return round(cpu_percent, 2)
        except Exception:
            cpu_load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
            return round(cpu_load, 2)
