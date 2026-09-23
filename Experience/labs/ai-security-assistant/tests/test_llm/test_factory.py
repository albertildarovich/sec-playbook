"""LLM provider factory tests — configuration-driven provider selection."""

from __future__ import annotations

import pytest

from llm import factory
from llm.anthropic import AnthropicProvider
from llm.local import LocalProvider
from llm.mock import MockLLMProvider
from llm.openai import OpenAIProvider


@pytest.fixture(autouse=True)
def _clear_provider_cache():
    """`get_provider` is lru_cached — reset it around every test."""
    factory.get_provider.cache_clear()
    yield
    factory.get_provider.cache_clear()


def test_mock_provider_requires_no_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory.settings, "llm_provider", "mock")

    assert isinstance(factory.get_provider(), MockLLMProvider)


def test_local_provider_uses_lm_studio_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory.settings, "llm_provider", "local")
    monkeypatch.setattr(factory.settings, "llm_model", "qwen2.5-coder-7b-instruct")
    monkeypatch.setattr(factory.settings, "llm_base_url", None)
    monkeypatch.setattr(factory.settings, "llm_api_key", None)

    provider = factory.get_provider()

    assert isinstance(provider, LocalProvider)
    assert provider.base_url == LocalProvider.DEFAULT_BASE_URL
    assert provider.model == "qwen2.5-coder-7b-instruct"
    assert provider.api_key == LocalProvider.DEFAULT_API_KEY


def test_local_provider_honours_configured_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory.settings, "llm_provider", "local")
    monkeypatch.setattr(factory.settings, "llm_base_url", "http://localhost:11434/v1")
    monkeypatch.setattr(factory.settings, "llm_api_key", "ollama")

    provider = factory.get_provider()

    assert isinstance(provider, LocalProvider)
    assert provider.base_url == "http://localhost:11434/v1"
    assert provider.api_key == "ollama"


def test_openai_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory.settings, "llm_provider", "openai")
    monkeypatch.setattr(factory.settings, "openai_api_key", None)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        factory.get_provider()


def test_openai_provider_is_built_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory.settings, "llm_provider", "openai")
    monkeypatch.setattr(factory.settings, "openai_api_key", "sk-test")
    monkeypatch.setattr(factory.settings, "llm_model", "gpt-4o-mini")
    monkeypatch.setattr(factory.settings, "llm_base_url", None)

    assert isinstance(factory.get_provider(), OpenAIProvider)


def test_anthropic_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory.settings, "llm_provider", "anthropic")
    monkeypatch.setattr(factory.settings, "anthropic_api_key", None)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        factory.get_provider()


def test_anthropic_provider_is_built_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory.settings, "llm_provider", "anthropic")
    monkeypatch.setattr(factory.settings, "anthropic_api_key", "sk-ant-test")

    assert isinstance(factory.get_provider(), AnthropicProvider)


def test_unknown_provider_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory.settings, "llm_provider", "gpt5-turbo-ultra")

    with pytest.raises(ValueError, match="Unknown LLM provider"):
        factory.get_provider()
