"""LLM behind one interface, so the graph does not care which model answers.

The default is a mock that composes a grounded answer from the retrieved context
and cites it, so the whole pipeline runs and is testable with no API key. Set
LLM_PROVIDER to openai, anthropic or gemini for a real model.
"""
from __future__ import annotations


class LLMError(RuntimeError):
    pass


def _trim(text: str, limit: int) -> str:
    """Cut at the last sentence that fits, rather than mid-word. A quoted answer
    that stops half way through a sentence looks like a bug to whoever reads it."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if end > limit // 3:
        return cut[: end + 1]
    return cut.rsplit(" ", 1)[0] + "..."


class MockLLM:
    name = "mock"

    def answer(self, system: str, question: str, context: str) -> str:
        # Pull the first context block as the grounded basis and cite it.
        first = ""
        if "[1]" in context:
            after = context.split("[1]", 1)[1]
            first = _trim(after.split("[2]", 1)[0].strip(), 240)
        if not first:
            return "I don't know based on the provided documents."
        return f"Based on the documents: {first} [1]"


class OpenAILLM:
    name = "openai"

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMError("OpenAI selected but LLM_API_KEY is empty.")
        from openai import OpenAI

        self._c = OpenAI(api_key=api_key)
        self._m = model or "gpt-4o-mini"

    def answer(self, system: str, question: str, context: str) -> str:
        r = self._c.chat.completions.create(
            model=self._m,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"{context}\n\nQuestion: {question}"},
            ],
        )
        return r.choices[0].message.content or ""


class AnthropicLLM:
    name = "anthropic"

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMError("Anthropic selected but LLM_API_KEY is empty.")
        from anthropic import Anthropic

        self._c = Anthropic(api_key=api_key)
        self._m = model or "claude-3-5-sonnet-latest"

    def answer(self, system: str, question: str, context: str) -> str:
        r = self._c.messages.create(
            model=self._m, system=system, max_tokens=800,
            messages=[{"role": "user", "content": f"{context}\n\nQuestion: {question}"}],
        )
        return "".join(b.text for b in r.content if hasattr(b, "text"))


def build_llm(settings):
    p = settings.llm_provider
    if p == "mock":
        return MockLLM()
    if p == "openai":
        return OpenAILLM(settings.llm_api_key, settings.llm_model)
    if p == "anthropic":
        return AnthropicLLM(settings.llm_api_key, settings.llm_model)
    raise LLMError(f"Unknown llm_provider: {p}")
