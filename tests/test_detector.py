
from datetime import datetime, timedelta

from app.core.models import ProcessEvidence, ProcessSnapshot, SystemSnapshot
from app.detector.detector import detect_cpu_incident


def test_detector_identifies_sustained_high_cpu():
    timestamp = datetime.now()

    processes = [
        ProcessSnapshot(
            pid=1234,
            name="python.exe",
            cpu_percent=85.0,
            memory_percent=2.5,
        )
    ]

    incident = None

    # Simulate three consecutive abnormal CPU samples.
    for sample_number in range(1, 4):
        snapshot = SystemSnapshot(
            timestamp=timestamp + timedelta(seconds=sample_number),
            cpu_percent=30.0,
            memory_percent=60.0,
            disk_percent=20.0,
        )

        incident = detect_cpu_incident(
            snapshot,
            processes,
            average_cpu=10.0,
            history_size=3,
        )

    assert incident is not None
    assert incident.type == "HIGH_CPU"
    assert len(incident.evidence) == 1

    evidence = incident.evidence[0]
    assert isinstance(evidence, ProcessEvidence)
    assert evidence.pid == 1234
    assert evidence.name == "python.exe"
    assert evidence.cpu_percent == 85.0