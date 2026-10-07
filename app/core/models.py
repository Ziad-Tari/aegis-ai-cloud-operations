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
class Incident:
    timestamp: datetime
    type: str
    message: str
    evidence: list[str]

@dataclass
class Investigation:
    incident_type: str
    summary: str
    findings: list[str]

@dataclass
class CpuSample:
    timestamp: datetime
    cpu_percent: float