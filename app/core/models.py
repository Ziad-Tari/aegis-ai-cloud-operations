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