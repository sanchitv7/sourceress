# sourceress/src/sourceress/agents/pitch_generator.py

"""Pitch Generator Agent.

Creates personalised outreach messages for each candidate.
"""

from __future__ import annotations

from typing import Any

from sourceress.agents.base import BaseAgent
from sourceress.models import KeyMatchResult, PitchResult


class PitchGenerator(BaseAgent):
    """Agent responsible for generating recruiter outreach messages."""

    name: str = "pitch_generator"

    def __init__(self) -> None:
        super().__init__(
            role="Recruitment Outreach Specialist",
            goal="Create personalized and compelling outreach messages for qualified candidates",
            backstory="You are a charismatic recruitment professional with excellent communication skills. "
                     "You specialize in crafting personalized outreach messages that resonate with candidates "
                     "and generate high response rates. You understand how to balance professionalism with "
                     "warmth, and you excel at highlighting mutual benefits in your messaging.",
        )

    async def run(self, matched: KeyMatchResult, **kwargs: Any) -> PitchResult:  # noqa: D401
        """Execute the agent.

        Args:
            matched: Results from the KeyMatcher.
            **kwargs: Additional runtime parameters.

        Returns:
            A :class:`sourceress.models.PitchResult` instance.
        """
        self.log.debug("Generating pitches for %d candidates", len(matched.matches))
        # TODO(student): Generate personalised outreach messages.
        #   1. Design Jinja2 templates for each channel (cold call, LinkedIn DM, WhatsApp).
        #   2. Feed the filled template into GPT-4 Turbo via `openai.ChatCompletion` to polish tone.
        #   3. Track token usage; experiment with temperature 0.3-0.7 for variation.
        #   4. Consider A/B testing tone variants and logging response rates for future ML ranking.
        from sourceress.models import PitchMaterials
        dummy_pitches = [
            PitchMaterials(
                linkedin_url=match.linkedin_url,
                cold_call="Hi! I'm reaching out because I have an exciting opportunity that matches your background perfectly. Would you be open to a brief conversation?",
                dm_message="Hi there! I came across your profile and was impressed by your experience. I have a role that seems like a great fit for your skills. Would you be interested in learning more?",
                whatsapp_message="Hi! I'm a recruiter and found your profile interesting. I have a great opportunity that matches your background. Are you open to new opportunities?"
            )
            for match in matched.matches
        ]
        return PitchResult(pitches=dummy_pitches) 