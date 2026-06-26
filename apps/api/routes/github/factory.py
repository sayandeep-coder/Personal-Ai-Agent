"""GitHub service factory for routes.

Purpose: construct GitHubService from the DI container.
Responsibilities: resolve GITHUB_TOKEN from settings; never expose it.
Dependencies: container, GitHubApiClient, GitHubService.
"""

from core.container import ServiceContainer
from core.exceptions import ValidationException
from integrations.github.client import GitHubApiClient
from services.github.service import GitHubService


def github(container: ServiceContainer) -> GitHubService:
    """Create a GitHubService using the configured PAT.

    Raises ValidationException if GITHUB_TOKEN is not configured so that
    the error is caught by the standard error handler and returned as 400
    rather than a 500 from a NoneType dereference.
    """
    token = container.settings.github_token
    if not token:
        raise ValidationException(
            "GITHUB_TOKEN is not configured. Set it in .env to enable GitHub integration.",
            code="github.token_not_configured",
        )
    return GitHubService(GitHubApiClient(token.get_secret_value()))
