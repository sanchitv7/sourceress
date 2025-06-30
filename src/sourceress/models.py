# sourceress/src/sourceress/models.py

"""Core Pydantic models shared across agents."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# -----------------------------------------------------------------------------
# Job-description ingestion
# -----------------------------------------------------------------------------


class JobDescription(BaseModel):
    """Structured representation of a job description."""

    title: str
    must_haves: List[str]
    nice_to_haves: List[str] = Field(default_factory=list)
    seniority: Optional[str] = None
    location: Optional[str] = None
    raw_text: Optional[str] = None

    @validator("title")
    @classmethod
    def _title_not_empty(cls, v: str) -> str:  # noqa: D401,N805
        if not v:
            raise ValueError("title must not be empty")
        return v


class JDIngestResult(BaseModel):
    """Return type for :class:`agents.jd_ingestor.JDIngestor`."""

    job_description: JobDescription


# -----------------------------------------------------------------------------
# Sourcing & Scoring
# -----------------------------------------------------------------------------


class CandidateProfile(BaseModel):
    """Minimal candidate profile."""

    name: str
    linkedin_url: str
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    location: Optional[str] = None


class SourcingResult(BaseModel):
    """Return type for :class:`agents.linkedin_sourcer.LinkedInSourcer`."""

    candidates: List[Dict[str, Any]]  # TODO: Replace dict with CandidateProfile


class ScoredCandidate(BaseModel):
    """Relevance-scored candidate entry."""

    linkedin_url: str
    score: int = Field(ge=0, le=100)
    feature_weights: Dict[str, float] = Field(default_factory=dict)


class ScoringResult(BaseModel):
    """Return type for :class:`agents.relevance_scorer.RelevanceScorer`."""

    scores: List[ScoredCandidate]


# -----------------------------------------------------------------------------
# Key matches & pitch
# -----------------------------------------------------------------------------


class KeyMatch(BaseModel):
    """Mapping of JD requirement to candidate evidence."""

    requirement: str
    evidence: str


class KeyMatchEntry(BaseModel):
    """Key matches for a single candidate."""

    linkedin_url: str
    matches: List[KeyMatch]


class KeyMatchResult(BaseModel):
    """Return type for :class:`agents.key_matcher.KeyMatcher`."""

    matches: List[KeyMatchEntry]


class PitchMaterials(BaseModel):
    """Personalised outreach copy for a single candidate."""

    linkedin_url: str
    cold_call: str
    dm_message: str
    whatsapp_message: str


class PitchResult(BaseModel):
    """Return type for :class:`agents.pitch_generator.PitchGenerator`."""

    pitches: List[PitchMaterials] 