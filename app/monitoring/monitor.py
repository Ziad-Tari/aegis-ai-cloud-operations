import time

from app.system.observer import (
    get_system_snapshot,
    get_running_processes,
)
from app.detector.detector import detect_cpu_incident
from app.investigator.cpu import investigate_cpu_incident


from app.core.models import CpuSample
from app.monitoring.cpu_analysis import calculate_average_cpu


def monitor(interval: float = 2.0):
    cpu_history: list[CpuSample] = []
    while True:
        snapshot = get_system_snapshot()

        average_cpu = calculate_average_cpu(cpu_history)

        cpu_history.append(
            CpuSample(
                timestamp=snapshot.timestamp,
                cpu_percent=snapshot.cpu_percent,
            )
        )

        if len(cpu_history) > 10:
            cpu_history.pop(0)

        print(f"CPU HISTORY: {len(cpu_history)} samples")

        cpu_difference = snapshot.cpu_percent - average_cpu

        print(
            f"RECENT CPU AVERAGE: {average_cpu:.1f}% "
            f"| DIFFERENCE: {cpu_difference:+.1f}%"
        )
        processes = get_running_processes()

        incident = detect_cpu_incident(
            snapshot,
            processes,
            average_cpu,
            len(cpu_history),
        )

        if incident:
            print("\n🚨 INCIDENT DETECTED")
            print(incident)

            investigation = investigate_cpu_incident(incident, snapshot)

            print("\n🔎 INVESTIGATION")
            print(investigation)

        processes.sort(
            key=lambda process: process.cpu_percent,
            reverse=True,
        )

        print("\nSYSTEM")
        print(snapshot)

        print("\nTOP CPU PROCESSES")

        for process in processes[:5]:
            print(process)

        print("\n" + "-" * 60)

        time.sleep(interval)