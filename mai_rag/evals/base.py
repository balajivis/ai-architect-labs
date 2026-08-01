"""Shared types for the evaluator engines."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvalInput:
    """Everything an evaluator might need. Each engine uses the subset it cares
    about and returns None when it does not apply (e.g. no reference answer)."""
    question: str
    answer: str
    contexts: list[str]
    expected: str = ""
    criteria: list[str] = field(default_factory=list)
    # ── retrieval evidence (optional) — what the retriever RETURNED vs what the golden
    # case says SHOULD have been found. Both are doc ids/sources in rank order; supply
    # them and the keyless retrieval engines (recall_at_k / mrr / hit_at_1) light up.
    retrieved: list[str] = field(default_factory=list)
    supporting: list[str] = field(default_factory=list)
    # ── run telemetry (optional) — {"ms": float, "tokens": int, "calls": int}. Lets cost
    # and latency be scored as first-class eval dimensions, not a footnote.
    meta: dict = field(default_factory=dict)


@dataclass
class Score:
    evaluator: str
    score: float          # normalized to [0, 1]
    passed: bool
    reasoning: str = ""


def clamp01(x) -> float:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return 0.0
    if x != x:   # NaN is how RAGAS reports a FAILED metric — min(1.0, nan) is 1.0, so
        return 0.0   # without this a broken metric prints as a perfect score.
    return max(0.0, min(1.0, x))
