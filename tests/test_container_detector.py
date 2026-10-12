
from datetime import datetime, timezone

from app.core.container_models import ContainerSnapshot
from app.detector.container_detector import (
    ContainerIncidentDetector,
)


def make_snapshot(
    cpu: float | None = 0.1,
    memory_bytes: int | None = 20 * 1024 * 1024,
) -> ContainerSnapshot:
    return ContainerSnapshot(
        container_name="aegis-demo",
        service="demo",
        cpu_cores=cpu,
        memory_bytes=memory_bytes,
        observed_at=datetime.now(timezone.utc),
    )


def test_detects_sustained_high_cpu():
    detector = ContainerIncidentDetector()

    high_cpu = make_snapshot(cpu=0.8)

    assert detector.detect([high_cpu]) == []
    assert detector.detect([high_cpu]) == []

    incidents = detector.detect([high_cpu])

    assert len(incidents) == 1
    assert incidents[0].incident_type == "HIGH_CONTAINER_CPU"
    assert incidents[0].observed_value == 0.8
    assert incidents[0].threshold == 0.5


def test_does_not_repeat_active_incident():
    detector = ContainerIncidentDetector()
    high_cpu = make_snapshot(cpu=0.8)

    detector.detect([high_cpu])
    detector.detect([high_cpu])

    assert len(detector.detect([high_cpu])) == 1
    assert detector.detect([high_cpu]) == []


def test_normal_sample_resets_cpu_streak():
    detector = ContainerIncidentDetector()

    assert detector.detect([make_snapshot(cpu=0.8)]) == []
    assert detector.detect([make_snapshot(cpu=0.8)]) == []
    assert detector.detect([make_snapshot(cpu=0.1)]) == []
    assert detector.detect([make_snapshot(cpu=0.8)]) == []

    # Three new consecutive abnormal samples are required.
    assert detector.detect([make_snapshot(cpu=0.8)]) == []
    incidents = detector.detect([make_snapshot(cpu=0.8)])

    assert len(incidents) == 1
    assert incidents[0].incident_type == "HIGH_CONTAINER_CPU"


def test_detects_high_memory():
    detector = ContainerIncidentDetector()

    high_memory = make_snapshot(
        cpu=0.1,
        memory_bytes=120 * 1024 * 1024,
    )

    assert detector.detect([high_memory]) == []
    assert detector.detect([high_memory]) == []

    incidents = detector.detect([high_memory])

    assert len(incidents) == 1
    assert incidents[0].incident_type == "HIGH_CONTAINER_MEMORY"
    assert incidents[0].observed_value == 120
    assert incidents[0].unit == "MiB"


def test_missing_metrics_do_not_trigger_incidents():
    detector = ContainerIncidentDetector()

    missing = make_snapshot(cpu=None, memory_bytes=None)

    for _ in range(5):
        assert detector.detect([missing]) == []


def test_cpu_and_memory_are_detected_independently():
    detector = ContainerIncidentDetector()

    high_both = make_snapshot(
        cpu=0.8,
        memory_bytes=120 * 1024 * 1024,
    )

    detector.detect([high_both])
    detector.detect([high_both])
    incidents = detector.detect([high_both])

    assert {i.incident_type for i in incidents} == {
        "HIGH_CONTAINER_CPU",
        "HIGH_CONTAINER_MEMORY",
    }
