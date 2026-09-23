"""LLM provider tests — no network and no provider SDKs required.

The OpenAI/Anthropic providers accept an injected client, so we exercise the
real mapping logic with lightweight fakes.
"""

from __future__ import annotations

from llm.anthropic import AnthropicProvider
from llm.base import LLMMessage, MessageRole
from llm.local import LocalProvider
from llm.mock import MockLLMProvider
from llm.openai import OpenAIProvider

# --- OpenAI-compatible fakes -------------------------------------------------


class _FakeFunction:
    def __init__(self, name: str, arguments: str) -> None:
        self.name = name
        self.arguments = arguments


class _FakeToolCall:
    def __init__(self, call_id: str, name: str, arguments: str) -> None:
        self.id = call_id
        self.function = _FakeFunction(name, arguments)


class _FakeMessage:
    def __init__(self, content: str | None, tool_calls: list[_FakeToolCall] | None = None) -> None:
        self.content = content
        self.tool_calls = tool_calls or []


class _FakeCompletions:
    def __init__(self, message: _FakeMessage, recorder: list[dict]) -> None:
        self._message = message
        self._recorder = recorder

    async def create(self, **kwargs):
        self._recorder.append(kwargs)

        class _Completion:
            def __init__(self, message: _FakeMessage) -> None:
                self.choices = [type("_Choice", (), {"message": message})()]

        return _Completion(self._message)


class FakeOpenAIClient:
    def __init__(self, message: _FakeMessage) -> None:
        self.calls: list[dict] = []
        self.chat = type("_Chat", (), {"completions": _FakeCompletions(message, self.calls)})()


# --- Anthropic fakes ---------------------------------------------------------


class _FakeTextBlock:
    type = "text"

    def __init__(self, text: str) -> None:
        self.text = text


class _FakeToolUseBlock:
    type = "tool_use"

    def __init__(self, block_id: str, name: str, tool_input: dict) -> None:
        self.id = block_id
        self.name = name
        self.input = tool_input


class _FakeAnthropicMessages:
    def __init__(self, blocks: list, recorder: list[dict]) -> None:
        self._blocks = blocks
        self._recorder = recorder

    async def create(self, **kwargs):
        self._recorder.append(kwargs)

        class _Response:
            def __init__(self, blocks: list) -> None:
                self.content = blocks

        return _Response(self._blocks)


class FakeAnthropicClient:
    def __init__(self, blocks: list) -> None:
        self.calls: list[dict] = []
        self.messages = _FakeAnthropicMessages(blocks, self.calls)


# --- OpenAI provider ---------------------------------------------------------


async def test_openai_provider_maps_messages_and_returns_content() -> None:
    client = FakeOpenAIClient(_FakeMessage("hello"))
    provider = OpenAIProvider(api_key="k", model="m", client=client)

    response = await provider.complete([LLMMessage(role=MessageRole.USER, content="hi")])

    assert response.content == "hello"
    assert response.tool_calls == []
    assert client.calls[0]["model"] == "m"
    assert client.calls[0]["messages"] == [{"role": "user", "content": "hi"}]
    assert client.calls[0]["temperature"] == 0.0


async def test_openai_provider_parses_tool_calls() -> None:
    message = _FakeMessage("", [_FakeToolCall("call-1", "get_cve", '{"cve_id": "CVE-2024-1234"}')])
    client = FakeOpenAIClient(message)
    provider = OpenAIProvider(api_key="k", model="m", client=client)

    response = await provider.complete(
        [LLMMessage(role=MessageRole.USER, content="hi")],
        tools=[{"type": "function", "function": {"name": "get_cve"}}],
    )

    assert response.tool_calls == [
        {"id": "call-1", "name": "get_cve", "arguments": {"cve_id": "CVE-2024-1234"}}
    ]
    assert "tools" in client.calls[0]


async def test_openai_provider_tolerates_unparsable_tool_arguments() -> None:
    message = _FakeMessage("", [_FakeToolCall("call-1", "get_cve", "not-json")])
    provider = OpenAIProvider(api_key="k", model="m", client=FakeOpenAIClient(message))

    response = await provider.complete([LLMMessage(role=MessageRole.USER, content="hi")])

    assert response.tool_calls[0]["arguments"] == {}


# --- Anthropic provider ------------------------------------------------------


async def test_anthropic_provider_splits_system_message() -> None:
    client = FakeAnthropicClient([_FakeTextBlock("ok")])
    provider = AnthropicProvider(api_key="k", model="m", client=client)

    response = await provider.complete(
        [
            LLMMessage(role=MessageRole.SYSTEM, content="be careful"),
            LLMMessage(role=MessageRole.USER, content="hi"),
        ]
    )

    assert response.content == "ok"
    sent = client.calls[0]
    assert sent["system"] == "be careful"
    assert sent["messages"] == [{"role": "user", "content": "hi"}]
    assert sent["max_tokens"] > 0  # required by the Anthropic API


async def test_anthropic_provider_parses_tool_use_blocks() -> None:
    blocks = [_FakeTextBlock("thinking"), _FakeToolUseBlock("t-1", "search_knowledge", {"query": "x"})]
    client = FakeAnthropicClient(blocks)
    provider = AnthropicProvider(api_key="k", model="m", client=client)

    response = await provider.complete(
        [LLMMessage(role=MessageRole.USER, content="hi")],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "search",
                    "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
                },
            }
        ],
    )

    assert response.content == "thinking"
    assert response.tool_calls == [
        {"id": "t-1", "name": "search_knowledge", "arguments": {"query": "x"}}
    ]
    assert client.calls[0]["tools"][0]["input_schema"]["properties"] == {"query": {"type": "string"}}


# --- Local provider ----------------------------------------------------------


def test_local_provider_defaults_to_lm_studio() -> None:
    provider = LocalProvider()

    assert provider.base_url == "http://localhost:1234/v1"
    assert provider.api_key == "lm-studio"


def test_local_provider_accepts_overrides() -> None:
    provider = LocalProvider(api_key="custom", base_url="http://localhost:8080/v1", model="qwen3")

    assert provider.base_url == "http://localhost:8080/v1"
    assert provider.api_key == "custom"
    assert provider.model == "qwen3"


# --- Mock provider -----------------------------------------------------------


async def test_mock_provider_returns_scripted_responses_in_order() -> None:
    provider = MockLLMProvider(responses=["first", "second"])

    assert (await provider.complete([])).content == "first"
    assert (await provider.complete([])).content == "second"
    assert len(provider.calls) == 2


async def test_mock_provider_defaults_to_empty_json_object() -> None:
    provider = MockLLMProvider()

    assert (await provider.complete([])).content == "{}"


async def test_mock_provider_records_sent_messages() -> None:
    provider = MockLLMProvider(response="ok")
    messages = [LLMMessage(role=MessageRole.USER, content="hi")]

    await provider.complete(messages)

    assert provider.calls[0]["messages"] == messages
