from app.core.models import Incident, Investigation, SystemSnapshot

def investigate_cpu_incident(
    incident: Incident,
    snapshot: SystemSnapshot,
) -> Investigation:
    if not incident.evidence:
        return Investigation(
            incident_type=incident.type,
            summary="No process evidence was available.",
            findings=[],
        )

    primary_process = incident.evidence[0]

    findings = [
        f"Primary CPU contributor: {primary_process}",
        f"System CPU usage at detection: {snapshot.cpu_percent:.1f}%",
    ]

    if snapshot.cpu_percent < 50.0:
        findings.append(
            "System-wide CPU usage is moderate despite high "
            "process-level CPU activity."
        )

    summary = (
        "The incident is primarily associated with "
        f"{primary_process}. "
        f"System CPU usage was {snapshot.cpu_percent:.1f}%."
        )

    return Investigation(
        incident_type=incident.type,
        summary=summary,
        findings=findings,
    )