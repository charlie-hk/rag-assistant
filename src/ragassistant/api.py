from fastapi import FastAPI

from .assistant import Assistant
from .schemas import ChatRequest, ChatResponse, IngestRequest

app = FastAPI(title="RAG Assistant")
assistant = Assistant()


@app.get("/api/health")
def health():
    return {"status": "ok", "llm": assistant.llm.name,
            "store": assistant.settings.vector_store, "embedder": assistant.embedder.name}


@app.post("/api/ingest")
def ingest(req: IngestRequest):
    n = assistant.ingest(req.tenant_id, req.documents)
    return {"tenant_id": req.tenant_id, "chunks_indexed": n}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return assistant.chat(req.tenant_id, req.question)
