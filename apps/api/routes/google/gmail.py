"""Gmail API routes.

Purpose: expose Gmail SDK wrapper endpoints.
Responsibilities: validate HTTP input and call GmailService.
Dependencies: FastAPI and Google route factory.
Extension Notes: keep AI and summarization out of these routes.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from apps.api.dependencies import get_container
from apps.api.responses import success
from apps.api.routes.google import factory
from apps.api.routes.google.gmail_send import router as send_router
from apps.api.schemas.google.gmail import GmailSearchQuery
from core.container import ServiceContainer

router = APIRouter(prefix="/gmail", tags=["gmail"])


def list_messages(
    email: str = Query(..., description="Authenticated Google account email"),
    page_token: str | None = Query(None, description="Google pagination token"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum messages"),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """List normalized Gmail message summaries."""
    with container.database.get_session_factory()() as session:
        data = factory.gmail(container, session).list_messages(email, page_token, max_results)
    return success(data)

def get_message(
    id: str,
    email: str = Query(...),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Read and decode a Gmail message."""
    with container.database.get_session_factory()() as session:
        data = factory.gmail(container, session).get_message(email, id)
    return success(data)

def search(
    email: str = Query(...),
    subject: str | None = None,
    from_: str | None = Query(None, alias="from"),
    to: str | None = None,
    label: str | None = None,
    after: date | None = None,
    before: date | None = None,
    has_attachment: bool = Query(False, alias="has:attachment"),
    unread: bool = Query(False, alias="is:unread"),
    page_token: str | None = None,
    max_results: int = Query(10, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Search Gmail with structured filters."""
    query = GmailSearchQuery(
        subject=subject,
        sender=from_,
        to=to,
        label=label,
        after=after,
        before=before,
        has_attachment=has_attachment,
        unread=unread,
    )
    with container.database.get_session_factory()() as session:
        data = factory.gmail(container, session).search_messages(
            email,
            query.to_query(),
            max_results,
            page_token,
        )
    return success(data, {"query": query.to_query()})

def unread(email: str = Query(...), container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return unread count."""
    with container.database.get_session_factory()() as session:
        service = factory.gmail(container, session)
        data = service.search_messages(email, "is:unread", 10)
        data["count"] = service.unread_count(email)
    return success(data)

def labels(email: str = Query(...), container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Return labels."""
    with container.database.get_session_factory()() as session:
        data = factory.gmail(container, session).labels(email)
    return success(data)

router.add_api_route("/messages", list_messages, methods=["GET"])
router.add_api_route("/messages/{id}", get_message, methods=["GET"])
router.add_api_route("/search", search, methods=["GET"])
router.add_api_route("/unread", unread, methods=["GET"])
router.add_api_route("/labels", labels, methods=["GET"])
router.include_router(send_router)
