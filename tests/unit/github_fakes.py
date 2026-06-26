"""GitHub service test fakes.

Purpose: provide a deterministic fake GitHub API client for unit tests.
Responsibilities: simulate public repos, private repos, auth errors, and rate limits.
Dependencies: GitHubApiPort protocol shape, ValidationException.
Extension Notes: add new path-keyed payloads as new endpoints are added.
"""

from core.exceptions import ValidationException
from integrations.github.protocols import JsonDict


def _public_repo(owner: str = "octocat", name: str = "hello-world") -> JsonDict:
    return {
        "id": 1296269,
        "name": name,
        "full_name": f"{owner}/{name}",
        "owner": {"login": owner},
        "description": "A test repository.",
        "html_url": f"https://github.com/{owner}/{name}",
        "clone_url": f"https://github.com/{owner}/{name}.git",
        "language": "Python",
        "stargazers_count": 42,
        "forks_count": 7,
        "watchers_count": 42,
        "open_issues_count": 3,
        "license": {"name": "MIT License"},
        "topics": ["python", "testing"],
        "default_branch": "main",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2026-06-01T00:00:00Z",
        "pushed_at": "2026-06-20T00:00:00Z",
        "size": 128,
        "archived": False,
        "disabled": False,
        "visibility": "public",
        "private": False,
    }


def _private_repo(owner: str = "corp", name: str = "secret") -> JsonDict:
    repo = _public_repo(owner, name)
    repo["private"] = True
    repo["visibility"] = "private"
    return repo


def _user() -> JsonDict:
    return {
        "login": "octocat",
        "name": "The Octocat",
        "bio": "GitHub mascot.",
        "avatar_url": "https://avatars.githubusercontent.com/u/583231",
        "html_url": "https://github.com/octocat",
        "public_repos": 10,
        "followers": 9000,
        "following": 9,
        "created_at": "2011-01-25T18:44:36Z",
        "updated_at": "2026-06-01T00:00:00Z",
        "location": "San Francisco",
        "company": "GitHub",
        "blog": "https://github.blog",
        "twitter_username": "github",
    }


def _commit() -> JsonDict:
    return {
        "sha": "abc123",
        "commit": {
            "message": "Initial commit",
            "author": {"name": "Octocat", "email": "octocat@github.com", "date": "2026-06-01T00:00:00Z"},
            "committer": {"name": "Octocat", "date": "2026-06-01T00:00:00Z"},
        },
        "author": {"login": "octocat"},
        "html_url": "https://github.com/octocat/hello-world/commit/abc123",
    }


def _issue() -> JsonDict:
    return {
        "number": 1,
        "title": "Bug report",
        "state": "open",
        "body": "Something is broken.",
        "user": {"login": "reporter"},
        "labels": [{"name": "bug"}],
        "created_at": "2026-06-01T00:00:00Z",
        "updated_at": "2026-06-10T00:00:00Z",
        "closed_at": None,
        "html_url": "https://github.com/octocat/hello-world/issues/1",
        "comments": 2,
    }


def _pull() -> JsonDict:
    return {
        "number": 5,
        "title": "Feature: add widget",
        "state": "open",
        "body": "Adds a widget.",
        "user": {"login": "developer"},
        "head": {"ref": "feature/widget"},
        "base": {"ref": "main"},
        "draft": False,
        "merged": False,
        "merged_at": None,
        "created_at": "2026-06-15T00:00:00Z",
        "updated_at": "2026-06-20T00:00:00Z",
        "closed_at": None,
        "html_url": "https://github.com/octocat/hello-world/pull/5",
        "commits": 3,
        "additions": 50,
        "deletions": 10,
        "changed_files": 4,
    }


def _release() -> JsonDict:
    return {
        "id": 100,
        "tag_name": "v1.0.0",
        "name": "Version 1.0",
        "body": "First stable release.",
        "draft": False,
        "prerelease": False,
        "created_at": "2026-06-01T00:00:00Z",
        "published_at": "2026-06-01T00:00:00Z",
        "html_url": "https://github.com/octocat/hello-world/releases/tag/v1.0.0",
        "author": {"login": "octocat"},
    }


def _branch() -> JsonDict:
    return {"name": "main", "commit": {"sha": "abc123"}, "protected": True}


def _readme() -> JsonDict:
    import base64
    encoded = base64.b64encode(b"# Hello World\n\nThis is the readme.").decode()
    return {
        "name": "README.md",
        "path": "README.md",
        "encoding": "base64",
        "html_url": "https://github.com/octocat/hello-world/blob/main/README.md",
        "content": encoded + "\n",
    }


class FakeGitHubClient:
    """Fake GitHub API client for unit tests.

    Routes by path prefix. Simulates:
      - Public repos (normal flow)
      - Private repos (for enforcement tests)
      - 401 invalid token
      - 429 rate limit
    """

    def __init__(self, *, force_private: bool = False, force_401: bool = False, force_429: bool = False) -> None:
        self._force_private = force_private
        self._force_401 = force_401
        self._force_429 = force_429
        self.calls: list[tuple[str, JsonDict | None]] = []

    def get(self, path: str, params: JsonDict | None = None) -> JsonDict:
        self.calls.append((path, params))
        self._check_errors(path)

        # /users/{username}/repos — must precede the plain /users/{username} check
        if path.startswith("/users/") and path.endswith("/repos"):
            username = path.split("/")[2]
            return _public_repo(owner=username)

        if path.startswith("/users/"):
            return _user()

        # Specific /repos sub-paths — must precede the bare /repos/{owner}/{repo} check
        if path.startswith("/repos/") and path.endswith("/readme"):
            return _readme()

        if path.startswith("/repos/") and path.endswith("/languages"):
            return {"Python": 12000, "Shell": 500}

        if path.startswith("/repos/") and "/commits/" in path:
            return _commit()

        if path.startswith("/repos/") and "/pulls/" in path:
            return _pull()

        # Bare /repos/{owner}/{repo} — exactly 4 segments: ['', 'repos', owner, repo]
        if path.startswith("/repos/"):
            parts = path.split("/")
            if len(parts) == 4:
                owner, repo = parts[2], parts[3]
                return _private_repo(owner, repo) if self._force_private else _public_repo(owner, repo)

        if path.startswith("/search/repositories"):
            item = _public_repo()
            return {"total_count": 1, "incomplete_results": False, "items": [item]}

        if path.startswith("/search/users"):
            return {
                "total_count": 1,
                "incomplete_results": False,
                "items": [{"login": "octocat", "avatar_url": "", "html_url": "", "type": "User", "score": 1.0}],
            }

        return {}

    def get_list(self, path: str, params: JsonDict | None = None) -> list[JsonDict]:
        self.calls.append((path, params))
        self._check_errors(path)

        if path.endswith("/repos"):
            return [_public_repo()]

        if path.endswith("/commits"):
            return [_commit()]

        if path.endswith("/issues"):
            return [_issue()]

        if path.endswith("/pulls"):
            return [_pull()]

        if path.endswith("/releases"):
            return [_release()]

        if path.endswith("/branches"):
            return [_branch()]

        if path.endswith("/contributors"):
            return [{"login": "octocat", "avatar_url": "", "html_url": "", "contributions": 99, "type": "User"}]

        return []

    def _check_errors(self, path: str) -> None:
        if self._force_401:
            raise ValidationException(
                "GitHub token is invalid or expired.",
                code="github.api_error",
                details={"github_status": 401, "path": path},
            )
        if self._force_429:
            raise ValidationException(
                "GitHub API rate limit exceeded.",
                code="github.api_error",
                details={"github_status": 429, "path": path},
            )
