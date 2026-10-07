from app.core.models import Incident, ProcessSnapshot, SystemSnapshot


CPU_THRESHOLD = 5.0
HIGH_CPU_REQUIRED_COUNT = 3

_high_cpu_count = 0
    
def detect_cpu_incident(
    snapshot: SystemSnapshot,
    processes: list[ProcessSnapshot],
) -> Incident | None:
    global _high_cpu_count

    if snapshot.cpu_percent <= CPU_THRESHOLD:
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
            f"{process.name} (PID {process.pid}) → {process.cpu_percent:.1f}% CPU"
            for process in top_processes
        ]

        return Incident(
            timestamp=snapshot.timestamp,
            type="HIGH_CPU",
            message=f"System CPU usage is {snapshot.cpu_percent:.1f}%",
            evidence=evidence,
        )

    return None