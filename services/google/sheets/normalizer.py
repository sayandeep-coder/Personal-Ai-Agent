"""Sheets response normalization.

Purpose: convert Sheets API payloads into stable spreadsheet contracts.
Responsibilities: simplify worksheet metadata and value ranges.
Dependencies: Google Sheets JSON shapes.
Extension Notes: add typed column inference for AI table reasoning later.
"""

from integrations.google.common.http import JsonDict


def spreadsheet(payload: JsonDict, values: JsonDict | None = None) -> dict[str, object]:
    """Return a normalized spreadsheet."""
    spreadsheet_id = str(payload.get("spreadsheetId", ""))
    sheets = payload.get("sheets", [])
    sheets = sheets if isinstance(sheets, list) else []
    raw_rows = values.get("values", []) if values else []
    rows = raw_rows if isinstance(raw_rows, list) else []
    row_lists = [row for row in rows if isinstance(row, list)]
    url = str(payload.get("spreadsheetUrl") or _url(spreadsheet_id))
    return {
        "id": spreadsheet_id,
        "title": _title(payload),
        "url": url,
        "worksheets": [_worksheet(item) for item in sheets if isinstance(item, dict)],
        "rows": len(row_lists),
        "columns": max((len(row) for row in row_lists), default=0),
        "cell_values": rows,
        "metadata": {"url": url},
    }


def update_result(payload: JsonDict) -> dict[str, object]:
    """Return normalized update result."""
    return {
        "updated": True,
        "updated_range": payload.get("updatedRange"),
        "updated_rows": payload.get("updatedRows", 0),
        "updated_cells": payload.get("updatedCells", 0),
    }


def spreadsheet_files(payload: JsonDict) -> dict[str, object]:
    """Return normalized available Google Sheets."""
    files = payload.get("files", [])
    files = files if isinstance(files, list) else []
    return {"spreadsheets": [_file(item) for item in files if isinstance(item, dict)], "next_page_token": payload.get("nextPageToken")}


def _file(item: JsonDict) -> dict[str, object]:
    """Return a normalized spreadsheet file entry."""
    spreadsheet_id = str(item.get("id", ""))
    return {
        "id": spreadsheet_id,
        "title": item.get("name", ""),
        "url": _url(spreadsheet_id),
        "created_at": item.get("createdTime"),
        "updated_at": item.get("modifiedTime"),
    }


def _title(payload: JsonDict) -> object:
    """Return spreadsheet title."""
    props = payload.get("properties", {})
    return props.get("title") if isinstance(props, dict) else None


def _url(spreadsheet_id: str) -> str | None:
    """Return the browser URL for a Google Sheet."""
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit" if spreadsheet_id else None


def _worksheet(item: JsonDict) -> dict[str, object]:
    """Return normalized worksheet metadata."""
    props = item.get("properties", {})
    return {
        "id": props.get("sheetId"),
        "title": props.get("title"),
        "rows": props.get("gridProperties", {}).get("rowCount", 0),
        "columns": props.get("gridProperties", {}).get("columnCount", 0),
    } if isinstance(props, dict) else {}
