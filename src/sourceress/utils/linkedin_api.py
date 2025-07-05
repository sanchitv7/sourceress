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
    # TODO(student): Convert `raw` dicts into strongly-typed `CandidateProfile` objects.
    #   – Normalise names, trim whitespace/emojis, canonicalise URLs.
    #   – Optionally enrich data by hitting LinkedIn REST/GraphQL endpoints
    #     or parsing JSON embedded in profile pages.
    #   – Leverage libraries like `rapidfuzz` for deduplication and
    #     `langchain.text_splitter` + OpenAI embeddings for skill extraction.
    #   – Add unit tests using `pytest-asyncio` and fixtures to validate edge cases.
    return raw 