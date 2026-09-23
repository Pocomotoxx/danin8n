"""Provider-agnostic LLM access — no OpenAI SDK lock-in.

Uses LiteLLM, which speaks to 100+ providers (OpenAI, Anthropic, Google, Mistral, local, …) behind
one ``completion`` call. The model id carries the provider, e.g. ``anthropic/claude-sonnet-4``,
``gpt-4.1``, ``ollama/llama3``. Keys come from the provider's usual env vars.

The ``Completer`` protocol keeps the rest of the app testable offline: pass any object with a
``complete(system, user)`` method (a real LiteLLM one, or a fake in tests).
"""

from __future__ import annotations

import os
from typing import Protocol


class Completer(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class LiteLLMCompleter:
    """Calls any provider through LiteLLM. Import is lazy so the app runs without litellm installed
    until an LLM feature is actually used."""

    def __init__(self, model: str | None = None, temperature: float = 0.2) -> None:
        self.model = model or os.getenv("N8N_FACTORY_MODEL") or "gpt-4.1"
        self.temperature = temperature

    def complete(self, system: str, user: str) -> str:
        try:
            from litellm import completion
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "litellm is required for LLM features. Install it: pip install litellm"
            ) from exc

        resp = completion(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp["choices"][0]["message"]["content"] or ""


class EchoCompleter:
    """A deterministic offline stand-in used by tests and when no provider is configured."""

    def complete(self, system: str, user: str) -> str:  # noqa: ARG002
        return user
