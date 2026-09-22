from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def cluster_feedback(
    texts: Sequence[str],
    *,
    clusters: int = 4,
    random_state: int = 42,
) -> dict:
    if len(texts) < clusters:
        raise ValueError("need at least as many documents as clusters")

    vectorizer = TfidfVectorizer(
        max_features=2_000,
        ngram_range=(1, 2),
        stop_words="english",
    )
    matrix = vectorizer.fit_transform(texts)
    model = KMeans(n_clusters=clusters, n_init="auto", random_state=random_state)
    labels = model.fit_predict(matrix)

    terms = np.asarray(vectorizer.get_feature_names_out())
    cluster_terms = {}

    for cluster_id in range(clusters):
        center = model.cluster_centers_[cluster_id]
        cluster_terms[str(cluster_id)] = terms[np.argsort(center)[-8:][::-1]].tolist()

    return {
        "labels": labels.tolist(),
        "cluster_terms": cluster_terms,
        "method": "TF-IDF + KMeans baseline",
        "warning": "Cluster labels require human interpretation; themes are not causal drivers.",
    }
