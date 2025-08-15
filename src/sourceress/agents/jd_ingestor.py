# sourceress/src/sourceress/agents/jd_ingestor.py

"""Job Description Ingestor Agent.

Parses raw job description text into a structured :class:`sourceress.models.JobDescription`.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from sourceress.agents.base import BaseAgent
from sourceress.models import JDIngestResult, JobDescription
from sourceress.utils.llm import async_chat


class JDIngestor(BaseAgent):
    """Convert raw job-description text into a validated :class:`JobDescription`."""

    name: str = "jd_ingestor"

    def __init__(self) -> None:
        super().__init__(
            role="Job Description Analyst",
            goal="Parse and extract structured information from raw job description text",
            backstory="You are an expert recruitment analyst with deep understanding of job descriptions. "
                     "You excel at identifying key requirements, skills, and qualifications from "
                     "unstructured text. You can distinguish between must-have and nice-to-have "
                     "requirements and extract meaningful metadata like seniority levels and locations.",
        )

    # Allow callers to override temperature etc. via kwargs.
    async def run(self, jd_text: str, **kwargs: Any) -> JDIngestResult:  # noqa: D401
        self.log.debug("Starting JD ingestion for %d characters", len(jd_text))

        # ------------------------------------------------------------------
        # 1. LLM-based structured extraction
        # ------------------------------------------------------------------

        system_prompt = (
            "You are an expert recruitment analyst. Given a raw job description, "
            "extract structured JSON with keys: title (string), must_haves (list[str]), "
            "nice_to_haves (list[str]), seniority (string|optional), location (string|optional), "
            "company_info (string|optional), role_description (string|optional). "
            "Be thorough in extracting requirements from the text. "
            "Respond with ONLY the JSON object, no additional text or markdown."
        )

        # In some environments an LLM may not be available; handle gracefully.
        jd_json: Dict[str, Any]
        try:
            llm_response = await async_chat(system_prompt, jd_text, temperature=0.1)
            self.log.debug("LLM raw response: %s", llm_response)

            # Clean the response - remove markdown code blocks if present
            cleaned_response = llm_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            jd_json = json.loads(cleaned_response)
        except Exception as exc:  # noqa: BLE001
            self.log.warning(
                "LLM parsing failed (%s). Response was: %s. Falling back to heuristic stub.", 
                exc, llm_response[:200] if 'llm_response' in locals() else 'N/A'
            )
            # ------------------------------------------------------------------
            # 2. Heuristic fallback – ensures downstream pipeline doesn\'t break
            # ------------------------------------------------------------------
            # Extract title from first non-empty line
            lines = [line.strip() for line in jd_text.split('\n') if line.strip()]
            title = lines[0][:120] if lines else "Unknown Position"
            
            jd_json = {
                "title": title,
                "must_haves": [],
                "nice_to_haves": [],
                "seniority": None,
                "location": None,
                "raw_text": jd_text,
            }

        # ------------------------------------------------------------------
        # 3. Validation & Model conversion
        # ------------------------------------------------------------------

        try:
            job_desc = JobDescription.model_validate(jd_json)
        except Exception as exc:  # noqa: BLE001
            self.log.error("Structured payload validation failed: %s", exc)
            raise

        result = JDIngestResult(job_description=job_desc)
        self.log.info("JD parsed: %s", job_desc.title)
        return result
