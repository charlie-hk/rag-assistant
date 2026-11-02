"""Learned re-ranker — RESERVED (gap 1 of 2).

Baseline hybrid retrieval (retrieval.py) returns a good shortlist. In production,
a learned cross-encoder re-ranks that shortlist by how well each chunk actually
answers the question, which is the single biggest lever on answer quality and on
cutting hallucinations.

The interface is shown so the pipeline is complete and testable. The trained
cross-encoder, its training data and the fusion weights are delivered under a
paid engagement, not published here. Calling it raises ReservedComponent rather
than shipping a fake implementation.
"""
from __future__ import annotations

from .schemas import Chunk


class ReservedComponent(NotImplementedError):
    pass


class LearnedReranker:
    def rerank(self, question: str, candidates: list[tuple[Chunk, float]]
               ) -> list[tuple[Chunk, float]]:
        raise ReservedComponent(
            "The learned re-ranker is reserved. The public demo uses the baseline "
            "hybrid scores from retrieval.Retriever."
        )
