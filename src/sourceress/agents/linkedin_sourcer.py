# sourceress/src/sourceress/agents/linkedin_sourcer.py

"""LinkedIn Sourcer Agent.

Searches LinkedIn for candidate profiles matching a given job description.
"""

from __future__ import annotations

from typing import Any

from sourceress.agents.base import BaseAgent
from sourceress.models import JobDescription, SourcingResult
from sourceress.utils.linkedin_api import fetch_profiles


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

        # 1. Construct optimized boolean search query for LinkedIn
        # Strategy: Use LinkedIn's boolean operators for precise targeting
        # Format: "title" AND ("skill1" OR "skill2") - keep it simple and effective
        
        # Extract core components
        core_title = jd.title.split(" - ")[0].split(" at ")[0].strip()
        
        # Build boolean query components
        query_parts = []
        key_skills = []  # Initialize key_skills to avoid scope issues
        
        # Title (required) - use quotes for exact match
        query_parts.append(f'"{core_title}"')
        
        # Must-have skills (OR group) - extract key terms dynamically
        if jd.must_haves:
            # Extract key terms from must-haves (avoid generic words)
            generic_words = {"experience", "years", "plus", "with", "and", "or", "the", "a", "an", "of", "in", "on", "at", "to", "for", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "must", "shall"}
            
            for skill in jd.must_haves:
                # Clean and extract meaningful terms
                words = skill.lower().replace("+", " ").replace("-", " ").split()
                meaningful_words = [word for word in words if word not in generic_words and len(word) > 2]
                
                # Take the most distinctive terms (likely technologies/skills)
                for word in meaningful_words:
                    if word not in [s.strip('"') for s in key_skills]:  # Avoid duplicates
                        key_skills.append(f'"{word}"')
                        break
                
                if len(key_skills) >= 2:  # Limit to 2 for URL length
                    break
            
            # Add skills as OR group
            if key_skills:
                skills_group = " OR ".join(key_skills)
                query_parts.append(f"({skills_group})")
        
        # Add location filter if available
        if jd.location:
            query_parts.append(f'"{jd.location}"')
        
        # Combine with AND operators
        search_query = " AND ".join(query_parts)
        
        self.log.info(f"Boolean search query: {search_query}")
        self.log.debug(f"Components: title='{core_title}', skills={key_skills}, location='{jd.location}'")

        # 2. Fetch profiles using the linkedin_api utility
        try:
            profiles = fetch_profiles(search_query, limit=20)  # Using a limit for MVP
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
