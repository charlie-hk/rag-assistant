r"""The assistant as a LangGraph workflow.

Flow:
    guard -> retrieve -> grade --(confident)--> answer --> END
                               \--(not confident / injection)--> escalate --> END

Each node is small and pure. The graph is what the job brief calls the
"LangGraph workflow for query routing, retrieval, tool calling and human
escalation": routing is the grade step, retrieval is its own node, the answer
node is where a tool call would hang, and escalation is a first-class path.
"""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from . import guards
from .retrieval import Retriever, to_citations
from .schemas import Citation


class State(TypedDict, total=False):
    tenant_id: str
    question: str
    chunks: list
    citations: list
    confidence: float
    answer: str
    escalated: bool
    reason: str


def build_graph(retriever: Retriever, llm, settings):
    def guard(state: State) -> State:
        if guards.is_suspicious(state["question"]):
            return {"escalated": True, "reason": "Flagged possible prompt injection in the question."}
        return {}

    def retrieve(state: State) -> State:
        if state.get("escalated"):
            return {}
        ranked, confidence = retriever.retrieve(state["tenant_id"], state["question"], settings.top_k)
        return {"chunks": ranked, "citations": to_citations(ranked), "confidence": confidence}

    def grade(state: State) -> str:
        # Routing decision: answer only when the best match is confident enough.
        if state.get("escalated"):
            return "escalate"
        if not state.get("chunks") or state.get("confidence", 0.0) < settings.min_confidence:
            return "escalate"
        return "answer"

    def answer(state: State) -> State:
        ranked = state["chunks"]
        context = guards.wrap_context([c.text for c, _ in ranked])
        text = llm.answer(settings.system_prompt, state["question"], context)
        return {"answer": text, "escalated": False}

    def escalate(state: State) -> State:
        reason = state.get("reason") or "No sufficiently relevant document was found."
        return {
            "answer": "I can't answer this reliably from your documents, so I'm routing it to a human.",
            "escalated": True,
            "reason": reason,
            "citations": state.get("citations", []),
        }

    g = StateGraph(State)
    g.add_node("guard", guard)
    g.add_node("retrieve", retrieve)
    g.add_node("answer", answer)
    g.add_node("escalate", escalate)

    g.set_entry_point("guard")
    g.add_edge("guard", "retrieve")
    g.add_conditional_edges("retrieve", grade, {"answer": "answer", "escalate": "escalate"})
    g.add_edge("answer", END)
    g.add_edge("escalate", END)
    return g.compile()
