
from pydantic import BaseModel
from datetime import datetime

class ProcessEvidenceResponse(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


class ContainerEvidenceResponse(BaseModel):
    container_name: str
    service: str
    metric_type: str
    observed_value: float
    threshold: float
    unit: str


class InvestigationResponse(BaseModel):
    incident_type: str
    summary: str
    findings: list[str]


class IncidentResponse(BaseModel):
    id: int
    timestamp: datetime
    incident_type: str
    message: str
    evidence: list[
        ProcessEvidenceResponse | ContainerEvidenceResponse
    ]
    investigation: InvestigationResponse | None = None