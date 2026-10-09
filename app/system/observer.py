
import time
from datetime import datetime

import psutil

from app.core.models import SystemSnapshot, ProcessSnapshot


PROCESS_ERRORS = (psutil.Error, OSError)


def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=1)


def get_memory_usage() -> float:
    return psutil.virtual_memory().percent


def get_disk_usage() -> float:
    return psutil.disk_usage("C:\\").percent


def get_system_snapshot() -> SystemSnapshot:
    return SystemSnapshot(
        timestamp=datetime.now(),
        cpu_percent=get_cpu_usage(),
        memory_percent=get_memory_usage(),
        disk_percent=get_disk_usage(),
    )


def get_running_processes() -> list[ProcessSnapshot]:
    processes = []

    # First pass: initialize psutil's per-process CPU measurements.
    for process in psutil.process_iter(["pid", "name"]):
        try:
            if process.info["pid"] == 0:
                continue

            process.cpu_percent(interval=None)
            processes.append(process)

        except PROCESS_ERRORS:
            continue

    # Measure CPU usage across a short interval.
    time.sleep(0.1)

    snapshots = []

    # Second pass: collect metrics independently for each process.
    for process in processes:
        try:
            snapshots.append(
                ProcessSnapshot(
                    pid=process.pid,
                    name=process.info.get("name") or "unknown",
                    cpu_percent=process.cpu_percent(interval=None),
                    memory_percent=process.memory_percent(),
                )
            )
        except PROCESS_ERRORS:
            # A process may disappear or deny access between reads.
            continue

    return snapshots