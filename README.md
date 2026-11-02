# RAG Assistant

A production-shaped Retrieval-Augmented Generation assistant: FastAPI backend, a
LangGraph workflow, source-grounded answers with citations, multi-tenant
isolation, a prompt-injection guard, and human escalation when the answer is not
reliable.

It runs end to end with no API key and no database, using a local embedder, an
in-memory vector store and a mock LLM. Switch to real embeddings, pgvector or
Qdrant, and OpenAI or Claude through environment variables.

Author: A. Amini

## What it does

- **Ingestion** (`ingest.py`): PDF or text to clean, overlapping chunks.
- **Embeddings** (`embeddings.py`): a local hashing embedder by default (no key),
  or OpenAI embeddings.
- **Vector store** (`vectorstore/`): in-memory by default; pgvector and Qdrant
  adapters included, each enforcing tenant isolation at query time.
- **Hybrid retrieval** (`retrieval.py`): dense (vector) and sparse (keyword)
  scores blended, with a grounding-confidence check.
- **LangGraph workflow** (`graph.py`): `guard -> retrieve -> grade -> answer`,
  with a first-class `escalate` path when confidence is low or a prompt-injection
  pattern is detected.
- **Grounded answers** (`llm.py`): every answer is built only from retrieved
  context and cites it as `[n]`. Mock, OpenAI and Claude behind one interface.
- **Multi-tenant isolation** (`vectorstore/`, `tenancy`): a query for one tenant
  cannot retrieve another tenant's chunks.
- **Prompt-injection guard** (`guards.py`): flags override/exfiltration patterns
  and labels retrieved text as data, not instructions.
- **Evaluation** (`eval.py`): hit@k and MRR on a labelled retrieval set.

## Run it

```bash
pip install -r requirements.txt
python demo.py                 # ingest sample docs, ask questions, see citations + escalation
python -m pytest tests/ -q     # tests: answering, escalation, tenant isolation, guard
uvicorn ragassistant.api:app --app-dir src --port 8000   # the API
```

API: `POST /api/ingest` ({tenant_id, documents:[{source,text}]}) and
`POST /api/chat` ({tenant_id, question}) returning the answer, citations and
whether it escalated.

## Configure (env)

`LLM_PROVIDER` mock|openai|anthropic, `EMBEDDER` local|openai,
`VECTOR_STORE` memory|pgvector|qdrant (`DATABASE_URL` / `QDRANT_URL`). See
`.env.example`.

## Answers to the brief's questions

- **Preventing cross-tenant access**: every store scopes a query to its
  `tenant_id`, so retrieval physically cannot return another tenant's chunks; the
  API takes the tenant from the authenticated request, not from the question.
- **Evaluating retrieval and reducing hallucinations**: `eval.py` scores
  retrieval (hit@k, MRR); answers are built only from retrieved context and must
  cite it; low grounding confidence escalates instead of guessing.
- **Multi-step workflows**: the LangGraph graph routes, retrieves, grades and
  escalates as explicit nodes, which is where tool-calling steps hang in
  production.

## What is reserved

This is a capability demonstration under an open-core model. Two parts that carry
the real production value are deliberately not published here; they are delivered
under a paid engagement. Both are present as working interfaces (calling them
raises `ReservedComponent`), so the architecture is complete and testable.

1. **Learned re-ranker** (`reranker.py`): the baseline returns a good shortlist;
   the trained cross-encoder that reorders it for answer quality, the single
   biggest lever on relevance and hallucination rate, is reserved.
2. **Hardened multi-tenant security policy** (`security.py`): the demo is safe by
   default (query-time tenant isolation and a baseline injection guard); the
   production policy engine (database row-level security, adversarially tested
   injection defense, output filtering, per-tenant policy) is reserved.

## License

See `LICENSE.txt`. Private portfolio sample; no reuse without written consent.
