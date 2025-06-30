# sourceress/src/sourceress/workflows.py

"""High-level workflow definitions using CrewAI (or similar orchestration lib)."""

from __future__ import annotations

from typing import Any

from sourceress.agents import (
    JDIngestor,
    LinkedInSourcer,
    RelevanceScorer,
    KeyMatcher,
    PitchGenerator,
    ExcelWriter,
)
from sourceress.utils.logging import logger


async def run_end_to_end(jd_text: str, **kwargs: Any) -> str:
    """Run the full sourcing pipeline for a given JD.

    Args:
        jd_text: Raw job description text.
        **kwargs: Runtime overrides propagated to agents.

    Returns:
        Path to the generated Excel artefact.
    """
    logger.info("Starting end-to-end pipeline…")

    jd_ingestor = JDIngestor()
    linkedin_sourcer = LinkedInSourcer()
    relevance_scorer = RelevanceScorer()
    key_matcher = KeyMatcher()
    pitch_generator = PitchGenerator()
    excel_writer = ExcelWriter()

    jd_ingest_res = await jd_ingestor.run(jd_text, **kwargs)
    sourcing_res = await linkedin_sourcer.run(jd_ingest_res.job_description, **kwargs)
    scoring_res = await relevance_scorer.run(
        jd_ingest_res.job_description, sourcing_res, **kwargs
    )
    key_match_res = await key_matcher.run(jd_ingest_res.job_description, scoring_res)
    pitch_res = await pitch_generator.run(key_match_res)
    output_path = await excel_writer.run(pitch_res, **kwargs)

    logger.info("Pipeline finished. Output written to %s", output_path)
    return str(output_path) 