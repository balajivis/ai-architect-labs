"""
mai_rag.evals — the nine-engine evaluator suite (mirrors Kapi's registry) plus
the golden-set runner that persists every run into the data layer.

Pluggable RAGAS backend: the four RAG metrics can run as `native` (the
from-scratch code in native.py) or `ragas` (the real library) — same Score
shape either way. This is the foil/reference spine made literal: concept you
build → RAGAS the library → Kapi's native TS in production.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from ..store import Store
from .base import EvalInput, Score
from . import native, safety

# name → native callable
REGISTRY = {
    "llm_judge": native.llm_judge,
    "faithfulness": native.faithfulness,
    "answer_relevancy": native.answer_relevancy,
    "context_precision": native.context_precision,
    "context_recall": native.context_recall,
    "semantic_similarity": native.semantic_similarity,
    "contains": native.contains,
    "exact_match": native.exact_match,
    "pii_exposure": safety.pii_exposure,
    "harmful_intent": safety.harmful_intent,
    "relevancy": safety.relevancy,
}

RAGAS_NAMES = {"faithfulness", "answer_relevancy", "context_precision", "context_recall"}

# A sensible default that touches all three layers (retrieval / generation / safety).
DEFAULT_SUITE = [
    "context_precision", "context_recall",      # retrieval
    "faithfulness", "answer_relevancy",          # generation
    "pii_exposure", "relevancy",                 # safety
]


def _resolve(name: str, backend: str):
    if backend == "ragas" and name in RAGAS_NAMES:
        from . import ragas_backend
        return lambda e: ragas_backend.score(name, e)
    return REGISTRY[name]


def evaluate(e: EvalInput, evaluators=DEFAULT_SUITE, backend: str = "native") -> list[Score]:
    out: list[Score] = []
    for name in evaluators:
        sc = _resolve(name, backend)(e)
        if sc is not None:
            out.append(sc)
    return out


def aggregate(results: list[dict]) -> dict[str, float]:
    """Mean score per evaluator across all cases."""
    buckets: dict[str, list[float]] = {}
    for r in results:
        buckets.setdefault(r["evaluator"], []).append(r["score"])
    return {k: sum(v) / len(v) for k, v in buckets.items()}


def run_suite(store: Store, golden_set, rag_fn, label: str,
              module: str = "module-1-eval-first",
              evaluators=DEFAULT_SUITE, backend: str = "native") -> dict:
    """Run `rag_fn(store, question)` over every golden case, score it with the
    suite, and persist an eval_run + eval_results. Returns
    {run_id, label, results, summary}. The persisted run is what
    `viz.compare()` reads later — Module 2 just appends another."""
    cur = store.conn.execute(
        "INSERT INTO eval_runs (label, module, config, created_at) VALUES (?, ?, ?, ?)",
        (label, module, json.dumps({"backend": backend, "evaluators": evaluators}),
         datetime.now(timezone.utc).isoformat()),
    )
    run_id = int(cur.lastrowid)

    results: list[dict] = []
    for case in golden_set:
        out = rag_fn(store, case.question)
        e = EvalInput(question=case.question, answer=out["answer"],
                      contexts=out.get("contexts", []), expected=case.expected,
                      criteria=case.criteria)
        for sc in evaluate(e, evaluators=evaluators, backend=backend):
            store.conn.execute(
                "INSERT INTO eval_results (run_id, case_id, evaluator, score, passed, reasoning) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, case.id, sc.evaluator, sc.score, int(sc.passed), sc.reasoning),
            )
            results.append({"case_id": case.id, "evaluator": sc.evaluator,
                            "score": sc.score, "passed": sc.passed, "reasoning": sc.reasoning})
    store.commit()
    return {"run_id": run_id, "label": label, "results": results, "summary": aggregate(results)}
