# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sourceress is an agentic AI-powered recruiting assistant that automates the end-to-end talent sourcing pipeline. It processes job descriptions, scrapes LinkedIn profiles, scores candidates for relevance, extracts key requirement matches, generates personalized outreach messages, and outputs everything to a formatted Excel workbook.

## Development Commands

### Installation & Setup
```bash
# Install with development dependencies using uv
uv pip install -e .[dev]

# Install Playwright browsers (required for LinkedIn scraping)
playwright install chromium
```

### Environment Variables
Required environment variables:
- `OPENAI_API_KEY`: For LLM calls and embeddings
- `LINKEDIN_COOKIE`: LinkedIn session cookie for scraping authentication
- `LLM_BACKEND=openai`: Backend selection (or huggingface/openrouter)
- `LINKEDIN_SESSION_FILE=.linkedin_session`: Session persistence file

### Running the Application
```bash
# Main CLI entry point
python -m sourceress --jd-file path/to/job_description.txt --output output.xlsx

# Direct module execution
python src/sourceress/main.py --jd-file example_jd.txt
```

### Testing
```bash
# Run unit tests
pytest -q

# Run specific test files
pytest tests/test_agents.py
pytest tests/test_jd_ingestor.py

# Manual integration tests (in root directory)
python test_linkedin_sourcer.py
python test_jd_llm.py
```

### Code Quality Tools
The project uses pre-commit hooks with:
- `ruff`: Linting and code formatting
- `black`: Code formatting
- `isort`: Import sorting
- `mypy`: Type checking

## Architecture Overview

### Core Pipeline Flow
1. **JD Ingestor**: Parses raw job description text → structured `JobDescription`
2. **LinkedIn Sourcer**: Searches LinkedIn → list of `CandidateProfile` objects  
3. **Relevance Scorer**: Scores candidates 0-100 → `ScoredCandidate` objects
4. **Key Matcher**: Maps job requirements to candidate evidence → `KeyMatchEntry`
5. **Pitch Generator**: Creates personalized outreach messages → `PitchMaterials`
6. **Excel Writer**: Generates final formatted workbook

### Key Components

**Agent System** (`src/sourceress/agents/`):
- `BaseAgent`: Common retry logic, logging, CrewAI compatibility
- Each agent inherits from `BaseAgent` and implements `async run()` method
- Agents use structured Pydantic models for input/output validation

**Models** (`src/sourceress/models.py`):
- Pydantic models defining data contracts between pipeline stages
- Key models: `JobDescription`, `CandidateProfile`, `ScoredCandidate`, `KeyMatch`, `PitchMaterials`

**Orchestration** (`src/sourceress/workflows.py`):
- Manual chaining approach (current): `run_end_to_end_manual()`
- CrewAI orchestration (target): `run_end_to_end_crewai()` with proper Task dependencies
- Task definitions in `tasks.py` with context passing between stages

**Utilities** (`src/sourceress/utils/`):
- `linkedin_api.py`: LinkedIn profile fetching and scraping integration
- `scraping.py`: Playwright-based LinkedIn scraping with session management
- `linkedin_auth.py`: Authentication and session persistence
- `llm.py`: LLM abstraction layer supporting multiple backends

### Current Development State
- ✅ **Foundation Complete**: Models, agents, CrewAI tasks, orchestration framework
- ⚠️ **Implementation Needed**: Real logic in agents (currently use dummy data)
- **Active Focus**: Slice-based development replacing dummy implementations

## Implementation Guidelines

### Cursor Rule Integration
The project includes a grounding rule that emphasizes:
- Thorough codebase analysis before making changes
- Understanding architecture and component responsibilities  
- Identifying external dependencies and patterns
- Prioritizing accuracy and fidelity to existing code
- Explicit acknowledgment of uncertainties

### LinkedIn Scraping
Uses `undetected_chromedriver` with session-based authentication. The scraping utilities are in `utils/scraping.py` with session persistence to avoid repeated logins.

### LLM Integration
Supports multiple backends via `utils/llm.py`. Primary usage is OpenAI GPT-4 for text generation and embeddings for relevance scoring.

### Testing Strategy
- **Primary**: Unit tests in `tests/` directory using pytest with mocks for external dependencies
- **Integration**: Automated pytest tests for component interactions (no manual test files)
- **External Dependencies**: Mock LinkedIn scraping and LLM calls in tests
- **Test Data**: Use fixtures and sample data, avoid live API calls in tests
- **IMPORTANT**: Do NOT create manual test files (test_*.py) in project root - use proper pytest structure only

### Error Handling
- Exponential backoff retry logic in `BaseAgent`
- Structured logging with Loguru, agent-specific contexts
- Graceful degradation for API failures (LinkedIn rate limits, LLM timeouts)

## Development Guidelines

### Testing Best Practices
- **NO manual test files**: Never create test_*.py files in project root during development
- **Use pytest properly**: All tests go in tests/ directory with proper structure and fixtures
- **Mock external services**: LinkedIn scraping, LLM calls should be mocked in tests to avoid dependencies
- **Automated testing only**: Tests should run via `pytest` without manual intervention
- **Focus on unit tests**: Test individual components with mocked dependencies rather than full integration