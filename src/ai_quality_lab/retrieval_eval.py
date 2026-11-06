"""Dataset-driven retrieval quality metrics for the bundled support articles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ai_quality_lab.assistant import retrieve_articles

_EVALUATION_CASES = Path(__file__).resolve().parents[2] / "data" / "retrieval_eval.json"


def calculate_retrieval_metrics(
    ranked_article_ids: Sequence[Sequence[str]],
    relevant_article_ids: Sequence[set[str]],
    *,
    k_values: Sequence[int] = (1, 3),
) -> dict[str, float]:
    """Calculate macro Recall@k, mean reciprocal rank, and no-answer accuracy."""
    if len(ranked_article_ids) != len(relevant_article_ids):
        raise ValueError("predicted and relevant query counts must match")
    if not ranked_article_ids:
        raise ValueError("at least one evaluation query is required")
    if not k_values or any(k < 1 for k in k_values):
        raise ValueError("k_values must contain positive integers")

    answerable = [
        (ranked, relevant)
        for ranked, relevant in zip(ranked_article_ids, relevant_article_ids)
        if relevant
    ]
    if not answerable:
        raise ValueError("at least one answerable query is required")

    metrics = {}
    for k in k_values:
        query_recalls = [
            len(set(ranked[:k]) & relevant) / len(relevant)
            for ranked, relevant in answerable
        ]
        metrics[f"recall@{k}"] = sum(query_recalls) / len(query_recalls)

    reciprocal_ranks = []
    for ranked, relevant in answerable:
        first_relevant_rank = next(
            (rank for rank, article_id in enumerate(ranked, start=1) if article_id in relevant),
            None,
        )
        reciprocal_ranks.append(1 / first_relevant_rank if first_relevant_rank else 0.0)
    metrics["mrr"] = sum(reciprocal_ranks) / len(reciprocal_ranks)

    unanswerable = [
        ranked
        for ranked, relevant in zip(ranked_article_ids, relevant_article_ids)
        if not relevant
    ]
    if unanswerable:
        metrics["no_answer_accuracy"] = sum(not ranked for ranked in unanswerable) / len(unanswerable)

    return metrics


def load_evaluation_cases() -> list[dict[str, object]]:
    """Read the checked-in retrieval questions and relevance labels."""
    return json.loads(_EVALUATION_CASES.read_text(encoding="utf-8"))


def run_retrieval_evaluation(
    cases: Sequence[dict[str, object]],
) -> dict[str, float]:
    """Retrieve candidates for each case and calculate the quality metrics."""
    if not cases:
        raise ValueError("at least one evaluation query is required")

    relevant_ids = [set(case["relevant_article_ids"]) for case in cases]
    max_k = 1
    # Keep the candidate list wide enough for the default Recall@3 metric.
    max_k = max(max_k, 3)
    ranked_ids = [
        [article["id"] for article in retrieve_articles(str(case["question"]), top_k=max_k)]
        for case in cases
    ]
    return calculate_retrieval_metrics(ranked_ids, relevant_ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate support-article retrieval quality.")
    parser.add_argument("--min-recall-at-1", type=float, default=0.9)
    parser.add_argument("--min-no-answer-accuracy", type=float, default=1.0)
    args = parser.parse_args()

    cases = load_evaluation_cases()
    metrics = run_retrieval_evaluation(cases)
    print(f"Queries: {len(cases)}")
    for name, value in metrics.items():
        print(f"{name}: {value:.3f}")

    passed = (
        metrics["recall@1"] >= args.min_recall_at_1
        and metrics.get("no_answer_accuracy", 1.0) >= args.min_no_answer_accuracy
    )
    print("Retrieval quality gate: PASS" if passed else "Retrieval quality gate: FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
