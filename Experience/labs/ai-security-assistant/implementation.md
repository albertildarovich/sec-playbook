# Implementation

> Status: Phase 1 complete (LLM abstraction + structured triage). Phase 2 (RAG) next.

## Phases

| Phase | Scope | Status |
|---|---|---|
| 0 | Repo structure + docs skeleton | ✅ |
| 1 | LLM abstraction + structured triage | ✅ |
| 2 | RAG ingestion + retrieval | planned |
| 3 | Agent loop + tools | planned |
| 4 | Security controls + audit | planned |
| 5 | MCP server | planned |
| 6 | Jira + evaluation | planned |

## Phase 1 — Delivered

| Component | File | What it does |
|---|---|---|
| Provider interface | `llm/base.py` | Vendor-neutral `LLMProvider.complete()` |
| OpenAI provider | `llm/openai.py` | Chat completions + tool calls; lazy SDK import; injectable client |
| Anthropic provider | `llm/anthropic.py` | Messages API + tool use; system-prompt extraction |
| Local provider | `llm/local.py` | Any OpenAI-compatible server (LM Studio / Ollama / vLLM) |
| Mock provider | `llm/mock.py` | Deterministic offline responses for tests and demos |
| Factory | `llm/factory.py` | `LLM_PROVIDER` → provider (openai \| anthropic \| local \| mock) |
| Triage service | `backend/app/services/triage.py` | Prompt + JSON schema → `TriageResponse`, validate, retry, redact |
| Triage API | `backend/app/api/routes/triage.py` | `POST /triage` |
| Offline demo | `scripts/demo_triage.py` | End-to-end triage run without credentials |
| Dev server | `scripts/serve.py` | Puts both source roots on `sys.path`, loads `.env`, runs uvicorn |

### Design notes

- **Structured output is prompt-based, not vendor-specific.** The service embeds
  `TriageResponse.model_json_schema()` in the system prompt, then validates the
  reply with `model_validate`. One retry with a correction prompt recovers from
  malformed replies. This works identically on hosted and local models.
- **Deterministic controls never depend on the model.** `injection_flagged` is
  written by the injection detector, not taken from the model's answer; secrets in
  `impact`/`remediation`/`cwe`/source titles are redacted after validation.
- **Provider SDKs are imported lazily.** `local` and `mock` work with no SDKs
  installed; providers accept a `client=` argument so tests use fakes, not network.

## Conventions

- Python 3.11+, type hints everywhere.
- Pydantic v2 for every boundary.
- `structlog` JSON logging.
- `httpx` async client for external calls.
- `pytest` + `pytest-asyncio` for tests.

## Environment Variables

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | `openai` \| `anthropic` \| `local` \| `mock` |
| `LLM_MODEL` | Model name (e.g. `gpt-4o-mini`, `qwen2.5-coder-7b-instruct`) |
| `LLM_BASE_URL` | Base URL for OpenAI-compatible endpoints (LM Studio: `http://localhost:1234/v1`) |
| `LLM_API_KEY` | Key for OpenAI-compatible endpoints (local servers ignore it) |
| `OPENAI_API_KEY` | OpenAI provider credential |
| `ANTHROPIC_API_KEY` | Anthropic provider credential |
| `DATABASE_URL` | PostgreSQL + pgvector connection (Phase 2) |
| `JIRA_URL`, `JIRA_TOKEN` | Jira integration (Phase 6) |
| `MCP_AUTH_TOKEN` | MCP server auth (Phase 5) |
| `AGENT_MAX_TURNS` | Agent loop iteration cap (Phase 3) |

## Related

- [Architecture](architecture.md)
- [ai-security: implementation notes](../../../Knowledge/ai-security/project/implementation.md)
