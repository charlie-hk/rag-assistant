---
title: RAG Assistant
emoji: 📚
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# RAG Assistant

A retrieval-augmented assistant that answers only from the documents you give
it, cites them, and routes anything it cannot ground to a human. This Space runs
the real backend: FastAPI, a LangGraph workflow, hybrid retrieval and the
multi-tenant store, with the React panel served from the same origin.

Load the sample documents, then try the four example questions. One is
answerable, one is not, and one is a prompt injection.

Two things to know about this demo specifically. It runs the mock model, so no
API key leaves anywhere and the answer is composed from the retrieved text
rather than written by a model. And the vector store is in memory in one shared
process, so anything you index is visible to anyone else looking at the same
time and is gone when the Space restarts.

Source code: https://github.com/charlie-hk/rag-assistant
