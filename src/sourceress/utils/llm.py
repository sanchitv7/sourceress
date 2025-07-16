"""Lightweight abstraction over language-model back-ends.

This module currently supports two free/non-OpenAI options:

1. **Hugging Face Transformers** – runs a local or cached model via the
   `text-generation` pipeline. Example model: ``mistralai/Mistral-7B-Instruct-v0.2``.

2. **OpenRouter API** – HTTPS endpoint offering hosted open-source models.
   Docs: https://openrouter.ai/docs

An environment variable ``LLM_BACKEND`` determines which route to use. Allowed
values: ``huggingface`` (default) or ``openrouter``.

Usage
-----
>>> from sourceress.utils.llm import async_chat
>>> reply = await async_chat("You are a helpful bot", "Hello!")
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Literal

import aiohttp
from loguru import logger

BACKEND = os.getenv("LLM_BACKEND", "huggingface").lower()
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")

__all__ = ["async_chat", "generate"]


async def async_chat(system_prompt: str, user_prompt: str, **kwargs: Any) -> str:  # noqa: D401
    """Generate a chat completion.

    Args:
        system_prompt: Role instruction passed to the model.
        user_prompt: User message.
        **kwargs: Backend-specific overrides such as ``temperature`` or ``max_tokens``.

    Returns:
        The assistant's reply as a string.
    """

    if BACKEND == "huggingface":
        return await _hf_chat(system_prompt, user_prompt, **kwargs)
    if BACKEND == "openrouter":
        return await _openrouter_chat(system_prompt, user_prompt, **kwargs)

    raise ValueError(f"Unsupported LLM_BACKEND: {BACKEND}")


auto_backend_type = Literal["huggingface", "openrouter"]


async def generate(prompt: str, **kwargs: Any) -> str:  # noqa: D401
    """Single-prompt generation helper (non-chat)."""

    if BACKEND == "huggingface":
        return await _hf_generate(prompt, **kwargs)
    if BACKEND == "openrouter":
        return await _openrouter_generate(prompt, **kwargs)

    raise ValueError(f"Unsupported LLM_BACKEND: {BACKEND}")


# -----------------------------------------------------------------------------
# Hugging Face implementation (runs in threadpool to avoid blocking event loop)
# -----------------------------------------------------------------------------


async def _hf_chat(system_prompt: str, user_prompt: str, **kwargs: Any) -> str:

    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    def _run() -> str:
        model_id = kwargs.get("model", HF_MODEL)
        logger.debug("Loading HF model: %s", model_id)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
        chat_pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=kwargs.get("max_new_tokens", 256),
            temperature=kwargs.get("temperature", 0.7),
            do_sample=kwargs.get("temperature", 0.7) > 0,
        )
        # Concatenate system + user prompt – many instruct models expect \n<eos> style separator.
        full_prompt = f"<s>[INST] {system_prompt} \n\n{user_prompt} [/INST]"
        logger.debug("Prompting HF model (%d chars)", len(full_prompt))
        output = chat_pipe(full_prompt)[0]["generated_text"]
        # Drop the prompt part from output if the pipeline returns it.
        return output.replace(full_prompt, "", 1).strip()

    return await asyncio.to_thread(_run)


async def _hf_generate(prompt: str, **kwargs: Any) -> str:
    # Reuse the chat helper for simplicity.
    return await _hf_chat("", prompt, **kwargs)


# -----------------------------------------------------------------------------
# OpenRouter implementation (simple fetch) – remains async throughout
# -----------------------------------------------------------------------------


async def _openrouter_chat(system_prompt: str, user_prompt: str, **kwargs: Any) -> str:
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY not set")

    payload = {
        "model": kwargs.get("model", OPENROUTER_MODEL),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": kwargs.get("temperature", 0.7),
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }

    logger.debug("Calling OpenRouter model %s", payload["model"])
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            # OpenRouter returns OpenAI-style choices list
            return data["choices"][0]["message"]["content"].strip()


async def _openrouter_generate(prompt: str, **kwargs: Any) -> str:
    return await _openrouter_chat("", prompt, **kwargs)
