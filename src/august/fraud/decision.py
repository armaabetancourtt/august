from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FraudCosts:
    false_negative_multiplier: float = 1.0
    false_positive_cost: float = 120.0
    review_cost: float = 40.0


def expected_fraud_loss(probability: float, amount: float) -> float:
    if not 0 <= probability <= 1:
        raise ValueError("probability must be in [0, 1]")
    if amount < 0:
        raise ValueError("amount must be non-negative")
    return probability * amount


def decide_transaction(
    probability: float,
    amount: float,
    *,
    review_threshold: float = 0.25,
    block_threshold: float = 0.80,
    review_cost: float = 40.0,
) -> dict:
    loss = expected_fraud_loss(probability, amount)

    if probability >= block_threshold:
        action = "BLOCK"
    elif probability >= review_threshold and loss > review_cost:
        action = "REVIEW"
    else:
        action = "APPROVE"

    return {
        "fraud_probability": probability,
        "risk_score": round(probability * 100),
        "transaction_amount": amount,
        "expected_fraud_loss": round(loss, 2),
        "manual_review_cost": review_cost,
        "recommended_action": action,
    }


def optimize_review_threshold(
    probabilities: np.ndarray,
    labels: np.ndarray,
    amounts: np.ndarray,
    *,
    thresholds: np.ndarray | None = None,
    costs: FraudCosts | None = None,
) -> dict:
    costs = costs or FraudCosts()
    probabilities = np.asarray(probabilities, dtype=float)
    labels = np.asarray(labels, dtype=int)
    amounts = np.asarray(amounts, dtype=float)

    if not (len(probabilities) == len(labels) == len(amounts)):
        raise ValueError("arrays must have equal length")

    thresholds = thresholds if thresholds is not None else np.linspace(0.02, 0.98, 97)
    results = []

    for threshold in thresholds:
        review = probabilities >= threshold
        false_negative = (~review) & (labels == 1)
        false_positive = review & (labels == 0)

        fn_cost = float(np.sum(amounts[false_negative]) * costs.false_negative_multiplier)
        fp_cost = float(np.sum(false_positive) * costs.false_positive_cost)
        manual_cost = float(np.sum(review) * costs.review_cost)

        results.append(
            {
                "threshold": float(threshold),
                "expected_cost": fn_cost + fp_cost + manual_cost,
                "review_rate": float(np.mean(review)),
                "false_negative_cost": fn_cost,
                "false_positive_cost": fp_cost,
                "manual_review_cost": manual_cost,
            }
        )

    return min(results, key=lambda row: row["expected_cost"])
