# The RAG Assistant panel

**Live:** https://rag-assistant-h9o7.onrender.com

React, Vite, TypeScript in strict mode, Tailwind. It is the operator's view of
the assistant: what is indexed for a tenant, what the answer was, what it was
grounded in, and which way the graph went.

```bash
cd web
npm install
npm run dev     # http://localhost:5173, proxying /api to 127.0.0.1:8000
npm run build   # type check, then build into web/dist
npm test        # 13 tests
```

In development the panel runs on its own port and proxies `/api` to the running
API. In production FastAPI serves `web/dist` at `/`, so there is one origin and
no CORS to configure. `src/ragassistant/api.py` mounts it only if it has been
built, which is why the API has to work without it.

## What it shows, and why each part is there

- **Tenant switcher.** Isolation is the kind of claim nobody should take on
  trust. Index the sample documents under `acme`, switch to `globex`, ask the
  same question, and watch it come back with nothing to cite.
- **Documents.** The sample docs in one click, or paste your own. The file name
  you give is the name the citation will carry.
- **Four example questions.** One the assistant can ground, one where the detail
  matters, one with nothing to ground it in, and one prompt injection. Each takes
  a different route through the graph.
- **The answer, with its citations inline.** Every `[n]` in the text links to the
  chunk it came from, and each retrieved chunk is marked as either used in the
  answer or retrieved only. Those are different things, and the difference is
  how you judge whether an answer is really grounded.
- **Grounding confidence against the threshold.** The bar is how much of the
  question's content appears in the retrieved text; the line is the point below
  which the graph escalates rather than answering.
- **The route.** `guard → retrieve → grade → answer | escalate`, with the nodes
  this question actually passed through lit up, and the raw path underneath.
  "It escalated" is a claim; this is the evidence.

## Tests

`src/test/citations.test.ts` covers the `[n]` marker parsing, including the case
it gets wrong (a bracketed number that was never meant as a citation).
`src/test/panel.test.tsx` covers the answer, the route and the documents panel:
used-versus-retrieved, the escalation reason and the pattern that fired, the
confidence threshold, the skipped retrieval, and indexing pasted text under the
name given to it.

The API shapes these components are written against are checked on the Python
side in `tests/test_api.py`, so a renamed field fails there first.
