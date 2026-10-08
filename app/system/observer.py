import psutil
import time
from datetime import datetime
from app.core.models import SystemSnapshot, ProcessSnapshot

def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=1)


def get_memory_usage() -> float:
    memory = psutil.virtual_memory()
    return memory.percent


def get_disk_usage() -> float:
    disk = psutil.disk_usage("C:\\")
    return disk.percent


def get_system_snapshot() -> SystemSnapshot:
    return SystemSnapshot(
        timestamp=datetime.now(),
        cpu_percent=get_cpu_usage(),
        memory_percent=get_memory_usage(),
        disk_percent=get_disk_usage(),
    )


def get_running_processes() -> list[ProcessSnapshot]:
    processes = []

    # First snapshot: establish CPU baselines
    for process in psutil.process_iter(["pid", "name"]):
        try:
            if process.info["pid"] == 0:
                continue

            process.cpu_percent(interval=None)
            processes.append(process)

        except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
            continue

    # Wait once for the measurement interval
    time.sleep(0.1)

    # Second snapshot: calculate CPU usage
    snapshots = []

    for process in processes:
        try:
            name = process.info["name"]
            cpu_percent = process.cpu_percent(interval=None)
            memory_percent = process.memory_percent()

            snapshots.append(
                ProcessSnapshot(
                    pid=process.pid,
                    name=name,
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                )
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
            continue

    return snapshots

