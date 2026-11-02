"""Hybrid retrieval: dense (vector) + sparse (keyword) signals combined.

The vector store gives semantic matches; a keyword overlap score catches exact
terms and names that embeddings can miss. Scores are min-max normalised and
blended. This is a solid baseline. The learned re-ranker that reorders the
shortlist for answer quality is reserved (see reranker.py and README).
"""
from __future__ import annotations

import re

import numpy as np

from .schemas import Chunk, Citation

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "in", "on", "for",
    "and", "or", "how", "what", "when", "where", "can", "i", "do", "does", "my",
    "me", "you", "it", "this", "that", "with", "at", "by", "much", "many", "get",
    "after", "before", "about", "please", "we", "they",
}


def _content_words(text: str) -> set[str]:
    return {w for w in _TOKEN.findall(text.lower()) if w not in _STOP and len(w) > 1}


def _kw_score(query: str, text: str) -> float:
    q = set(_TOKEN.findall(query.lower()))
    if not q:
        return 0.0
    t = _TOKEN.findall(text.lower())
    if not t:
        return 0.0
    hits = sum(1 for w in t if w in q)
    return hits / len(t) ** 0.5  # length-normalised overlap


def _norm(xs: list[float]) -> list[float]:
    if not xs:
        return xs
    lo, hi = min(xs), max(xs)
    if hi - lo < 1e-9:
        return [0.0 for _ in xs]
    return [(x - lo) / (hi - lo) for x in xs]


class Retriever:
    def __init__(self, store, embedder, alpha: float = 0.5):
        self.store = store
        self.embedder = embedder
        self.alpha = alpha  # weight on the dense score, vs keyword

    def retrieve(self, tenant_id: str, query: str, k: int, pool: int = 20):
        """Return (ranked, confidence).

        ranked items carry the RAW dense cosine as their score (an absolute,
        comparable number), while ordering uses the normalised hybrid blend.
        confidence is the best raw cosine in the pool, used by the graph to
        decide whether to answer or escalate.
        """
        qvec = self.embedder.embed([query])[0]
        dense = self.store.search(tenant_id, qvec, pool)  # [(chunk, raw_cosine)]
        if not dense:
            return [], 0.0

        chunks = [c for c, _ in dense]
        raw = [s for _, s in dense]
        dnorm = _norm(raw)
        knorm = _norm([_kw_score(query, c.text) for c in chunks])
        blended = [self.alpha * d + (1 - self.alpha) * kw for d, kw in zip(dnorm, knorm)]

        order = np.argsort(blended)[::-1][:k]
        ranked = [(chunks[i], float(raw[i])) for i in order]

        # Grounding confidence: how much of the question's content actually appears
        # in the retrieved context. Robust to the weak baseline embedder, and the
        # honest signal for "is this answerable from the docs at all".
        q_words = _content_words(query)
        if not q_words:
            confidence = 0.0
        else:
            ctx_words = set()
            for c, _ in ranked:
                ctx_words |= _content_words(c.text)
            confidence = len(q_words & ctx_words) / len(q_words)
        return ranked, float(confidence)


def to_citations(ranked: list[tuple[Chunk, float]]) -> list[Citation]:
    out = []
    for n, (c, score) in enumerate(ranked, start=1):
        snippet = c.text[:160] + ("..." if len(c.text) > 160 else "")
        out.append(Citation(n=n, source=c.source, chunk_id=c.id, score=round(score, 4), snippet=snippet))
    return out
