import time

from app.system.observer import (
    get_system_snapshot,
    get_running_processes,
)


def monitor(interval: float = 2.0):
    while True:
        snapshot = get_system_snapshot()
        processes = get_running_processes()

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