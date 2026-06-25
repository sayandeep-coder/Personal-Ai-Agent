"""CLI doctor checks.

Purpose: evaluate infrastructure configuration readiness.
Responsibilities: produce human-readable diagnostic checks without side effects.
Dependencies: service container and health reports.
Extension Notes: add provider API reachability only when integrations are built.
"""

from dataclasses import dataclass

from core.container import ServiceContainer


@dataclass(frozen=True)
class DoctorCheck:
    """Result of a single doctor diagnostic."""

    name: str
    healthy: bool
    detail: str


def _configured(value: object | None) -> bool:
    """Return whether a configuration value is present."""
    return value is not None


def run_doctor(container: ServiceContainer) -> list[DoctorCheck]:
    """Run infrastructure doctor diagnostics."""
    settings = container.settings
    checks = [
        DoctorCheck("Configuration", True, "settings loaded"),
        DoctorCheck("Environment Variables", True, "required variables loaded"),
        DoctorCheck("OpenAI Configuration", _configured(settings.openai_api_key), "key"),
        DoctorCheck(
            "Google Configuration",
            all(
                (
                    settings.google_client_id,
                    settings.google_client_secret,
                    settings.google_maps_api_key,
                )
            ),
            "client id, secret, maps key",
        ),
        DoctorCheck("GitHub Configuration", _configured(settings.github_token), "token"),
        DoctorCheck("Weather Configuration", _configured(settings.weather_api_key), "key"),
    ]
    for report in container.health.reports():
        checks.append(DoctorCheck(report.name.title(), report.healthy, report.detail))
    return checks

