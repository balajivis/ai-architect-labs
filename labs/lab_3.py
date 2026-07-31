# -*- coding: utf-8 -*-
"""Lab 3 — Agentic RAG: The Five Decisions (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · Module 3

Run it as a guided walkthrough:   python labs/lab_3.py
Piped / non-interactive input auto-runs every stage (CI-safe).

Single-shot RAG is a PIPELINE: retrieve once, answer, hope. Agentic RAG is a LOOP —
at every step the agent asks itself a question and acts on the answer:

  1. Should I retrieve at all?        → the router
  2. What should I search FOR?        → HyDE + multi-query
  3. Is ONE search enough?            → decomposition
  4. Did I actually get enough?       → sufficiency + corrective web fallback (CRAG)
  5. When do I stop?                  → budget caps

The corpus is a deliberately SHALLOW catalog — so depth questions force the agent to do
more than retrieve once. The recipe that wins: when your corpus can't answer, the agent
reasons and reaches out — instead of confidently making something up.
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
import time
import textwrap

import numpy as np
import pandas as pd

import mai_rag
from mai_rag import corpus, llm
from mai_rag.tutor import Tutor, Stage, Spinner, note, show_df, dim, green, bold, yellow

# ── shared state ─────────────────────────────────────────────────────────────
store = None
golden: list[dict] = []
_tavily = None          # lazy + OPTIONAL — the lab degrades gracefully without a key

def ask(prompt, temperature=0.0):
    return llm.complete(prompt, tier="small", temperature=temperature)

def _json(raw):
    return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])

def web_available() -> bool:
    return bool(os.environ.get("TAVILY_API_SEARCH") or os.environ.get("TAVILY_API_KEY"))

def web_search(q, k=3):
    """Tavily web search — lazy client, and honest [] when no key is configured."""
    global _tavily
    if not web_available():
        return []
    if _tavily is None:
        from tavily import TavilyClient
        _tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_SEARCH") or os.environ.get("TAVILY_API_KEY"))
    r = _tavily.search(query=q, max_results=k)
    return [(x["url"][:60], x["content"]) for x in r["results"]]

def search(q, k=5):
    return store.search(q, k=k)

def naive_rag(q, k=5):
    hits = search(q, k)
    ctx = "\n\n".join(f"[{i+1}] ({h.source}) {h.content}" for i, h in enumerate(hits))
    p = ("Answer using ONLY the context. If it isn't there, say you don't have enough information.\n\n"
         f"Question: {q}\n\nContext:\n{ctx}\n\nAnswer:")
    return ask(p)

# ── Decision 1 · the router ──────────────────────────────────────────────────
# v1: the "obvious" prompt — it fails in a subtle way Stage 3 exposes with an eval.
# v2 (corpus_aware): routes by WHAT THE KNOWLEDGE BASE COVERS, not by whether the
# model thinks it already knows the answer. The whole point: a router that trusts
# its own knowledge silently bypasses YOUR corpus (and your citations/governance).
def analyze_query(q, corpus_aware=True):
    if corpus_aware:
        p = ('You route queries for a RAG system over a knowledge base about Modern AI Pro '
             '(courses, plans, support) and AI-engineering topics (RAG, agents, retrieval, memory). '
             'Reply JSON only: {"needs_retrieval": true|false, "type": "factual|comparison|conversational|math", '
             '"complexity": "simple|complex", "reason": "<short>"}. '
             'needs_retrieval=true whenever the query is ABOUT those domains — even if you could answer '
             'from your own knowledge; the system must answer from its documents, with citations. '
             'needs_retrieval=false ONLY for greetings, chit-chat, and pure math/general knowledge '
             'unrelated to the domain.\n\n'
             f'Query: {q}')
    else:
        p = ('Classify this query. Reply JSON only: '
             '{"needs_retrieval": true|false, "type": "factual|comparison|conversational|math", '
             '"complexity": "simple|complex", "reason": "<short>"}. '
             'needs_retrieval=false for greetings, chit-chat, and pure math / general knowledge that needs no documents.\n\n'
             f'Query: {q}')
    return _json(ask(p))

def route(q, corpus_aware=True):
    a = analyze_query(q, corpus_aware)
    if not a["needs_retrieval"]:                                   return "direct"
    if a["type"] == "comparison" or a["complexity"] == "complex":  return "decompose"
    return "retrieve"

# ── Decision 2 · search for the answer's shadow ──────────────────────────────
def hyde(q):
    return ask(f"Write a 2-sentence hypothetical answer to this question:\n{q}\nAnswer:")

def multi_query(q, n=3):
    out = ask(f"Write {n} alternative search queries for this question, one per line:\n{q}")
    return [l.strip(" -*0123456789.") for l in out.splitlines() if l.strip()][:n]

def hyde_search(q, k=5):
    return store.search(f"{q}\n{hyde(q)}", k=k)

# ── Decision 3 · decomposition ───────────────────────────────────────────────
def decompose(q):
    out = ask(f"Break this into 2-3 standalone sub-questions, one per line:\n{q}")
    return [l.strip(" -*0123456789.") for l in out.splitlines() if "?" in l][:3]

def agentic_retrieve(q, k=4):
    subs = decompose(q)
    docs, seen = [], set()
    for s in subs:
        for h in store.search(s, k=k):
            if h.source not in seen:
                seen.add(h.source); docs.append((h.source, h.content))
    return subs, docs

# ── Decision 4 · sufficiency + corrective fallback (CRAG) ────────────────────
def sufficient(q, docs):
    ctx = "\n".join(c for _, c in docs)[:2500]
    p = ('Can the CONTEXT answer the QUESTION specifically and completely (exact facts, not just the topic)? '
         'Reply JSON only: {"sufficient": true|false, "why": "<short>"}.\n\n'
         f'QUESTION: {q}\nCONTEXT: {ctx}')
    return _json(ask(p))

def crag_answer(q, k=4):
    hits = [(h.source, h.content) for h in store.search(q, k=k)]
    verdict = sufficient(q, hits)
    source = "catalog"
    if not verdict["sufficient"]:                         # the corrective step
        web = web_search(q)
        if web:
            hits = hits[:2] + web
            source = "catalog + WEB"
        else:
            source = "catalog (insufficient — no web key)"
    ctx = "\n\n".join(f"[{s}] {c}" for s, c in hits)
    ans = ask(f"Answer using ONLY the context; cite sources inline as [source].\n\nQ: {q}\n\nContext:\n{ctx}\n\nAnswer:")
    return source, ans, verdict

# ── Decision 5 · the budget ──────────────────────────────────────────────────
class Budget:
    def __init__(self, max_calls=10, max_seconds=40):
        self.max_calls, self.max_seconds, self.calls, self.t0 = max_calls, max_seconds, 0, time.time()
    def tick(self):
        self.calls += 1
        if self.calls > self.max_calls:               raise RuntimeError("budget: too many LLM calls")
        if time.time() - self.t0 > self.max_seconds:  raise RuntimeError("budget: wall-clock exceeded")

def agent(q, max_calls=10, max_seconds=60):
    """The finished product: route → (direct | retrieve | decompose) → sufficiency → web → answer."""
    b = Budget(max_calls, max_seconds)
    strat = route(q); b.tick()
    if strat == "direct":
        return "direct", ask(f"Answer this briefly and directly: {q}")
    if strat == "decompose":
        _, docs = agentic_retrieve(q); b.tick()
    else:
        docs = [(h.source, h.content) for h in store.search(q, k=4)]
    used = "catalog"
    if not sufficient(q, docs)["sufficient"]:
        web = web_search(q); b.tick()
        if web:
            docs = docs[:2] + web; used = "catalog+WEB"
    ctx = "\n\n".join(f"[{s}] {c}" for s, c in docs)
    ans = ask(f"Answer using ONLY the context; cite sources inline as [source].\n\nQ: {q}\n\nContext:\n{ctx}\n\nAnswer:")
    return f"{strat}/{used}", ans

# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_setup():
    global store
    with Spinner("embedding the catalog corpus (keyless, local MiniLM, ~20s)"):
        store = corpus.load_catalog_corpus(rebuild=True)
    golden[:] = corpus.load_golden_catalog()
    s = store.stats()
    tags = {t: sum(c["tag"] == t for c in golden) for t in sorted({c["tag"] for c in golden})}
    print(f"  {green('corpus ready')}: {s.get('documents')} docs · {s.get('chunks')} chunks · golden: {len(golden)} cases")
    print("  cases by shape: " + " · ".join(f"{k}={v}" for k, v in tags.items()))
    print(f"  web fallback (Tavily): {green('configured') if web_available() else yellow('NO KEY — the CRAG stage will degrade honestly (set TAVILY_API_SEARCH in .env)')}")
    note("the catalog is SHALLOW on purpose: it knows what courses exist, not every technical "
         "depth. Four query shapes are seeded in the golden set — each breaks single-shot RAG "
         "differently, and each maps to one agentic decision.")

def s2_breaks():
    shapes = {"multi-hop": "needs facts from TWO docs — one retrieval can't get both",
              "needs-web": "the catalog only covers the topic — the specifics aren't there",
              "no-retrieval": "needs NO documents — retrieval is pure waste here"}
    for tag, why in shapes.items():
        c = next((c for c in golden if c["tag"] == tag), None)
        if not c:
            continue
        print(f"  {bold('[' + tag + ']')} {c['q'][:66]}")
        print(f"  {dim('why it breaks: ' + why)}")
        with Spinner("single-shot answer"):
            a = naive_rag(c["q"])
        print(f"  {dim('→ ' + a[:150].replace(chr(10), ' '))}\n")
    note("three different failure SHAPES — incomplete (multi-hop), declined-or-invented "
         "(needs-web), wasteful (no-retrieval). One hammer, three different nails. The next five "
         "stages give the agent five decisions — one per nail, plus two for sharpening.")

def s3_router():
    expected = {c["q"]: ("direct" if c["tag"] == "no-retrieval" else
                         "decompose" if c["tag"] == "multi-hop" else "retrieve") for c in golden}
    def score_router(corpus_aware, label):
        rows = []
        with Spinner(f"routing all {len(golden)} golden queries ({label})"):
            for c in golden:
                got = route(c["q"], corpus_aware=corpus_aware)
                rows.append({"query": c["q"][:44], "tag": c["tag"], "routed": got,
                             "expected": expected[c["q"]], "ok": got == expected[c["q"]]})
        return pd.DataFrame(rows)
    # v1 — the "obvious" prompt
    df1 = score_router(False, "v1: the obvious prompt")
    show_df(df1, "router v1 — decisions vs the golden tags")
    print(f"  v1 accuracy: {df1['ok'].mean():.2f}  ({int(df1['ok'].sum())}/{len(df1)})\n")
    leaks = df1[(df1["routed"] == "direct") & (df1["expected"] != "direct")]
    if len(leaks):
        print(f"  {yellow('⚠ look at the misses:')} {len(leaks)} in-domain questions routed 'direct' — "
              f"the model THINKS it already knows\n  {dim('HyDE, ReAct, agent memory… so it skips YOUR corpus, your citations, your governance.')}\n")
    # v2 — corpus-aware: route by what the KB covers, not by what the model knows
    df2 = score_router(True, "v2: corpus-aware prompt")
    print(f"  v2 accuracy: {df2['ok'].mean():.2f}  ({int(df2['ok'].sum())}/{len(df2)})   "
          f"{green('← the fix: route by what the KB covers, not by what the model knows')}")
    flipped = df2[(df2['ok']) & (~df1['ok'].values)]
    if len(flipped):
        print(f"  cases the fix won back: {dim(' · '.join(q[:38] for q in flipped['query']))}")
    note("this stage is the whole course in miniature: eval the component → the score exposes a "
         "REAL bug (the router trusting its own knowledge over your corpus) → fix the prompt → "
         "re-score. Residual misses are the labeling debates Lab 5's calibration formalizes. "
         "Components get evals, not just pipelines.")

def s4_hyde():
    q = "How does an agent decide what action to take at each step?"
    h = hyde(q)
    print(f"  Q: {q}\n")
    print(f"  {bold('the hypothetical answer (the “shadow” we search with):')}")
    print(textwrap.indent(textwrap.fill(h, 84), f"  {dim('│')} ") + "\n")
    naive_docs = [x.source for x in search(q, 3)]
    hyde_docs = [x.source for x in hyde_search(q, 3)]
    print(f"  query-only retrieval : {dim(' · '.join(d[:34] for d in naive_docs))}")
    print(f"  HyDE retrieval       : {dim(' · '.join(d[:34] for d in hyde_docs))}")
    with Spinner("multi-query expansions"):
        mq = multi_query(q)
    print(f"\n  multi-query rewrites: ")
    for m in mq:
        print(f"    · {m[:78]}")
    note("the vocabulary gap: users write QUESTION-shaped text, documents contain ANSWER-shaped "
         "text. HyDE drafts a hypothetical answer and searches with THAT — answer-to-answer "
         "matching. Multi-query attacks the same gap sideways: three phrasings, pooled hits. "
         "Both widen recall BEFORE the agent commits to a context.")

def s5_decompose():
    q = next(c["q"] for c in golden if c["tag"] == "multi-hop")
    print(f"  Q: {q}\n")
    with Spinner("single-shot retrieval"):
        single = [h.source for h in search(q, 4)]
    with Spinner("decompose → retrieve per sub-question"):
        subs, docs = agentic_retrieve(q)
    print(f"  {bold('sub-questions:')}")
    for s_ in subs:
        print(f"    · {s_[:78]}")
    union = [d for d, _ in docs]
    print(f"\n  single-shot docs : {dim(' · '.join(d[:30] for d in single[:4]))}")
    print(f"  union of subs    : {dim(' · '.join(d[:30] for d in union[:6]))}")
    gained = [d for d in union if d not in single]
    if gained:
        print(f"  {green('docs the union GAINED:')} {' · '.join(d[:34] for d in gained[:4])}")
    with Spinner("synthesizing from the union"):
        ctx = "\n\n".join(f"[{s_}] {c}" for s_, c in docs)
        ans = ask(f"Using this context, answer with inline [source] citations: {q}\n\nContext:\n{ctx}\n\nAnswer:")
    print(f"\n  {dim('→ ' + ans[:170].replace(chr(10), ' '))}")
    note("a comparison question needs one fact per THING compared — one embedding can't point two "
         "directions at once. Decompose into standalone sub-questions, retrieve each, union, "
         "synthesize. Rule of thumb: one retrieval per fact the answer needs.")

def s6_crag():
    q = next(c["q"] for c in golden if c["tag"] == "needs-web")
    print(f"  Q: {q}\n")
    hits = [(h.source, h.content) for h in store.search(q, k=4)]
    print(f"  retrieved (looks relevant!): {dim(' · '.join(s for s, _ in hits[:3]))}")
    with Spinner("the sufficiency judge reads the context"):
        v = sufficient(q, hits)
    flag = green("sufficient") if v["sufficient"] else yellow("NOT sufficient")
    print(f"  verdict: {flag} — {dim(v['why'][:80])}\n")
    with Spinner("CRAG answer (corrective fallback if needed)"):
        source, ans, _ = crag_answer(q)
    print(f"  SOURCE USED: {bold(source)}")
    print(textwrap.indent(textwrap.fill(ans[:420], 84), "  "))
    if not web_available():
        note("no Tavily key, so the corrective step had nowhere to reach — but notice what the "
             "sufficiency judge still bought you: the agent KNOWS it doesn't know. That alone "
             "beats a confident hallucination. With a key, this becomes a sourced web answer.")
    else:
        note("THE star move: retrieval LOOKED relevant (right topic!) but the judge caught that "
             "the specifics aren't there — so the agent corrected course, reached the web, and "
             "cited both. 'I don't have that' and hallucination both became a real answer.")

def s7_budget():
    print(f"  {bold('watch the cap actually fire')} — a decompose-shaped query on a 1-call budget:\n")
    q = next(c["q"] for c in golden if c["tag"] == "multi-hop")
    try:
        with Spinner("agent(q, max_calls=1)"):
            agent(q, max_calls=1)
        print(f"  {yellow('…finished under budget (routing was cheap this run)')}")
    except RuntimeError as e:
        print(f"  {green('✋ stopped:')} {e}")
    print(f"\n  now with a sane budget (10 calls / 60s):")
    with Spinner("agent(q) full run"):
        strat, a = agent(q)
    print(f"  [{strat}]  {dim('→ ' + a[:140].replace(chr(10), ' '))}")
    note("an agentic loop without a budget is an outage generator: every decision is an LLM call, "
         "and a judge that keeps saying 'not sufficient' loops forever. Cap calls AND wall-clock, "
         "fail loudly, and treat the caps as product decisions — they ARE your latency + cost SLO.")

def s8_rescore():
    def grade(q, ans, expected):
        p = ('Grade the ANSWER against EXPECTED: 1.0 fully correct, 0.5 partial, 0.0 wrong/missing. '
             'If EXPECTED says no-retrieval/direct, reward a correct direct answer; if it says needs-web, '
             'reward a correct sourced answer. JSON only: {"score": <1.0|0.5|0.0>}.\n\n'
             f'Q: {q}\nEXPECTED: {expected}\nANSWER: {ans}')
        return _json(ask(p))["score"]
    rows = []
    with Spinner(f"naive vs agent on {len(golden)} cases (answer + judge, both paths)"):
        for c in golden:
            try:
                n = naive_rag(c["q"])
                route_used, a = agent(c["q"])
                rows.append({"tag": c["tag"], "route": route_used[:22],
                             "naive": grade(c["q"], n, c["expected"]),
                             "agentic": grade(c["q"], a, c["expected"])})
            except (ValueError, KeyError, RuntimeError):
                pass                            # one bad case drops, the scorecard survives
    df = pd.DataFrame(rows)
    show_df(df, "the finale — naive vs agentic, per case")
    means = df[["naive", "agentic"]].mean().round(3)
    print(f"  MEANS: naive={means['naive']}  agentic={means['agentic']}")
    by_tag = df.groupby("tag")[["naive", "agentic"]].mean().round(2)
    show_df(by_tag.reset_index(), "where the win comes from (by failure shape)")
    note("read the by-shape table against Stage 2: the agent's lift lands EXACTLY on the shapes "
         "that broke single-shot — direct answers for no-retrieval, decomposition for multi-hop, "
         "the web for depth. And the route column shows the price: agentic isn't free, which is "
         "why the router only pays for it when the query needs it.")

TUTOR = Tutor(
    title="Lab 3 — Agentic RAG: The Five Decisions",
    tagline="Modern AI Pro · AI Architect · Pillar I · Module 3",
    mission="""
    Single-shot RAG is a PIPELINE: retrieve once, answer, hope. Agentic RAG is a LOOP —
    at each step the agent asks itself a question and acts on the answer. This lab builds
    those five decisions one at a time: Should I retrieve at all? What should I search
    FOR? Is one search enough? Did I actually get enough? When do I stop?

    The corpus is a deliberately shallow catalog — it knows what courses exist, not every
    technical depth — so the agent is forced to route, decompose, self-check, and reach
    the web. The recipe that wins: when your corpus can't answer, reason and reach out —
    never confidently make something up.
    """,
    stages=[
        Stage("Setup — the shallow catalog + the four query shapes", """
            Load the ~136-doc catalog (keyless, embeds live) and a golden set whose cases
            are TAGGED by shape: site/topic (single-shot handles these), multi-hop (spans
            two docs), needs-web (the catalog is too shallow), no-retrieval (documents
            can't help). Each shape breaks the pipeline differently — and each maps to one
            of the five decisions.""", s1_setup, "0"),
        Stage("Where single-shot breaks — three failure shapes, live", """
            Run naive RAG on one case of each hard shape and read the failures: multi-hop
            comes back HALF-complete, needs-web gets declined or confidently invented, and
            'what's 17×4' wastes a retrieval on documents that cannot help. Name the shape
            → know the fix. This is Lab 1's diagnosis discipline, applied to query shapes.""", s2_breaks, "~4"),
        Stage("Decision 1 · Should I retrieve at all? — the router (eval → bug → fix)", """
            The first agentic decision is triage: direct (greetings, math — just answer),
            retrieve (in-corpus), decompose (comparisons). The router is a CLASSIFIER, so it
            gets an eval — and the eval will expose a real, subtle bug: the model routes
            questions it THINKS it knows (HyDE? ReAct?) straight past your corpus. Then we
            fix the prompt — route by what the KB covers, not what the model knows — and
            re-score. The eval-driven loop, applied to one component.""", s3_router, "~26"),
        Stage("Decision 2 · What should I search FOR? — HyDE + multi-query", """
            The vocabulary gap: users write question-shaped text, documents contain
            answer-shaped text. HyDE drafts a hypothetical answer — the answer's SHADOW —
            and retrieves with that; multi-query rewrites the question three ways and pools
            the hits. Watch the retrieved docs change with your own eyes.""", s4_hyde, "~3"),
        Stage("Decision 3 · Is ONE search enough? — decomposition", """
            A comparison needs one fact per thing compared — a single embedding can't point
            two directions at once. Split into standalone sub-questions, retrieve each,
            union the docs, synthesize with citations. We show exactly which docs the union
            GAINED over single-shot — that gain is the multi-hop fix.""", s5_decompose, "~4"),
        Stage("Decision 4 · Did I get enough? — sufficiency + CRAG ⭐", """
            The star move. On a shallow corpus, retrieval can LOOK relevant (right topic!)
            while the specifics aren't there. A sufficiency judge reads the context and
            answers: can this actually answer the question? If not — correct course: search
            the web, synthesize catalog + web, cite both. Degrades honestly without a web
            key: knowing you don't know already beats hallucinating.""", s6_crag, "~4"),
        Stage("Decision 5 · When do I stop? — budget caps", """
            Every decision so far is an LLM call, and loops love to loop. We cap calls and
            wall-clock, then PROVE the cap works by running the agent on a 1-call budget
            and watching it stop loudly. Budgets aren't plumbing — they're your latency and
            cost SLO, decided at design time.""", s7_budget, "~5"),
        Stage("The re-score — agentic vs naive, and where the win lives", """
            Grade the finished agent() against naive RAG on the whole golden set, then
            break the scores down BY SHAPE. The lift should land exactly on the shapes that
            broke in Stage 2 — and the route column shows what each win cost. Agentic isn't
            free; routing is why you only pay when the query needs it.""", s8_rescore, "~60"),
    ],
    outro="""
    The five decisions are the whole pattern: triage the query, search with the answer's
    shadow, one retrieval per fact, check sufficiency before answering, and never run
    unbounded. Lab 4 gives the agent MEMORY across turns; Lab 5 turns today's hand-rolled
    judges into a calibrated suite.
    """,
)

def main():
    provider = "provider: "
    try:
        provider += llm._provider()
    except Exception:
        provider += "NONE — set OPENAI_API_KEY (class token) in .env"
    web = "web: Tavily ✓" if web_available() else "web: no key (CRAG degrades honestly)"
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · {provider} · {web}")

if __name__ == "__main__":
    main()
