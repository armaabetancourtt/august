from __future__ import annotations

from collections.abc import Callable

import numpy as np


def bootstrap_interval(
    values: np.ndarray,
    statistic: Callable[[np.ndarray], float] = np.mean,
    *,
    confidence: float = 0.95,
    resamples: int = 5_000,
    seed: int = 42,
) -> dict:
    values = np.asarray(values, dtype=float)
    if values.size < 2:
        raise ValueError("at least two observations are required")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1)")

    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(resamples, len(values)), replace=True)
    stats = np.apply_along_axis(statistic, 1, draws)

    alpha = 1 - confidence
    return {
        "estimate": float(statistic(values)),
        "lower": float(np.quantile(stats, alpha / 2)),
        "upper": float(np.quantile(stats, 1 - alpha / 2)),
        "confidence": confidence,
        "resamples": resamples,
        "seed": seed,
    }
