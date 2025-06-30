# sourceress/src/sourceress/agents/pitch_generator.py

"""Pitch Generator Agent.

Creates personalised outreach messages for each candidate.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from sourceress.models import KeyMatchResult, PitchResult


class PitchGenerator:
    """Agent responsible for generating recruiter outreach messages."""

    name: str = "pitch_generator"

    async def run(self, matched: KeyMatchResult, **kwargs: Any) -> PitchResult:  # noqa: D401
        """Execute the agent.

        Args:
            matched: Results from the KeyMatcher.
            **kwargs: Additional runtime parameters.

        Returns:
            A :class:`sourceress.models.PitchResult` instance.
        """
        logger.debug("Generating pitches for %d candidates", len(matched.matches))
        # TODO: Use LLM with templates to create personalised messages
        return PitchResult.model_validate({"pitches": []}) 