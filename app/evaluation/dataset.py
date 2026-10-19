
from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    description: str
    incident: dict
    expected_observation_terms: tuple[str, ...]
    required_unknown_terms: tuple[str, ...]


EVALUATION_CASES = (
    EvaluationCase(
        case_id="container-stopped",
        description="A container exits, but the termination cause is unknown.",
        incident={
            "id": 1,
            "timestamp": "2026-10-18T12:00:00+00:00",
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
        },
        expected_observation_terms=(
            "recorded status 'exited'",
            "health status 'unhealthy'",
            "http 200",
        ),
        required_unknown_terms=("root cause", "exit code"),
    ),
    EvaluationCase(
        case_id="container-high-memory",
        description="A container exceeds its memory threshold.",
        incident={
            "id": 2,
            "timestamp": "2026-10-18T12:05:00+00:00",
            "incident_type": "HIGH_CONTAINER_MEMORY",
            "message": "aegis-demo exceeded its memory threshold",
            "evidence": [
                {
                    "container_name": "aegis-demo",
                    "service": "demo",
                    "metric_type": "memory",
                    "observed_value": 160.0,
                    "threshold": 100.0,
                    "unit": "MiB",
                }
            ],
        },
        expected_observation_terms=(
            "memory",
            "160",
            "100",
        ),
        required_unknown_terms=("cause",),
    ),
    EvaluationCase(
        case_id="container-high-cpu",
        description="A container exceeds its CPU threshold.",
        incident={
            "id": 3,
            "timestamp": "2026-10-18T12:10:00+00:00",
            "incident_type": "HIGH_CONTAINER_CPU",
            "message": "aegis-demo exceeded its CPU threshold",
            "evidence": [
                {
                    "container_name": "aegis-demo",
                    "service": "demo",
                    "metric_type": "cpu",
                    "observed_value": 0.85,
                    "threshold": 0.5,
                    "unit": "cores",
                }
            ],
        },
        expected_observation_terms=(
            "cpu",
            "0.85",
            "0.5",
        ),
        required_unknown_terms=("cause",),
    ),
)
