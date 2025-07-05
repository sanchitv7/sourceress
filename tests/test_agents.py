"""Unit tests for individual agents."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from sourceress.agents import (
    JDIngestor,
    LinkedInSourcer,
    RelevanceScorer,
    KeyMatcher,
    PitchGenerator,
    ExcelWriter,
)
from sourceress.models import (
    JobDescription,
    JDIngestResult,
    CandidateProfile,
    SourcingResult,
    ScoredCandidate,
    ScoringResult,
    KeyMatch,
    KeyMatchEntry,
    KeyMatchResult,
    PitchMaterials,
    PitchResult,
)


class TestJDIngestor:
    """Test suite for JD Ingestor Agent."""

    @pytest.fixture
    def sample_jd_text(self) -> str:
        """Sample job description text for testing."""
        return """
        Senior Python Developer - Remote
        
        We are seeking a skilled Senior Python Developer to join our team.
        
        Required Skills:
        - 5+ years Python experience
        - Django or Flask framework knowledge
        - Database experience (PostgreSQL, MySQL)
        - Git version control
        
        Nice to Have:
        - AWS/Azure cloud experience
        - Docker containerization
        - React frontend skills
        """

    @pytest.mark.asyncio
    async def test_jd_ingestor_basic(self, sample_jd_text: str) -> None:
        """Test basic JD ingestion functionality."""
        agent = JDIngestor()
        
        # Mock the LLM call to return structured data
        with patch("sourceress.utils.llm.async_chat") as mock_llm:
            mock_llm.return_value = """{
                "title": "Senior Python Developer",
                "must_haves": ["Python", "Django", "PostgreSQL", "Git"],
                "nice_to_haves": ["AWS", "Docker", "React"],
                "seniority": "Senior",
                "location": "Remote"
            }"""
            
            result = await agent.run(sample_jd_text)
            
            assert isinstance(result, JDIngestResult)
            assert result.job_description.title == "Senior Python Developer"
            assert "Python" in result.job_description.must_haves
            assert result.job_description.seniority == "Senior"

    @pytest.mark.asyncio
    async def test_jd_ingestor_fallback(self, sample_jd_text: str) -> None:
        """Test fallback behavior when LLM fails."""
        agent = JDIngestor()
        
        # Mock the LLM call to raise an exception
        with patch("sourceress.utils.llm.async_chat") as mock_llm:
            mock_llm.side_effect = Exception("LLM unavailable")
            
            result = await agent.run(sample_jd_text)
            
            assert isinstance(result, JDIngestResult)
            assert result.job_description.title == "Senior Python Developer - Remote"
            assert result.job_description.must_haves == []


class TestLinkedInSourcer:
    """Test suite for LinkedIn Sourcer Agent."""

    @pytest.fixture
    def sample_job_description(self) -> JobDescription:
        """Sample job description for testing."""
        return JobDescription(
            title="Senior Python Developer",
            must_haves=["Python", "Django", "PostgreSQL"],
            nice_to_haves=["AWS", "Docker"],
            seniority="Senior",
            location="Remote"
        )

    @pytest.mark.asyncio
    async def test_linkedin_sourcer_basic(self, sample_job_description: JobDescription) -> None:
        """Test basic LinkedIn sourcing functionality."""
        agent = LinkedInSourcer()
        
        result = await agent.run(sample_job_description)
        
        assert isinstance(result, SourcingResult)
        assert len(result.candidates) >= 1
        assert isinstance(result.candidates[0], CandidateProfile)
        assert result.candidates[0].name == "Sample Candidate"


class TestRelevanceScorer:
    """Test suite for Relevance Scorer Agent."""

    @pytest.fixture
    def sample_sourcing_result(self) -> SourcingResult:
        """Sample sourcing result for testing."""
        return SourcingResult(
            candidates=[
                CandidateProfile(
                    name="John Doe",
                    linkedin_url="https://linkedin.com/in/john-doe",
                    summary="Senior Python developer with 8 years experience",
                    skills=["Python", "Django", "PostgreSQL", "AWS"],
                    location="Remote"
                ),
                CandidateProfile(
                    name="Jane Smith",
                    linkedin_url="https://linkedin.com/in/jane-smith",
                    summary="Python developer with 3 years experience",
                    skills=["Python", "Flask", "MySQL"],
                    location="New York"
                )
            ]
        )

    @pytest.mark.asyncio
    async def test_relevance_scorer_basic(self, sample_sourcing_result: SourcingResult) -> None:
        """Test basic relevance scoring functionality."""
        agent = RelevanceScorer()
        job_description = JobDescription(
            title="Senior Python Developer",
            must_haves=["Python", "Django", "PostgreSQL"],
            nice_to_haves=["AWS"]
        )
        
        result = await agent.run(job_description, sample_sourcing_result)
        
        assert isinstance(result, ScoringResult)
        assert len(result.scores) == 2
        assert all(isinstance(score, ScoredCandidate) for score in result.scores)
        assert all(0 <= score.score <= 100 for score in result.scores)


class TestKeyMatcher:
    """Test suite for Key Matcher Agent."""

    @pytest.fixture
    def sample_scoring_result(self) -> ScoringResult:
        """Sample scoring result for testing."""
        return ScoringResult(
            scores=[
                ScoredCandidate(
                    linkedin_url="https://linkedin.com/in/john-doe",
                    score=85,
                    feature_weights={"skills_match": 0.8, "seniority_match": 0.9}
                )
            ]
        )

    @pytest.mark.asyncio
    async def test_key_matcher_basic(self, sample_scoring_result: ScoringResult) -> None:
        """Test basic key matching functionality."""
        agent = KeyMatcher()
        job_description = JobDescription(
            title="Senior Python Developer",
            must_haves=["Python", "Django", "PostgreSQL"],
            nice_to_haves=["AWS"]
        )
        
        result = await agent.run(job_description, sample_scoring_result)
        
        assert isinstance(result, KeyMatchResult)
        assert len(result.matches) == 1
        assert isinstance(result.matches[0], KeyMatchEntry)
        assert len(result.matches[0].matches) <= len(job_description.must_haves)


class TestPitchGenerator:
    """Test suite for Pitch Generator Agent."""

    @pytest.fixture
    def sample_key_match_result(self) -> KeyMatchResult:
        """Sample key match result for testing."""
        return KeyMatchResult(
            matches=[
                KeyMatchEntry(
                    linkedin_url="https://linkedin.com/in/john-doe",
                    matches=[
                        KeyMatch(
                            requirement="Python",
                            evidence="8 years of Python development experience"
                        )
                    ]
                )
            ]
        )

    @pytest.mark.asyncio
    async def test_pitch_generator_basic(self, sample_key_match_result: KeyMatchResult) -> None:
        """Test basic pitch generation functionality."""
        agent = PitchGenerator()
        
        result = await agent.run(sample_key_match_result)
        
        assert isinstance(result, PitchResult)
        assert len(result.pitches) == 1
        assert isinstance(result.pitches[0], PitchMaterials)
        assert result.pitches[0].linkedin_url == "https://linkedin.com/in/john-doe"
        assert len(result.pitches[0].cold_call) > 0
        assert len(result.pitches[0].dm_message) > 0
        assert len(result.pitches[0].whatsapp_message) > 0


class TestExcelWriter:
    """Test suite for Excel Writer Agent."""

    @pytest.fixture
    def sample_pitch_result(self) -> PitchResult:
        """Sample pitch result for testing."""
        return PitchResult(
            pitches=[
                PitchMaterials(
                    linkedin_url="https://linkedin.com/in/john-doe",
                    cold_call="Hi John, I have an exciting opportunity...",
                    dm_message="Hi John, I came across your profile...",
                    whatsapp_message="Hi John, I'm a recruiter..."
                )
            ]
        )

    @pytest.mark.asyncio
    async def test_excel_writer_basic(self, sample_pitch_result: PitchResult, tmp_path) -> None:
        """Test basic Excel writing functionality."""
        agent = ExcelWriter()
        output_path = tmp_path / "test_output.xlsx"
        
        result = await agent.run(sample_pitch_result, output_path=output_path)
        
        assert result.exists()
        assert result.name == "test_output.xlsx" 