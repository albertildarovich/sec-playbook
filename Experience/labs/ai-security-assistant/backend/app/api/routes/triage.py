"""Triage API routes.

`POST /triage` is the Phase 1 deliverable: it runs the LLM triage pipeline and
returns a schema-validated `TriageResponse`. RBAC/authentication lands in Phase 4.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage import TriageError, TriageService
from security.output_validation import OutputValidationError

router = APIRouter(tags=["triage"])


def get_triage_service() -> TriageService:
    """Build the triage service using the configured LLM provider.

    Overridden in tests via `app.dependency_overrides` to inject a mock provider.
    """
    return TriageService()


@router.post(
    "/triage",
    response_model=TriageResponse,
    summary="Triage a vulnerability finding",
    description=(
        "Enrich a scanner finding with an LLM-backed assessment "
        "(type, CWE, CVSS, impact, priority, remediation) and return "
        "schema-validated JSON. Model output passes deterministic DLP checks."
    ),
)
async def triage(
    request: TriageRequest,
    service: TriageService = Depends(get_triage_service),
) -> TriageResponse:
    try:
        return await service.triage(request)
    except TriageError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except OutputValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
