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
    async def test_jd_ingestor_with_clean_json(self, sample_jd_text: str) -> None:
        """Test JD ingestion with clean JSON response from LLM."""
        agent = JDIngestor()
        
        # Mock the LLM call to return structured data
        with patch("sourceress.agents.jd_ingestor.async_chat") as mock_llm:
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
            assert "Django" in result.job_description.must_haves
            assert "AWS" in result.job_description.nice_to_haves
            assert result.job_description.seniority == "Senior"
            assert result.job_description.location == "Remote"
            
            # Verify the LLM was called with correct system prompt
            mock_llm.assert_called_once()
            args = mock_llm.call_args[0]
            assert "expert recruitment analyst" in args[0]
            assert "JSON" in args[0]
            assert args[1] == sample_jd_text

    @pytest.mark.asyncio
    async def test_jd_ingestor_markdown_cleaning(self, sample_jd_text: str) -> None:
        """Test JD ingestion handles markdown code blocks in LLM response."""
        agent = JDIngestor()
        
        # Mock LLM response with markdown code blocks
        with patch("sourceress.agents.jd_ingestor.async_chat") as mock_llm:
            mock_llm.return_value = """```json
{
    "title": "Senior Python Developer",
    "must_haves": ["Python", "Django"],
    "nice_to_haves": ["AWS"],
    "seniority": "Senior",
    "location": "Remote"
}
```"""
            
            result = await agent.run(sample_jd_text)
            
            assert isinstance(result, JDIngestResult)
            assert result.job_description.title == "Senior Python Developer"
            assert "Python" in result.job_description.must_haves
            assert result.job_description.seniority == "Senior"

    @pytest.mark.asyncio
    async def test_jd_ingestor_llm_failure_fallback(self, sample_jd_text: str) -> None:
        """Test fallback behavior when LLM fails completely."""
        agent = JDIngestor()
        
        # Mock the LLM call to raise an exception
        with patch("sourceress.agents.jd_ingestor.async_chat") as mock_llm:
            mock_llm.side_effect = Exception("LLM unavailable")
            
            result = await agent.run(sample_jd_text)
            
            assert isinstance(result, JDIngestResult)
            # Should extract title from first line
            assert result.job_description.title == "Senior Python Developer - Remote"
            # Should have empty lists for requirements
            assert result.job_description.must_haves == []
            assert result.job_description.nice_to_haves == []
            assert result.job_description.seniority is None
            assert result.job_description.location is None

    @pytest.mark.asyncio
    async def test_jd_ingestor_invalid_json_fallback(self, sample_jd_text: str) -> None:
        """Test fallback when LLM returns invalid JSON."""
        agent = JDIngestor()
        
        # Mock LLM to return invalid JSON
        with patch("sourceress.agents.jd_ingestor.async_chat") as mock_llm:
            mock_llm.return_value = "This is not JSON at all!"
            
            result = await agent.run(sample_jd_text)
            
            assert isinstance(result, JDIngestResult)
            # Should extract title from first line
            assert result.job_description.title == "Senior Python Developer - Remote"
            assert result.job_description.must_haves == []
            assert result.job_description.nice_to_haves == []


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
        """Test basic LinkedIn sourcing functionality with mocked fetch_profiles."""
        agent = LinkedInSourcer()
        
        # Mock the fetch_profiles function to return sample candidates
        sample_candidates = [
            CandidateProfile(
                name="John Doe",
                linkedin_url="https://linkedin.com/in/john-doe",
                summary="Senior Python Developer with 8 years experience",
                skills=["Python", "Django", "PostgreSQL"],
                location="San Francisco"
            ),
            CandidateProfile(
                name="Jane Smith",
                linkedin_url="https://linkedin.com/in/jane-smith",
                summary="Python Developer with Django expertise",
                skills=["Python", "Django", "React"],
                location="Remote"
            )
        ]
        
        with patch("sourceress.agents.linkedin_sourcer.fetch_profiles") as mock_fetch:
            mock_fetch.return_value = sample_candidates
            
            result = await agent.run(sample_job_description)
            
            assert isinstance(result, SourcingResult)
            assert len(result.candidates) == 2
            assert isinstance(result.candidates[0], CandidateProfile)
            assert result.candidates[0].name == "John Doe"
            
            # Verify the search query construction
            mock_fetch.assert_called_once()
            search_query = mock_fetch.call_args[0][0]
            assert '"Senior Python Developer"' in search_query
            assert "Python" in search_query or "Django" in search_query

    @pytest.mark.asyncio
    async def test_linkedin_sourcer_deduplication(self, sample_job_description: JobDescription) -> None:
        """Test that duplicate profiles are removed."""
        agent = LinkedInSourcer()
        
        # Mock with duplicate profiles
        duplicate_candidates = [
            CandidateProfile(
                name="John Doe",
                linkedin_url="https://linkedin.com/in/john-doe",
                summary="Senior Python Developer",
                skills=["Python", "Django"],
                location="SF"
            ),
            CandidateProfile(
                name="John Doe Updated",  # Same URL, different data
                linkedin_url="https://linkedin.com/in/john-doe", 
                summary="Different summary",
                skills=["Python", "Flask"],
                location="NYC"
            )
        ]
        
        with patch("sourceress.agents.linkedin_sourcer.fetch_profiles") as mock_fetch:
            mock_fetch.return_value = duplicate_candidates
            
            result = await agent.run(sample_job_description)
            
            # Should deduplicate based on LinkedIn URL
            assert len(result.candidates) == 1
            assert result.candidates[0].name == "John Doe"  # First one kept

    @pytest.mark.asyncio
    async def test_linkedin_sourcer_api_failure(self, sample_job_description: JobDescription) -> None:
        """Test graceful handling when LinkedIn API fails."""
        agent = LinkedInSourcer()
        
        with patch("sourceress.agents.linkedin_sourcer.fetch_profiles") as mock_fetch:
            mock_fetch.side_effect = Exception("LinkedIn API unavailable")
            
            result = await agent.run(sample_job_description)
            
            # Should return empty result on failure
            assert isinstance(result, SourcingResult)
            assert len(result.candidates) == 0


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
        """Test basic relevance scoring functionality with dummy implementation."""
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
        # The dummy implementation should score based on simple skill matching
        # John Doe has more skills matching (Python, Django, PostgreSQL, AWS) -> higher score
        # Jane Smith has fewer matching skills -> lower score
        john_score = next(s for s in result.scores if s.linkedin_url == "https://linkedin.com/in/john-doe")
        jane_score = next(s for s in result.scores if s.linkedin_url == "https://linkedin.com/in/jane-smith")
        assert john_score.score >= jane_score.score  # John should score higher


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
        """Test basic key matching functionality with dummy implementation."""
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
        # The dummy implementation should create matches for each must-have skill
        assert len(result.matches[0].matches) >= 1
        assert all(isinstance(match, KeyMatch) for match in result.matches[0].matches)
        # Verify that the matches contain reasonable evidence text
        for match in result.matches[0].matches:
            assert len(match.requirement) > 0
            assert len(match.evidence) > 0


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
        """Test basic pitch generation functionality with dummy implementation."""
        agent = PitchGenerator()
        
        result = await agent.run(sample_key_match_result)
        
        assert isinstance(result, PitchResult)
        assert len(result.pitches) == 1
        assert isinstance(result.pitches[0], PitchMaterials)
        assert result.pitches[0].linkedin_url == "https://linkedin.com/in/john-doe"
        # The dummy implementation should generate realistic pitch content
        assert len(result.pitches[0].cold_call) > 50  # Should be substantial
        assert len(result.pitches[0].dm_message) > 30  # Should be concise but meaningful
        assert len(result.pitches[0].whatsapp_message) > 20  # Should be brief but engaging
        # Verify the content contains relevant information (dummy implementation uses generic terms)
        assert "opportunity" in result.pitches[0].cold_call.lower() or "exciting" in result.pitches[0].cold_call.lower()
        assert "opportunity" in result.pitches[0].dm_message.lower() or "role" in result.pitches[0].dm_message.lower()


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


class TestIntegration:
    """Integration tests for agent pipeline workflows."""

    @pytest.mark.asyncio
    async def test_jd_to_sourcing_pipeline(self) -> None:
        """Test JD Ingestor -> LinkedIn Sourcer pipeline integration."""
        sample_jd_text = """
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
        """
        
        # Step 1: JD Ingestion
        jd_agent = JDIngestor()
        with patch("sourceress.agents.jd_ingestor.async_chat") as mock_llm:
            mock_llm.return_value = """{
                "title": "Senior Python Developer",
                "must_haves": ["Python", "Django", "PostgreSQL", "Git"],
                "nice_to_haves": ["AWS", "Docker"],
                "seniority": "Senior",
                "location": "Remote"
            }"""
            
            jd_result = await jd_agent.run(sample_jd_text)
            
        assert isinstance(jd_result, JDIngestResult)
        job_description = jd_result.job_description
        
        # Step 2: LinkedIn Sourcing
        sourcer_agent = LinkedInSourcer()
        sample_candidates = [
            CandidateProfile(
                name="Alice Johnson",
                linkedin_url="https://linkedin.com/in/alice-johnson",
                summary="Senior Python Developer with Django expertise",
                skills=["Python", "Django", "PostgreSQL", "AWS"],
                location="Remote"
            )
        ]
        
        with patch("sourceress.agents.linkedin_sourcer.fetch_profiles") as mock_fetch:
            mock_fetch.return_value = sample_candidates
            
            sourcing_result = await sourcer_agent.run(job_description)
            
        assert isinstance(sourcing_result, SourcingResult)
        assert len(sourcing_result.candidates) == 1
        assert sourcing_result.candidates[0].name == "Alice Johnson"
        
        # Verify the search query was constructed properly
        mock_fetch.assert_called_once()
        search_query = mock_fetch.call_args[0][0]
        assert '"Senior Python Developer"' in search_query
        assert "python" in search_query.lower() or "django" in search_query.lower()

    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self) -> None:
        """Test that pipeline gracefully handles errors at each stage."""
        sample_jd_text = "Invalid job description with minimal content"
        
        # Test JD Ingestor with LLM failure
        jd_agent = JDIngestor()
        with patch("sourceress.agents.jd_ingestor.async_chat") as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")
            
            jd_result = await jd_agent.run(sample_jd_text)
            
        # Should fallback gracefully
        assert isinstance(jd_result, JDIngestResult)
        assert jd_result.job_description.title == "Invalid job description with minimal content"
        assert jd_result.job_description.must_haves == []
        
        # Test LinkedIn Sourcer with API failure
        sourcer_agent = LinkedInSourcer()
        with patch("sourceress.agents.linkedin_sourcer.fetch_profiles") as mock_fetch:
            mock_fetch.side_effect = Exception("LinkedIn API rate limited")
            
            sourcing_result = await sourcer_agent.run(jd_result.job_description)
            
        # Should return empty result gracefully
        assert isinstance(sourcing_result, SourcingResult)
        assert len(sourcing_result.candidates) == 0 