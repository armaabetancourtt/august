from __future__ import annotations

import numpy as np


def robust_z_scores(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    median = np.median(values)
    mad = np.median(np.abs(values - median))
    if mad == 0:
        return np.zeros_like(values)
    return 0.6745 * (values - median) / mad


def detect_robust_anomalies(values: np.ndarray, threshold: float = 3.5) -> dict:
    scores = robust_z_scores(values)
    mask = np.abs(scores) >= threshold
    return {
        "scores": scores,
        "mask": mask,
        "count": int(np.sum(mask)),
        "severity": np.abs(scores),
        "threshold": threshold,
    }
