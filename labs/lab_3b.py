# -*- coding: utf-8 -*-
"""Lab 3b — Route Smart, Not Slow: Adaptive RAG (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · after Lab 3 (agentic RAG)

Run it as a guided walkthrough:   python labs/lab_3b.py
Piped / non-interactive input auto-runs every stage (CI-safe).

The syllabus line this lab exists to PROVE, not assert:
    "Route smart, not slow — Adaptive RAG: simple to naïve, complex to agentic.
     Cut cost 5× without quality loss."

One pipeline for every query is always wrong somewhere: the agentic loop wastes 4+
LLM calls on "hi there", and naive single-shot RAG faceplants on multi-hop. Adaptive
RAG puts a cheap COMPLEXITY ROUTER in front and sends each query to the cheapest
path that can actually answer it. Every claim is measured: a live LLM-call cost
meter runs the whole lab, the router gets ITS OWN eval, and the finale races
always-naive vs adaptive vs always-agentic on quality AND cost.
"""

# --- repo local-run shim: load .env, work with or without __file__ ----------
import os, pathlib, sys

_here = pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path.cwd()
for _cand in (pathlib.Path(".env"), _here.parent / ".env", _here / ".env"):
    if _cand.exists():
        for _line in _cand.read_text().splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
        break

import json
import re

import numpy as np
import pandas as pd

import mai_rag
from mai_rag import corpus, llm
from mai_rag.tutor import Tutor, Stage, Spinner, note, panel, show_df, dim, green, yellow, bold

# ── shared state ─────────────────────────────────────────────────────────────
store = None
GOLDEN: list[dict] = []
ROUTES: dict[str, str] = {}          # question -> direct | simple | complex
ADAPTIVE_ROWS: list[dict] = []       # per-case results from the adaptive run
SHOWDOWN: dict[str, dict] = {}       # system -> {"quality":…, "calls":…}

# The cost meter — every LLM call in the lab passes through ask(), so cost is MEASURED.
METER = {"calls": 0, "chars": 0}

def ask(prompt, temperature=0.0):
    METER["calls"] += 1
    METER["chars"] += len(prompt)
    return llm.complete(prompt, tier="small", temperature=temperature)

def meter_reset():
    METER["calls"] = 0; METER["chars"] = 0

def meter_read():
    return METER["calls"], METER["chars"] // 4      # chars/4 ≈ prompt tokens

def _json(raw):
    """Structural JSON extraction (parsing, not classification). Clear ValueError on non-JSON."""
    m = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if not m:
        raise ValueError(f"model did not return JSON: {(raw or '')[:120]!r}")
    return json.loads(m.group(0))

# ── the three paths on the ladder (cost measured, not estimated) ─────────────
def path_direct(q: str) -> str:
    """No retrieval at all — greetings, arithmetic, general chat. 1 call."""
    return ask(f"Answer briefly and helpfully.\n\nuser: {q}\nassistant:")

def path_naive(q: str, k: int = 4) -> str:
    """Single-shot RAG — retrieve once, answer once. 1 call + retrieval."""
    hits = store.search(q, k=k)
    ctx = "\n\n".join(f"[{i+1}] ({h.title}) {h.content}" for i, h in enumerate(hits))
    return ask("Answer using ONLY the context. If the answer isn't there, say you don't "
               f"have enough information.\n\nQuestion: {q}\n\nContext:\n{ctx}\n\nAnswer:")

def path_agentic(q: str, k: int = 4) -> str:
    """Decompose → answer each sub-question → synthesize. ~4 calls + retrievals."""
    sub_raw = ask("Break this question into 1-3 standalone sub-questions (JSON only: "
                  f'{{"subs": ["...", ...]}}).\n\nQuestion: {q}')
    try:
        subs = _json(sub_raw).get("subs", [q])
        if not isinstance(subs, list) or not subs:   # a string-valued "subs" must not be sliced into chars
            subs = [q]
        subs = subs[:3]
    except ValueError:
        subs = [q]
    partials = []
    for s in subs:
        hits = store.search(s, k=k)
        ctx = "\n\n".join(f"({h.title}) {h.content}" for h in hits)
        partials.append(f"Q: {s}\nA: " + ask(
            f"Answer from the context only; say so if it isn't there.\n\nQuestion: {s}\n\nContext:\n{ctx}\n\nAnswer:"))
    return ask("Synthesize ONE final answer to the ORIGINAL question from these partial "
               "answers. If they show the information isn't available, say you don't have "
               f"enough information.\n\nOriginal question: {q}\n\n" + "\n\n".join(partials) + "\n\nFinal answer:")

PATHS = {"direct": path_direct, "simple": path_naive, "complex": path_agentic}
PATH_BLURB = {"direct": "no retrieval · 1 call", "simple": "naive RAG · 1 call + retrieval",
              "complex": "decompose→answer→synthesize · ~4 calls"}

# ── the router (classification → LLM, never a keyword rule) ──────────────────
def route(q: str) -> str:
    if q in ROUTES:
        return ROUTES[q]
    raw = ask(
        "You are a query-complexity router for a RAG system over a COURSE-CATALOG corpus "
        "(courses, curriculum topics, platform features). Classify the query:\n"
        '  "direct"  — needs NO corpus: greeting, chit-chat, arithmetic, general knowledge\n'
        '  "simple"  — one lookup answers it: a single fact/course/topic in the catalog\n'
        '  "complex" — needs multiple lookups (comparison, spans topics) OR likely reaches '
        "beyond the catalog (specific benchmarks, external facts)\n"
        f'Reply JSON only: {{"route": "direct"|"simple"|"complex", "why": "<short>"}}\n\nQuery: {q}',
        temperature=0)
    try:
        r = _json(raw).get("route", "simple")
    except ValueError:
        r = "simple"
    ROUTES[q] = r if r in PATHS else "simple"
    return ROUTES[q]

def answer_adaptive(q: str) -> tuple[str, str]:
    r = route(q)
    return PATHS[r](q), r

def grade(q, answer, expected):
    p = ("Grade the ANSWER against EXPECTED. 1.0 fully correct, 0.5 partial, 0.0 wrong/missing. "
         "An honest 'I don't have enough information' is CORRECT when EXPECTED says the "
         "information isn't in the corpus.\n"
         'Reply JSON only: {"reason":"<short>","score":<1.0|0.5|0.0>}.\n\n'
         f"QUESTION: {q}\nEXPECTED: {expected}\nANSWER: {answer}")
    try:
        return float(_json(ask(p, temperature=0))["score"])
    except (ValueError, KeyError, TypeError):        # one prose/keyless judge reply must not kill the showdown
        return 0.0

# expected route per golden tag — the router's own ground truth
TAG2ROUTE = {"no-retrieval": "direct", "site": "simple", "topic": "simple",
             "multi-hop": "complex", "needs-web": "complex"}

# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_cost_problem():
    global store, GOLDEN
    with Spinner("loading the catalog corpus (keyless, local embeddings)"):
        store = corpus.load_catalog_corpus("catalog.db")
    GOLDEN[:] = corpus.load_golden_catalog()
    print(f"  {green('loaded')}: {store.stats().get('documents')} docs · {len(GOLDEN)} golden cases\n")
    trivial = next(c["q"] for c in GOLDEN if c["tag"] == "no-retrieval")
    hard = next(c["q"] for c in GOLDEN if c["tag"] == "multi-hop")
    for label, q in (("TRIVIAL", trivial), ("MULTI-HOP", hard)):
        print(f"  {bold(label)}: {dim(q[:70])}")
        for pname in ("simple", "complex"):
            meter_reset()
            with Spinner(f"{pname} path"):
                a = PATHS[pname](q)
            calls, toks = meter_read()
            print(f"    {pname:<8} {yellow(str(calls) + ' calls')} · ≈{toks} prompt tokens → {dim(a[:60])}")
        print()
    note("same pipelines, opposite failures: the agentic loop spends 4+ calls answering 'hi', and "
         "naive RAG can't span two documents. One-size-fits-all is always overpaying or underserving.")

def s2_router():
    print("  routing all 12 golden queries (1 cheap classifier call each):\n")
    meter_reset()
    rows = []
    with Spinner("classifying"):
        for c in GOLDEN:
            r = route(c["q"])
            want = TAG2ROUTE[c["tag"]]
            rows.append({"question": c["q"][:38], "tag": c["tag"], "routed": r,
                         "expected": want, "ok": r == want})
    calls, _ = meter_read()
    df = pd.DataFrame(rows)
    show_df(df, "the router's own eval — routed vs expected (from the golden tags)")
    acc = df["ok"].mean()
    print(f"  router accuracy: {acc:.2f}   ({int(df['ok'].sum())}/{len(df)} · {calls} calls)")
    conf = df.groupby(["expected", "routed"]).size().unstack(fill_value=0)
    show_df(conf.reset_index(), "confusion — where the router over- or under-spends")
    note("the router is a CLASSIFIER, so it's an LLM call — never a keyword rule — and it gets its "
         "own eval before we trust it. A mis-route DOWN loses quality; a mis-route UP only loses money.")

def s3_ladder():
    print("  the strategy ladder — one worked example per rung:\n")
    examples = {"direct": next(c["q"] for c in GOLDEN if c["tag"] == "no-retrieval"),
                "simple": next(c["q"] for c in GOLDEN if c["tag"] == "topic"),
                "complex": next(c["q"] for c in GOLDEN if c["tag"] == "multi-hop")}
    for pname, q in examples.items():
        meter_reset()
        with Spinner(f"{pname}: {PATH_BLURB[pname]}"):
            a = PATHS[pname](q)
        calls, toks = meter_read()
        print(f"  {bold(pname):<18} {yellow(f'{calls} calls · ≈{toks} tok')}  {dim(PATH_BLURB[pname])}")
        print(f"    Q: {dim(q[:66])}")
        print(f"    A: {dim(a[:80])}\n")
    note("cost is measured by the meter, not estimated: every ask() is counted. The ladder only "
         "works because the rungs are REAL alternatives — same corpus, same store, different spend.")

def s4_adaptive_run():
    ADAPTIVE_ROWS.clear()
    ROUTES.clear()          # re-route LIVE so the router's own classify call is metered into serving cost,
    meter_reset()           # not hidden by stage-2's cache — otherwise adaptive looks ~1 call/query cheaper than it is
    print(f"  routing + answering + judging all {len(GOLDEN)} cases adaptively:\n")
    for c in GOLDEN:
        before = METER["calls"]
        with Spinner(f"[{c['tag']}] {c['q'][:44]}"):
            a, r = answer_adaptive(c["q"])
            cost = METER["calls"] - before          # router classify + path calls; judge excluded (called below)
            g = grade(c["q"], a, c["expected"])
        ADAPTIVE_ROWS.append({"question": c["q"][:36], "tag": c["tag"], "routed": r,
                              "calls": cost, "score": g})
        print(f"    {c['tag']:<13} → {r:<8} {yellow(str(cost) + ' calls')}  score {g}")
    df = pd.DataFrame(ADAPTIVE_ROWS)
    show_df(df, "the adaptive run — every case: route taken, calls spent, judge score")
    SHOWDOWN["adaptive"] = {"quality": float(df["score"].mean()), "calls": int(df["calls"].sum())}
    print(f"  adaptive: quality {SHOWDOWN['adaptive']['quality']:.3f} · {SHOWDOWN['adaptive']['calls']} serving calls")
    note("watch the calls column follow the routes: ~2 for direct/simple (a route + the answer), and "
         "more only where the query earned decomposition. Spend follows complexity — that's the whole idea.")

def s5_showdown():
    for system, fn in (("always-naive", path_naive), ("always-agentic", path_agentic)):
        meter_reset()
        scores = []
        with Spinner(f"{system}: {len(GOLDEN)} cases (answer + judge)"):
            for c in GOLDEN:
                before = METER["calls"]
                a = fn(c["q"])
                serving = METER["calls"] - before
                scores.append((grade(c["q"], a, c["expected"]), serving))
        SHOWDOWN[system] = {"quality": float(np.mean([s for s, _ in scores])),
                            "calls": int(sum(c for _, c in scores))}
    if "adaptive" not in SHOWDOWN:
        note("adaptive run missing (stage 4 skipped) — run stage 4 for the 3-way comparison.")
        return
    rows = []
    base = SHOWDOWN["always-agentic"]
    for name in ("always-naive", "adaptive", "always-agentic"):
        s = SHOWDOWN[name]
        rows.append({"system": name, "quality": round(s["quality"], 3), "serving calls": s["calls"],
                     "cost vs agentic": f"{s['calls'] / base['calls']:.2f}×"})
    show_df(pd.DataFrame(rows), "the showdown — quality vs cost, measured")
    ad, ag, na = SHOWDOWN["adaptive"], SHOWDOWN["always-agentic"], SHOWDOWN["always-naive"]
    kept = ad["quality"] / ag["quality"] if ag["quality"] else 1.0
    cut = ag["calls"] / ad["calls"] if ad["calls"] else 1.0
    print(f"\n  {bold('the verdict')}: adaptive kept {green(f'{kept:.0%}')} of agentic quality "
          f"at {green(f'1/{cut:.1f}')} the serving cost (and beat always-naive's {na['quality']:.3f} quality).")
    note("that's the syllabus line, earned with a meter instead of asserted: route simple to naïve, "
         "complex to agentic, and the cost falls without the quality. If YOUR numbers show adaptive "
         "losing quality, look at the router confusion first — mis-routes DOWN are where quality leaks.")

TUTOR = Tutor(
    title="Lab 3b — Route Smart, Not Slow: Adaptive RAG",
    tagline="Modern AI Pro · AI Architect · Pillar I · adaptive routing",
    mission="""
    The syllabus promises: 'simple to naïve, complex to agentic — cut cost 5× without
    quality loss.' This lab EARNS that sentence with a meter. Every LLM call is counted;
    a cheap complexity router (an LLM classifier with its own eval) sends each query to
    the cheapest path that can answer it; and the finale races always-naive vs adaptive
    vs always-agentic on quality AND cost, on the same golden set.
    """,
    stages=[
        Stage("The cost problem — one size always fails somewhere", """
            Load the catalog corpus, then run one trivial query and one multi-hop query
            through BOTH the naive and the agentic path, meter on: agentic wastes 4+ calls
            on chit-chat, naive faceplants on multi-hop. Neither pipeline should serve
            every query.""", s1_cost_problem, "~10"),
        Stage("The complexity router — with its own eval", """
            An LLM classifier (never a keyword rule) sorts each query: direct / simple /
            complex. The golden tags give us ground truth, so the router is evaluated like
            everything else — accuracy + a confusion table showing where it over- or
            under-spends before we trust it with traffic.""", s2_router, "~12"),
        Stage("The strategy ladder — three rungs, three price points", """
            direct (no retrieval, 1 call) → naive RAG (1 call + retrieval) → agentic
            (decompose → answer subs → synthesize, ~4 calls). One worked example per rung
            with the meter printing what each ACTUALLY cost.""", s3_ladder, "~6"),
        Stage("The adaptive run — spend follows complexity", """
            Route and answer all 12 golden cases adaptively, judging each answer. The
            per-case table shows the route taken, the calls spent, and the score earned —
            1-call cases and 4-call cases living honestly side by side.""", s4_adaptive_run, "~30"),
        Stage("The showdown — quality × cost, three systems", """
            The finale: always-naive vs adaptive vs always-agentic on the same cases. One
            table — quality, serving calls, cost ratio — and a computed verdict: how much
            quality adaptive kept and how much cost it cut. The syllabus line, measured.""", s5_showdown, "~85"),
    ],
    outro="""
    Routing is the cost architecture of production RAG: classify first, spend accordingly.
    The same pattern scales past this lab — a graph strategy, a web fallback, a bigger
    model are all just MORE RUNGS the router can price. (GraphRAG's honest home is exactly
    here: a routed strategy for entity-hop queries, defended by this same scorecard.)
    """,
)

def main():
    provider = "provider: "
    try:
        provider += llm._provider()
    except Exception:
        provider += "NONE — set OPENAI_API_KEY (class token) in .env"
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · {provider} · every LLM call metered")

if __name__ == "__main__":
    main()
