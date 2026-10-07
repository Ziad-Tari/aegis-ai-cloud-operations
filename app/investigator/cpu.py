from app.core.models import Incident, Investigation


def investigate_cpu_incident(
    incident: Incident,
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
    ]

    summary = (
        "The incident is primarily associated with "
        f"{primary_process}."
    )

    return Investigation(
        incident_type=incident.type,
        summary=summary,
        findings=findings,
    )