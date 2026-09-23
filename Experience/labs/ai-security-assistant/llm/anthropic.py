"""Anthropic LLM provider (messages API + tool use).

The `anthropic` SDK is imported lazily so this package can be imported, and the
providers unit-tested, without the SDK installed. Tests inject a fake client
through the `client=` argument.
"""

from __future__ import annotations

from typing import Any

from llm.base import LLMMessage, LLMProvider, LLMResponse, MessageRole

# Anthropic requires an explicit max_tokens value.
_DEFAULT_MAX_TOKENS = 1024


class AnthropicProvider(LLMProvider):
    """Anthropic provider (messages API + tool use)."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._client = client

    def _get_client(self) -> Any:
        """Return the SDK client, creating it lazily on first use."""
        if self._client is None:
            from anthropic import AsyncAnthropic  # imported lazily: the SDK is optional

            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def complete(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        system, conversation = _split_system(messages)
        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens or _DEFAULT_MAX_TOKENS,
            "temperature": temperature,
            "messages": conversation,
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = [_to_anthropic_tool(tool) for tool in tools]

        completion = await self._get_client().messages.create(**payload)
        content, tool_calls = _parse_anthropic_content(getattr(completion, "content", None))
        return LLMResponse(content=content, tool_calls=tool_calls)


def _split_system(messages: list[LLMMessage]) -> tuple[str, list[dict[str, Any]]]:
    """Anthropic takes the system prompt out-of-band, not as a message."""
    system_parts: list[str] = []
    conversation: list[dict[str, Any]] = []
    for message in messages:
        if message.role == MessageRole.SYSTEM:
            system_parts.append(message.content)
            continue
        role = "user" if message.role == MessageRole.TOOL else message.role.value
        conversation.append({"role": role, "content": message.content})
    return "\n\n".join(part for part in system_parts if part), conversation


def _to_anthropic_tool(tool: dict[str, Any]) -> dict[str, Any]:
    """Convert an OpenAI-style tool schema to the Anthropic format."""
    function = tool.get("function", tool)
    return {
        "name": function.get("name"),
        "description": function.get("description", ""),
        "input_schema": function.get("parameters", {"type": "object", "properties": {}}),
    }


def _parse_anthropic_content(blocks: Any) -> tuple[str, list[dict[str, Any]]]:
    """Flatten Anthropic content blocks into text + normalised tool calls."""
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    for block in blocks or []:
        block_type = _get(block, "type")
        if block_type == "text":
            text_parts.append(_get(block, "text") or "")
        elif block_type == "tool_use":
            tool_calls.append(
                {
                    "id": _get(block, "id"),
                    "name": _get(block, "name"),
                    "arguments": _get(block, "input") or {},
                }
            )
    return "".join(text_parts), tool_calls


def _get(obj: Any, key: str) -> Any:
    """Read `key` from a dict or an object attribute (SDK responses)."""
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)
