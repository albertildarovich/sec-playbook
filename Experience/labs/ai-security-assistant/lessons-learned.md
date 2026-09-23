# Lessons Learned

> Status: filled in as phases land (Phase 1 done).

## LLM

- **Provider abstraction before the first prompt.** Keeping everything on a single
  `LLMProvider` interface paid off immediately: the same triage service runs on
  OpenAI, Anthropic, a local Qwen via LM Studio and a deterministic mock, with no
  branching in the business logic.
- **Lazy-import the provider SDKs.** Importing `openai`/`anthropic` inside the
  provider keeps the package importable — and unit-testable — without the SDKs
  installed, and lets `local`/`mock` run with zero dependencies.
- **Inject the client, don't construct it.** Providers accept a `client=` argument,
  so tests exercise the real message/tool-call mapping with lightweight fakes:
  no network, no SDK, no flakiness.
- **Never let the model make security decisions.** `injection_flagged` is computed
  by the deterministic detector and written over whatever the model returned.
- **Prompt-based JSON beats vendor-specific structured output.** Asking for JSON
  against the Pydantic schema and validating with `model_validate` works across
  every provider — including small local models — while `response_format` and
  tool-schema tricks are provider-specific. One retry recovers most malformed
  replies.
- **A local model is enough for triage.** Qwen served by LM Studio handles
  single-finding triage well; the pipeline is byte-for-byte the same as with
  hosted providers, which made local development cheap and private.
- **Latency, not quality, is what bites with local models.** A 9B "thinking"
  model (`qwen/qwen3.5-9b` via LM Studio) needed ~60 s for one triage call on
  this laptop, so HTTP clients must use generous timeouts and the API should not
  be treated as interactive at that size.

## RAG
- _(to be added in Phase 2)_

## Agent
- _(to be added in Phase 3)_

## Security
- _(to be added in Phase 4)_

## Process
- Threat model before code.
- Red-team after every phase, not at the end.
- **Two source roots are a startup trap.** With the app in `backend/app` and the
  domain packages (`llm`, `security`, `agent`, `rag`) in the repository root,
  `uvicorn app.main:app --app-dir backend` fails with
  `ModuleNotFoundError: No module named 'llm'`: uvicorn's console script adds
  only `--app-dir` to `sys.path` (pytest covered both roots via `pythonpath` in
  `pyproject.toml`, which is why tests were green while the server was not).
  Fixed with `scripts/serve.py`, which bootstraps both paths, exports
  `PYTHONPATH` for uvicorn's reload subprocess and `chdir`s to the project root
  so `.env` is always found.
- **Verify the documented command, not just the code.** The README/`Getting
  Started` command had never been executed end-to-end; the very first `uvicorn`
  run surfaced the import error.

## Related

- [Attack Scenarios](attack-scenarios.md)
- [ai-security: lessons learned](../../../Knowledge/ai-security/project/lessons-learned.md)
