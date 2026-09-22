from __future__ import annotations

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss


def calibration_report(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    *,
    bins: int = 10,
) -> dict:
    y_true = np.asarray(y_true, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)

    if np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("probabilities must be in [0, 1]")

    fraction_positive, mean_predicted = calibration_curve(
        y_true,
        probabilities,
        n_bins=bins,
        strategy="quantile",
    )

    weights = np.full(len(fraction_positive), 1 / max(len(fraction_positive), 1))
    ece = float(np.sum(weights * np.abs(fraction_positive - mean_predicted)))

    return {
        "brier_score": float(brier_score_loss(y_true, probabilities)),
        "expected_calibration_error": ece,
        "calibration_curve": [
            {
                "predicted": float(predicted),
                "observed": float(observed),
            }
            for predicted, observed in zip(mean_predicted, fraction_positive, strict=True)
        ],
    }
