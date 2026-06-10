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
    return max(0.0, min(1.0, x))
