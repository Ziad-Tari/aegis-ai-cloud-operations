
from datetime import datetime

from app.core.models import Incident, ProcessEvidence, SystemSnapshot
from app.investigator.cpu import investigate_cpu_incident


def test_investigate_cpu_incident_identifies_primary_process():
    timestamp = datetime.now()

    process = ProcessEvidence(
        pid=1234,
        name="python.exe",
        cpu_percent=85.0,
        memory_percent=2.5,
    )

    incident = Incident(
        timestamp=timestamp,
        type="HIGH_CPU",
        message="System CPU usage is 75.0%",
        evidence=[process],
    )

    snapshot = SystemSnapshot(
        timestamp=timestamp,
        cpu_percent=75.0,
        memory_percent=60.0,
        disk_percent=20.0,
    )

    investigation = investigate_cpu_incident(incident, snapshot)

    assert investigation.incident_type == "HIGH_CPU"
    assert "python.exe (PID 1234)" in investigation.summary
    assert "85.0%" in investigation.summary
    assert any(
        "python.exe (PID 1234)" in finding
        for finding in investigation.findings
    )