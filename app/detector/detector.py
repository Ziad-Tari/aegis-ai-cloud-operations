from app.core.models import (
    Incident,
    ProcessEvidence,
    ProcessSnapshot,
    SystemSnapshot,
)

CPU_THRESHOLD = 2.5
HIGH_CPU_REQUIRED_COUNT = 3
CPU_ANOMALY_DIFFERENCE =-30.0
MIN_CPU_HISTORY = 3

_high_cpu_count = 0
    
def detect_cpu_incident(
    snapshot: SystemSnapshot,
    processes: list[ProcessSnapshot],
    average_cpu: float,
    history_size: int,
) -> Incident | None:

    global _high_cpu_count

    if history_size < MIN_CPU_HISTORY:
        _high_cpu_count = 0
        return None

    if (
    snapshot.cpu_percent <= CPU_THRESHOLD
    or snapshot.cpu_percent - average_cpu < CPU_ANOMALY_DIFFERENCE
    ):
        _high_cpu_count = 0
        return None

    _high_cpu_count += 1

    if _high_cpu_count < HIGH_CPU_REQUIRED_COUNT:
        return None

    if _high_cpu_count == HIGH_CPU_REQUIRED_COUNT:
        top_processes = sorted(
            processes,
            key=lambda process: process.cpu_percent,
            reverse=True,
        )[:3]

        evidence = [
            ProcessEvidence(
                pid=process.pid,
                name=process.name,
                cpu_percent=process.cpu_percent,
                memory_percent=process.memory_percent,
            )
            for process in top_processes
        ]

        return Incident(
            timestamp=snapshot.timestamp,
            type="HIGH_CPU",
            message=f"System CPU usage is {snapshot.cpu_percent:.1f}%",
            evidence=evidence,
        )

    return None