"""Hardened multi-tenant security policy — RESERVED (gap 2 of 2).

The public demo is safe by default: the vector store isolates tenants at query
time (a search for tenant A cannot return tenant B's rows), and guards.py flags
common prompt-injection patterns and labels retrieved text as data.

Production needs more than a safe default: database row-level security policies,
an adversarially tested injection rule set, output filtering for leaked secrets
or cross-tenant identifiers, and per-tenant policy configuration. That hardened
policy engine is reserved and delivered under a paid engagement.
"""
from __future__ import annotations


class ReservedComponent(NotImplementedError):
    pass


class HardenedPolicy:
    def enforce(self, tenant_id: str, question: str, answer: str) -> str:
        raise ReservedComponent(
            "The hardened security policy engine is reserved. The public demo relies "
            "on query-time tenant isolation and the baseline guard in guards.py."
        )
