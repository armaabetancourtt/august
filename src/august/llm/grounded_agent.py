"""Deterministic retrieval-first agent. No network access or uncontrolled tool execution."""
import math
import re
from dataclasses import dataclass

def tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))

@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str

class GroundedAgent:
    def __init__(self, documents: list[Document], min_overlap: float = 0.12):
        self.documents = documents
        self.min_overlap = min_overlap

    def retrieve(self, question: str, limit: int = 3):
        query = tokens(question)
        if not query:
            return []
        ranked = []
        for document in self.documents:
            words = tokens(document.text)
            score = len(query & words) / math.sqrt(max(1, len(query) * len(words)))
            if score >= self.min_overlap:
                ranked.append((score, document))
        ranked.sort(key=lambda x: (-x[0], x[1].doc_id))
        return [doc for _, doc in ranked[:limit]]

    def answer(self, question: str, generate=None):
        evidence = self.retrieve(question)
        if not evidence:
            return {"answer": "Insufficient evidence.", "citations": [], "grounded": False}
        context = "\n".join(f"[{d.doc_id}] {d.text}" for d in evidence)
        # Caller-supplied LLM is optional; never interpolate retrieved text into tool execution.
        answer = generate(question, context) if generate else context
        return {"answer": answer, "citations": [d.doc_id for d in evidence], "grounded": True}
