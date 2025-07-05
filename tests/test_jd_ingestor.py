"""Tests for JD Ingestor Agent."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from sourceress.agents.jd_ingestor import JDIngestor
from sourceress.models import JobDescription, JDIngestResult


class TestJDIngestor:
    """Test suite for JD Ingestor Agent."""

    @pytest.fixture
    def sample_jd_text(self) -> str:
        """Sample job description text for testing."""
        return """
        Senior Python Developer - Remote
        
        We are seeking a skilled Senior Python Developer to join our team.
        
        Required Skills:
        - Python 3.8+
        - FastAPI/Django experience
        - PostgreSQL knowledge
        - Docker containerization
        
        Nice to have:
        - Machine Learning experience
        - AWS/GCP cloud platforms
        - Kubernetes
        
        Location: Remote (US timezone)
        Experience: 5+ years
        """

    @pytest.fixture
    def expected_llm_response(self) -> str:
        """Expected LLM response for successful parsing."""
        return json.dumps({
            "title": "Senior Python Developer - Remote",
            "must_haves": [
                "Python 3.8+",
                "FastAPI/Django experience", 
                "PostgreSQL knowledge",
                "Docker containerization"
            ],
            "nice_to_haves": [
                "Machine Learning experience",
                "AWS/GCP cloud platforms",
                "Kubernetes"
            ],
            "seniority": "Senior",
            "location": "Remote (US timezone)"
        })

    @pytest.fixture
    def ingestor(self) -> JDIngestor:
        """Create a JDIngestor instance for testing."""
        return JDIngestor()

    @pytest.mark.asyncio
    async def test_successful_jd_parsing(
        self, 
        ingestor: JDIngestor, 
        sample_jd_text: str, 
        expected_llm_response: str
    ) -> None:
        """Test successful JD parsing with valid LLM response."""
        with patch('sourceress.agents.jd_ingestor.async_chat') as mock_chat:
            mock_chat.return_value = expected_llm_response
            
            result = await ingestor.run(sample_jd_text)
            
            assert isinstance(result, JDIngestResult)
            assert isinstance(result.job_description, JobDescription)
            assert result.job_description.title == "Senior Python Developer - Remote"
            assert len(result.job_description.must_haves) == 4
            assert len(result.job_description.nice_to_haves) == 3
            assert result.job_description.seniority == "Senior"
            
            # Verify LLM was called with correct parameters
            mock_chat.assert_called_once()
            args, kwargs = mock_chat.call_args
            assert len(args) == 2  # system_prompt, user_prompt
            assert sample_jd_text in args[1]
            assert kwargs.get('temperature') == 0.3

    @pytest.mark.asyncio
    async def test_llm_json_parsing_error(
        self, 
        ingestor: JDIngestor, 
        sample_jd_text: str
    ) -> None:
        """Test fallback behavior when LLM returns invalid JSON."""
        with patch('sourceress.agents.jd_ingestor.async_chat') as mock_chat:
            mock_chat.return_value = "This is not valid JSON"
            
            result = await ingestor.run(sample_jd_text)
            
            assert isinstance(result, JDIngestResult)
            # Should fall back to heuristic parsing
            assert result.job_description.title == "Senior Python Developer - Remote"
            assert result.job_description.must_haves == []
            assert result.job_description.nice_to_haves == []

    @pytest.mark.asyncio
    async def test_llm_network_error(
        self, 
        ingestor: JDIngestor, 
        sample_jd_text: str
    ) -> None:
        """Test fallback behavior when LLM call fails completely."""
        with patch('sourceress.agents.jd_ingestor.async_chat') as mock_chat:
            mock_chat.side_effect = Exception("Network error")
            
            result = await ingestor.run(sample_jd_text)
            
            assert isinstance(result, JDIngestResult)
            # Should fall back to heuristic parsing
            assert result.job_description.title == "Senior Python Developer - Remote"
            assert result.job_description.must_haves == []

    @pytest.mark.asyncio
    async def test_invalid_llm_response_structure(
        self, 
        ingestor: JDIngestor, 
        sample_jd_text: str
    ) -> None:
        """Test model validation when LLM returns valid JSON but wrong structure."""
        invalid_response = json.dumps({
            "wrong_field": "value",
            "missing_title": True
        })
        
        with patch('sourceress.agents.jd_ingestor.async_chat') as mock_chat:
            mock_chat.return_value = invalid_response
            
            # This should raise a validation error
            with pytest.raises(Exception):
                await ingestor.run(sample_jd_text)

    @pytest.mark.asyncio
    async def test_empty_jd_text(self, ingestor: JDIngestor) -> None:
        """Test handling of empty job description text."""
        with patch('sourceress.agents.jd_ingestor.async_chat') as mock_chat:
            mock_chat.return_value = json.dumps({
                "title": "Untitled",
                "must_haves": [],
                "nice_to_haves": []
            })
            
            result = await ingestor.run("")
            
            assert isinstance(result, JDIngestResult)
            assert result.job_description.title == "Untitled"

    @pytest.mark.asyncio
    async def test_custom_temperature_parameter(
        self, 
        ingestor: JDIngestor, 
        sample_jd_text: str,
        expected_llm_response: str
    ) -> None:
        """Test that custom temperature parameter is passed through."""
        with patch('sourceress.agents.jd_ingestor.async_chat') as mock_chat:
            mock_chat.return_value = expected_llm_response
            
            await ingestor.run(sample_jd_text, temperature=0.5)
            
            # Verify custom temperature was passed
            args, kwargs = mock_chat.call_args
            assert kwargs.get('temperature') == 0.5 