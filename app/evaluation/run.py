
import json

from app.evaluation.dataset import EVALUATION_CASES
from app.evaluation.quality import evaluate_investigation
from app.investigator.ai import investigate_incident


def main() -> None:
    results = []

    for case in EVALUATION_CASES:
        print(f"Evaluating: {case.case_id}")

        report = investigate_incident(case.incident)
        score = evaluate_investigation(case, report)

        results.append(score.to_dict())

    average_score = round(
        sum(result["overall_score"] for result in results)
        / len(results),
        2,
    )

    print(
        json.dumps(
            {
                "case_count": len(results),
                "average_score": average_score,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
