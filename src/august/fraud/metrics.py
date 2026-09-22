from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def precision_recall_at_k(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    *,
    review_rate: float,
) -> dict:
    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)

    if not 0 < review_rate <= 1:
        raise ValueError("review_rate must be in (0, 1]")

    k = max(1, int(np.ceil(len(y_true) * review_rate)))
    order = np.argsort(probabilities)[::-1][:k]
    reviewed_labels = y_true[order]

    true_positives = int(reviewed_labels.sum())
    total_positives = int(y_true.sum())

    return {
        "review_rate": review_rate,
        "reviewed": k,
        "precision_at_k": true_positives / k,
        "recall_at_k": true_positives / total_positives if total_positives else None,
        "pr_auc": float(average_precision_score(y_true, probabilities)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)) if len(np.unique(y_true)) > 1 else None,
    }
