# sourceress/src/sourceress/workflows.py

"""High-level workflow definitions using CrewAI orchestration."""

from __future__ import annotations

from typing import Any

from crewai import Crew
from sourceress.agents import (
    JDIngestor,
    LinkedInSourcer,
    RelevanceScorer,
    KeyMatcher,
    PitchGenerator,
    ExcelWriter,
)
from sourceress.tasks import create_all_tasks
from sourceress.utils.logging import logger


async def run_end_to_end_manual(jd_text: str, **kwargs: Any) -> str:
    """Run the full sourcing pipeline using manual agent chaining.
    
    This is the current approach that will be replaced by CrewAI orchestration.

    Args:
        jd_text: Raw job description text.
        **kwargs: Runtime overrides propagated to agents.

    Returns:
        Path to the generated Excel artefact.
    """
    logger.info("Starting end-to-end pipeline (manual chaining)…")

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

    logger.info("Manual pipeline finished. Output written to %s", output_path)
    return str(output_path)


def run_end_to_end_crewai(jd_text: str, **kwargs: Any) -> str:
    """Run the full sourcing pipeline using CrewAI orchestration.
    
    This is the target approach using proper CrewAI Task and Crew coordination.

    Args:
        jd_text: Raw job description text.
        **kwargs: Runtime overrides propagated to agents.

    Returns:
        Path to the generated Excel artefact.
    """
    logger.info("Starting end-to-end pipeline (CrewAI orchestration)…")

    # Create all tasks with proper dependencies
    jd_task, sourcing_task, scoring_task, matching_task, pitching_task, excel_task = create_all_tasks()
    
    # Get all agents from tasks
    all_tasks = [jd_task, sourcing_task, scoring_task, matching_task, pitching_task, excel_task]
    agents = [task.agent for task in all_tasks if task.agent is not None]
    tasks = all_tasks
    
    # Create CrewAI crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        memory=False,  # Disable memory for MVP
    )
    
    # Execute the crew
    result = crew.kickoff(inputs={"jd_text": jd_text})
    
    logger.info("CrewAI pipeline finished. Output: %s", result)
    return str(result)


# Default to manual approach for MVP, will switch to CrewAI once ready
async def run_end_to_end(jd_text: str, **kwargs: Any) -> str:
    """Run the full sourcing pipeline.
    
    Currently uses manual chaining, will be switched to CrewAI orchestration
    once Task 10 (CrewAI Integration) is complete.

    Args:
        jd_text: Raw job description text.
        **kwargs: Runtime overrides propagated to agents.

    Returns:
        Path to the generated Excel artefact.
    """
    # TODO: Switch to run_end_to_end_crewai once Task 10 is complete
    return await run_end_to_end_manual(jd_text, **kwargs) 