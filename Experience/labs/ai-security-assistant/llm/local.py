"""Local LLM provider — any OpenAI-compatible server running on this machine.

Works with LM Studio (default), Ollama, llama.cpp server, vLLM and anything else
that speaks the OpenAI chat-completions protocol.

    LM Studio:  start the local server, then
                LLM_PROVIDER=local LLM_MODEL=<loaded-model> LLM_BASE_URL=http://localhost:1234/v1

The implementation is inherited from `llm.openai.OpenAIProvider` — only the
defaults differ (local base URL + a placeholder API key that local servers ignore).
"""

from __future__ import annotations

from typing import Any

from llm.openai import OpenAIProvider


class LocalProvider(OpenAIProvider):
    """OpenAI-compatible provider pointing at a local inference server."""

    DEFAULT_BASE_URL = "http://localhost:1234/v1"  # LM Studio
    DEFAULT_API_KEY = "lm-studio"  # local servers do not validate the key

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "qwen2.5-coder-7b-instruct",
        base_url: str | None = None,
        client: Any | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key or self.DEFAULT_API_KEY,
            model=model,
            base_url=base_url or self.DEFAULT_BASE_URL,
            client=client,
        )