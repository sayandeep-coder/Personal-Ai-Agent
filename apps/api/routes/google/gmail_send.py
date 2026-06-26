"""Gmail send API route.

Purpose: expose production Gmail send operation.
Responsibilities: validate send requests and return safe metadata.
Dependencies: FastAPI, Google route factory, and Gmail schemas.
Extension Notes: add attachment support without changing route ownership.
"""

from fastapi import APIRouter, Depends

from apps.api.dependencies import get_container
from apps.api.responses import success
from apps.api.routes.google import factory
from apps.api.schemas.google.gmail import GmailSendRequest
from core.container import ServiceContainer
from services.google.gmail.send import AttachmentSpec

router = APIRouter()


def send_message(
    request: GmailSendRequest,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Send a Gmail message."""
    attachments = [
        AttachmentSpec(a.filename, a.mime_type, a.content_base64)
        for a in request.attachments
    ] or None
    with container.database.get_session_factory()() as session:
        data = factory.gmail(container, session).send_message(
            str(request.email),
            [str(r) for r in request.to],
            request.subject,
            request.body_text,
            request.body_html,
            cc=[str(r) for r in request.cc] or None,
            bcc=[str(r) for r in request.bcc] or None,
            attachments=attachments,
        )
    return success(data)


router.add_api_route("/send", send_message, methods=["POST"])
