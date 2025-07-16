# sourceress/src/sourceress/agents/linkedin_sourcer.py

"""LinkedIn Sourcer Agent.

Searches LinkedIn for candidate profiles matching a given job description.
"""

from __future__ import annotations

from typing import Any

from sourceress.agents.base import BaseAgent
from sourceress.models import JobDescription, SourcingResult


class LinkedInSourcer(BaseAgent):
    """Agent responsible for sourcing candidates on LinkedIn."""

    name: str = "linkedin_sourcer"

    def __init__(self) -> None:
        super().__init__(
            role="LinkedIn Talent Sourcer",
            goal="Find and extract relevant candidate profiles from LinkedIn based on job requirements",
            backstory="You are an expert LinkedIn sourcer with 5+ years of experience in talent acquisition. "
                     "You excel at crafting targeted search queries and identifying high-quality candidates "
                     "who match specific job requirements. You understand LinkedIn's search capabilities "
                     "and can efficiently navigate through profiles to find the best matches.",
        )

    async def run(self, jd: JobDescription, **kwargs: Any) -> SourcingResult:  # noqa: D401
        """Execute the agent.

        Args:
            jd: Structured job description.
            **kwargs: Additional runtime parameters.

        Returns:
            A :class:`sourceress.models.SourcingResult` instance.
        """
        self.log.debug("Starting LinkedIn sourcing for JD: %s", jd.title)

        # 1. Construct a search query from the job description
        query_parts = [jd.title] + jd.must_haves
        search_query = " ".join(query_parts)
        self.log.info(f"Constructed search query: {search_query}")

        # 2. Fetch profiles using the linkedin_api utility
        try:
            profiles = await fetch_profiles(search_query, limit=20)  # Using a limit for MVP
        except Exception as e:
            self.log.error(f"Failed to fetch profiles from LinkedIn: {e}")
            profiles = []

        # 3. Deduplicate profiles by LinkedIn URL to ensure uniqueness
        seen_urls = set()
        unique_profiles = []
        for profile in profiles:
            if profile.linkedin_url not in seen_urls:
                unique_profiles.append(profile)
                seen_urls.add(profile.linkedin_url)
        
        self.log.info(f"Sourced {len(unique_profiles)} unique candidate profiles.")

        return SourcingResult(candidates=unique_profiles) 