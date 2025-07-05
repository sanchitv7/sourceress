"""CrewAI Task definitions for the Sourceress pipeline.

This module defines the Task objects that coordinate agent execution and manage
dependencies between pipeline stages.
"""

from __future__ import annotations

from crewai import Task
from pydantic import BaseModel

from sourceress.agents import (
    JDIngestor,
    LinkedInSourcer,
    RelevanceScorer,
    KeyMatcher,
    PitchGenerator,
    ExcelWriter,
)


class TaskOutputs(BaseModel):
    """Expected output schema for task validation."""
    
    jd_ingest: str = "A structured JobDescription with title, must_haves, nice_to_haves, seniority, and location"
    sourcing: str = "A list of 10-20 CandidateProfile objects with name, linkedin_url, summary, and skills"
    scoring: str = "A list of ScoredCandidate objects with linkedin_url, score (0-100), and feature_weights"
    matching: str = "A list of KeyMatchEntry objects with linkedin_url and specific requirement-evidence matches"
    pitching: str = "A list of PitchMaterials objects with personalized cold_call, dm_message, and whatsapp_message"
    excel: str = "Path to the generated Excel file containing all candidate data and messaging"


def create_jd_ingest_task(jd_ingestor: JDIngestor) -> Task:
    """Create task for job description ingestion."""
    return Task(
        description=(
            "Parse the raw job description text and extract structured information. "
            "Identify the job title, required skills (must-haves), preferred skills (nice-to-haves), "
            "seniority level, and location. Return a structured JobDescription object."
        ),
        agent=jd_ingestor,
        expected_output=TaskOutputs.model_fields["jd_ingest"].default,
    )


def create_sourcing_task(linkedin_sourcer: LinkedInSourcer) -> Task:
    """Create task for LinkedIn candidate sourcing."""
    return Task(
        description=(
            "Search LinkedIn for candidate profiles that match the job requirements. "
            "Focus on finding 10-20 high-quality candidates who have the required skills "
            "and experience level. Extract their basic profile information including name, "
            "LinkedIn URL, summary, skills, and location."
        ),
        agent=linkedin_sourcer,
        expected_output=TaskOutputs.model_fields["sourcing"].default,
    )


def create_scoring_task(relevance_scorer: RelevanceScorer) -> Task:
    """Create task for candidate relevance scoring."""
    return Task(
        description=(
            "Score each candidate's relevance to the job requirements on a scale of 0-100. "
            "Consider factors like skill match, experience level, and location preference. "
            "Provide feature weights to explain the scoring decision for transparency."
        ),
        agent=relevance_scorer,
        expected_output=TaskOutputs.model_fields["scoring"].default,
    )


def create_matching_task(key_matcher: KeyMatcher) -> Task:
    """Create task for key requirement matching."""
    return Task(
        description=(
            "For each candidate, identify specific matches between job requirements and "
            "their qualifications. Highlight exact skills, experience, or achievements "
            "that align with the job's must-have requirements. Provide evidence from "
            "their profile to support each match."
        ),
        agent=key_matcher,
        expected_output=TaskOutputs.model_fields["matching"].default,
    )


def create_pitching_task(pitch_generator: PitchGenerator) -> Task:
    """Create task for personalized message generation."""
    return Task(
        description=(
            "Generate personalized outreach messages for each candidate across three channels: "
            "cold call script, LinkedIn DM, and WhatsApp message. Each message should be "
            "tailored to the candidate's background and highlight relevant matches with "
            "the job requirements. Keep messages professional but friendly."
        ),
        agent=pitch_generator,
        expected_output=TaskOutputs.model_fields["pitching"].default,
    )


def create_excel_task(excel_writer: ExcelWriter) -> Task:
    """Create task for Excel report generation."""
    return Task(
        description=(
            "Create a comprehensive Excel report with all candidate information. "
            "Include columns for candidate name, LinkedIn URL, match score, key matches, "
            "and all three outreach messages. Format the report professionally with "
            "conditional formatting for high scores and frozen headers."
        ),
        agent=excel_writer,
        expected_output=TaskOutputs.model_fields["excel"].default,
    )


def create_all_tasks() -> tuple[Task, Task, Task, Task, Task, Task]:
    """Create all tasks with their respective agents."""
    # Initialize agents
    jd_ingestor = JDIngestor()
    linkedin_sourcer = LinkedInSourcer()
    relevance_scorer = RelevanceScorer()
    key_matcher = KeyMatcher()
    pitch_generator = PitchGenerator()
    excel_writer = ExcelWriter()
    
    # Create tasks
    jd_task = create_jd_ingest_task(jd_ingestor)
    sourcing_task = create_sourcing_task(linkedin_sourcer)
    scoring_task = create_scoring_task(relevance_scorer)
    matching_task = create_matching_task(key_matcher)
    pitching_task = create_pitching_task(pitch_generator)
    excel_task = create_excel_task(excel_writer)
    
    # Set up dependencies (context passing)
    sourcing_task.context = [jd_task]
    scoring_task.context = [jd_task, sourcing_task]
    matching_task.context = [jd_task, scoring_task]
    pitching_task.context = [matching_task]
    excel_task.context = [pitching_task]
    
    return jd_task, sourcing_task, scoring_task, matching_task, pitching_task, excel_task 