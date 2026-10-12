
import time

from app.core.models import ContainerEvidence, Incident
from app.detector.container_detector import ContainerIncidentDetector
from app.monitoring.container_collector import (
    collect_container_snapshots,
)
from app.storage.incident_store import (
    initialize_database,
    save_incident,
)


def save_container_incident(container_incident) -> int:
    metric_type = (
        "cpu"
        if container_incident.incident_type == "HIGH_CONTAINER_CPU"
        else "memory"
    )

    incident = Incident(
        timestamp=container_incident.observed_at,
        type=container_incident.incident_type,
        message=container_incident.message,
        evidence=[
            ContainerEvidence(
                container_name=container_incident.container_name,
                service=container_incident.service,
                metric_type=metric_type,
                observed_value=container_incident.observed_value,
                threshold=container_incident.threshold,
                unit=container_incident.unit,
            )
        ],
    )

    return save_incident(incident)


def run_container_monitor(interval: float = 5.0) -> None:
    initialize_database()
    detector = ContainerIncidentDetector()

    print("Aegis container monitor started.")

    while True:
        try:
            snapshots = collect_container_snapshots()
            incidents = detector.detect(snapshots)

            for incident in incidents:
                incident_id = save_container_incident(incident)

                print("\nCONTAINER INCIDENT DETECTED")
                print(incident)
                print(f"SAVED INCIDENT | ID: {incident_id}")

        except (OSError, RuntimeError, ValueError, KeyError) as exc:
            print(f"Container monitoring error: {exc}")

        time.sleep(interval)


if __name__ == "__main__":
    run_container_monitor()
