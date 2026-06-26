"""Sheets API routes.

Purpose: expose Google Sheets SDK wrapper endpoints.
Responsibilities: validate HTTP input and call SheetsService.
Dependencies: FastAPI and Google route factory.
Extension Notes: spreadsheet business validation belongs above these routes.
"""

from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from apps.api.dependencies import get_container
from apps.api.responses import success
from apps.api.routes.google import factory
from apps.api.schemas.google.sheets import CreateSpreadsheetRequest, ShareEntry, SheetOperation
from apps.api.schemas.google.sheets import UpdateSpreadsheetRequest
from core.container import ServiceContainer

router = APIRouter(prefix="/sheets", tags=["sheets"])


def list_sheets(
    email: str = Query(...),
    page_token: str | None = None,
    max_results: int = Query(25, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """List available Google Sheets."""
    with container.database.get_session_factory()() as session:
        data = factory.sheets(container, session).list_spreadsheets(email, page_token, max_results)
    return success(data)


def read_sheet(
    id: str,
    email: str = Query(...),
    range: str = Query("A1:Z100"),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Read spreadsheet metadata."""
    with container.database.get_session_factory()() as session:
        data = factory.sheets(container, session).read_spreadsheet(email, id, range)
    return success(data)


def create_sheet(
    request: CreateSpreadsheetRequest,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Create spreadsheet, then apply headers, data rows, formatting, and sharing."""
    owner = str(request.email)
    worksheet = request.worksheet
    spreadsheet_id: str = ""

    with container.database.get_session_factory()() as session:
        svc = factory.sheets(container, session)
        data = svc.create_spreadsheet(owner, request.title, worksheet)
        spreadsheet_id = str(data.get("id", ""))

        if spreadsheet_id:
            # Resolve the real sheetId from the API response (never assume 0)
            worksheets = data.get("worksheets", [])
            sheet_id: int = 0
            if isinstance(worksheets, list) and worksheets:
                first = worksheets[0]
                if isinstance(first, dict) and first.get("id") is not None:
                    sheet_id = int(first["id"])

            # Write header row, then data rows in a single append call when possible
            all_rows: list[list[object]] = []
            if request.headers:
                all_rows.append(list(request.headers))
            all_rows.extend(request.rows)
            if all_rows:
                svc.append_rows(owner, spreadsheet_id, f"{worksheet}!A1", all_rows)

            batch_requests: list[dict[str, object]] = []

            if request.freeze_header and request.headers:
                batch_requests.append(_freeze_row_request(sheet_id))

            if request.auto_resize_columns:
                batch_requests.append(_auto_resize_request(sheet_id))

            if request.create_chart and request.headers and request.rows:
                batch_requests.append(_basic_chart_request(sheet_id, len(request.headers), len(request.rows)))

            if batch_requests:
                svc.batch_update(owner, spreadsheet_id, {"requests": batch_requests})

    # Sharing goes through Drive Permissions API — outside the Sheets session
    shares: list[dict[str, object]] = []
    if spreadsheet_id and request.share_with:
        with container.database.get_session_factory()() as session:
            drv = factory.drive(container, session)
            for entry in request.share_with:
                if isinstance(entry, ShareEntry):
                    target, role = str(entry.email), entry.role
                else:
                    target, role = str(entry), "reader"
                shares.append(drv.share_file(owner, spreadsheet_id, target, role))

    return success(data, {"shares": shares})


def update_sheet(
    id: str,
    request: UpdateSpreadsheetRequest,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Update spreadsheet cells."""
    with container.database.get_session_factory()() as session:
        service = factory.sheets(container, session)
        if request.operation == SheetOperation.BATCH:
            data = service.batch_update(str(request.email), id, {"requests": request.requests})
        elif request.operation == SheetOperation.APPEND:
            data = service.append_rows(str(request.email), id, request.a1_range(), request.values)
        else:
            data = service.update_cells(str(request.email), id, request.a1_range(), request.values)
    return success(data)


# ── Sheets batchUpdate request builders ──────────────────────────────────────

def _freeze_row_request(sheet_id: int) -> dict[str, object]:
    return {
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {"frozenRowCount": 1},
            },
            "fields": "gridProperties.frozenRowCount",
        }
    }


def _auto_resize_request(sheet_id: int) -> dict[str, object]:
    return {
        "autoResizeDimensions": {
            "dimensions": {
                "sheetId": sheet_id,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": 26,
            }
        }
    }


def _basic_chart_request(sheet_id: int, col_count: int, row_count: int) -> dict[str, object]:
    """Embed a basic column chart over the data range (best-effort)."""
    return {
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Data Chart",
                    "basicChart": {
                        "chartType": "COLUMN",
                        "legendPosition": "BOTTOM_LEGEND",
                        "axis": [{"position": "BOTTOM_AXIS"}, {"position": "LEFT_AXIS"}],
                        "domains": [
                            {
                                "domain": {
                                    "sourceRange": {
                                        "sources": [
                                            {
                                                "sheetId": sheet_id,
                                                "startRowIndex": 0,
                                                "endRowIndex": row_count + 1,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 1,
                                            }
                                        ]
                                    }
                                }
                            }
                        ],
                        "series": [
                            {
                                "series": {
                                    "sourceRange": {
                                        "sources": [
                                            {
                                                "sheetId": sheet_id,
                                                "startRowIndex": 0,
                                                "endRowIndex": row_count + 1,
                                                "startColumnIndex": i,
                                                "endColumnIndex": i + 1,
                                            }
                                        ]
                                    }
                                },
                                "targetAxis": "LEFT_AXIS",
                            }
                            for i in range(1, min(col_count, 5))
                        ],
                    },
                },
                "position": {"newSheet": True},
            }
        }
    }


def export_sheet(
    id: str,
    email: str = Query(...),
    format: str = Query("xlsx", description="xlsx, csv, tsv, pdf, ods"),
    container: ServiceContainer = Depends(get_container),
) -> StreamingResponse:
    """Export a Google Sheet as a downloadable file."""
    with container.database.get_session_factory()() as session:
        raw, content_type, filename = factory.sheets(container, session).export_spreadsheet(email, id, format)
    safe_filename = quote(filename, safe=".-_")
    headers = {"Content-Disposition": f"attachment; filename=\"{safe_filename}\""}
    return StreamingResponse(BytesIO(raw), media_type=content_type, headers=headers)


router.add_api_route("", list_sheets, methods=["GET"])
router.add_api_route("/{id}", read_sheet, methods=["GET"])
router.add_api_route("/{id}/export", export_sheet, methods=["GET"])
router.add_api_route("", create_sheet, methods=["POST"])
router.add_api_route("/{id}", update_sheet, methods=["PATCH"])
