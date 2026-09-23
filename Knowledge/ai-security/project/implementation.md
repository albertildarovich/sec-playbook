# Implementation Notes

> Status: Phase 1 landed (LLM abstraction + structured triage, `POST /triage`).
> Phases 2–6 still planned.

## Phase Tracker

| Phase | Scope | Key files | Status |
|---|---|---|---|
| 0 | Repo structure + docs skeleton | — | ✅ |
| 1 | LLM abstraction, structured triage output | `llm/*.py`, `backend/app/services/triage.py`, `backend/app/api/routes/triage.py` | ✅ |
| 2 | RAG ingestion + retrieval, knowledge seed | `rag/*.py` | planned |
| 3 | Agent loop, tools, tool registry | `agent/*.py` | planned |
| 4 | Security controls + audit | `security/*.py`, `backend/app/core/*` | planned |
| 5 | MCP server | `mcp-server/*.py` | planned |
| 6 | Jira integration + evaluation | `integrations/*.py`, `evaluation/*.py` | planned |

## Phase 1 — Notable Decisions

- **One provider interface, four providers.** `openai`, `anthropic`, `local`
  (any OpenAI-compatible server: LM Studio / Ollama / vLLM) and `mock` (offline,
  deterministic). Everything above `llm/` is provider-agnostic.
- **Local-first is a real option.** A Qwen model served by LM Studio on
  `http://localhost:1234/v1` runs the exact same triage pipeline as a hosted
  model — useful for private/offline development and for demos without keys.
- **Two source roots: the app in `backend/app`, the domain packages in the root.**
  pytest sees both via `pythonpath` in `pyproject.toml`, but uvicorn's console
  script only honours `--app-dir`, so a bare `uvicorn app.main:app --app-dir
  backend` cannot import `llm`. `scripts/serve.py` bootstraps both paths and
  `chdir`s to the project root (so `.env` is found) before starting uvicorn.
- **Structured output via prompt + Pydantic, not `response_format`.** The JSON
  schema is embedded in the prompt and the reply validated with `model_validate`;
  one retry with a correction prompt handles malformed output. Portable across
  providers, including small local models.
- **Security controls are deterministic.** Scanner output is capped and framed,
  prompt-injection detection sets `injection_flagged` (the model's value is
  overwritten), and secrets in model output are redacted post-validation.
- **SDK-free testability.** Provider SDKs are imported lazily and clients are
  injectable, so the whole suite runs offline.

## Conventions

- Python 3.11+, strict type hints.
- Pydantic v2 models for all boundaries (API, tools, agent loop).
- Structured JSON logging via `structlog`.
- Every external call goes through `httpx` async client.
- Tests: `pytest` + `pytest-asyncio`; security tests in `tests/test_security/`.

## What "Done" Means Per Phase

- Phase 1: `POST /triage` returns schema-validated JSON for a real CVE.
- Phase 2: query against seeded knowledge base returns chunks with sources.
- Phase 3: end-to-end CVE → enrichment → risk → ticket proposal flow.
- Phase 4: red-team tests pass (injection, leakage, escalation).
- Phase 5: MCP client (MCP Inspector) can call security tools.
- Phase 6: evaluation report with detection rates.

## Known Constraints / Assumptions

- LLM API keys are provided via environment variables (never committed).
- Jira integration targets a Jira-like API (mockable for tests).
- pgvector runs in Docker Compose for local development.
- The project targets demonstration + evaluation, not production workload scale.

## Related

- [Architecture](architecture.md)
- [Attack Scenarios](attack-scenarios.md)
