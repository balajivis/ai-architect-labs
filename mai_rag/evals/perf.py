"""
mai_rag.evals.perf — cost and latency as EVAL DIMENSIONS, not a footnote.

A system that answers perfectly in nine seconds and 40k tokens may be worse, in
production, than one that answers well in one second and 3k. Quality-only scorecards
can't say that — so every technique looks "free" and the ladder always argues for more.
These engines put the price on the same scorecard as the score.

They read `EvalInput.meta`, which the caller fills from a metered run:

    from mai_rag import llm
    llm.METER.reset()
    t0 = time.time(); out = my_system(q); ms = (time.time() - t0) * 1000
    e = EvalInput(q, out["answer"], out["contexts"], expected=...,
                  meta={"ms": ms, **llm.METER.snapshot()})   # tokens, calls

Scoring is a BUDGET, not a curve: 1.0 while you're inside it, degrading linearly to 0.0
at twice the budget. Budgets are product decisions — a chat assistant and a nightly batch
job have different ones — so they're overridable per call, and the defaults are declared
here in one place rather than buried in a notebook.
"""
from __future__ import annotations

from .base import EvalInput, Score

# Defaults: one interactive answer. Override per system/product.
LATENCY_BUDGET_MS = 4000.0
TOKEN_BUDGET = 8000
CALL_BUDGET = 6


def _budget_score(value: float, budget: float) -> float:
    """1.0 inside budget → linear decay → 0.0 at 2× budget. Cheap, legible, gate-able."""
    if budget <= 0:
        return 0.0
    if value <= budget:
        return 1.0
    if value >= 2 * budget:
        return 0.0
    return 1.0 - (value - budget) / budget


def latency_budget(e: EvalInput, budget_ms: float = LATENCY_BUDGET_MS) -> Score | None:
    """Wall-clock for one answer, scored against a latency budget."""
    ms = (e.meta or {}).get("ms")
    if ms is None:
        return None
    s = _budget_score(float(ms), budget_ms)
    return Score("latency_budget", s, s >= 0.999,
                 f"{float(ms):.0f}ms vs {budget_ms:.0f}ms budget")


def token_budget(e: EvalInput, budget: int = TOKEN_BUDGET) -> Score | None:
    """Total tokens (prompt + completion) for one answer, scored against a cost budget."""
    tok = (e.meta or {}).get("tokens")
    if tok is None:
        return None
    s = _budget_score(float(tok), float(budget))
    return Score("token_budget", s, s >= 0.999, f"{int(tok)} tokens vs {budget} budget")


def call_budget(e: EvalInput, budget: int = CALL_BUDGET) -> Score | None:
    """LLM calls per answer — the knob that actually drives latency AND rate limits."""
    calls = (e.meta or {}).get("calls")
    if calls is None:
        return None
    s = _budget_score(float(calls), float(budget))
    return Score("call_budget", s, s >= 0.999, f"{int(calls)} LLM call(s) vs {budget} budget")
