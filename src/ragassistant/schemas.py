from __future__ import annotations

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    id: str
    tenant_id: str
    source: str
    chunk_index: int
    text: str


class Citation(BaseModel):
    n: int
    source: str
    chunk_id: str
    score: float
    snippet: str


class IngestRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    documents: list[dict]  # [{"source": "file.pdf", "text": "..."}]


class ChatRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    escalated: bool
    reason: str | None = None
    # Diagnostics. A grounded answer is only worth trusting if you can see what
    # it was grounded in, so the response carries the route the graph took, the
    # grounding confidence it was graded on, and any guard pattern that fired.
    path: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    flagged: list[str] = Field(default_factory=list)


class SourceSummary(BaseModel):
    source: str
    chunks: int
