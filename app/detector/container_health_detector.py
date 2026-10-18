
from app.core.container_models import (
    ContainerHealthIncident,
    ContainerHealthSnapshot,
)


class ContainerHealthDetector:
    def __init__(self):
        self._previous_status: dict[tuple[str, str], str] = {}
        self._previous_health: dict[tuple[str, str], str | None] = {}
        self._last_restart_count: dict[tuple[str, str], int] = {}
        self._active: set[tuple[str, str, str]] = set()

    def detect(
        self,
        snapshots: list[ContainerHealthSnapshot],
    ) -> list[ContainerHealthIncident]:
        incidents = []

        for snapshot in snapshots:
            key = (snapshot.container_name, snapshot.service)
            previous_status = self._previous_status.get(key)
            previous_health = self._previous_health.get(key)
            previous_restart_count = self._last_restart_count.get(key)

            # A container that was already stopped at startup establishes
            # a baseline; it does not automatically create a new incident.
            stopped_now = snapshot.status != "running"
            stopped_before = (
                previous_status is not None
                and previous_status != "running"
            )

            if stopped_now and previous_status == "running":
                incidents.append(
                    ContainerHealthIncident(
                        incident_type="CONTAINER_STOPPED",
                        container_name=snapshot.container_name,
                        service=snapshot.service,
                        status=snapshot.status,
                        health_status=snapshot.health_status,
                        restart_count=snapshot.restart_count,
                        message=(
                            f"{snapshot.container_name} changed from "
                            f"running to {snapshot.status}."
                        ),
                        observed_at=snapshot.observed_at,
                    )
                )

            # Only report an unhealthy transition for a running container.
            if (
                snapshot.status == "running"
                and snapshot.health_status == "unhealthy"
                and previous_health != "unhealthy"
            ):
                incidents.append(
                    ContainerHealthIncident(
                        incident_type="CONTAINER_UNHEALTHY",
                        container_name=snapshot.container_name,
                        service=snapshot.service,
                        status=snapshot.status,
                        health_status=snapshot.health_status,
                        restart_count=snapshot.restart_count,
                        message=(
                            f"{snapshot.container_name} is running "
                            "but its health check is unhealthy."
                        ),
                        observed_at=snapshot.observed_at,
                    )
                )

            # Restart count is cumulative. Establish a baseline on first
            # observation so an old restart is not reported as a new one.
            if (
                previous_restart_count is not None
                and snapshot.restart_count > previous_restart_count
            ):
                incidents.append(
                    ContainerHealthIncident(
                        incident_type="CONTAINER_RESTARTED",
                        container_name=snapshot.container_name,
                        service=snapshot.service,
                        status=snapshot.status,
                        health_status=snapshot.health_status,
                        restart_count=snapshot.restart_count,
                        message=(
                            f"{snapshot.container_name} restart count "
                            f"increased from {previous_restart_count} "
                            f"to {snapshot.restart_count}."
                        ),
                        observed_at=snapshot.observed_at,
                    )
                )

            self._previous_status[key] = snapshot.status
            self._previous_health[key] = snapshot.health_status
            self._last_restart_count[key] = snapshot.restart_count

        return incidents
