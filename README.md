# RAG Assistant

![RAG Assistant](docs/cover.png)

A production-shaped Retrieval-Augmented Generation assistant: FastAPI backend, a
LangGraph workflow, source-grounded answers with citations, multi-tenant
isolation, a prompt-injection guard, and human escalation when the answer is not
reliable.

It runs end to end with no API key and no database, using a local embedder, an
in-memory vector store and a mock LLM. Switch to real embeddings, pgvector or
Qdrant, and OpenAI or Claude through environment variables.

**[Open the live demo](https://rag-assistant.onrender.com)** - the real backend,
running this repository's code. It is on a free instance that sleeps when idle,
so the first request after a quiet spell takes about a minute to wake it.

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
- **Operator panel** (`web/`): React and TypeScript, served by the API itself.

## The panel

![The panel](docs/panel.png)

`web/` is a React and TypeScript panel for the assistant, served by FastAPI from
the same origin as the API. It is built to be used, not admired: index documents
for a tenant, ask, and see what the answer was actually grounded in.

- Every `[n]` in the answer links to the chunk it came from, and each retrieved
  chunk is marked **used in the answer** or **retrieved only**. Those are
  different things, and the difference is how you judge a RAG system.
- The grounding confidence is shown against the threshold it was graded on, so
  "why did this escalate" is answered on the screen.
- The route through the graph is drawn with the nodes this question passed
  through lit up, including retrieval being skipped when the guard stops a
  prompt injection.
- Two tenants, so isolation can be checked rather than believed: index under
  `acme`, switch to `globex`, ask the same question, get nothing.

```bash
cd web && npm install && npm run build   # into web/dist, served at /
cd .. && uvicorn ragassistant.api:app --app-dir src --port 8000
# http://localhost:8000
```

Or in one image:

```bash
docker build -t rag-assistant .
docker run -p 8000:8000 rag-assistant        # http://localhost:8000
```

That same image is what the hosted demo runs: `render.yaml` is a blueprint that
builds this Dockerfile on Render's free instance, with `/api/health` as the
health check. A host that assigns its own port sets `PORT`, which the image
honours.

## Run it

```bash
pip install -r requirements.txt
python demo.py                 # ingest sample docs, ask questions, see citations + escalation
python -m pytest tests/ -q     # 12 tests: answering, escalation, isolation, guard, the API
npm --prefix web test          # 13 more for the panel
uvicorn ragassistant.api:app --app-dir src --port 8000   # the API, and the panel if built
```

The API:

```
GET    /api/health                      what is wired: model, store, embedder, thresholds
GET    /api/samples                     the bundled sample documents
POST   /api/ingest                      {tenant_id, documents:[{source,text}]}
GET    /api/sources?tenant_id=          what that tenant has indexed, per source
DELETE /api/sources?tenant_id=          remove one tenant's data
POST   /api/chat                        {tenant_id, question}
```

A chat reply carries the answer and its citations, whether it escalated and why,
the grounding confidence, the route the graph took, and any guard pattern that
fired. The diagnostics are part of the contract, not a debug extra: an answer you
cannot inspect is an answer you cannot trust.

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
