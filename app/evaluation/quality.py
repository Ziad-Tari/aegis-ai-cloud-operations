
from dataclasses import asdict, dataclass

from app.core.models import Investigation
from app.evaluation.dataset import EvaluationCase


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    traceability_score: float
    observation_coverage_score: float
    uncertainty_coverage_score: float
    overall_score: float
    invalid_claims: tuple[str, ...]
    missing_observations: tuple[str, ...]
    missing_unknowns: tuple[str, ...]
    actual_observations: tuple[str, ...]
    actual_hypotheses: tuple[str, ...]
    actual_unknowns: tuple[str, ...]
    actual_missing_evidence: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _coverage_score(expected: tuple[str, ...], actual_text: str) -> float:
    if not expected:
        return 100.0

    actual_text = actual_text.lower()
    found = sum(term.lower() in actual_text for term in expected)

    return round(100 * found / len(expected), 2)


def evaluate_investigation(
    case: EvaluationCase,
    report: Investigation,
) -> EvaluationResult:
    evidence_count = len(case.incident.get("evidence", []))
    valid_ids = {f"E{i}" for i in range(1, evidence_count + 1)}

    claims = report.observations + report.hypotheses

    invalid_claims = tuple(
        claim.text
        for claim in claims
        if not claim.evidence_references
        or not set(claim.evidence_references).issubset(valid_ids)
    )

    if claims:
        traceability_score = round(
            100 * (len(claims) - len(invalid_claims)) / len(claims),
            2,
        )
    else:
        # An empty report must not receive perfect traceability.
        traceability_score = 0.0

    observation_text = " ".join(
        claim.text for claim in report.observations
    ).lower()

    missing_observations = tuple(
        term
        for term in case.expected_observation_terms
        if term.lower() not in observation_text
    )

    observation_coverage_score = _coverage_score(
        case.expected_observation_terms,
        observation_text,
    )

    uncertainty_text = " ".join(
        report.unknowns + report.missing_evidence
    ).lower()

    missing_unknowns = tuple(
        term
        for term in case.required_unknown_terms
        if term.lower() not in uncertainty_text
    )

    uncertainty_coverage_score = _coverage_score(
        case.required_unknown_terms,
        uncertainty_text,
    )

    overall_score = round(
        traceability_score * 0.4
        + observation_coverage_score * 0.4
        + uncertainty_coverage_score * 0.2,
        2,
    )

    return EvaluationResult(
        case_id=case.case_id,
        traceability_score=traceability_score,
        observation_coverage_score=observation_coverage_score,
        uncertainty_coverage_score=uncertainty_coverage_score,
        overall_score=overall_score,
        invalid_claims=invalid_claims,
        missing_observations=missing_observations,
        missing_unknowns=missing_unknowns,
                actual_observations=tuple(
            claim.text for claim in report.observations
        ),
        actual_hypotheses=tuple(
            claim.text for claim in report.hypotheses
        ),
        actual_unknowns=tuple(report.unknowns),
        actual_missing_evidence=tuple(report.missing_evidence),
    )
