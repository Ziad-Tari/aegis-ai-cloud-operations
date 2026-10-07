import time

from app.system.observer import (
    get_system_snapshot,
    get_running_processes,
)
from app.detector.detector import detect_cpu_incident
from app.investigator.cpu import investigate_cpu_incident

def monitor(interval: float = 2.0):
    while True:
        snapshot = get_system_snapshot()
        processes = get_running_processes()

        incident = detect_cpu_incident(snapshot, processes)

        if incident:
            print("\n🚨 INCIDENT DETECTED")
            print(incident)

            investigation = investigate_cpu_incident(incident)

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