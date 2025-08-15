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
        raw_profiles = search_linkedin(search_terms, max_results=limit)
        
        validated_profiles = []
        for profile_data in raw_profiles:
            try:
                # Basic normalization and data cleaning
                name = profile_data.get("name", "").strip()
                linkedin_url = profile_data.get("linkedin_url", "").split("?")[0]
                title = profile_data.get("title", "").strip()
                location = profile_data.get("location", "").strip()

                # Fix common data extraction issues
                if not name or name == "Unknown":
                    if title and " at " in title:
                        name = title.split(" at ")[0].strip()
                    else:
                        logger.warning(f"Could not determine name for profile: {profile_data}")
                        continue

                if title == location and title:
                    location = ""

                # Create CandidateProfile instance
                validated_profiles.append(
                    CandidateProfile(
                        name=name,
                        linkedin_url=linkedin_url,
                        title=title,
                        location=location,
                        summary=profile_data.get("summary", ""),
                        skills=profile_data.get("skills", []),
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping profile due to validation error: {e} | Data: {profile_data}")
                continue
        
        logger.info(f"Successfully fetched and validated {len(validated_profiles)} profiles.")
        return validated_profiles

    except Exception as e:
        logger.error(f"An error occurred while fetching profiles: {e}")
        return [] 