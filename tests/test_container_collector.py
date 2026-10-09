from app.monitoring.container_collector import (
    collect_container_snapshots,
)


class FakePrometheusClient:
    def query(self, expression: str) -> list[dict]:
        if "rate(" in expression:
            return [
                {
                    "metric": {
                        "name": "aegis-demo",
                        "container_label_com_docker_compose_service": "demo",
                    },
                    "value": [1791520000, "0.25"],
                }
            ]

        return [
            {
                "metric": {
                    "name": "aegis-demo",
                    "container_label_com_docker_compose_service": "demo",
                },
                "value": [1791520000, "14889779"],
            },
            {
                "metric": {
                    "id": "/",
                },
                "value": [1791520000, "500000000"],
            },
        ]


def test_collects_and_combines_container_metrics():
    snapshots = collect_container_snapshots(
        FakePrometheusClient()
    )

    assert len(snapshots) == 1

    snapshot = snapshots[0]

    assert snapshot.container_name == "aegis-demo"
    assert snapshot.service == "demo"
    assert snapshot.cpu_cores == 0.25
    assert snapshot.memory_bytes == 14889779
    assert snapshot.memory_mib is not None
    assert snapshot.memory_mib > 14
    assert snapshot.observed_at.tzinfo is not None


def test_keeps_container_when_cpu_metric_is_missing():
    class MemoryOnlyClient:
        def query(self, expression: str) -> list[dict]:
            if "rate(" in expression:
                return []

            return [
                {
                    "metric": {
                        "name": "aegis-demo",
                        "container_label_com_docker_compose_service": "demo",
                    },
                    "value": [1791520000, "1048576"],
                }
            ]

    snapshots = collect_container_snapshots(
        MemoryOnlyClient()
    )

    assert len(snapshots) == 1
    assert snapshots[0].cpu_cores is None
    assert snapshots[0].memory_bytes == 1048576