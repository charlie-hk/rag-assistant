"""Retrieval evaluation: does the right document come back for each question?

Given a small labelled set of (question -> expected source), it reports hit@k
and mean reciprocal rank. This is the honest, minimal evaluation the brief asks
for ("evaluate retrieval relevance"); the production harness adds answer-level
faithfulness scoring and latency/token tracking, which is reserved.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalResult:
    n: int
    hit_at_k: float
    mrr: float

    def as_dict(self) -> dict:
        return {"n": self.n, "hit_at_k": round(self.hit_at_k, 3), "mrr": round(self.mrr, 3)}


def evaluate(retriever, tenant_id: str, labelled: list[dict], k: int = 5) -> EvalResult:
    """labelled: [{"question": str, "expected_source": str}, ...]"""
    hits, rr = 0, 0.0
    for row in labelled:
        ranked, _ = retriever.retrieve(tenant_id, row["question"], k)
        sources = [c.source for c, _ in ranked]
        if row["expected_source"] in sources:
            hits += 1
            rr += 1.0 / (sources.index(row["expected_source"]) + 1)
    n = len(labelled)
    return EvalResult(n, hits / n if n else 0.0, rr / n if n else 0.0)
