"""Thin wrapper around LinkedIn scraping utilities.

Abstracted to enable unit testing via mocks.
"""

from __future__ import annotations

from typing import List, Dict, Any

from loguru import logger

from .scraping import search_linkedin


async def fetch_profiles(search_terms: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Return structured LinkedIn profiles matching the search terms."""
    logger.debug("Fetching up to %d profiles for search terms: %s", limit, search_terms)
    raw = await search_linkedin(search_terms, max_results=limit)
    # TODO: Clean & enrich scraping output
    return raw 