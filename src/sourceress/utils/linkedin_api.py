"""Thin wrapper around LinkedIn scraping utilities.

Abstracted to enable unit testing via mocks.
"""

from __future__ import annotations

from typing import List

from loguru import logger

from .scraping import search_linkedin_async, search_linkedin
from sourceress.models import CandidateProfile


def fetch_profiles(search_terms: str, limit: int = 50) -> List[CandidateProfile]:
    """Return structured LinkedIn profiles matching the search terms."""
    logger.debug("Fetching up to %d profiles for search terms: %s", limit, search_terms)
    
    try:
        # Use the direct function instead of async wrapper to avoid browser issues
        # This is more reliable than the async wrapper which has browser management issues
        raw_profiles = search_linkedin(search_terms, max_results=limit)
        
        validated_profiles = []
        for profile_data in raw_profiles:
            try:
                # Basic normalization and data cleaning
                profile_data["name"] = profile_data.get("name", "").strip()
                profile_data["linkedin_url"] = profile_data.get("linkedin_url", "").split("?")[0]
                
                # Fix common data extraction issues
                if not profile_data["name"] or profile_data["name"] == "Unknown":
                    # Try to extract name from title if name is empty
                    title = profile_data.get("title", "")
                    if title and " at " in title:
                        profile_data["name"] = title.split(" at ")[0].strip()
                
                # Clean up title/location confusion
                title = profile_data.get("title", "")
                location = profile_data.get("location", "")
                
                # If title and location are the same, location is probably wrong
                if title == location and title:
                    profile_data["location"] = ""
                
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