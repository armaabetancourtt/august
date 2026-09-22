from __future__ import annotations

from collections.abc import Sequence


def evaluate_llm_judgments(rows: Sequence[dict]) -> dict:
    """Aggregate a reproducible manually/externally-scored LLM benchmark.

    Expected row keys: factual_consistency, answer_relevance,
    citation_correctness, hallucinated (all 0..1 except hallucinated bool).
    """
    if not rows:
        raise ValueError("at least one evaluation row is required")

    return {
        "examples": len(rows),
        "factual_consistency": sum(float(r["factual_consistency"]) for r in rows) / len(rows),
        "answer_relevance": sum(float(r["answer_relevance"]) for r in rows) / len(rows),
        "citation_correctness": sum(float(r["citation_correctness"]) for r in rows) / len(rows),
        "hallucination_rate": sum(bool(r["hallucinated"]) for r in rows) / len(rows),
    }
