"""End-to-end demo, no API key or database required.

Ingests the sample ACME docs for one tenant, asks a few questions (answered with
citations), shows the human-escalation path on an out-of-scope question, shows
tenant isolation, and runs a small retrieval evaluation.

    python demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from ragassistant.assistant import Assistant  # noqa: E402
from ragassistant.eval import evaluate  # noqa: E402

DOCS = Path(__file__).resolve().parent / "data/acme_docs"


def main():
    a = Assistant()
    docs = [{"source": p.name, "text": p.read_text()} for p in sorted(DOCS.glob("*.txt"))]
    n = a.ingest("acme", docs)
    print(f"ingested {n} chunks for tenant 'acme' "
          f"(llm={a.llm.name}, store={a.settings.vector_store}, embedder={a.embedder.name})\n")

    for q in [
        "How much is the Team plan?",
        "Can I get a refund after 20 days?",
        "How often are encryption keys rotated?",
    ]:
        r = a.chat("acme", q)
        print(f"Q: {q}")
        print(f"A: {r.answer}")
        if r.citations:
            print("   sources: " + ", ".join(f"[{c.n}] {c.source} ({c.score})" for c in r.citations[:3]))
        print()

    print("== Human escalation (out-of-scope question) ==")
    r = a.chat("acme", "What is the capital of France?")
    print(f"escalated={r.escalated}  reason={r.reason}\n")

    print("== Tenant isolation ==")
    r = a.chat("other-tenant", "How much is the Team plan?")
    print(f"tenant 'other-tenant' sees acme data? escalated={r.escalated} "
          f"(it cannot retrieve acme's chunks)\n")

    print("== Retrieval evaluation ==")
    labelled = [
        {"question": "refund policy", "expected_source": "billing.txt"},
        {"question": "data residency region", "expected_source": "security.txt"},
        {"question": "failed payment retry", "expected_source": "billing.txt"},
        {"question": "two-factor authentication", "expected_source": "security.txt"},
    ]
    print(evaluate(a.retriever, "acme", labelled).as_dict())


if __name__ == "__main__":
    main()
