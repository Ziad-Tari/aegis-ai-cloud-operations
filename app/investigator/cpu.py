from app.core.models import Incident, Investigation


def investigate_cpu_incident(
    incident: Incident,
) -> Investigation:
    findings = []

    for evidence in incident.evidence:
        findings.append(
            f"High CPU process detected: {evidence}"
        )

    summary = (
        "CPU pressure was detected and the following "
        "processes are the primary contributors."
    )

    return Investigation(
        incident_type=incident.type,
        summary=summary,
        findings=findings,
    )