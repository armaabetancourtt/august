from __future__ import annotations

import numpy as np
from sklearn.metrics import davies_bouldin_score, silhouette_score


def clustering_quality(features: np.ndarray, labels: np.ndarray) -> dict:
    features = np.asarray(features, dtype=float)
    labels = np.asarray(labels)

    unique = np.unique(labels)
    if len(unique) < 2 or len(unique) >= len(labels):
        raise ValueError("clustering metrics require at least two non-trivial clusters")

    return {
        "clusters": int(len(unique)),
        "silhouette_score": float(silhouette_score(features, labels)),
        "davies_bouldin_score": float(davies_bouldin_score(features, labels)),
        "note": "Do not name clusters until feature profiles have been inspected.",
    }
