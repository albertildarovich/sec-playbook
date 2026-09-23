# Lessons Learned

> Status: growing with the project. The LLM section is now confirmed in practice
> (Phase 1); RAG / Agents / Security sections remain forward-looking.

## Planned Sections

### LLM
- Structured output validation is a security control, not just a convenience.
- Provider abstraction pays off when swapping models.
- **Confirmed in Phase 1:** a single `LLMProvider` interface now runs on OpenAI,
  Anthropic, a local Qwen (LM Studio) and a deterministic mock.
  See [project lessons](../../../Experience/labs/ai-security-assistant/lessons-learned.md).

### RAG
- Grounding + citations reduce hallucinations but introduce injection surface.
- Permission filtering must happen before content reaches the model.

### Agents
- Tool allowlist + RBAC + approval beats any amount of prompt engineering.
- The agent is only as safe as its least-scoped tool.

### Security
- Prompt injection can't be "solved" by prompting — defense in depth required.
- Redaction must be deterministic and independent of the model.

### Process
- Threat model before code.
- Red-team after every phase, not at the end.
- **Two source roots bite at startup:** with the app in `backend/app` and the
  domain packages in the root, a stock `uvicorn … --app-dir backend` cannot
  import `llm` — bootstrap both paths in a runner script (`scripts/serve.py`).
  Tests passing says nothing about the documented start command.

## Related

- [Attack Scenarios](attack-scenarios.md)
- [Implementation](implementation.md)
