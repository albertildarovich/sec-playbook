"""LLM provider abstraction layer.

Providers: OpenAI, Anthropic, local (OpenAI-compatible: LM Studio / Ollama / vLLM)
and a deterministic mock for offline tests and demos.

The rest of the code depends only on `LLMProvider` from `llm.base` — swap
providers via `llm.factory.get_provider` (configured through `LLM_PROVIDER`).
"""

from llm.anthropic import AnthropicProvider
from llm.base import LLMMessage, LLMProvider, LLMResponse, MessageRole
from llm.factory import get_provider
from llm.local import LocalProvider
from llm.mock import MockLLMProvider
from llm.openai import OpenAIProvider

__all__ = [
    "AnthropicProvider",
    "LLMMessage",
    "LLMProvider",
    "LLMResponse",
    "LocalProvider",
    "MessageRole",
    "MockLLMProvider",
    "OpenAIProvider",
    "get_provider",
]
