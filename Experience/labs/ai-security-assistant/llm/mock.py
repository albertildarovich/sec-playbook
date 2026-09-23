"""Deterministic mock LLM provider.

Used for offline tests, demos and CI where no model endpoint is available, and
as `LLM_PROVIDER=mock` for a zero-configuration run.

Responses are scripted: pass a single `response`, or an ordered `responses` list
that is consumed one entry per call. Every call is recorded in `calls` so tests
can assert on what was sent to the model.
"""

from __future__ import annotations

from typing import Any

from llm.base import LLMMessage, LLMProvider, LLMResponse

_DEFAULT_RESPONSE = "{}"


class MockLLMProvider(LLMProvider):
    """Returns scripted responses with no network or SDK dependency."""

    def __init__(
        self,
        response: str | None = None,
        responses: list[str] | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> None:
        self._response = response if response is not None else _DEFAULT_RESPONSE
        self._responses = list(responses) if responses else []
        self._tool_calls = tool_calls or []
        self.calls: list[dict[str, Any]] = []

    async def complete(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        self.calls.append(
            {
                "messages": messages,
                "tools": tools,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        content = self._responses.pop(0) if self._responses else self._response
        return LLMResponse(content=content, tool_calls=list(self._tool_calls))