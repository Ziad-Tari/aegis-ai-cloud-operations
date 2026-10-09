
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




def test_investigator_reports_multiple_processes():
    timestamp = datetime.now()

    incident = Incident(
        timestamp=timestamp,
        type="HIGH_CPU",
        message="High CPU detected",
        evidence=[
            ProcessEvidence(
                pid=1001,
                name="worker.exe",
                cpu_percent=45.0,
                memory_percent=3.0,
            ),
            ProcessEvidence(
                pid=1002,
                name="python.exe",
                cpu_percent=85.0,
                memory_percent=2.0,
            ),
        ],
    )

    snapshot = SystemSnapshot(
        timestamp=timestamp,
        cpu_percent=70.0,
        memory_percent=60.0,
        disk_percent=20.0,
    )

    investigation = investigate_cpu_incident(incident, snapshot)

    assert "2 process(es)" in investigation.summary
    assert "python.exe (PID 1002)" in investigation.summary
    assert any("worker.exe (PID 1001)" in finding for finding in investigation.findings)
    assert any("System CPU usage is elevated" in finding for finding in investigation.findings)


def test_investigator_handles_missing_process_evidence():
    timestamp = datetime.now()

    incident = Incident(
        timestamp=timestamp,
        type="HIGH_CPU",
        message="High CPU detected",
        evidence=[],
    )

    snapshot = SystemSnapshot(
        timestamp=timestamp,
        cpu_percent=75.0,
        memory_percent=60.0,
        disk_percent=20.0,
    )

    investigation = investigate_cpu_incident(incident, snapshot)

    assert investigation.incident_type == "HIGH_CPU"
    assert "No process evidence was available" in investigation.summary
    assert any(
        "cannot be attributed" in finding
        for finding in investigation.findings
    )


def test_investigator_reports_moderate_system_cpu():
    timestamp = datetime.now()

    incident = Incident(
        timestamp=timestamp,
        type="HIGH_CPU",
        message="High CPU detected",
        evidence=[
            ProcessEvidence(
                pid=1001,
                name="python.exe",
                cpu_percent=85.0,
                memory_percent=2.0,
            ),
        ],
    )

    snapshot = SystemSnapshot(
        timestamp=timestamp,
        cpu_percent=30.0,
        memory_percent=60.0,
        disk_percent=20.0,
    )

    investigation = investigate_cpu_incident(incident, snapshot)

    assert any(
        "System-wide CPU usage is moderate" in finding
        for finding in investigation.findings
    )