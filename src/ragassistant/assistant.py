"""Wires the pieces together: embedder, vector store, retriever, LLM and graph."""
from __future__ import annotations

from .config import get_settings
from .embeddings import build_embedder
from .graph import build_graph
from .ingest import make_chunks
from .llm import build_llm
from .retrieval import Retriever
from .schemas import ChatResponse
from .vectorstore.factory import build_store


class Assistant:
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self.embedder = build_embedder(self.settings)
        self.store = build_store(self.settings)
        self.retriever = Retriever(self.store, self.embedder)
        self.llm = build_llm(self.settings)
        self.graph = build_graph(self.retriever, self.llm, self.settings)

    def ingest(self, tenant_id: str, documents: list[dict]) -> int:
        total = 0
        for doc in documents:
            chunks = make_chunks(tenant_id, doc["source"], doc["text"],
                                 self.settings.chunk_size, self.settings.chunk_overlap)
            if not chunks:
                continue
            vecs = self.embedder.embed([c.text for c in chunks])
            self.store.add(chunks, vecs)
            total += len(chunks)
        return total

    def chat(self, tenant_id: str, question: str) -> ChatResponse:
        result = self.graph.invoke({"tenant_id": tenant_id, "question": question})
        return ChatResponse(
            answer=result.get("answer", ""),
            citations=result.get("citations", []),
            escalated=bool(result.get("escalated", False)),
            reason=result.get("reason"),
        )
