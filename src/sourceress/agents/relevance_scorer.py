# sourceress/src/sourceress/agents/relevance_scorer.py

"""Relevance Scorer Agent.

Scores candidate profiles against the job description.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from sourceress.models import JobDescription, SourcingResult, ScoringResult


class RelevanceScorer:
    """Agent responsible for computing candidate relevance scores."""

    name: str = "relevance_scorer"

    async def run(
        self,
        jd: JobDescription,
        sourced: SourcingResult,
        **kwargs: Any,
    ) -> ScoringResult:  # noqa: D401
        """Execute the agent.

        Args:
            jd: Structured job description.
            sourced: Results from the LinkedInSourcer.
            **kwargs: Additional runtime parameters.

        Returns:
            A :class:`sourceress.models.ScoringResult` instance.
        """
        logger.debug("Scoring %d candidates for JD: %s", len(sourced.candidates), jd.title)
        # TODO: Implement ML/LLM scoring logic
        dummy_scores = [
            {
                "linkedin_url": c["linkedin_url"],
                "score": 0,
                "feature_weights": {},
            }
            for c in sourced.candidates
        ]
        return ScoringResult.model_validate({"scores": dummy_scores}) 