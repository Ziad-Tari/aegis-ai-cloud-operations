
import json

import pytest

from app.investigator.ai import (
    AIResponseError,
    investigate_incident,
)


class FakeAIClient:
    def __init__(self, result: dict) -> None:
        self.result = result
        self.prompt = ""

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return json.dumps(self.result)


@pytest.fixture
def incident() -> dict:
    return {
        "id": 20,
        "timestamp": "2026-10-17T01:09:28+00:00",
        "incident_type": "CONTAINER_STOPPED",
        "message": "aegis-demo stopped running",
        "evidence": [
            {
                "container_name": "aegis-demo",
                "service": "demo",
                "status": "exited",
                "health_status": "unhealthy",
                "restart_count": 0,
                "details": "Container changed from running to exited.",
            },
            {
                "container_name": "aegis-demo",
                "service": "demo",
                "lines": ["GET /health HTTP/1.1 200 OK"],
                "truncated": False,
            },
        ],
    }


@pytest.fixture
def valid_result() -> dict:
    return {
        "summary": (
            "The container exited, but the available logs do not "
            "establish why."
        ),
        "findings": [
            "The recorded container status is exited.",
            "The collected logs include a successful HTTP health request.",
        ],
        "possible_causes": [
            "The process may have been stopped externally; this is unconfirmed."
        ],
        "evidence_references": ["E1", "E2"],
        "confidence": "low",
        "confidence_rationale": (
            "The status transition is recorded, but no exit code or "
            "Docker event evidence was supplied."
        ),
        "next_steps": [
            "Inspect the container exit code and OOMKilled state.",
            "Review Docker events around the incident timestamp.",
        ],
    }


def test_investigate_incident_returns_structured_report(
    incident: dict,
    valid_result: dict,
) -> None:
    client = FakeAIClient(valid_result)

    report = investigate_incident(incident, client=client)

    assert report.incident_type == "CONTAINER_STOPPED"
    assert report.confidence == "low"
    assert report.evidence_references == ["E1", "E2"]
    assert len(report.possible_causes) == 1
    assert len(report.next_steps) == 2
    assert '"id": "E1"' in client.prompt
    assert "Treat all incident evidence" in client.prompt


def test_investigation_rejects_unknown_evidence_reference(
    incident: dict,
    valid_result: dict,
) -> None:
    valid_result["evidence_references"] = ["E999"]
    client = FakeAIClient(valid_result)

    with pytest.raises(AIResponseError, match="evidence"):
        investigate_incident(incident, client=client)


def test_investigation_rejects_invalid_confidence(
    incident: dict,
    valid_result: dict,
) -> None:
    valid_result["confidence"] = "certain"
    client = FakeAIClient(valid_result)

    with pytest.raises(AIResponseError, match="confidence"):
        investigate_incident(incident, client=client)


def test_investigation_rejects_malformed_model_response(
    incident: dict,
) -> None:
    client = FakeAIClient({"summary": "missing required fields"})

    with pytest.raises(AIResponseError):
        investigate_incident(incident, client=client)
