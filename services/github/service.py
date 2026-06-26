"""GitHub service wrapper.

Purpose: provide read-only access to public GitHub data.
Responsibilities:
  - Enforce the public-repository-only policy at the service layer.
  - Normalize all GitHub API responses into stable application contracts.
  - Log every operation with correlation context (never the PAT).
Dependencies: GitHubApiPort, normalizers, ValidationException.

Security invariants:
  - EVERY repository operation calls _assert_public() before proceeding.
  - _assert_public() is the single, non-bypassable enforcement point.
  - No route or controller can skip it.
  - Private repositories are rejected with HTTP 403 before any data is read.
"""

from core.exceptions import ValidationException
from core.logging import get_logger
from integrations.github.protocols import GitHubApiPort, JsonDict
from services.github import normalizers

_logger = get_logger(__name__)

_PRIVATE_REPO_CODE = "github.private_repository"


class GitHubService:
    """Read-only GitHub service enforcing public-repository-only access."""

    def __init__(self, client: GitHubApiPort) -> None:
        """Create a GitHub service."""
        self._client = client

    # ── User endpoints ────────────────────────────────────────────────────────

    def get_user(self, username: str) -> JsonDict:
        """Return normalized public profile for a GitHub user."""
        _logger.warning("github_get_user", username=username)
        raw = self._client.get(f"/users/{username}")
        return normalizers.user_profile(raw)

    def get_user_repos(
        self,
        username: str,
        page: int = 1,
        per_page: int = 30,
        sort: str = "updated",
    ) -> list[JsonDict]:
        """Return normalized public repositories for a user."""
        _logger.warning(
            "github_get_user_repos",
            username=username,
            page=page,
            per_page=per_page,
            sort=sort,
        )
        items = self._client.get_list(
            f"/users/{username}/repos",
            {"type": "public", "sort": sort, "page": page, "per_page": per_page},
        )
        return [normalizers.repository(r) for r in items]

    # ── Repository endpoints ──────────────────────────────────────────────────

    def get_repo(self, owner: str, repo: str) -> JsonDict:
        """Return normalized metadata for a public repository."""
        _logger.warning("github_get_repo", owner=owner, repo=repo)
        raw = self._client.get(f"/repos/{owner}/{repo}")
        self._assert_public(raw, owner, repo)
        return normalizers.repository(raw)

    def get_readme(self, owner: str, repo: str) -> JsonDict:
        """Return the decoded README for a public repository."""
        _logger.warning("github_get_readme", owner=owner, repo=repo)
        self._check_public(owner, repo)
        raw = self._client.get(f"/repos/{owner}/{repo}/readme")
        return normalizers.readme(raw)

    def get_languages(self, owner: str, repo: str) -> JsonDict:
        """Return language breakdown for a public repository."""
        _logger.warning("github_get_languages", owner=owner, repo=repo)
        self._check_public(owner, repo)
        return self._client.get(f"/repos/{owner}/{repo}/languages")

    def get_contributors(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30
    ) -> list[JsonDict]:
        """Return contributors for a public repository."""
        _logger.warning("github_get_contributors", owner=owner, repo=repo)
        self._check_public(owner, repo)
        items = self._client.get_list(
            f"/repos/{owner}/{repo}/contributors",
            {"page": page, "per_page": per_page},
        )
        return [normalizers.contributor(c) for c in items]

    def get_branches(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30
    ) -> list[JsonDict]:
        """Return branches for a public repository."""
        _logger.warning("github_get_branches", owner=owner, repo=repo)
        self._check_public(owner, repo)
        items = self._client.get_list(
            f"/repos/{owner}/{repo}/branches",
            {"page": page, "per_page": per_page},
        )
        return [normalizers.branch(b) for b in items]

    def get_commits(
        self,
        owner: str,
        repo: str,
        page: int = 1,
        per_page: int = 30,
        branch: str | None = None,
    ) -> list[JsonDict]:
        """Return commits for a public repository."""
        _logger.warning(
            "github_get_commits", owner=owner, repo=repo, branch=branch
        )
        self._check_public(owner, repo)
        params: JsonDict = {"page": page, "per_page": per_page}
        if branch:
            params["sha"] = branch
        items = self._client.get_list(f"/repos/{owner}/{repo}/commits", params)
        return [normalizers.commit(c) for c in items]

    def get_releases(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30
    ) -> list[JsonDict]:
        """Return releases for a public repository."""
        _logger.warning("github_get_releases", owner=owner, repo=repo)
        self._check_public(owner, repo)
        items = self._client.get_list(
            f"/repos/{owner}/{repo}/releases",
            {"page": page, "per_page": per_page},
        )
        return [normalizers.release(r) for r in items]

    def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: str | None = None,
        page: int = 1,
        per_page: int = 30,
    ) -> list[JsonDict]:
        """Return issues for a public repository (excludes pull requests)."""
        _logger.warning(
            "github_get_issues", owner=owner, repo=repo, state=state
        )
        self._check_public(owner, repo)
        params: JsonDict = {"state": state, "page": page, "per_page": per_page}
        if labels:
            params["labels"] = labels
        items = self._client.get_list(f"/repos/{owner}/{repo}/issues", params)
        # GitHub /issues mixes in PRs — filter them out
        return [
            normalizers.issue(i)
            for i in items
            if not i.get("pull_request")
        ]

    def get_pulls(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> list[JsonDict]:
        """Return pull requests for a public repository."""
        _logger.warning(
            "github_get_pulls", owner=owner, repo=repo, state=state
        )
        self._check_public(owner, repo)
        items = self._client.get_list(
            f"/repos/{owner}/{repo}/pulls",
            {"state": state, "page": page, "per_page": per_page},
        )
        return [normalizers.pull_request(p) for p in items]

    def get_pull(self, owner: str, repo: str, pull_number: int) -> JsonDict:
        """Return a single pull request for a public repository."""
        _logger.warning(
            "github_get_pull", owner=owner, repo=repo, pull_number=pull_number
        )
        self._check_public(owner, repo)
        raw = self._client.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")
        return normalizers.pull_request(raw)

    # ── Search endpoints ──────────────────────────────────────────────────────

    def search_repositories(
        self, query: str, page: int = 1, per_page: int = 30, sort: str = "stars"
    ) -> JsonDict:
        """Search public GitHub repositories."""
        _logger.warning("github_search_repos", query=query)
        raw = self._client.get(
            "/search/repositories",
            {"q": query, "sort": sort, "page": page, "per_page": per_page},
        )
        result = normalizers.search_repositories(raw)
        # Filter any private repos that may appear in search results
        items = result.get("items", [])
        if isinstance(items, list):
            result["items"] = [r for r in items if not r.get("private")]
        return result

    def search_users(
        self, query: str, page: int = 1, per_page: int = 30
    ) -> JsonDict:
        """Search GitHub users."""
        _logger.warning("github_search_users", query=query)
        raw = self._client.get(
            "/search/users",
            {"q": query, "page": page, "per_page": per_page},
        )
        return normalizers.search_users(raw)

    # ── Private-repo enforcement ──────────────────────────────────────────────

    def _check_public(self, owner: str, repo: str) -> None:
        """Fetch repo metadata and assert it is public before any further API call.

        This is the enforcement gateway for all non-metadata repository
        operations.  It is called BEFORE fetching commits, branches, issues,
        PRs, releases, or README — never after.
        """
        raw = self._client.get(f"/repos/{owner}/{repo}")
        self._assert_public(raw, owner, repo)

    @staticmethod
    def _assert_public(raw: JsonDict, owner: str, repo: str) -> None:
        """Raise immediately if the repository is private.

        This is the single, central enforcement point.  It is:
          - Called by every repository operation path.
          - Cannot be skipped via any route or middleware.
          - Audited via the structured log line below.
        """
        if raw.get("private") is True:
            _logger.warning(
                "github_private_repo_rejected",
                owner=owner,
                repo=repo,
            )
            raise ValidationException(
                "Access to private repositories is disabled by server policy.",
                code=_PRIVATE_REPO_CODE,
            )
