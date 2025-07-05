# sourceress/src/sourceress/agents/key_matcher.py

"""Key Matcher Agent.

Extracts bullet-level matches between JD and candidate profiles.
"""

from __future__ import annotations

from typing import Any

from sourceress.agents.base import BaseAgent
from sourceress.models import JobDescription, ScoringResult, KeyMatchResult


class KeyMatcher(BaseAgent):
    """Agent responsible for highlighting matching bullet points."""

    name: str = "key_matcher"

    def __init__(self) -> None:
        super().__init__(
            role="Requirement Matching Specialist",
            goal="Identify and highlight specific matches between job requirements and candidate qualifications",
            backstory="You are a detail-oriented recruitment specialist who excels at finding precise "
                     "connections between job requirements and candidate profiles. You have a keen eye "
                     "for matching skills, experience, and qualifications, and you can articulate "
                     "these connections clearly for hiring managers.",
        )

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
        self.log.debug("Matching key points for JD: %s", jd.title)
        # TODO(student): Implement key-match extraction.
        #   1. Tokenise JD requirements and candidate summary using spaCy (`en_core_web_lg`).
        #   2. Compute semantic similarity with Sentence-Transformers (`all-miniLM-L6-v2`).
        #   3. For each requirement above a similarity threshold (e.g., 0.75), capture the most
        #      representative candidate sentence as evidence.
        #   4. Return populated `KeyMatchResult` objects.
        #   Reading: spaCy similarity docs, `sentence-transformers` quickstart, `rapidfuzz` fuzzy matching.
        from sourceress.models import KeyMatchEntry, KeyMatch
        dummy_matches = [
            KeyMatchEntry(
                linkedin_url=score.linkedin_url,
                matches=[
                    KeyMatch(
                        requirement=req,
                        evidence=f"Candidate has demonstrated experience with {req.lower()}"
                    )
                    for req in jd.must_haves[:2]  # Just first 2 requirements for demo
                ]
            )
            for score in scored.scores
        ]
        return KeyMatchResult(matches=dummy_matches) 