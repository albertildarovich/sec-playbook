"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes.triage import router as triage_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="AI Security Assistant — vulnerability triage, risk assessment "
    "and remediation workflows with LLM, RAG and controlled tool access.",
)

app.include_router(triage_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "service": settings.app_name}
