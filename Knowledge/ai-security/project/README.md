# AI Security Project — Hands-On Implementation

> The theory from `ai-security/` is applied in a working project:
> **[`Experience/labs/ai-security-assistant/`](../../../Experience/labs/ai-security-assistant/)**

## What This Project Is

A production-oriented **AI Security Assistant** for vulnerability management:

- Vulnerability triage with LLM + structured output
- RAG knowledge base (CVE, CWE, OWASP, CIS, playbooks) with source citations
- Security agent with controlled tool calling, RBAC and human approval
- Jira integration for the ticket lifecycle
- MCP server exposing security tools to any MCP client
- Security hardening: prompt injection, data leakage, excessive agency
- Audit logging for every action
- Evaluation suite with attack scenarios

## Phases

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Repo structure + docs skeleton | ✅ done |
| 1 | LLM abstraction + triage API | ✅ done |
| 2 | RAG knowledge base | planned |
| 3 | Security agent + tools | planned |
| 4 | Security hardening (injection, RBAC, redaction, audit) | planned |
| 5 | MCP server | planned |
| 6 | Jira lifecycle + evaluation | planned |

## Project Docs

- [Architecture](architecture.md)
- [Implementation](implementation.md)
- [Attack Scenarios](attack-scenarios.md)
- [Lessons Learned](lessons-learned.md)

## Related

- [ai-security README](../README.md)
