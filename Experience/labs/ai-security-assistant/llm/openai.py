"""OpenAI LLM provider (chat completions + tool calling).

Also serves as the base class for any OpenAI-compatible endpoint — see
`llm/local.py` for local inference servers (LM Studio, Ollama, vLLM).

The `openai` SDK is imported lazily so this package can be imported, and the
providers unit-tested, without the SDK installed. Tests inject a fake client
through the `client=` argument.
"""

from __future__ import annotations

import json
from typing import Any

from llm.base import LLMMessage, LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI-compatible provider (chat completions + tool calling)."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = client

    def _get_client(self) -> Any:
        """Return the SDK client, creating it lazily on first use."""
        if self._client is None:
            from openai import AsyncOpenAI  # imported lazily: the SDK is optional

            kwargs: dict[str, Any] = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = AsyncOpenAI(**kwargs)
        return self._client

    async def complete(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [_to_openai_message(message) for message in messages],
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = tools

        completion = await self._get_client().chat.completions.create(**payload)
        message = completion.choices[0].message
        return LLMResponse(
            content=getattr(message, "content", "") or "",
            tool_calls=parse_openai_tool_calls(getattr(message, "tool_calls", None)),
        )


def _to_openai_message(message: LLMMessage) -> dict[str, Any]:
    """Map a vendor-neutral message to the OpenAI chat format."""
    payload: dict[str, Any] = {"role": message.role.value, "content": message.content}
    payload.update(message.extra)
    return payload


def parse_openai_tool_calls(tool_calls: Any) -> list[dict[str, Any]]:
    """Normalise OpenAI tool calls (SDK objects or plain dicts) to dicts."""
    if not tool_calls:
        return []
    parsed: list[dict[str, Any]] = []
    for call in tool_calls:
        function = _get(call, "function")
        parsed.append(
            {
                "id": _get(call, "id"),
                "name": _get(function, "name"),
                "arguments": _loads_object(_get(function, "arguments")),
            }
        )
    return parsed


def _get(obj: Any, key: str) -> Any:
    """Read `key` from a dict or an object attribute (SDK responses)."""
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def _loads_object(raw: Any) -> dict[str, Any]:
    """Parse a JSON-encoded argument string into a dict; empty dict on failure."""
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw:
        return {}
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}
