from datetime import datetime, timezone

from app.core.container_models import ContainerSnapshot
from app.monitoring.prometheus_client import PrometheusClient


CPU_QUERY = """
sum by (name, container_label_com_docker_compose_service) (
    rate(
        container_cpu_usage_seconds_total{
            container_label_com_docker_compose_service!=""
        }[1m]
    )
)
"""

MEMORY_QUERY = """
container_memory_working_set_bytes{
    container_label_com_docker_compose_service!=""
}
"""


def _series_key(metric: dict) -> tuple[str, str] | None:
    name = metric.get("name")
    service = metric.get(
        "container_label_com_docker_compose_service"
    )

    if not name or not service:
        return None

    return name, service


def _series_value(series: dict) -> float:
    return float(series["value"][1])


def collect_container_snapshots(
    client: PrometheusClient | None = None,
) -> list[ContainerSnapshot]:
    client = client or PrometheusClient()

    cpu_by_container = {}
    for series in client.query(CPU_QUERY):
        key = _series_key(series["metric"])
        if key is not None:
            cpu_by_container[key] = _series_value(series)

    memory_by_container = {}
    for series in client.query(MEMORY_QUERY):
        key = _series_key(series["metric"])
        if key is not None:
            memory_by_container[key] = int(
                _series_value(series)
            )

    container_keys = set(cpu_by_container) | set(
        memory_by_container
    )
    observed_at = datetime.now(timezone.utc)

    snapshots = [
        ContainerSnapshot(
            container_name=name,
            service=service,
            cpu_cores=cpu_by_container.get((name, service)),
            memory_bytes=memory_by_container.get((name, service)),
            observed_at=observed_at,
        )
        for name, service in sorted(container_keys)
    ]

    return snapshots


if __name__ == "__main__":
    for snapshot in collect_container_snapshots():
        print(
            f"{snapshot.container_name} "
            f"| service={snapshot.service} "
            f"| CPU={snapshot.cpu_cores} cores "
            f"| Memory={snapshot.memory_mib} MiB"
        )