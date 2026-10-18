from dataclasses import dataclass
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

@dataclass
class CpuSample:
    timestamp: datetime
    cpu_percent: float





