"""Docs API routes.

Purpose: expose Google Docs SDK wrapper endpoints.
Responsibilities: validate HTTP input and call DocsService.
Dependencies: FastAPI and Google route factory.
Extension Notes: document editing policy belongs above these routes.
"""

from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from apps.api.dependencies import get_container
from apps.api.responses import success
from apps.api.routes.google import factory
from apps.api.schemas.google.docs import CreateDocumentRequest, DocShareEntry, PatchDocumentRequest
from core.container import ServiceContainer

router = APIRouter(prefix="/docs", tags=["docs"])


def list_docs(
    email: str = Query(...),
    page_token: str | None = None,
    max_results: int = Query(25, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """List available Google Docs."""
    with container.database.get_session_factory()() as session:
        data = factory.docs(container, session).list_documents(email, page_token, max_results)
    return success(data)


def read_doc(id: str, email: str = Query(...), container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Read a document."""
    with container.database.get_session_factory()() as session:
        data = factory.docs(container, session).read_document(email, id)
    return success(data)


def create_doc(request: CreateDocumentRequest, container: ServiceContainer = Depends(get_container)) -> dict[str, object]:
    """Create a document with optional structure, formatting, and sharing."""
    owner = str(request.email)
    body = _build_body(request)

    with container.database.get_session_factory()() as session:
        data = factory.docs(container, session).create_document(owner, request.title, body)

    doc_id = str(data.get("id", ""))

    shares: list[dict[str, object]] = []
    if doc_id and request.share_with:
        with container.database.get_session_factory()() as session:
            drv = factory.drive(container, session)
            for entry in request.share_with:
                if isinstance(entry, DocShareEntry):
                    target, role = str(entry.email), entry.role
                else:
                    target, role = str(entry), "reader"
                shares.append(drv.share_file(owner, doc_id, target, role))

    return success(data, {"folder_id": request.folder_id, "shares": shares})


def patch_doc(
    id: str,
    request: PatchDocumentRequest,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Patch a document using a structured edit operation."""
    with container.database.get_session_factory()() as session:
        data = factory.docs(container, session).batch_update(str(request.email), id, request.to_batch())
    return success(data)


# ── Body builder ─────────────────────────────────────────────────────────────

def _build_body(req: CreateDocumentRequest) -> str:
    """Assemble the full document body from all structured fields."""
    parts: list[str] = []

    if req.generate_title_page:
        meta = req.metadata
        parts.append(f"{req.title}\n{'=' * len(req.title)}")
        if meta:
            if meta.author:
                parts.append(f"Author: {meta.author}")
            if meta.version:
                parts.append(f"Version: {meta.version}")
            if meta.project:
                parts.append(f"Project: {meta.project}")
            if meta.department:
                parts.append(f"Department: {meta.department}")
            if meta.classification:
                parts.append(f"Classification: {meta.classification}")
        if req.tags:
            parts.append(f"Tags: {', '.join(req.tags)}")
        parts.append(f"Locale: {req.locale}  |  Timezone: {req.timezone}")
        parts.append("")

    if req.add_header and req.header_text:
        parts.append(req.header_text)
        parts.append("-" * len(req.header_text))
        parts.append("")

    if req.create_table_of_contents and req.content:
        toc_lines = _extract_toc(req.content, req.format)
        if toc_lines:
            parts.append("Table of Contents")
            parts.append("-" * 17)
            parts.extend(toc_lines)
            parts.append("")

    if req.content:
        if req.page_break_between_sections and req.format == "markdown":
            parts.append(_insert_page_breaks(req.content))
        else:
            parts.append(req.content)

    if req.add_footer and req.footer_text:
        parts.append("")
        parts.append("-" * len(req.footer_text))
        parts.append(req.footer_text)

    return "\n".join(parts)


def _extract_toc(content: str, fmt: str) -> list[str]:
    """Return a plain-text TOC from Markdown headings."""
    if fmt != "markdown":
        return []
    lines: list[str] = []
    for line in content.splitlines():
        if line.startswith("### "):
            lines.append(f"    • {line[4:].strip()}")
        elif line.startswith("## "):
            lines.append(f"  • {line[3:].strip()}")
        elif line.startswith("# "):
            lines.append(f"• {line[2:].strip()}")
    return lines


def _insert_page_breaks(content: str) -> str:
    """Insert a page-break marker before each top-level Markdown heading."""
    out: list[str] = []
    for line in content.splitlines():
        if line.startswith("# ") and out:
            out.append("\n--- page break ---\n")
        out.append(line)
    return "\n".join(out)


def export_doc(
    id: str,
    email: str = Query(...),
    format: str = Query("pdf", description="pdf, docx, odt, html, txt, markdown, epub"),
    container: ServiceContainer = Depends(get_container),
) -> StreamingResponse:
    """Export a Google Doc as a downloadable file."""
    with container.database.get_session_factory()() as session:
        raw, content_type, filename = factory.docs(container, session).export_document(email, id, format)
    safe_filename = quote(filename, safe=".-_")
    headers = {"Content-Disposition": f"attachment; filename=\"{safe_filename}\""}
    return StreamingResponse(BytesIO(raw), media_type=content_type, headers=headers)


router.add_api_route("", list_docs, methods=["GET"])
router.add_api_route("/{id}", read_doc, methods=["GET"])
router.add_api_route("/{id}/export", export_doc, methods=["GET"])
router.add_api_route("", create_doc, methods=["POST"])
router.add_api_route("/{id}", patch_doc, methods=["PATCH"])
