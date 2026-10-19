from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SystemSnapshot:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float


@dataclass
class ProcessSnapshot:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


@dataclass
class ProcessEvidence:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float

@dataclass
class ContainerEvidence:
    container_name: str
    service: str
    metric_type: str
    observed_value: float
    threshold: float
    unit: str


@dataclass
class ContainerLogEvidence:
    container_name: str
    service: str
    lines: list[str]
    truncated: bool


@dataclass
class ContainerHealthEvidence:
    container_name: str
    service: str
    status: str
    health_status: str | None
    restart_count: int
    details: str


@dataclass
class InvestigationClaim:
    text: str
    evidence_references: list[str] = field(default_factory=list)
    source: str = "unspecified"


@dataclass
class Incident:
    timestamp: datetime
    type: str
    message: str
    evidence: list[ProcessEvidence | ContainerEvidence | ContainerHealthEvidence | ContainerLogEvidence]

@dataclass
class Investigation:
    incident_type: str
    summary: str
    findings: list[str]
    possible_causes: list[str] = field(default_factory=list)
    evidence_references: list[str] = field(default_factory=list)
    confidence: str = "low"
    confidence_rationale: str = (
        "No confidence assessment was provided."
    )
    next_steps: list[str] = field(default_factory=list)
    
    observations: list[InvestigationClaim] = field(default_factory=list)
    hypotheses: list[InvestigationClaim] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)


@dataclass
class CpuSample:
    timestamp: datetime
    cpu_percent: float





