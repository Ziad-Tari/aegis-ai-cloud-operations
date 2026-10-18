
import time

from app.core.container_models import ContainerHealthIncident
from app.core.models import ContainerHealthEvidence, Incident, ContainerLogEvidence
from app.detector.container_health_detector import ContainerHealthDetector
from app.monitoring.container_health_collector import (
    collect_container_health,
)
from app.storage.incident_store import (
    initialize_database,
    save_incident,
)
from app.monitoring.container_log_collector import collect_container_logs

def save_health_incident(
    health_incident: ContainerHealthIncident,
) -> int:
    incident = Incident(
        timestamp=health_incident.observed_at,
        type=health_incident.incident_type,
        message=health_incident.message,
        evidence=[
            ContainerHealthEvidence(
                container_name=health_incident.container_name,
                service=health_incident.service,
                status=health_incident.status,
                health_status=health_incident.health_status,
                restart_count=health_incident.restart_count,
                details=health_incident.message,
            )
        ],
    )



    try:
        log_snapshot = collect_container_logs(
            health_incident.container_name,
            tail=50,
        )

        incident.evidence.append(
            ContainerLogEvidence(
                container_name=log_snapshot.container_name,
                service=log_snapshot.service,
                lines=log_snapshot.lines,
                truncated=log_snapshot.truncated,
            )
        )
    except Exception as exc:
        print(
            f"Could not collect logs for "
            f"{health_incident.container_name}: {exc}"
        )

    return save_incident(incident)



def run_health_monitor(interval: float = 5.0) -> None:
    initialize_database()
    detector = ContainerHealthDetector()

    print("Aegis container health monitor started.")

    while True:
        try:
            snapshots = collect_container_health()

            for incident in detector.detect(snapshots):
                incident_id = save_health_incident(incident)
                print("\nCONTAINER HEALTH INCIDENT")
                print(incident)
                print(f"SAVED INCIDENT | ID: {incident_id}")

        except Exception as exc:
            # Keep the monitor alive if Docker is temporarily unavailable.
            print(f"Container health monitoring error: {exc}")

        time.sleep(interval)


if __name__ == "__main__":
    run_health_monitor()
