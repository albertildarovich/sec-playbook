# AI Security Assistant

> **Production-oriented AI agent for automating vulnerability management and security operations.**

The system combines **LLM, RAG, tool calling and MCP** to assist security engineers with
vulnerability triage, threat analysis and remediation workflows.

**Security is treated as a first-class architectural concern:**
least privilege, RBAC, human approval, prompt-injection protection, data-loss prevention
and comprehensive audit logging.

## Core Principle

> The LLM never gets direct, uncontrolled access to infrastructure.
> The agent works through a small set of typed tools with RBAC, parameter validation,
> audit logging and human approval for dangerous operations.

## Capabilities

| Capability | Description |
|---|---|
| Vulnerability Triage | CVE → enrichment → impact → risk → priority → remediation (**Phase 1: `POST /triage`**) |
| RAG Knowledge Base | Grounded answers with source citations (CVE/CWE/OWASP/CIS/playbooks) |
| Security Agent | Controlled tool calling with typed schemas and RBAC |
| Jira Integration | Ticket lifecycle with human approval |
| MCP Server | Security tools exposed over the Model Context Protocol |
| Audit Logging | Every action logged as structured JSON |

## Security Controls

- **RBAC** — viewer / analyst / security_engineer / admin
- **Human approval** — for dangerous or irreversible actions
- **Prompt-injection defense** — untrusted-data framing + detection
- **Secret redaction** — deterministic DLP on outputs and logs
- **Tool allowlist** — no arbitrary code or HTTP execution
- **Audit logging** — full trail of user → tool → result

## Repository Layout

```
backend/       FastAPI application (API, models, schemas, core)
llm/           LLM provider abstraction (OpenAI / Anthropic / local)
agent/         Agent loop, tool registry, approval workflow
rag/           Ingestion + retrieval + knowledge base
mcp-server/    MCP server exposing security tools
integrations/  Jira / external integrations
security/      Security controls (redaction, validation, RBAC, injection detection)
evaluation/    Evaluation dataset + metrics
tests/         Test suite
```

## Roadmap

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Repo structure + docs skeleton | ✅ |
| 1 | LLM abstraction + triage API | ✅ |
| 2 | RAG knowledge base | planned |
| 3 | Security agent + tools | planned |
| 4 | Security hardening | planned |
| 5 | MCP server | planned |
| 6 | Jira lifecycle + evaluation | planned |

## Getting Started

```bash
# 1. Create and activate a virtual environment (Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API server (explicit interpreter: immune to `python` aliases/shim)
.venv/bin/python scripts/serve.py

# 4. Open Swagger UI
# http://127.0.0.1:8000/docs

# 5. Run the security-controls demo (offline)
PYTHONPATH=.:backend .venv/bin/python scripts/demo_security.py

# 6. Run the triage demo (offline, deterministic mock LLM)
PYTHONPATH=.:backend .venv/bin/python scripts/demo_triage.py

# 7. Run tests
.venv/bin/pytest
```

> **Why not a bare `uvicorn app.main:app --app-dir backend`?** The API package
> lives in `backend/app`, but the domain packages (`llm`, `security`, `agent`,
> `rag`, …) live in the repository root. uvicorn's console script puts only
> `--app-dir` on `sys.path` — unlike `python -m uvicorn`, it never adds the working
> directory — so the plain command fails with
> `ModuleNotFoundError: No module named 'llm'`. `scripts/serve.py` bootstraps both
> roots and `chdir`s to the project root so `.env` is found; the manual equivalent
> (run from the project root) is
> `PYTHONPATH=.:backend .venv/bin/uvicorn app.main:app --app-dir backend --port 8000`.
>
> The commands above call `.venv/bin/python` explicitly because activating the venv
> only prepends it to `PATH`: a `python` alias or shim (common on macOS, where
> `python` may point at the Xcode command-line tools) still takes precedence and
> pulls in an interpreter without the dependencies installed.

### Using a Local LLM (e.g. Qwen via LM Studio)

The triage pipeline talks to any OpenAI-compatible server on your machine — no cloud keys needed.

```bash
# 0. Find the exact model name LM Studio is serving
curl -s http://localhost:1234/v1/models

# 1. In LM Studio: load a Qwen instruct model and start the local server
#    (default endpoint: http://localhost:1234/v1)

# 2. Point the assistant at it — either export the variables...
export LLM_PROVIDER=local
export LLM_MODEL=qwen/qwen3.5-9b                 # the exact name from step 0
export LLM_BASE_URL=http://localhost:1234/v1
# ...or put the same names in a .env file (see .env.example; .env is gitignored)

# 3. Start the API
.venv/bin/python scripts/serve.py

# 4. Triage a finding
curl -s localhost:8000/triage -H 'content-type: application/json' -d '{
  "cve_id": "CVE-2024-1234",
  "asset_id": "prod-web-01",
  "severity": "high",
  "scanner": "trivy",
  "scanner_output": "nginx 1.25.3 is vulnerable to RCE"
}'
```

Want a zero-configuration run? `LLM_PROVIDER=mock` executes the whole pipeline
deterministically with no model server and no credentials — that is what the
tests and demos use.

### What's already runnable (Phase 1)

- `GET /health` — liveness probe.
- `POST /triage` — LLM-backed triage of a scanner finding, returning
  schema-validated JSON (type, CWE, CVSS, impact, priority, remediation, sources).
- `GET /docs` — Swagger UI (auto-generated from FastAPI).
- `scripts/serve.py` — dev server runner that puts both source roots
  (`backend/` + the repository root) on `sys.path` and loads `.env` from the
  project root. Use it instead of a bare `uvicorn app.main:app --app-dir backend`.
- `scripts/demo_security.py` — interactive demo of RBAC, secret redaction,
  prompt-injection detection, tool schema validation and the approval workflow.
- `scripts/demo_triage.py` — offline end-to-end demo of the triage pipeline.
- LLM providers: `openai`, `anthropic`, `local` (LM Studio/Ollama/vLLM) and `mock`.
- `pytest` — 87 passing tests covering security controls, domain models,
  LLM providers and the triage pipeline.

**Security controls active in Phase 1:** untrusted scanner output is size-capped
and framed with delimiters, prompt-injection signals are detected deterministically,
secrets in model output are redacted, and every triage step is audit-logged.


## Docs

- [Architecture](architecture.md)
- [Implementation](implementation.md)
- [Attack Scenarios](attack-scenarios.md)
- [Lessons Learned](lessons-learned.md)
- [Theory & Threat Model](../../../Knowledge/ai-security/README.md)
