# -*- coding: utf-8 -*-
"""The eval gate, as a test. Lab 5's last stage, wired into CI.

Modern AI Pro · AI Architect · Pillar II · Evals & Benchmarks

Lab 5 ends by saying: *"in CI this verdict IS the assert — a red gate blocks the
merge, and no un-evaluated change reaches production."* This file is that assert.
It is the whole course's central claim made executable, and it is meant to be
**copied into your own repo** — see `tests/README.md`.

The rule, in one line:

    the candidate ships only if the HEADLINE metric rises, and NOTHING regresses.

Two levels of protection live here, on purpose:

  1. `test_eval_registry_and_deterministic_engines` — **keyless**. Always runs,
     even on a fork with no secrets. It proves the eval machinery itself is intact
     (the engines are registered, and a deterministic engine scores correctly).
     Cheap, fast, zero LLM calls. This is your smoke alarm.

  2. `test_no_metric_regresses` + `test_headline_metric_improves` — **the real
     gate**. Needs an LLM key. Scores a baseline system and a candidate system on
     the same golden cases with the same metrics, then asserts the rule above.

If no key is configured the gated tests SKIP rather than fail — CI on a fork
with no secrets must be GREEN, not red. A skipped gate is honest ("we didn't
measure"); a red gate is a claim ("we measured, and it got worse"). Never
conflate the two.

To adapt this to YOUR app, change exactly two functions: `baseline_system` and
`candidate_system`. Everything else — the metrics, the tolerance, the rule — is
already the thing you want.
"""
from __future__ import annotations

import os

import pytest

from mai_rag import evals
from mai_rag.evals.base import EvalInput

# ── the key check, done ONCE at import time ──────────────────────────────────
# `mai_rag.llm._provider()` is the single chokepoint that resolves GROQ / OPENAI /
# AZURE / GEMINI from the environment. It RAISES when nothing is configured, so a
# try/except around it is the honest "can we reach a model at all?" question.
# Asked once, at import — a keyless CI job then pays nothing for the gated tests.
try:
    from mai_rag import llm

    _PROVIDER: str | None = llm._provider()
except Exception:  # noqa: BLE001 — any resolution failure means "no key", full stop
    _PROVIDER = None

# One mark, applied to every test that needs a model. Read the reason string in
# the CI log: "skipped — no LLM key configured" is a fact, not a failure.
#
# Why a mark and not `pytest.skip("no LLM key configured", allow_module_level=True)`:
# a module-level skip is evaluated at COLLECTION time and takes the whole file with
# it — including the keyless test below, which is precisely the one that must still
# run on a fork with no secrets. Use `allow_module_level=True` only if you split the
# gated tests into their own file. We keep them together so a student copies ONE file.
requires_llm = pytest.mark.skipif(_PROVIDER is None, reason="no LLM key configured")


# ─────────────────────────────────────────────────────────────────────────────
# 1. THE KEYLESS TEST — always runs, no model, no money, no secrets.
# ─────────────────────────────────────────────────────────────────────────────
# CI signal you get for free. If someone renames an evaluator or breaks the
# registry wiring, this goes red on every PR — including PRs from forks that
# will never have your API key.

EXPECTED_ENGINES = {
    # retrieval
    "context_precision", "context_recall",
    # generation
    "llm_judge", "faithfulness", "answer_relevancy", "semantic_similarity",
    # deterministic (no model call)
    "contains", "exact_match",
    # safety — these are EVALUATORS, not a regex. That is the course's hard rule.
    "pii_exposure", "harmful_intent", "relevancy",
}


def test_eval_registry_and_deterministic_engines():
    """The eval machinery is intact — and a deterministic engine scores correctly."""
    # (a) every engine the suite advertises is actually registered and callable
    missing = EXPECTED_ENGINES - set(evals.REGISTRY)
    assert not missing, f"evaluator(s) vanished from the REGISTRY: {sorted(missing)}"
    assert all(callable(fn) for fn in evals.REGISTRY.values())

    # (b) the default suite touches all three layers — retrieval, generation, safety.
    #     A suite that only grades generation cannot tell you WHERE it broke.
    assert set(evals.DEFAULT_SUITE) <= set(evals.REGISTRY)
    assert {"context_precision", "context_recall"} & set(evals.DEFAULT_SUITE)
    assert {"faithfulness", "answer_relevancy"} & set(evals.DEFAULT_SUITE)

    # (c) end-to-end through the real `evaluate()` entry point, on a hand-built
    #     EvalInput, using engines that never call a model. Same code path the
    #     gated test uses — just with the LLM taken out of the loop.
    hit = EvalInput(
        question="Which pillar covers evals?",
        answer="Pillar II covers evals and benchmarks, including RAGAS.",
        contexts=["The AI Architect course has four pillars."],
        expected="Pillar II covers evals and benchmarks, including RAGAS.",
        criteria=["Pillar II", "RAGAS"],
    )
    scores = {s.evaluator: s for s in evals.evaluate(hit, evaluators=["contains", "exact_match"])}
    assert scores["contains"].score == 1.0 and scores["contains"].passed
    assert scores["exact_match"].score == 1.0 and scores["exact_match"].passed

    # ...and the same engines must be able to say NO. A metric that only ever
    # returns 1.0 is decor. Half the criteria present → 0.5; different text → 0.0.
    miss = EvalInput(
        question=hit.question,
        answer="Pillar II covers evals.",          # 'RAGAS' missing on purpose
        contexts=hit.contexts,
        expected=hit.expected,
        criteria=hit.criteria,
    )
    scores = {s.evaluator: s for s in evals.evaluate(miss, evaluators=["contains", "exact_match"])}
    assert scores["contains"].score == 0.5 and not scores["contains"].passed
    assert scores["exact_match"].score == 0.0 and not scores["exact_match"].passed

    # (d) engines return None when they don't apply (no criteria / no reference),
    #     and `evaluate()` drops them rather than scoring a phantom 0.0.
    #     Silently scoring an inapplicable metric as zero is how dashboards lie.
    bare = EvalInput(question="q", answer="a", contexts=[])
    assert evals.evaluate(bare, evaluators=["contains", "exact_match"]) == []

    # (e) aggregate() means per evaluator — the arithmetic the gate is built on.
    agg = evals.aggregate([
        {"evaluator": "faithfulness", "score": 1.0},
        {"evaluator": "faithfulness", "score": 0.5},
        {"evaluator": "answer_relevancy", "score": 0.8},
    ])
    assert agg == {"faithfulness": 0.75, "answer_relevancy": 0.8}


# ─────────────────────────────────────────────────────────────────────────────
# 2. THE GATE — the real thing. Needs a key.
# ─────────────────────────────────────────────────────────────────────────────
# Everything below is marked `@requires_llm`: with no key these SKIP and the job
# stays green, with the keyless test above still executed. Nothing here costs a
# model call until a test actually runs — the fixtures are lazy.
from mai_rag import corpus
from mai_rag.baseline import naive_rag


# ── the knobs ────────────────────────────────────────────────────────────────
GATE_METRICS = ["faithfulness", "answer_relevancy"]
HEADLINE = "faithfulness"     # the one metric that must actually IMPROVE

# The noise floor. Judges wobble; a move smaller than EPS is not a result.
# Lab 5 uses 0.02 over the whole gradable golden set. CI scores a 4-case SAMPLE,
# and the noise in a mean scales with 1/√n — so the CI tolerance is wider on
# purpose. Tighten it back toward 0.02 as you raise EVAL_GATE_CASES.
EPS = 0.05

# Cheap by default. Each case costs (1 generation + 2 judge calls) × 2 systems, so
# 4 cases ≈ 24 model calls — a handful, not hundreds. Raise it when you want a
# result you'd bet a release on; 4 is enough to catch a system that broke outright.
CASES = int(os.getenv("EVAL_GATE_CASES", "4"))

# In-corpus tags only. `needs-web` / `no-retrieval` cases are Lab 3 ROUTER
# behaviours — grading a retrieval metric on a question the corpus can't answer
# measures nothing and adds noise to the gate.
GRADABLE_TAGS = ("site", "topic", "multi-hop")


@pytest.fixture(scope="session")
def store():
    """The corpus, embedded once per test session (keyless MiniLM, ~15-25s)."""
    return corpus.load_catalog_corpus()


@pytest.fixture(scope="session")
def golden():
    cases = [c for c in corpus.load_golden_catalog() if c["tag"] in GRADABLE_TAGS]
    assert cases, "golden set is empty — the gate has nothing to measure"
    return cases[:CASES]


# ── THE TWO FUNCTIONS YOU CHANGE ─────────────────────────────────────────────
# Swap these for your own app's "what's in production" and "what this PR does".
# Each takes (store, question) and returns {"answer": str, "contexts": list[str]}
# — that is the shape every evaluator expects. Nothing else in this file moves.
#
# The pair shipped here makes the course's FIRST claim executable: that grounding
# an answer in retrieved context beats the model answering from memory. It is a
# claim, so it gets measured, every PR, like everything else in this course.

_NAKED = "Answer the question.\n\nQuestion: {q}\n\nAnswer:"


def baseline_system(store, question: str) -> dict:
    """WHAT'S IN PRODUCTION TODAY — here, the model alone. No retrieval.

    `contexts` is empty, which is not a trick: it is what ungrounded generation
    IS. faithfulness asks "which of these claims does the context support?" and
    an empty context supports none of them. The answer can still be fluent,
    plausible, and completely unverifiable — which is the failure mode the whole
    course exists to make visible.

    (It ignores `store` on purpose; the signature stays symmetric so you can swap
    in a retrieval-based baseline without touching anything below.)
    """
    return {"answer": llm.complete(_NAKED.format(q=question), tier="small"),
            "contexts": []}


def candidate_system(store, question: str) -> dict:
    """WHAT THIS PR SHIPS — here, Lab 1's naive RAG: retrieve top-4, then answer.

    In your repo this is your new chunker, your reranker, your agent — whatever
    the diff actually changes. The gate does not care what you changed; it only
    cares whether the golden set noticed.
    """
    return naive_rag(store, question, k=4)


# ── the machinery (you shouldn't need to touch this) ─────────────────────────

def score_system(store, cases, system_fn) -> dict[str, float]:
    """Run one system over every golden case and return {metric: mean score}."""
    results: list[dict] = []
    for c in cases:
        out = system_fn(store, c["q"])
        e = EvalInput(question=c["q"], answer=out["answer"],
                      contexts=out["contexts"], expected=c["expected"])
        results += [{"evaluator": s.evaluator, "score": s.score}
                    for s in evals.evaluate(e, evaluators=GATE_METRICS)]
    return evals.aggregate(results)


@pytest.fixture(scope="session")
def gate(store, golden) -> dict:
    """Score both systems once; the assertions below read the same numbers.

    Session-scoped on purpose — splitting the gate into several asserts must not
    multiply the API bill. Measure once, assert many.
    """
    return {
        "baseline": score_system(store, golden, baseline_system),
        "candidate": score_system(store, golden, candidate_system),
        "n_cases": len(golden),
    }


def _table(gate: dict) -> str:
    """A readable verdict in the pytest failure output. When a gate goes red the
    first question is always 'which metric, and by how much' — answer it here."""
    base, cand = gate["baseline"], gate["candidate"]
    lines = [f"\n  eval gate · {gate['n_cases']} golden cases · provider={_PROVIDER}",
             f"  {'metric':<20}{'baseline':>10}{'candidate':>11}{'Δ':>9}   verdict"]
    for m in GATE_METRICS:
        if m not in base or m not in cand:        # never crash while explaining a failure
            lines.append(f"  {m:<20}{'—':>10}{'—':>11}{'—':>9}   NOT MEASURED")
            continue
        d = cand[m] - base[m]
        verdict = "REGRESSION" if d < -EPS else ("↑" if d > EPS else "flat")
        lines.append(f"  {m:<20}{base[m]:>10.3f}{cand[m]:>11.3f}{d:>+9.3f}   {verdict}")
    return "\n".join(lines)


@requires_llm
def test_gate_measured_every_metric(gate):
    """Sanity: the gate actually produced a number for every metric it claims to
    guard. A metric that silently returned nothing is an un-guarded metric — and
    an un-guarded metric is exactly how a regression reaches production."""
    for side in ("baseline", "candidate"):
        missing = [m for m in GATE_METRICS if m not in gate[side]]
        assert not missing, f"{side} produced no score for {missing}{_table(gate)}"


@requires_llm
def test_no_metric_regresses(gate):
    """NOTHING MAY REGRESS. Half the gate — and the half people forget.

    It is easy to raise faithfulness by making the system refuse everything;
    answer_relevancy is what catches that trade. A candidate that wins one metric
    by wrecking another has not improved the system, it has moved the failure.
    """
    base, cand = gate["baseline"], gate["candidate"]
    regressed = [m for m in GATE_METRICS if cand[m] < base[m] - EPS]
    assert not regressed, (
        f"🔴 GATE FAIL — regression in {regressed}. Merge blocked.{_table(gate)}\n"
        f"  (tolerance EPS={EPS}; a drop smaller than that is judge noise, not a regression)"
    )


@requires_llm
def test_headline_metric_improves(gate):
    """THE HEADLINE MUST RISE. The other half.

    'Nothing regressed' is not a reason to merge — it's a reason to ask what the
    change was for. A PR that claims to improve the system has to show it on the
    golden set, beyond the noise floor.
    """
    base, cand = gate["baseline"][HEADLINE], gate["candidate"][HEADLINE]
    assert cand > base + EPS, (
        f"🔴 GATE FAIL — headline '{HEADLINE}' did not rise: "
        f"{base:.3f} → {cand:.3f} (needs > +{EPS}). Merge blocked.{_table(gate)}\n"
        f"  Read the deltas before you touch this assert. Three honest outcomes:\n"
        f"    · the candidate genuinely isn't better — fix the candidate, not the gate;\n"
        f"    · {gate['n_cases']} cases can't resolve the difference — raise EVAL_GATE_CASES;\n"
        f"    · the judge is uncalibrated — Lab 5 stage 5 (Cohen's κ, bias probes) is\n"
        f"      the fix. An uncalibrated judge is a dashboard, not a control."
    )
