"""GitHub API route smoke tests.

Purpose: verify GitHub API router is registered with all 14 endpoints.
Responsibilities: assert expected route paths exist on the FastAPI app.
Dependencies: app factory with fake container.
"""

from apps.api.app import create_app
from core.factory import create_container


def test_github_routes_are_registered() -> None:
    """All GitHub integration routes are present on the application."""
    app = create_app(create_container())
    paths = set(app.openapi()["paths"])

    assert "/api/v1/github/users/{username}" in paths
    assert "/api/v1/github/users/{username}/repos" in paths

    assert "/api/v1/github/repos/{owner}/{repo}" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/readme" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/languages" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/contributors" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/branches" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/commits" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/releases" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/issues" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/pulls" in paths
    assert "/api/v1/github/repos/{owner}/{repo}/pulls/{pull_number}" in paths

    assert "/api/v1/github/search/repositories" in paths
    assert "/api/v1/github/search/users" in paths
