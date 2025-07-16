"""Thin wrapper around LinkedIn scraping utilities.

Abstracted to enable unit testing via mocks.
"""

from __future__ import annotations

from typing import List, Dict, Any

from loguru import logger

from .scraping import search_linkedin_async
from sourceress.models import CandidateProfile


async def fetch_profiles(search_terms: str, limit: int = 50) -> List[CandidateProfile]:
    """Return structured LinkedIn profiles matching the search terms."""
    logger.debug("Fetching up to %d profiles for search terms: %s", limit, search_terms)
    
    try:
        raw_profiles = await search_linkedin_async(search_terms, max_results=limit)
        
        validated_profiles = []
        for profile_data in raw_profiles:
            try:
                # Basic normalization
                profile_data["name"] = profile_data.get("name", "").strip()
                profile_data["linkedin_url"] = profile_data.get("linkedin_url", "").split("?")[0]

                # Validate with Pydantic model
                validated_profiles.append(CandidateProfile.model_validate(profile_data))
            except Exception as e:
                logger.warning(f"Skipping profile due to validation error: {e} | Data: {profile_data}")
                continue
        
        logger.info(f"Successfully fetched and validated {len(validated_profiles)} profiles.")
        return validated_profiles

    except Exception as e:
        logger.error(f"An error occurred while fetching profiles: {e}")
        return [] 