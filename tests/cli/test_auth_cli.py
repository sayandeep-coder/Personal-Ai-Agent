"""Auth CLI tests.

Purpose: verify auth command surface is available.
Responsibilities: smoke-test top-level CLI help for auth command registration.
Dependencies: subprocess and Python module execution.
Extension Notes: add command service tests with CLI runner fakes later.
"""

import subprocess
import sys


def test_cli_help_lists_auth_command() -> None:
    """CLI help lists the auth command group."""
    result = subprocess.run(
        [sys.executable, "-m", "apps.cli.main", "--help"],
        capture_output=True,
        check=True,
        text=True,
    )
    assert "auth" in result.stdout
    assert "gmail" in result.stdout
    assert "calendar" in result.stdout
    assert "drive" in result.stdout
    assert "docs" in result.stdout
    assert "sheets" in result.stdout
