from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def chunk_text(text: str, *, words_per_chunk: int = 180, overlap: int = 30) -> list[str]:
    words = text.split()
    if words_per_chunk <= overlap:
        raise ValueError("words_per_chunk must exceed overlap")

    chunks = []
    step = words_per_chunk - overlap
    for start in range(0, len(words), step):
        chunk = words[start : start + words_per_chunk]
        if chunk:
            chunks.append(" ".join(chunk))
    return chunks


def retrieve_lexical_baseline(
    query: str,
    documents: Sequence[str],
    *,
    top_k: int = 4,
) -> list[dict]:
    if not documents:
        return []

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform([query, *documents])
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    order = np.argsort(scores)[::-1][:top_k]

    return [
        {"index": int(index), "score": float(scores[index]), "text": documents[index]}
        for index in order
    ]
