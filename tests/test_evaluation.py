
from app.core.models import Investigation, InvestigationClaim
from app.evaluation.dataset import EvaluationCase
from app.evaluation.quality import evaluate_investigation


def make_case() -> EvaluationCase:
    return EvaluationCase(
        case_id="test-case",
        description="Test evidence evaluation.",
        incident={
            "evidence": [
                {"status": "exited"},
                {"lines": ["HTTP 200 OK"]},
            ]
        },
        expected_observation_terms=("exited", "http 200"),
        required_unknown_terms=("root cause", "exit code"),
    )


def make_report() -> Investigation:
    return Investigation(
        incident_type="CONTAINER_STOPPED",
        summary="The container exited for an unknown reason.",
        findings=["The container exited.", "Logs contain HTTP 200."],
        observations=[
            InvestigationClaim(
                text="The container status is exited.",
                evidence_references=["E1"],
                source="fallback",
            ),
            InvestigationClaim(
                text="Logs contain HTTP 200.",
                evidence_references=["E2"],
                source="model",
            ),
        ],
        unknowns=["The root cause is unknown."],
        missing_evidence=["The container exit code is needed."],
    )


def test_evaluator_scores_complete_report() -> None:
    result = evaluate_investigation(make_case(), make_report())

    assert result.traceability_score == 100.0
    assert result.observation_coverage_score == 100.0
    assert result.uncertainty_coverage_score == 100.0
    assert result.overall_score == 100.0
    assert not result.invalid_claims
    assert not result.missing_observations
    assert not result.missing_unknowns


def test_evaluator_detects_invalid_evidence_reference() -> None:
    report = make_report()
    report.observations[0].evidence_references = ["E999"]

    result = evaluate_investigation(make_case(), report)

    assert result.traceability_score == 50.0
    assert result.invalid_claims == ("The container status is exited.",)
    assert result.overall_score < 100.0


def test_evaluator_detects_missing_observations_and_unknowns() -> None:
    report = make_report()
    report.observations = report.observations[:1]
    report.unknowns = []
    report.missing_evidence = []

    result = evaluate_investigation(make_case(), report)

    assert result.observation_coverage_score == 50.0
    assert result.uncertainty_coverage_score == 0.0
    assert result.missing_observations == ("http 200",)
    assert result.missing_unknowns == ("root cause", "exit code")


def test_empty_report_does_not_receive_perfect_traceability() -> None:
    report = make_report()
    report.observations = []
    report.hypotheses = []

    result = evaluate_investigation(make_case(), report)

    assert result.traceability_score == 0.0
