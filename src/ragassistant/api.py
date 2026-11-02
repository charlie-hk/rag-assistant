"""HTTP API, and the panel in web/ served from the same origin.

Thin on purpose: the tenant comes from the request, every rule lives in the
graph, and the endpoints only translate. The panel calls exactly these.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .assistant import Assistant
from .schemas import ChatRequest, ChatResponse, IngestRequest, SourceSummary

app = FastAPI(title="RAG Assistant")
assistant = Assistant()

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DOCS = ROOT / "data" / "acme_docs"
PANEL = ROOT / "web" / "dist"


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm": assistant.llm.name,
        "store": assistant.settings.vector_store,
        "embedder": assistant.embedder.name,
        "top_k": assistant.settings.top_k,
        "min_confidence": assistant.settings.min_confidence,
        "chunk_size": assistant.settings.chunk_size,
    }


@app.post("/api/ingest")
def ingest(req: IngestRequest):
    for doc in req.documents:
        if not doc.get("source") or not str(doc.get("text", "")).strip():
            raise HTTPException(422, "each document needs a source and some text")
    n = assistant.ingest(req.tenant_id, req.documents)
    return {"tenant_id": req.tenant_id, "chunks_indexed": n,
            "sources": [SourceSummary(source=s, chunks=c) for s, c in assistant.sources(req.tenant_id)]}


@app.get("/api/sources")
def sources(tenant_id: str):
    return {"tenant_id": tenant_id,
            "sources": [SourceSummary(source=s, chunks=c) for s, c in assistant.sources(tenant_id)]}


@app.delete("/api/sources")
def clear(tenant_id: str):
    return {"tenant_id": tenant_id, "chunks_removed": assistant.clear(tenant_id)}


@app.get("/api/samples")
def samples():
    """The bundled ACME documents, so the panel can fill a tenant in one click."""
    if not SAMPLE_DOCS.is_dir():
        return {"documents": []}
    return {"documents": [{"source": p.name, "text": p.read_text(encoding="utf-8")}
                          for p in sorted(SAMPLE_DOCS.glob("*.txt"))]}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return assistant.chat(req.tenant_id, req.question)


# Served last so it never shadows /api. Absent until `npm run build` in web/,
# which is why the API has to work on its own.
if (PANEL / "index.html").is_file():
    app.mount("/", StaticFiles(directory=str(PANEL), html=True), name="panel")
