"""
mai_rag.evals — the seventeen-engine evaluator suite plus the golden-set runner
that persists every run into the data layer.

  8 native (llm_judge, the RAG triad, semantic_similarity, contains, exact_match)
  3 safety (pii_exposure, harmful_intent, relevancy)
  3 retrieval (recall_at_k, mrr, hit_at_1) — KEYLESS; score the retriever itself,
    so a regressed retriever can't hide behind a plausible answer
  3 perf (latency_budget, token_budget, call_budget) — KEYLESS; cost and latency
    as eval dimensions, because a quality-only scorecard makes everything look free

Pluggable backends: the four RAG metrics can run as `native` (the from-scratch
code in native.py), `ragas`, or `deepeval` — same Score shape either way, so the
golden set / viz / gate never care which ran. That is the foil/reference spine
made literal: concept you build → the libraries → production. Diffing them is the
lesson — a metric you've never compared to a second implementation is faith.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from ..store import Store
from .base import EvalInput, Score
from . import native, safety, retrieval, perf

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
    # Retrieval engines — KEYLESS, deterministic. They score the RETRIEVER against the
    # supporting docs the golden set labels, so a regressed retriever can't hide behind a
    # plausible answer. Need EvalInput.retrieved + .supporting (see evals/retrieval.py).
    "recall_at_k": retrieval.recall_at_k,
    "mrr": retrieval.mrr,
    "hit_at_1": retrieval.hit_at_1,
    # Cost/latency engines — keyless. Need EvalInput.meta {"ms","tokens","calls"} from a
    # metered run (llm.METER). Quality-only scorecards make every technique look free.
    "latency_budget": perf.latency_budget,
    "token_budget": perf.token_budget,
    "call_budget": perf.call_budget,
}

# Engines that need no LLM at all — safe to run everywhere, free, deterministic.
KEYLESS_NAMES = {"contains", "exact_match", "semantic_similarity",
                 "recall_at_k", "mrr", "hit_at_1",
                 "latency_budget", "token_budget", "call_budget"}

RAGAS_NAMES = {"faithfulness", "answer_relevancy", "context_precision", "context_recall"}

# A sensible default that touches all three layers (retrieval / generation / safety).
DEFAULT_SUITE = [
    "context_precision", "context_recall",      # retrieval
    "faithfulness", "answer_relevancy",          # generation
    "pii_exposure", "relevancy",                 # safety
]


def _resolve(name: str, backend: str):
    # Three implementations of the same four RAG metrics — same EvalInput in, same Score
    # out, so the golden set / viz / gate never care which one ran. Diffing them is the
    # lesson: a metric you've never compared to a second implementation is faith, not data.
    if backend == "ragas" and name in RAGAS_NAMES:
        from . import ragas_backend
        return lambda e: ragas_backend.score(name, e)
    if backend == "deepeval" and name in RAGAS_NAMES:
        from . import deepeval_backend
        return lambda e: deepeval_backend.score(name, e)
    try:
        return REGISTRY[name]
    except KeyError:
        raise KeyError(f"unknown evaluator {name!r}. Available: "
                       f"{', '.join(sorted(REGISTRY))}") from None


def evaluate(e: EvalInput, evaluators=None, backend: str = "native") -> list[Score]:
    out: list[Score] = []
    for name in (evaluators or DEFAULT_SUITE):
        # One flaky judge call (malformed JSON, 429, timeout) must not cost the
        # student the other metrics — score it 0 and say so, loudly, in the reasoning.
        try:
            sc = _resolve(name, backend)(e)
        except Exception as ex:
            print(f"[mai_rag.evals] evaluator {name!r} failed "
                  f"({type(ex).__name__}: {str(ex)[:120]}) — scored 0.0, run continues",
                  file=sys.stderr)
            sc = Score(name, 0.0, False, f"evaluator error: {type(ex).__name__}")
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
    skipped: list = []
    golden_set = list(golden_set)   # may be a generator; we report a count below
    for case in golden_set:
        # Isolate the case: a RAG failure on one question (timeout, 429, a bad
        # answer shape) must not throw away the cases already scored. We commit
        # per-case below so a crash mid-suite still leaves a readable run.
        try:
            out = rag_fn(store, case.question)
            answer = out.get("answer", "") if isinstance(out, dict) else str(out)
            contexts = out.get("contexts", []) if isinstance(out, dict) else []
        except Exception as ex:
            print(f"[mai_rag.evals] case {case.id!r} failed "
                  f"({type(ex).__name__}: {str(ex)[:120]}) — skipped, run continues",
                  file=sys.stderr)
            skipped.append(case.id)
            store.commit()
            continue
        e = EvalInput(question=case.question, answer=answer,
                      contexts=contexts, expected=case.expected,
                      criteria=case.criteria)
        for sc in evaluate(e, evaluators=evaluators, backend=backend):
            store.conn.execute(
                "INSERT INTO eval_results (run_id, case_id, evaluator, score, passed, reasoning) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (run_id, case.id, sc.evaluator, sc.score, int(sc.passed), sc.reasoning),
            )
            results.append({"case_id": case.id, "evaluator": sc.evaluator,
                            "score": sc.score, "passed": sc.passed, "reasoning": sc.reasoning})
        store.commit()   # per-case, so a crash mid-suite keeps what's scored so far
    if skipped:
        print(f"[mai_rag.evals] {len(skipped)}/{len(golden_set)} case(s) skipped: "
              f"{', '.join(str(s) for s in skipped)} — the scorecard below covers the rest",
              file=sys.stderr)
    return {"run_id": run_id, "label": label, "results": results,
            "skipped": skipped, "summary": aggregate(results)}
