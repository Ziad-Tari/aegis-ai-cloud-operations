from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContainerSnapshot:
    container_name: str
    service: str
    cpu_cores: float | None
    memory_bytes: int | None
    observed_at: datetime

    @property
    def memory_mib(self) -> float | None:
        if self.memory_bytes is None:
            return None

        return self.memory_bytes / (1024 ** 2)