
from datetime import datetime, timezone

from app.core.schemas import (
    ContainerEvidenceResponse,
    IncidentResponse,
)
from app.core.container_models import ContainerIncident
from app.monitoring.container_monitor import save_container_incident
from app.storage import incident_store


def test_saves_container_incident_and_exposes_its_evidence(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        incident_store,
        "DATABASE_PATH",
        tmp_path / "test_aegis.db",
    )

    incident = ContainerIncident(
        incident_type="HIGH_CONTAINER_MEMORY",
        container_name="aegis-demo",
        service="demo",
        observed_value=120.0,
        threshold=100.0,
        unit="MiB",
        message="aegis-demo exceeded the memory threshold.",
        observed_at=datetime.now(timezone.utc),
    )

    incident_id = save_container_incident(incident)

    saved = incident_store.get_incident(incident_id)

    assert saved is not None
    assert saved["incident_type"] == "HIGH_CONTAINER_MEMORY"
    assert saved["evidence"][0]["container_name"] == "aegis-demo"
    assert saved["evidence"][0]["metric_type"] == "memory"

    response = IncidentResponse.model_validate(saved)

    assert isinstance(
        response.evidence[0],
        ContainerEvidenceResponse,
    )
    assert response.evidence[0].observed_value == 120.0
