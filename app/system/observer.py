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

    # First snapshot: establish CPU baseline
    for process in psutil.process_iter(
        ["pid", "name", "memory_percent"]
    ):
        try:
            if process.info["pid"] == 0:
                continue

            process.cpu_percent(interval=None)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Wait once for the measurement interval
    
    time.sleep(0.1)

    # Second snapshot: calculate CPU usage
    for process in psutil.process_iter(
        ["pid", "name", "memory_percent"]
    ):
        try:
            if process.info["pid"] == 0:
                continue

            cpu_percent = process.cpu_percent(interval=None)

            processes.append(
                ProcessSnapshot(
                    pid=process.info["pid"],
                    name=process.info["name"],
                    cpu_percent=cpu_percent,
                    memory_percent=process.info["memory_percent"],
                )
            )           

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes