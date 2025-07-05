"""End-to-end workflow integration tests."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

from sourceress.workflows import run_end_to_end_manual, run_end_to_end_crewai
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


class TestWorkflowIntegration:
    """Test suite for end-to-end workflow integration."""

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
    async def test_manual_workflow_end_to_end(self, sample_jd_text: str, tmp_path) -> None:
        """Test complete manual workflow from JD text to Excel output."""
        
        # Mock all the LLM calls and agent responses
        with patch("sourceress.utils.llm.async_chat") as mock_llm:
            mock_llm.return_value = """{
                "title": "Senior Python Developer",
                "must_haves": ["Python", "Django", "PostgreSQL", "Git"],
                "nice_to_haves": ["AWS", "Docker", "React"],
                "seniority": "Senior",
                "location": "Remote"
            }"""
            
            # Set output path to tmp directory
            output_path = tmp_path / "test_workflow_output.xlsx"
            
            # Run the manual workflow
            result = await run_end_to_end_manual(
                sample_jd_text, 
                output_path=output_path
            )
            
            # Verify the workflow completed successfully
            assert isinstance(result, str)
            assert Path(result).exists()
            assert Path(result).name == "test_workflow_output.xlsx"

    @pytest.mark.asyncio
    async def test_manual_workflow_with_llm_failure(self, sample_jd_text: str, tmp_path) -> None:
        """Test manual workflow handles LLM failure gracefully."""
        
        # Mock LLM to fail
        with patch("sourceress.utils.llm.async_chat") as mock_llm:
            mock_llm.side_effect = Exception("LLM unavailable")
            
            # Set output path to tmp directory
            output_path = tmp_path / "test_workflow_fallback.xlsx"
            
            # Run the manual workflow
            result = await run_end_to_end_manual(
                sample_jd_text, 
                output_path=output_path
            )
            
            # Verify the workflow completed successfully even with LLM failure
            assert isinstance(result, str)
            assert Path(result).exists()
            assert Path(result).name == "test_workflow_fallback.xlsx"

    def test_crewai_workflow_structure(self, sample_jd_text: str) -> None:
        """Test CrewAI workflow structure (mocked execution)."""
        
        # Mock the CrewAI Crew execution
        with patch("sourceress.workflows.Crew") as mock_crew_class:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = "/path/to/output.xlsx"
            mock_crew_class.return_value = mock_crew_instance
            
            # Run the CrewAI workflow
            result = run_end_to_end_crewai(sample_jd_text)
            
            # Verify CrewAI was called properly
            mock_crew_class.assert_called_once()
            mock_crew_instance.kickoff.assert_called_once_with(
                inputs={"jd_text": sample_jd_text}
            )
            assert result == "/path/to/output.xlsx"

    def test_crewai_workflow_task_dependencies(self) -> None:
        """Test that CrewAI tasks have proper dependencies set up."""
        
        # Import the task creation function
        from sourceress.tasks import create_all_tasks
        
        # Create all tasks
        jd_task, sourcing_task, scoring_task, matching_task, pitching_task, excel_task = create_all_tasks()
        
        # Verify task dependencies are set up correctly
        assert sourcing_task.context == [jd_task]
        assert scoring_task.context == [jd_task, sourcing_task]
        assert matching_task.context == [jd_task, scoring_task]
        assert pitching_task.context == [matching_task]
        assert excel_task.context == [pitching_task]
        
        # Verify all tasks have agents assigned
        assert jd_task.agent is not None
        assert sourcing_task.agent is not None
        assert scoring_task.agent is not None
        assert matching_task.agent is not None
        assert pitching_task.agent is not None
        assert excel_task.agent is not None

    def test_task_descriptions_and_outputs(self) -> None:
        """Test that all tasks have proper descriptions and expected outputs."""
        
        from sourceress.tasks import create_all_tasks
        
        # Create all tasks
        jd_task, sourcing_task, scoring_task, matching_task, pitching_task, excel_task = create_all_tasks()
        
        # Verify all tasks have descriptions
        assert len(jd_task.description) > 0
        assert len(sourcing_task.description) > 0
        assert len(scoring_task.description) > 0
        assert len(matching_task.description) > 0
        assert len(pitching_task.description) > 0
        assert len(excel_task.description) > 0
        
        # Verify all tasks have expected outputs
        assert len(jd_task.expected_output) > 0
        assert len(sourcing_task.expected_output) > 0
        assert len(scoring_task.expected_output) > 0
        assert len(matching_task.expected_output) > 0
        assert len(pitching_task.expected_output) > 0
        assert len(excel_task.expected_output) > 0

    def test_agent_role_definitions(self) -> None:
        """Test that all agents have proper CrewAI role definitions."""
        
        from sourceress.agents import (
            JDIngestor,
            LinkedInSourcer,
            RelevanceScorer,
            KeyMatcher,
            PitchGenerator,
            ExcelWriter,
        )
        
        # Initialize all agents
        agents = [
            JDIngestor(),
            LinkedInSourcer(),
            RelevanceScorer(),
            KeyMatcher(),
            PitchGenerator(),
            ExcelWriter(),
        ]
        
        # Verify all agents have role definitions
        for agent in agents:
            assert hasattr(agent, 'role')
            assert hasattr(agent, 'goal')
            assert hasattr(agent, 'backstory')
            assert len(agent.role) > 0
            assert len(agent.goal) > 0
            assert len(agent.backstory) > 0
            assert agent.name is not None
            assert len(agent.name) > 0 