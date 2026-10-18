
from datetime import datetime

from app.core.container_models import ContainerLogSnapshot
from app.monitoring.container_log_collector import (
    collect_container_logs,
)


class FakeContainer:
    name = "aegis-demo"

    attrs = {
        "Config": {
            "Labels": {
                "com.docker.compose.service": "demo",
            }
        }
    }

    def logs(self, tail, timestamps):
        assert tail == 2
        assert timestamps is True
        return (
            b"2026-10-17T12:00:00Z first line\n"
            b"2026-10-17T12:00:01Z second line\n"
        )


class FakeContainers:
    def get(self, name):
        assert name == "aegis-demo"
        return FakeContainer()


class FakeClient:
    containers = FakeContainers()


def test_collects_timestamped_container_logs():
    result = collect_container_logs(
        "aegis-demo",
        tail=2,
        client=FakeClient(),
    )

    assert isinstance(result, ContainerLogSnapshot)
    assert result.container_name == "aegis-demo"
    assert result.service == "demo"
    assert len(result.lines) == 2
    assert "first line" in result.lines[0]
    assert "second line" in result.lines[1]
    assert result.truncated is False
    assert isinstance(result.observed_at, datetime)


def test_rejects_invalid_tail():
    try:
        collect_container_logs("aegis-demo", tail=0, client=FakeClient())
    except ValueError as exc:
        assert "tail must be at least 1" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
