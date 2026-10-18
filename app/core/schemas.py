
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
    possible_causes: list[str] = []
    evidence_references: list[str] = []
    confidence: str = "low"
    confidence_rationale: str = (
        "No confidence assessment was provided."
    )
    next_steps: list[str] = []

class ContainerHealthEvidenceResponse(BaseModel):
    container_name: str
    service: str
    status: str
    health_status: str | None
    restart_count: int
    details: str

class ContainerLogEvidenceResponse(BaseModel):
    container_name: str
    service: str
    lines: list[str]
    truncated: bool

class IncidentResponse(BaseModel):
    id: int
    timestamp: datetime
    incident_type: str
    message: str
    evidence: list[
        ProcessEvidenceResponse | ContainerEvidenceResponse | ContainerHealthEvidenceResponse | ContainerLogEvidenceResponse
    ]
    investigation: InvestigationResponse | None = None



