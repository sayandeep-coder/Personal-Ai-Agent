"""Google OAuth API routes.

Purpose: expose Google OAuth authentication endpoints.
Responsibilities: route HTTP requests to authentication services.
Dependencies: FastAPI, schemas, and auth service factory.
Extension Notes: keep provider SDK behavior out of route handlers.
"""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from apps.api.dependencies import get_container
from apps.api.routes.auth.factory import create_auth_service
from apps.api.schemas.auth.google import AuthActionRequest, AuthResultResponse
from apps.api.schemas.auth.google import AuthStatusResponse
from core.container import ServiceContainer
from core.exceptions import ApplicationException

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
def google_login(
    redirect_uri: str = Query(...),
    container: ServiceContainer = Depends(get_container),
) -> RedirectResponse:
    """Redirect the user to Google OAuth consent."""
    with container.database.get_session_factory()() as session:
        service = create_auth_service(container, session)
        return RedirectResponse(service.login(redirect_uri).authorization_url)


@router.get("/google/callback")
def google_callback(
    response: Response,
    code: str = Query(...),
    state: str = Query(...),
    container: ServiceContainer = Depends(get_container),
) -> AuthResultResponse:
    """Handle Google OAuth callback."""
    try:
        with container.database.get_session_factory()() as session:
            service = create_auth_service(container, session)
            result = service.callback(code, state)
            response.set_cookie("pa_user_email", result.email, httponly=True, secure=True)
            return AuthResultResponse(**result.__dict__)
    except ApplicationException as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc


@router.get("/status")
def auth_status(
    email: str | None = Query(default=None),
    cookie_email: str | None = Cookie(default=None, alias="pa_user_email"),
    container: ServiceContainer = Depends(get_container),
) -> AuthStatusResponse:
    """Return Google authentication status."""
    with container.database.get_session_factory()() as session:
        service = create_auth_service(container, session)
        return AuthStatusResponse(**service.status(email or cookie_email).__dict__)


@router.post("/logout")
def auth_logout(
    request: AuthActionRequest,
    response: Response,
    container: ServiceContainer = Depends(get_container),
) -> AuthStatusResponse:
    """Revoke Google token and disconnect integration."""
    with container.database.get_session_factory()() as session:
        service = create_auth_service(container, session)
        status_result = service.logout(str(request.email))
        response.delete_cookie("pa_user_email")
        return AuthStatusResponse(**status_result.__dict__)


@router.post("/refresh")
def auth_refresh(
    request: AuthActionRequest,
    container: ServiceContainer = Depends(get_container),
) -> AuthResultResponse:
    """Refresh Google OAuth tokens."""
    with container.database.get_session_factory()() as session:
        service = create_auth_service(container, session)
        return AuthResultResponse(**service.refresh(str(request.email)).__dict__)
