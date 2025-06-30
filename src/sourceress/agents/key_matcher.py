# sourceress/src/sourceress/agents/key_matcher.py

"""Key Matcher Agent.

Extracts bullet-level matches between JD and candidate profiles.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from sourceress.models import JobDescription, ScoringResult, KeyMatchResult


class KeyMatcher:
    """Agent responsible for highlighting matching bullet points."""

    name: str = "key_matcher"

    async def run(
        self,
        jd: JobDescription,
        scored: ScoringResult,
        **kwargs: Any,
    ) -> KeyMatchResult:  # noqa: D401
        """Execute the agent.

        Args:
            jd: Structured job description.
            scored: Results from the RelevanceScorer.
            **kwargs: Additional runtime parameters.

        Returns:
            A :class:`sourceress.models.KeyMatchResult` instance.
        """
        logger.debug("Matching key points for JD: %s", jd.title)
        # TODO: Implement extraction logic
        return KeyMatchResult.model_validate({"matches": []}) 