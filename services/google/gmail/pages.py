"""Gmail page normalization helpers.

Purpose: build normalized message pages from Gmail listings.
Responsibilities: fetch full messages for summaries and preserve pagination.
Dependencies: Gmail normalizer and typed Google JSON.
Extension Notes: add batched fetches here if Gmail list performance requires it.
"""

from collections.abc import Callable

from integrations.google.common.http import JsonDict
from services.google.gmail.normalizer import message_summary


def message_page(listing: JsonDict, fetch: Callable[[str], JsonDict]) -> JsonDict:
    """Return a normalized message page from a Gmail listing."""
    messages = listing.get("messages", [])
    messages = messages if isinstance(messages, list) else []
    summaries = [
        message_summary(fetch(str(item.get("id", ""))))
        for item in messages
        if isinstance(item, dict) and item.get("id")
    ]
    return {
        "messages": summaries,
        "next_page_token": listing.get("nextPageToken"),
        "result_size_estimate": listing.get("resultSizeEstimate", len(summaries)),
    }
