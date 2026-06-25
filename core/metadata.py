"""Application metadata.

Purpose: expose stable runtime and build metadata.
Responsibilities: report version, Python runtime, environment, git, platform.
Dependencies: platform runtime and application settings.
Extension Notes: prefer CI-provided metadata over local git subprocess calls.
"""

import os
import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.config import Settings
from core.constants import APP_VERSION


@dataclass(frozen=True)
class ApplicationMetadata:
    """Immutable application metadata for diagnostics."""

    settings: Settings
    version: str = APP_VERSION
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict[str, str]:
        """Return public metadata as a serializable dictionary."""
        metadata = {
            "application": self.settings.app_name,
            "version": self.version,
            "python_version": platform.python_version(),
            "environment": self.settings.app_env.value,
            "timezone": self.settings.timezone,
            "started_at": self.started_at.isoformat(),
            "git_commit": self._metadata_value("GIT_COMMIT", "rev-parse", "HEAD"),
            "git_branch": self._metadata_value("GIT_BRANCH", "branch", "--show-current"),
            "platform": f"{platform.system().lower()}-{platform.machine().lower()}",
        }
        build_time = os.getenv("BUILD_TIME")
        if build_time:
            metadata["build_time"] = build_time
        return metadata

    def _metadata_value(self, env_name: str, *git_args: str) -> str:
        """Return metadata from environment or local git."""
        if value := os.getenv(env_name):
            return value
        try:
            result = subprocess.run(
                ("git", *git_args),
                capture_output=True,
                check=True,
                text=True,
                timeout=1,
            )
            return result.stdout.strip() or "unknown"
        except Exception:
            return "unknown"
