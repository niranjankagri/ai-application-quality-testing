"""A small deterministic RAG-style target for repeatable evaluation examples."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_KNOWLEDGE_BASE = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.json"
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

_PROMPT_INJECTION_MARKERS = (
    "ignore all previous instructions",
    "reveal your hidden instructions",
    "system prompt",
    "stored passwords",
    "secret key",
)

_SAFE_REFUSAL = (
    "I can't reveal confidential instructions or credentials. "
    "I can help with supported account questions."
)
_NO_ANSWER = "I don't have that information in the provided help articles."


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_PATTERN.findall(text.casefold()))


def _load_articles() -> list[dict[str, Any]]:
    return json.loads(_KNOWLEDGE_BASE.read_text(encoding="utf-8"))


def retrieve_articles(question: str) -> list[dict[str, Any]]:
    """Return the best matching support article, or no article for unsupported questions."""
    question_tokens = _tokens(question)
    if not question_tokens:
        return []

    scored = []
    for article in _load_articles():
        overlap = question_tokens.intersection(article["keywords"])
        if overlap:
            scored.append((len(overlap), article["id"], article))

    if not scored:
        return []

    # Stable tie-breaking keeps evaluation results reproducible.
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [scored[0][2]]


def answer(question: str) -> str:
    """Answer from the fixed knowledge base and refuse injection-style requests."""
    normalized_question = question.casefold()
    if any(marker in normalized_question for marker in _PROMPT_INJECTION_MARKERS):
        return _SAFE_REFUSAL

    articles = retrieve_articles(question)
    if not articles:
        return _NO_ANSWER

    return articles[0]["response"]
