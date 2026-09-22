from __future__ import annotations

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import ks_2samp, wasserstein_distance


def population_stability_index(
    reference: np.ndarray,
    current: np.ndarray,
    *,
    bins: int = 10,
    epsilon: float = 1e-6,
) -> float:
    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)

    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0] = -np.inf
    edges[-1] = np.inf

    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)

    ref_pct = np.clip(ref_counts / max(ref_counts.sum(), 1), epsilon, None)
    cur_pct = np.clip(cur_counts / max(cur_counts.sum(), 1), epsilon, None)

    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def numeric_drift_report(reference: np.ndarray, current: np.ndarray) -> dict:
    reference = np.asarray(reference, dtype=float)
    current = np.asarray(current, dtype=float)

    ks = ks_2samp(reference, current)
    hist_range = (
        float(min(reference.min(), current.min())),
        float(max(reference.max(), current.max())),
    )
    ref_hist, _ = np.histogram(reference, bins=30, range=hist_range, density=True)
    cur_hist, _ = np.histogram(current, bins=30, range=hist_range, density=True)
    ref_hist = ref_hist + 1e-12
    cur_hist = cur_hist + 1e-12
    ref_hist /= ref_hist.sum()
    cur_hist /= cur_hist.sum()

    return {
        "psi": population_stability_index(reference, current),
        "ks_statistic": float(ks.statistic),
        "ks_pvalue": float(ks.pvalue),
        "wasserstein_distance": float(wasserstein_distance(reference, current)),
        "jensen_shannon_distance": float(jensenshannon(ref_hist, cur_hist)),
    }
