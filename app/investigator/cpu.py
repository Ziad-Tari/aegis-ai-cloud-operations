
from app.core.models import Incident, Investigation, SystemSnapshot


def investigate_cpu_incident(
    incident: Incident,
    snapshot: SystemSnapshot,
) -> Investigation:
    if not incident.evidence:
        return Investigation(
            incident_type=incident.type,
            summary="No process evidence was available.",
            findings=[
                "The incident cannot be attributed to a specific process.",
                f"System CPU usage at detection: {snapshot.cpu_percent:.1f}%",
            ],
        )

    processes = sorted(
        incident.evidence,
        key=lambda process: process.cpu_percent,
        reverse=True,
    )

    primary_process = processes[0]

    findings = [
        (
            f"Primary CPU contributor: {primary_process.name} "
            f"(PID {primary_process.pid})"
        ),
        f"Process CPU usage: {primary_process.cpu_percent:.1f}%",
        f"System CPU usage at detection: {snapshot.cpu_percent:.1f}%",
    ]

    for process in processes[1:]:
        findings.append(
            f"Other contributing process: {process.name} "
            f"(PID {process.pid}), "
            f"{process.cpu_percent:.1f}% CPU"
        )

    if snapshot.cpu_percent < 50.0:
        findings.append(
            "System-wide CPU usage is moderate despite the "
            "reported process-level CPU activity."
        )
    else:
        findings.append(
            "System CPU usage is elevated and may indicate "
            "broader resource pressure."
        )

    summary = (
        f"Identified {len(processes)} process(es) in the incident evidence. "
        f"The highest reported contributor is {primary_process.name} "
        f"(PID {primary_process.pid}) at "
        f"{primary_process.cpu_percent:.1f}% process CPU usage. "
        f"System CPU usage was {snapshot.cpu_percent:.1f}%."
    )

    return Investigation(
        incident_type=incident.type,
        summary=summary,
        findings=findings,
    )