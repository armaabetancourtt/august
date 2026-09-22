from __future__ import annotations

from typing import Any


def explain_structured_analysis(question: str, analysis: dict[str, Any]) -> dict:
    decision = analysis.get("decision", "No decision available")
    evidence = analysis.get("evidence", [])
    limitations = analysis.get("limitations", [])

    evidence_lines = [
        f"{item.get('label', 'signal')}: {item.get('value')}"
        for item in evidence[:4]
    ]

    answer = (
        f"AUGUST's current structured decision is: {decision}. "
        + ("Primary evidence: " + "; ".join(evidence_lines) + ". " if evidence_lines else "")
        + ("Important limitation: " + str(limitations[0]) if limitations else "")
    ).strip()

    return {
        "question": question,
        "answer": answer,
        "generation_mode": "deterministic_structured_explanation",
        "grounded": True,
        "citations": ["analysis.evidence", "analysis.assumptions", "analysis.limitations"],
    }
