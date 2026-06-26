"""Authentication CLI commands.

Purpose: expose Google OAuth authentication operations.
Responsibilities: call shared authentication services and render results.
Dependencies: Typer, Rich output helpers, and infrastructure container.
Extension Notes: add local callback server only as a separate command later.
"""

import typer

from apps.cli.output import render_mapping
from core.container import ServiceContainer

auth_app = typer.Typer(help="Google authentication commands.")


def _container() -> ServiceContainer:
    """Return the application container."""
    from core.factory import create_container

    return create_container()


@auth_app.command("login")
def login(redirect_uri: str) -> None:
    """Generate a Google OAuth login URL."""
    from apps.cli.console import console
    from services.auth.factory import create_auth_service

    container = _container()
    container.start()
    try:
        with container.database.get_session_factory()() as session:
            service = create_auth_service(container.settings, session, container.redis.get_client())
            result = service.login(redirect_uri)
            render_mapping(console, "Google Login", result.__dict__)
    finally:
        container.stop()


@auth_app.command("status")
def status(email: str) -> None:
    """Show Google authentication status."""
    from apps.cli.console import console
    from services.auth.factory import create_auth_service

    container = _container()
    container.start()
    try:
        with container.database.get_session_factory()() as session:
            service = create_auth_service(container.settings, session, container.redis.get_client())
            render_mapping(console, "Auth Status", service.status(email).__dict__)
    finally:
        container.stop()


@auth_app.command("logout")
def logout(email: str) -> None:
    """Logout and revoke Google OAuth token."""
    from apps.cli.console import console
    from services.auth.factory import create_auth_service

    container = _container()
    container.start()
    try:
        with container.database.get_session_factory()() as session:
            service = create_auth_service(container.settings, session, container.redis.get_client())
            render_mapping(console, "Logout", service.logout(email).__dict__)
    finally:
        container.stop()


@auth_app.command("refresh")
def refresh(email: str) -> None:
    """Refresh Google OAuth token."""
    from apps.cli.console import console
    from services.auth.factory import create_auth_service

    container = _container()
    container.start()
    try:
        with container.database.get_session_factory()() as session:
            service = create_auth_service(container.settings, session, container.redis.get_client())
            render_mapping(console, "Refresh", service.refresh(email).__dict__)
    finally:
        container.stop()
