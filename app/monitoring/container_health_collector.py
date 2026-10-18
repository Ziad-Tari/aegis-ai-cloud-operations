
from datetime import datetime, timezone

import docker

from app.core.container_models import ContainerHealthSnapshot


def collect_container_health(
    client=None,
) -> list[ContainerHealthSnapshot]:
    client = client or docker.from_env()
    snapshots = []

    try:
        containers = client.containers.list(all=True)

        for container in containers:
            attrs = container.attrs
            state = attrs.get("State", {})
            labels = attrs.get("Config", {}).get("Labels") or {}

            service = labels.get(
                "com.docker.compose.service",
                container.name,
            )

            health = state.get("Health") or {}

            snapshots.append(
                ContainerHealthSnapshot(
                    container_name=container.name,
                    service=service,
                    status=state.get("Status", container.status),
                    health_status=health.get("Status"),
                    restart_count=int(attrs.get("RestartCount", 0)),
                    observed_at=datetime.now(timezone.utc),
                ) 
            )

        return snapshots
    finally:
        client.close()
