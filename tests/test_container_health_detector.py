
from datetime import datetime, timezone

from app.core.container_models import ContainerHealthSnapshot
from app.detector.container_health_detector import ContainerHealthDetector


def snapshot(
    status="running",
    health="healthy",
    restarts=0,
):
    return ContainerHealthSnapshot(
        container_name="aegis-demo",
        service="demo",
        status=status,
        health_status=health,
        restart_count=restarts,
        observed_at=datetime.now(timezone.utc),
    )


def test_detects_unhealthy_transition_once_until_recovery():
    detector = ContainerHealthDetector()

    incidents = detector.detect([snapshot(health="unhealthy")])
    assert len(incidents) == 1
    assert incidents[0].incident_type == "CONTAINER_UNHEALTHY"

    assert detector.detect([snapshot(health="unhealthy")]) == []

    detector.detect([snapshot(health="healthy")])

    incidents = detector.detect([snapshot(health="unhealthy")])
    assert len(incidents) == 1
    assert incidents[0].incident_type == "CONTAINER_UNHEALTHY"


def test_stopped_container_at_startup_does_not_create_incident():
    detector = ContainerHealthDetector()

    incidents = detector.detect([
        snapshot(status="exited", health=None)
    ])

    assert incidents == []


def test_detects_running_to_exited_transition():
    detector = ContainerHealthDetector()

    assert detector.detect([snapshot(status="running")]) == []

    incidents = detector.detect([
        snapshot(status="exited", health=None)
    ])

    assert len(incidents) == 1
    assert incidents[0].incident_type == "CONTAINER_STOPPED"
    assert "running to exited" in incidents[0].message


def test_already_exited_container_does_not_repeat_incident():
    detector = ContainerHealthDetector()

    detector.detect([snapshot(status="running")])
    first = detector.detect([snapshot(status="exited", health=None)])
    second = detector.detect([snapshot(status="exited", health=None)])

    assert len(first) == 1
    assert second == []


def test_detects_container_recovery_then_another_stop():
    detector = ContainerHealthDetector()

    detector.detect([snapshot(status="running")])
    first_stop = detector.detect([
        snapshot(status="exited", health=None)
    ])

    assert first_stop[0].incident_type == "CONTAINER_STOPPED"

    # Recovery establishes running as the new state.
    assert detector.detect([snapshot(status="running")]) == []

    # A subsequent stop is a new transition and should alert again.
    second_stop = detector.detect([
        snapshot(status="exited", health=None)
    ])

    assert len(second_stop) == 1
    assert second_stop[0].incident_type == "CONTAINER_STOPPED"


def test_detects_restart_count_increase():
    detector = ContainerHealthDetector()

    assert detector.detect([snapshot(restarts=2)]) == []

    incidents = detector.detect([snapshot(restarts=3)])

    assert len(incidents) == 1
    assert incidents[0].incident_type == "CONTAINER_RESTARTED"
    assert "increased from 2 to 3" in incidents[0].message


def test_initial_restart_count_does_not_create_false_incident():
    detector = ContainerHealthDetector()

    assert detector.detect([snapshot(restarts=5)]) == []
    assert detector.detect([snapshot(restarts=5)]) == []


def test_restart_increase_emits_only_one_incident_per_increment():
    detector = ContainerHealthDetector()

    detector.detect([snapshot(restarts=0)])

    incidents = detector.detect([snapshot(restarts=1)])
    assert len(incidents) == 1
    assert incidents[0].incident_type == "CONTAINER_RESTARTED"

    assert detector.detect([snapshot(restarts=1)]) == []

    # A later increase represents a new restart event.
    incidents = detector.detect([snapshot(restarts=2)])
    assert len(incidents) == 1
    assert incidents[0].incident_type == "CONTAINER_RESTARTED"
