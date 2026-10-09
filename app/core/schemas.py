
from pydantic import BaseModel
from datetime import datetime

class ProcessEvidenceResponse(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


class InvestigationResponse(BaseModel):
    incident_type: str
    summary: str
    findings: list[str]


class IncidentResponse(BaseModel):
    id: int
    timestamp: datetime
    incident_type: str
    message: str
    evidence: list[ProcessEvidenceResponse]
    investigation: InvestigationResponse | None = None