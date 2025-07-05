#!/usr/bin/env python
# sourceress/src/sourceress/agents/base.py

"""Shared base class for all Sourceress agents.

Provides:
    • A common Loguru logger instance bound with the agent's ``name``.
    • Exponential back-off retry logic (via *tenacity*) around the core
      :py:meth:`run` coroutine.
    • Compatibility stubs for CrewAI's ``Agent`` API – subclasses only need to
      implement :py:meth:`run` and set ``name``.

This keeps individual agent files clean and consistent while ensuring robust
error-handling across the project.
"""

from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable, Coroutine, TypeVar

from crewai import Agent  # type: ignore
from loguru import logger
from tenacity import AsyncRetrying, RetryCallState, stop_after_attempt, wait_exponential

__all__ = ["BaseAgent"]

T = TypeVar("T")


class BaseAgent(Agent):
    """Common functionality shared by all Sourceress agents.

    Subclasses should override :pyattr:`name` and implement :pymeth:`run`.
    The public :pymeth:`execute` method expected by CrewAI wraps ``run`` with
    a configurable *tenacity* retry, logging each attempt.
    """

    # --- Class-level configuration -------------------------------------------------

    #: Agent identifier; subclasses **must** override.
    name: str = "base_agent"

    #: Maximum number of retry attempts for :pymeth:`run`.
    max_attempts: int = 3

    #: Exponential back-off multiplier in seconds (see *tenacity* docs).
    wait_multiplier: int = 1

    #: Maximum wait time between retries in seconds.
    wait_max: int = 10

    # -----------------------------------------------------------------------------

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
        """Initialise agent and bind a contextual logger."""

        # Delegate to CrewAI's ``Agent`` constructor (may accept various kwargs).
        super().__init__(*args, **kwargs)

        # Each agent gets its own logger context for readable structured logs.
        self.log = logger.bind(agent=self.name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def execute(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        """Entry-point invoked by CrewAI.

        Wraps the user-defined :pymeth:`run` coroutine with exponential back-off
        retry logic.  Subclasses generally should *not* override this method –
        place the business logic in :pymeth:`run` instead.
        """

        return await self._run_with_retry(self.run, *args, **kwargs)

    # ------------------------------------------------------------------
    # Methods for subclasses to override
    # ------------------------------------------------------------------

    async def run(self, *args: Any, **kwargs: Any) -> Any:  # noqa: D401
        """Agent business logic to be provided by concrete subclasses."""

        raise NotImplementedError("Subclasses must implement `run()`")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _run_with_retry(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute *func* with tenacity-powered exponential back-off.

        Parameters
        ----------
        func
            The coroutine function to execute (e.g. :pymeth:`run`).
        *args, **kwargs
            Forwarded to *func*.

        Returns
        -------
        T
            Whatever *func* returns.
        """

        # Build retry iterator.
        async for attempt in AsyncRetrying(
            reraise=True,
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=self.wait_multiplier, max=self.wait_max),
        ):
            try:
                with attempt:
                    attempt_n: int = attempt.retry_state.attempt_number  # type: ignore[attr-defined]
                    if attempt_n > 1:
                        self.log.warning(
                            "Retrying (%d/%d)…", attempt_n, self.max_attempts
                        )
                    result: T = await func(*args, **kwargs)
                    return result
            except Exception as exc:  # noqa: BLE001
                # Log exception; the *tenacity* context manager will decide if we retry.
                self.log.error(
                    "%s raised on attempt %d: %s", func.__name__, attempt_n, exc
                )
                raise

        # Should never reach here because reraise=True ensures final exception.
        raise RuntimeError("Retry loop exited without returning or raising.")
