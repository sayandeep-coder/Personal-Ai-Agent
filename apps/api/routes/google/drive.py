"""Drive API routes.

Purpose: expose Google Drive SDK wrapper endpoints.
Responsibilities: validate HTTP input and call DriveService.
Dependencies: FastAPI and Google route factory.
Extension Notes: streaming downloads/uploads can replace JSON payloads later.
"""

from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from apps.api.dependencies import get_container
from apps.api.responses import success
from apps.api.routes.google import factory
from apps.api.schemas.google.drive import DriveSearchQuery, DriveUploadRequest
from core.container import ServiceContainer

router = APIRouter(prefix="/drive", tags=["drive"])


def list_files(
    email: str = Query(...),
    name: str | None = None,
    mime_type: str | None = None,
    folder: str | None = None,
    owner: str | None = None,
    page_token: str | None = None,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """List or search normalized Drive files."""
    search = DriveSearchQuery(name=name, mime_type=mime_type, folder=folder, owner=owner)
    with container.database.get_session_factory()() as session:
        service = factory.drive(container, session)
        data = service.search_files(email, search.to_query()) if search.to_query() else service.list_files(email, page_token)
    return success(data)


def upload(request: DriveUploadRequest, container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Upload Drive file."""
    with container.database.get_session_factory()() as session:
        service = factory.drive(container, session)
        data = service.upload(str(request.email), request.metadata(), request.content)
    return success(data)


def download(
    id: str,
    email: str = Query(...),
    container: ServiceContainer = Depends(get_container),
) -> StreamingResponse:
    """Download a Drive file as a binary stream."""
    from urllib.parse import quote as _quote
    with container.database.get_session_factory()() as session:
        raw, content_type, filename = factory.drive(container, session).download(email, id)
    safe_filename = _quote(filename, safe=".-_")
    headers = {"Content-Disposition": f"attachment; filename=\"{safe_filename}\""}
    return StreamingResponse(BytesIO(raw), media_type=content_type, headers=headers)


def delete_file(
    id: str,
    email: str = Query(...),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Delete Drive file."""
    with container.database.get_session_factory()() as session:
        data = factory.drive(container, session).delete(email, id)
    return success(data)


router.add_api_route("/files", list_files, methods=["GET"])
router.add_api_route("/files/{id}/download", download, methods=["GET"])
router.add_api_route("/upload", upload, methods=["POST"])
router.add_api_route("/files/{id}", delete_file, methods=["DELETE"])
