"""LLM provider factory.

Selects a provider based on configuration. The rest of the system only ever
uses the `LLMProvider` interface.

Supported providers (`LLM_PROVIDER`):

| Value | Provider | Notes |
|---|---|---|
| `openai` | `OpenAIProvider` | requires `OPENAI_API_KEY` |
| `anthropic` | `AnthropicProvider` | requires `ANTHROPIC_API_KEY` |
| `local` | `LocalProvider` | OpenAI-compatible server on this machine (LM Studio, Ollama, vLLM) |
| `mock` | `MockLLMProvider` | deterministic, offline, no credentials |

Provider SDKs are imported lazily so `local`/`mock` work without them installed.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from llm.base import LLMProvider


@lru_cache
def get_provider() -> LLMProvider:
    """Build the configured provider (openai | anthropic | local | mock)."""
    provider_name = settings.llm_provider.lower()

    if provider_name == "openai":
        from llm.openai import OpenAIProvider

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )

    if provider_name == "anthropic":
        from llm.anthropic import AnthropicProvider

        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")
        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.llm_model)

    if provider_name == "local":
        from llm.local import LocalProvider

        return LocalProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )

    if provider_name == "mock":
        from llm.mock import MockLLMProvider

        return MockLLMProvider()

    raise ValueError(f"Unknown LLM provider: {provider_name!r}")
