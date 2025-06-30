# sourceress/src/sourceress/agents/jd_ingestor.py

"""Job Description Ingestor Agent.

Parses raw job description text into a structured :class:`sourceress.models.JobDescription`.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from sourceress.models import JDIngestResult


class JDIngestor:
    """Agent responsible for converting raw JD text into structured data."""

    name: str = "jd_ingestor"

    async def run(self, jd_text: str, **kwargs: Any) -> JDIngestResult:  # noqa: D401
        """Execute the agent.

        Args:
            jd_text: Raw job-description text.
            **kwargs: Additional runtime parameters (unused for now).

        Returns:
            An instance of :class:`sourceress.models.JDIngestResult`.
        """
        logger.debug("Starting JD ingestion for %d characters", len(jd_text))
        # TODO: Replace with actual LLM prompt & parsing logic
        parsed = {
            "title": "TODO",
            "must_haves": [],
            "nice_to_haves": [],
            "seniority": None,
            "location": None,
            "raw_text": jd_text,
        }
        logger.debug("Parsed JD payload: %s", parsed)
        return JDIngestResult.model_validate({"job_description": parsed}) 