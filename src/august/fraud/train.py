from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from august.fraud.decision import optimize_review_threshold


FEATURES = [
    "transaction_amount",
    "account_age_days",
    "velocity_10m",
    "device_changed",
    "distance_km",
    "refund_rate",
    "night",
]


def train_logistic_baseline(frame: pd.DataFrame, *, train_fraction: float = 0.70) -> dict:
    """Temporal logistic-regression fraud baseline.

    Intended for synthetic/demo or versioned public datasets. No random split.
    """
    ordered = frame.sort_values("timestamp").reset_index(drop=True)
    split = int(len(ordered) * train_fraction)

    train = ordered.iloc[:split]
    test = ordered.iloc[split:]

    transformer = ColumnTransformer(
        [("numeric", StandardScaler(), FEATURES)],
        remainder="drop",
    )
    model = Pipeline(
        [
            ("features", transformer),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1_000,
                    random_state=42,
                ),
            ),
        ]
    )

    model.fit(train[FEATURES], train["fraud"])
    probabilities = model.predict_proba(test[FEATURES])[:, 1]

    metrics = {
        "pr_auc": float(average_precision_score(test["fraud"], probabilities)),
        "roc_auc": float(roc_auc_score(test["fraud"], probabilities)),
        "brier_score": float(brier_score_loss(test["fraud"], probabilities)),
        "positive_rate_test": float(np.mean(test["fraud"])),
        "train_rows": len(train),
        "test_rows": len(test),
        "split_strategy": "temporal_70_30",
    }

    threshold = optimize_review_threshold(
        probabilities,
        test["fraud"].to_numpy(),
        test["transaction_amount"].to_numpy(),
    )

    return {
        "model": model,
        "metrics": metrics,
        "optimal_cost_threshold": threshold,
        "probabilities": probabilities,
        "test_index": test.index.to_numpy(),
    }
