
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
# from pydantic import BaseModel

from app.storage.incident_store import (
    get_incident,
    initialize_database,
    list_incidents,
    save_investigation,
)
from app.core.schemas import IncidentResponse, ProcessEvidenceResponse, InvestigationResponse
from app.core.models import Investigation
from app.investigator.ai import (
    AIProviderError,
    AIResponseError,
    investigate_incident,
)


app = FastAPI(
    title="Aegis API",
    description="Infrastructure incident monitoring and investigation",
    version="0.1.0",
)


# class ProcessEvidenceResponse(BaseModel):
#     pid: int
#     name: str
#     cpu_percent: float
#     memory_percent: float


# class InvestigationResponse(BaseModel):
#     incident_type: str
#     summary: str
#     findings: list[str]


# class IncidentResponse(BaseModel):
#     id: int
#     timestamp: datetime
#     incident_type: str
#     message: str
#     evidence: list[ProcessEvidenceResponse]
#     investigation: InvestigationResponse | None = None


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aegis-api"}


@app.get("/incidents", response_model=list[IncidentResponse])
def read_incidents(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    return list_incidents(limit=limit, offset=offset)


@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
def read_incident(incident_id: int) -> dict:
    incident = get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident



@app.post(
    "/incidents/{incident_id}/investigate",
    response_model=IncidentResponse,
)
def investigate_stored_incident(incident_id: int) -> dict:
    incident = get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    try:
        investigation = investigate_incident(incident)
    except AIProviderError as exc:
        raise HTTPException(
            status_code=503,
            detail="AI investigation service is unavailable.",
        ) from exc
    except AIResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail="AI returned an invalid investigation report.",
        ) from exc

    saved = save_investigation(incident_id, investigation)

    if not saved:
        raise HTTPException(
            status_code=404,
            detail="Incident no longer exists",
        )

    updated_incident = get_incident(incident_id)

    if updated_incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found after investigation",
        )

    return updated_incident