# -*- coding: utf-8 -*-
"""Lab 3e — Judge the Path, Not Just the Answer (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar II · after Lab 3 (agentic RAG)

Run it as a guided walkthrough:   python labs/lab_3e.py
Piped / non-interactive input auto-runs every stage (CI-safe).

Every eval you have written so far grades the ANSWER. Nothing grades the PATH.

Two agents hand you the identical answer. One routed straight to a direct reply in
one step; the other decomposed the question into three sub-questions, ran five
retrievals, second-guessed itself twice and pinged the web. Answer-only evals give
them the SAME score. Their cost, latency and blast radius are not remotely the same
— and the second one is the one that pages you at 2am.

This lab makes the path a first-class artifact. We wrap Lab 3's agent in a tracer so
every run emits a TRAJECTORY, then grade that trajectory four ways: deterministic
counters (no LLM at all), tool-call accuracy against the path SHAPE each query
deserves, a head-to-head where two agents tie on answers and diverge wildly on
steps, and finally an LLM judge that reads the path and not the answer. The lab ends
with a release gate that a "same answers, 3× the work" agent cannot sneak through.
"""

# --- repo local-run shim: load .env, work with or without __file__ ----------
import os, pathlib, sys

_here = pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path.cwd()
for _cand in (pathlib.Path(".env"), _here.parent / ".env", _here / ".env"):
    if _cand.exists():
        try:                                     # utf-8-sig eats a Windows Notepad BOM,
            _txt = _cand.read_text(encoding="utf-8-sig")   # which otherwise corrupts the FIRST key
        except (OSError, UnicodeDecodeError):
            _txt = ""                            # an unreadable .env must never crash the import
        for _line in _txt.splitlines():
            _line = _line.strip()
            if _line.startswith("export "):        # people paste shell-style lines into .env
                _line = _line[7:].lstrip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _v = _v.strip()
                if len(_v) > 1 and _v[0] == _v[-1] and _v[0] in ("\'", '"'):
                    _v = _v[1:-1]                # quoted: take it verbatim
                elif " #" in _v:
                    _v = _v.split(" #", 1)[0].strip()   # unquoted: drop a trailing comment
                os.environ.setdefault(_k.strip(), _v)
        break

import contextlib
import json
import re
import time

import pandas as pd

import mai_rag
from mai_rag import corpus, llm
from mai_rag.tutor import Tutor, Stage, Spinner, note, panel, show_df, dim, green, bold, yellow, red

# ── shared state ─────────────────────────────────────────────────────────────
store = None
GOLDEN: list[dict] = []
RUNS: dict[str, dict] = {"routed": {}, "always-agentic": {}}   # agent -> {question: (Trace, answer)}
AB_ROWS: list[dict] = []                                        # stage 5's head-to-head, reused by stage 7
_tavily = None                                                  # lazy + OPTIONAL

METER = {"calls": 0}
_CUR: dict | None = None          # the trajectory step currently open — ask() bills tokens to it


def ask(prompt, temperature=0.0):
    """The one LLM chokepoint. Every call is metered AND attributed to a trajectory step."""
    out = llm.complete(prompt, tier="small", temperature=temperature)
    METER["calls"] += 1
    if _CUR is not None:
        _CUR["calls"] += 1
        _CUR["tokens_est"] += (len(prompt) + len(out or "")) // 4     # chars/4 ≈ tokens
    return out


def _json(raw):
    """Structural JSON extraction (parsing, not classification). Clear ValueError on non-JSON."""
    m = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if not m:
        raise ValueError(f"model did not return JSON: {(raw or '')[:120]!r}")
    return json.loads(m.group(0))


def _score(v):
    try:
        return min(max(float(v), 0.0), 1.0)
    except (TypeError, ValueError):
        return 0.0


def web_available() -> bool:
    return bool(os.environ.get("TAVILY_API_SEARCH") or os.environ.get("TAVILY_API_KEY"))


def web_search(q, k=3):
    """Tavily — lazy client, honest [] when no key is configured."""
    global _tavily
    if not web_available():
        return []
    if _tavily is None:
        from tavily import TavilyClient
        _tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_SEARCH") or os.environ.get("TAVILY_API_KEY"))
    r = _tavily.search(query=q, max_results=k)
    return [(x["url"][:60], x["content"]) for x in r["results"]]


# ═════════════════════════════════════════════════════════════════════════════
# THE TRACER — 30 lines that turn an agent run into an inspectable artifact
# ═════════════════════════════════════════════════════════════════════════════
# A trajectory is just an ordered list of records. Nothing clever: a name, a detail
# string drawn from a SMALL FIXED VOCABULARY (so later checks compare enums, not
# prose), wall time, LLM calls, and an error slot. Everything downstream in this lab
# — counters, shape checks, the LLM path-judge, the gate — reads only this list.

STEP_NAMES = ("route", "decompose", "retrieve", "sufficiency", "web_search", "answer")


class Trace:
    def __init__(self, agent: str, q: str):
        self.agent, self.q, self.steps = agent, q, []

    def path(self) -> str:
        return " → ".join(s["step"] for s in self.steps)


@contextlib.contextmanager
def step(tr: Trace, name: str, detail: str = ""):
    """Open a trajectory step. The record is yielded so the body can fill in `detail`.

    Note the `finally`: a step that RAISES is still recorded, with its exception type
    in `error`. An eval that only sees successful steps cannot compute an error rate."""
    global _CUR
    rec = {"step": name, "detail": detail, "ms": 0, "calls": 0, "tokens_est": 0, "error": "", "query": ""}
    prev, _CUR = _CUR, rec
    t0 = time.time()
    try:
        yield rec
    except Exception as e:                       # noqa: BLE001 — recorded, then re-raised
        rec["error"] = type(e).__name__
        raise
    finally:
        rec["ms"] = int((time.time() - t0) * 1000)
        _CUR = prev
        tr.steps.append(rec)


# ── traced primitives (Lab 3's functions, each wrapped in exactly one step) ──
ROUTER_PROMPT = (
    'You route queries for a RAG system over a knowledge base about Modern AI Pro '
    '(courses, plans, support) and AI-engineering topics (RAG, agents, retrieval, memory). '
    'Reply JSON only: {"needs_retrieval": true|false, "type": "factual|comparison|conversational|math", '
    '"complexity": "simple|complex", "reason": "<short>"}. '
    'needs_retrieval=true whenever the query is ABOUT those domains — even if you could answer '
    'from your own knowledge. needs_retrieval=false ONLY for greetings, chit-chat, and pure '
    'math/general knowledge unrelated to the domain.\n\nQuery: '
)


def t_route(tr, q) -> str:
    with step(tr, "route") as rec:
        try:
            a = _json(ask(ROUTER_PROMPT + q))
            strat = ("direct" if not a["needs_retrieval"] else
                     "decompose" if a["type"] == "comparison" or a["complexity"] == "complex" else
                     "retrieve")
        except (ValueError, KeyError):
            strat, rec["error"] = "retrieve", "BadRouterJSON"   # safe default, recorded as a tool error
        rec["detail"] = strat
    return strat


def t_decompose(tr, q) -> list[str]:
    with step(tr, "decompose") as rec:
        out = ask(f"Break this into 2-3 standalone sub-questions, one per line:\n{q}")
        subs = [l.strip(" -*0123456789.") for l in (out or "").splitlines() if "?" in l][:3] or [q]
        rec["detail"] = f"{len(subs)} sub-questions"
    return subs


def t_retrieve(tr, q, k=4) -> list[tuple[str, str]]:
    with step(tr, "retrieve") as rec:
        docs = [(h.source, h.content) for h in store.search(q, k=k)]
        rec["query"] = " ".join(q.lower().split())        # normalized key — structural dedup, see stage 3
        rec["detail"] = f'{len(docs)} docs · "{q[:26]}"'
    return docs


def t_sufficiency(tr, q, docs) -> bool:
    with step(tr, "sufficiency") as rec:
        ctx = "\n".join(c for _, c in docs)[:2500]
        try:
            ok = bool(_json(ask(
                'Can the CONTEXT answer the QUESTION specifically and completely (exact facts, not '
                'just the topic)? Reply JSON only: {"sufficient": true|false, "why": "<short>"}.\n\n'
                f'QUESTION: {q}\nCONTEXT: {ctx}'))["sufficient"])
        except (ValueError, KeyError):
            ok, rec["error"] = False, "BadJudgeJSON"
        rec["detail"] = "sufficient" if ok else "insufficient"      # a 2-value enum, never free prose
    return ok


def t_web(tr, q):
    with step(tr, "web_search") as rec:
        hits = web_search(q)
        rec["detail"] = f"{len(hits)} results" if hits else "skipped — no key"
    return hits


def t_answer(tr, q, docs) -> str:
    with step(tr, "answer") as rec:
        if docs is None:
            ans = ask(f"Answer this briefly and directly: {q}")
            rec["detail"] = "direct (no context)"
        else:
            ctx = "\n\n".join(f"[{s}] {c}" for s, c in docs)
            ans = ask(f"Answer using ONLY the context; cite sources inline as [source].\n\n"
                      f"Q: {q}\n\nContext:\n{ctx}\n\nAnswer:")
            rec["detail"] = f"{len(ans or '')} chars · {len(docs)} docs"
    return ans or ""


# ── the two agents under test ───────────────────────────────────────────────
def routed_agent(q, k=4):
    """Lab 3's finished agent, traced: route → (direct | retrieve | decompose) → sufficiency → web → answer."""
    tr = Trace("routed", q)
    strat = t_route(tr, q)
    if strat == "direct":
        return tr, t_answer(tr, q, None)
    if strat == "decompose":
        docs, seen = [], set()
        for s in t_decompose(tr, q):
            for src, c in t_retrieve(tr, s, k):
                if src not in seen:
                    seen.add(src); docs.append((src, c))
    else:
        docs = t_retrieve(tr, q, k)
    if not t_sufficiency(tr, q, docs):
        web = t_web(tr, q)
        if web:
            docs = docs[:2] + web
    return tr, t_answer(tr, q, docs)


def always_agentic_agent(q, k=4):
    """The 'more agentic must be better' agent: no routing, ALWAYS decompose, ALWAYS
    check sufficiency, ALWAYS reach for the web. Same machinery, no judgement."""
    tr = Trace("always-agentic", q)
    docs, seen = [], set()
    for s in t_decompose(tr, q):
        for src, c in t_retrieve(tr, s, k):
            if src not in seen:
                seen.add(src); docs.append((src, c))
    t_sufficiency(tr, q, docs)              # verdict ignored — it searches the web either way
    web = t_web(tr, q)
    if web:
        docs = docs[:2] + web
    return tr, t_answer(tr, q, docs)


AGENTS = {"routed": routed_agent, "always-agentic": always_agentic_agent}


def run(agent: str, q: str):
    """Cached run — a trajectory is expensive, so every stage shares one per (agent, question)."""
    if q not in RUNS[agent]:
        RUNS[agent][q] = AGENTS[agent](q)
    return RUNS[agent][q]


# ═════════════════════════════════════════════════════════════════════════════
# THE METRICS — stage 3 (deterministic) and stage 4 (path shape)
# ═════════════════════════════════════════════════════════════════════════════
def step_count(tr):  return len(tr.steps)
def wall_ms(tr):     return sum(s["ms"] for s in tr.steps)
def llm_calls(tr):   return sum(s["calls"] for s in tr.steps)
def tokens_est(tr):  return sum(s["tokens_est"] for s in tr.steps)
def n_steps(tr, name): return sum(1 for s in tr.steps if s["step"] == name)


def redundant_steps(tr) -> int:
    """Retrievals that re-issue a query this run already issued. Pure bookkeeping over a
    recorded field — no interpretation of what the query MEANS."""
    seen, dupes = set(), 0
    for s in tr.steps:
        if s["step"] != "retrieve" or not s["query"]:
            continue
        if s["query"] in seen:
            dupes += 1
        else:
            seen.add(s["query"])
    return dupes


def tool_error_rate(tr) -> float:
    return round(sum(1 for s in tr.steps if s["error"]) / max(len(tr.steps), 1), 2)


def loop_detected(tr) -> bool:
    """A cycle of 1-3 steps repeated back-to-back — the signature of an agent stuck in
    retrieve→judge→retrieve. Sequence comparison over recorded enums, nothing more."""
    seq = [(s["step"], s["detail"]) for s in tr.steps]
    for w in (1, 2, 3):
        for i in range(len(seq) - 2 * w + 1):
            if seq[i:i + w] == seq[i + w:i + 2 * w]:
                return True
    return False


def metrics(tr) -> dict:
    return {"agent": tr.agent, "steps": step_count(tr), "wall_ms": wall_ms(tr),
            "llm_calls": llm_calls(tr), "tok~": tokens_est(tr),
            "redundant": redundant_steps(tr), "tool_err": tool_error_rate(tr),
            "loop": "YES" if loop_detected(tr) else "no"}


# ── tool-call accuracy: the path SHAPE each query tag deserves ──────────────
# NOTE ON THE HARD RULE: this is not classification. We are not reading the query text
# and guessing anything. We compare the agent's RECORDED step names against a shape the
# golden tag already declares — structural comparison of our own instrumentation, which
# is exactly what regex/keyword rules are banned from doing to CONTENT.
def _route_of(tr):
    return next((s["detail"] for s in tr.steps if s["step"] == "route"), "—")


def _sufficiency_fired(tr):
    return any(s["step"] == "sufficiency" and s["detail"] == "insufficient" for s in tr.steps)


SHAPE_RULES = {
    "no-retrieval": ("route=direct · 0 retrievals",
                     lambda t: _route_of(t) == "direct" and n_steps(t, "retrieve") == 0),
    "multi-hop":    ("decompose · ≥2 retrievals",
                     lambda t: n_steps(t, "decompose") >= 1 and n_steps(t, "retrieve") >= 2),
    "needs-web":    ("sufficiency=insufficient · web step",
                     lambda t: _sufficiency_fired(t) and n_steps(t, "web_search") >= 1),
    "site":         ("1 retrieval · no decompose",
                     lambda t: n_steps(t, "retrieve") == 1 and n_steps(t, "decompose") == 0),
    "topic":        ("1 retrieval · no decompose",
                     lambda t: n_steps(t, "retrieve") == 1 and n_steps(t, "decompose") == 0),
}


def expected_shape(tag):  return SHAPE_RULES.get(tag, ("(no rule)", lambda t: True))[0]
def shape_ok(tag, tr):    return bool(SHAPE_RULES.get(tag, ("", lambda t: True))[1](tr))


def actual_shape(tr) -> str:
    return (f"route={_route_of(tr)} · {n_steps(tr, 'retrieve')} retr · "
            f"{n_steps(tr, 'decompose')} dec · {n_steps(tr, 'web_search')} web")


def trace_df(tr) -> pd.DataFrame:
    return pd.DataFrame([{"#": i + 1, "step": s["step"], "detail": s["detail"][:40],
                          "ms": s["ms"], "calls": s["calls"], "tok~": s["tokens_est"],
                          "err": s["error"][:14]} for i, s in enumerate(tr.steps)])


def trace_lines(tr) -> str:
    return "\n".join(f"{i + 1}. {s['step']}({s['detail']})" for i, s in enumerate(tr.steps))


# ── lazily-built shared artifacts (every stage is skip-safe) ────────────────
def ensure_store():
    global store
    if store is None:
        with Spinner("embedding the catalog corpus (keyless, local MiniLM, ~20s)"):
            store = corpus.load_catalog_corpus(rebuild=True)
    if not GOLDEN:
        GOLDEN[:] = corpus.load_golden_catalog()


def slice_cases() -> list[dict]:
    """One case per tag — the A/B slice. Small on purpose: two agents × judge per case."""
    picked, out = set(), []
    for c in GOLDEN:
        if c["tag"] not in picked:
            picked.add(c["tag"]); out.append(c)
    return out


def grade_answer(q, ans, expected) -> float:
    p = ('Grade the ANSWER against EXPECTED: 1.0 fully correct, 0.5 partial, 0.0 wrong/missing. '
         'If EXPECTED says the fact is not in the catalog, reward an answer that says so or sources it. '
         'JSON only: {"score": <1.0|0.5|0.0>}.\n\n'
         f'Q: {q}\nEXPECTED: {expected}\nANSWER: {ans}')
    return _score(_json(ask(p))["score"])


def ensure_ab():
    """Stage 5's head-to-head table — also the substrate stage 7's gate reads."""
    if AB_ROWS:
        return
    ensure_store()
    cases = slice_cases()
    with Spinner(f"racing 2 agents × {len(cases)} cases, then judging both answers (~45 LLM calls)"):
        for c in cases:
            try:
                row = {"tag": c["tag"], "query": c["q"][:30]}
                for agent, prefix in (("routed", "R"), ("always-agentic", "A")):
                    tr, ans = run(agent, c["q"])
                    row[f"{prefix}.steps"] = step_count(tr)
                    row[f"{prefix}.ms"] = wall_ms(tr)
                    row[f"{prefix}.score"] = grade_answer(c["q"], ans, c["expected"])
                AB_ROWS.append(row)
            except (ValueError, KeyError, RuntimeError):
                pass                     # one bad case drops; the comparison survives


# ═════════════════════════════════════════════════════════════════════════════
# THE STAGES
# ═════════════════════════════════════════════════════════════════════════════
def s1_setup():
    ensure_store()
    s = store.stats()
    tags = {t: sum(c["tag"] == t for c in GOLDEN) for t in sorted({c["tag"] for c in GOLDEN})}
    print(f"  {green('corpus ready')}: {s.get('documents')} docs · {s.get('chunks')} chunks · golden: {len(GOLDEN)} cases")
    print("  cases by shape: " + " · ".join(f"{k}={v}" for k, v in tags.items()))
    print(f"  web step (Tavily): {green('configured') if web_available() else yellow('NO KEY — the web step still RECORDS as skipped, so path shape stays checkable')}")
    panel("two kinds of eval", (
        "ANSWER eval  (Labs 1, 3, 5)     grades the OUTPUT      → 'is it right?'\n"
        "PATH eval    (this lab)          grades the TRAJECTORY  → 'was getting there sane?'\n"
        "\n"
        "An agent that is right for the wrong reasons is a production incident waiting for\n"
        "a slightly different question. Answer evals cannot see it. Path evals can."))
    if not web_available():
        note("no Tavily key: web_search will record `skipped — no key` instead of results. Every "
             "path metric in this lab still works — a step that ran and returned nothing is still "
             "a step the agent chose to take. That's the honest degradation.")
    note("the golden tags do double duty now. In Lab 3 a tag told you which failure shape a case "
         "exposes. Here the same tag DECLARES the path shape the agent should take — which is what "
         "makes tool-call accuracy gradeable without hand-labelling every run.")


def s2_trace():
    ensure_store()
    c = next(c for c in GOLDEN if c["tag"] == "multi-hop")
    print(f"  Q: {c['q']}\n")
    with Spinner("running the routed agent, tracing every step (~5 LLM calls)"):
        tr, ans = run("routed", c["q"])
    show_df(trace_df(tr), f"TRAJECTORY · agent={tr.agent}")
    print(f"  path      : {bold(tr.path())}")
    print(f"  totals    : {step_count(tr)} steps · {wall_ms(tr)} ms · {llm_calls(tr)} LLM calls · ~{tokens_est(tr)} tokens")
    print(f"  {dim('→ answer: ' + (ans[:150] or '').replace(chr(10), ' '))}")
    note("that table is the exhibit for this whole lab. Nothing about it is exotic — the tracer is "
         "a context manager that appends a dict. But once the path is DATA instead of stdout noise, "
         "you can count it, compare it, diff it across releases, and hand it to a judge. Untraced "
         "agents aren't unmeasurable because measuring is hard; they're unmeasurable because nobody "
         "wrote down what happened.")


def s3_counters():
    ensure_store()
    c = next(c for c in GOLDEN if c["tag"] == "multi-hop")
    if c["q"] not in RUNS["routed"]:             # stage 2 was skipped — trace one run first
        print(f"  {dim('(no cached trajectory — tracing one run first, ~5 LLM calls)')}")
        with Spinner("tracing one routed run"):
            run("routed", c["q"])
    healthy, _ = run("routed", c["q"])           # cached from stage 2 when it ran

    # A trajectory recorded from an agent that got stuck. Hard-coded on purpose: you should
    # be able to compute every metric below with the LLM disconnected.
    stuck = Trace("stuck-agent", "Which plan includes Pitstop support and what does it cost?")
    qkey = "which plan includes pitstop support and what does it cost?"
    for name, detail, ms, err in [
        ("route", "retrieve", 640, ""),
        ("retrieve", '4 docs · "Which plan includes Pit"', 91, ""),
        ("sufficiency", "insufficient", 702, ""),
        ("web_search", "0 results", 3011, "TimeoutError"),
        ("retrieve", '4 docs · "Which plan includes Pit"', 88, ""),
        ("sufficiency", "insufficient", 690, ""),
        ("retrieve", '4 docs · "Which plan includes Pit"', 93, ""),
        ("sufficiency", "insufficient", 711, ""),
        ("answer", "402 chars · 4 docs", 900, ""),
    ]:
        stuck.steps.append({"step": name, "detail": detail, "ms": ms, "calls": 1 if name != "retrieve" else 0,
                            "tokens_est": 240 if name != "retrieve" else 0, "error": err,
                            "query": qkey if name == "retrieve" else ""})

    df = pd.DataFrame([metrics(healthy), metrics(stuck)])
    show_df(df, "deterministic trajectory metrics — ZERO LLM calls")
    show_df(trace_df(stuck), "the stuck agent's path (recorded, not simulated)")
    print(f"  the stuck agent answered. An answer-only eval would have scored it and moved on.")
    print(f"  the counters see it: {yellow(f'redundant={redundant_steps(stuck)} · loop={loop_detected(stuck)} · tool_err={tool_error_rate(stuck)}')}")
    note("five metrics, no judge, no key, no flakiness: step_count and wall_ms are your cost and "
         "latency SLO; redundant_steps catches an agent re-asking a question it already asked; "
         "tool_error_rate is the one number that separates 'the agent decided not to' from 'the "
         "tool was down'; loop_detected finds the retrieve→judge→retrieve cycle before your bill "
         "does. Reach for a judge only where counting genuinely can't reach — that's stage 6.")


def s4_shape():
    ensure_store()
    rows = []
    with Spinner(f"tracing the routed agent across all {len(GOLDEN)} golden cases (~50 LLM calls)"):
        for c in GOLDEN:
            try:
                tr, _ = run("routed", c["q"])
            except (ValueError, KeyError, RuntimeError):
                continue
            rows.append({"tag": c["tag"], "query": c["q"][:28], "expected shape": expected_shape(c["tag"]),
                         "actual": actual_shape(tr), "ok": "✓" if shape_ok(c["tag"], tr) else "✗"})
    if not rows:
        print(f"  {yellow('no cases completed — cannot score path shape this run')}"); return
    df = pd.DataFrame(rows)
    show_df(df, "tool-call accuracy — did the agent take the right SHAPE of path?")
    acc = (df["ok"] == "✓").mean() if len(df) else 0.0
    print(f"  {bold('TOOL-CALL ACCURACY')}: {acc:.2f}  ({int((df['ok'] == '✓').sum())}/{len(df)} cases took the expected path)")
    by_tag = df.assign(ok=(df["ok"] == "✓").astype(float)).groupby("tag")["ok"].mean().round(2)
    show_df(by_tag.reset_index().rename(columns={"ok": "shape accuracy"}), "where the path goes wrong (by tag)")
    misses = df[df["ok"] == "✗"]
    if len(misses):
        print(f"  {yellow('read the misses as bugs, not noise:')}")
        for _, m in misses.iterrows():
            print(f"    {dim('·')} [{m['tag']}] {m['query']}  {dim('wanted: ' + m['expected shape'])}  {dim('got: ' + m['actual'])}")
    note("this is the headline metric of the lab, and the one production teams skip. Answer accuracy "
         "tells you whether today's questions worked; tool-call accuracy tells you whether the agent's "
         "DECISION LOGIC is sound — which is what generalizes to tomorrow's questions. A no-retrieval "
         "case answered correctly after four retrievals is a latent failure, and only this table "
         "shows it to you.")


def s5_same_answer():
    ensure_ab()
    if not AB_ROWS:
        print(f"  {yellow('no comparable cases completed — skipping the head-to-head')}"); return
    df = pd.DataFrame(AB_ROWS)
    show_df(df, "same questions, two agents — answers vs paths")
    r_score, a_score = df["R.score"].mean(), df["A.score"].mean()
    r_steps, a_steps = df["R.steps"].mean(), df["A.steps"].mean()
    r_ms, a_ms = df["R.ms"].mean(), df["A.ms"].mean()
    summary = pd.DataFrame([
        {"agent": "routed", "answer score": round(r_score, 2), "avg steps": round(r_steps, 1),
         "avg ms": int(r_ms), "score per step": round(r_score / max(r_steps, 1), 3)},
        {"agent": "always-agentic", "answer score": round(a_score, 2), "avg steps": round(a_steps, 1),
         "avg ms": int(a_ms), "score per step": round(a_score / max(a_steps, 1), 3)},
    ])
    show_df(summary, "the money table — efficiency is the column answer evals don't have")
    print(f"  answer delta : {a_score - r_score:+.2f}   {dim('(what an answer-only eval would report)')}")
    print(f"  step delta   : {a_steps - r_steps:+.1f} steps  ·  {a_ms - r_ms:+.0f} ms   "
          f"{yellow('(what it would MISS)')}")
    if abs(a_score - r_score) <= 0.1 and a_steps > r_steps:
        print(f"  {green('→ the two agents are statistically tied on answers and nowhere near tied on work.')}")
    elif a_score < r_score - 0.1 and a_steps > r_steps:
        print(f"  {yellow('→ this run, the extra work also HURT the answers')} — always-agentic dragged a "
              f"no-retrieval case through retrieval and got it wrong. Doing more is not doing better.")
    note("this is the lab in one table. Ship-decision-by-answer-score says 'no regression, ship it' "
         "and you quietly pay 2-3× per query forever, with 2-3× the surface area for a tool to fail "
         "on. Efficiency — quality per step — is the metric that makes the waste visible, and it is "
         "impossible to compute without a trajectory.")


def s6_path_judge():
    ensure_store()
    cases = slice_cases()
    picks = []
    for c in cases:
        if c["tag"] in ("no-retrieval", "multi-hop"):
            picks.append(("always-agentic", c))
        if c["tag"] in ("no-retrieval", "needs-web"):
            picks.append(("routed", c))
    picks = picks[:4]
    rows = []
    with Spinner(f"judging {len(picks)} trajectories — the judge reads the PATH, never the answer"):
        for agent, c in picks:
            try:
                tr, _ = run(agent, c["q"])
                verdict = _json(ask(
                    "You audit an AI agent's EXECUTION TRAJECTORY. Judge the PATH ONLY — you are not "
                    "shown the answer and must not speculate about it.\n"
                    f"Available steps: {', '.join(STEP_NAMES)}.\n"
                    "Was any step unnecessary for THIS question? Was a needed step missing?\n"
                    'JSON only: {"efficient": true|false, "missing": ["<step>"], '
                    '"unnecessary": ["<step>"], "reason": "<one sentence>"}\n\n'
                    f"QUESTION: {c['q']}\n\nTRAJECTORY:\n{trace_lines(tr)}"))
                rows.append({"agent": agent, "tag": c["tag"], "steps": step_count(tr),
                             "efficient": "✓" if verdict.get("efficient") else "✗",
                             "unnecessary": ", ".join(verdict.get("unnecessary") or [])[:26],
                             "missing": ", ".join(verdict.get("missing") or [])[:20],
                             "reason": str(verdict.get("reason", ""))[:46]})
            except (ValueError, KeyError, RuntimeError):
                continue
    if not rows:
        print(f"  {yellow('no trajectories judged this run')}"); return
    show_df(pd.DataFrame(rows), "LLM-as-judge, applied to the PATH")
    counters = pd.DataFrame([metrics(run(a, c["q"])[0]) | {"tag": c["tag"]} for a, c in picks
                             if c["q"] in RUNS[a]])
    if len(counters):
        show_df(counters[["agent", "tag", "steps", "redundant", "loop", "tool_err"]],
                "the same trajectories, seen by the deterministic counters")
    note("compare the two tables. The counters are perfect at what they measure and blind to "
         "everything else: a decompose→retrieve→web path for 'what is 17 × 4' has zero redundant "
         "steps, no loop and a clean error rate — every counter says HEALTHY. The judge reads the "
         "question next to the path and says: you searched a document corpus for arithmetic. "
         "Counters catch structural waste; a judge catches SEMANTIC waste. Production needs both, "
         "and you run the cheap one on every request and the expensive one on a sample.")


def s7_gate():
    ensure_ab()
    if not AB_ROWS:
        print(f"  {yellow('no A/B data — cannot evaluate the gate')}"); return
    df = pd.DataFrame(AB_ROWS)
    base = {"score": df["R.score"].mean(), "steps": df["R.steps"].mean(), "ms": df["R.ms"].mean()}
    cand = {"score": df["A.score"].mean(), "steps": df["A.steps"].mean(), "ms": df["A.ms"].mean()}
    QUALITY_TOL, INFLATION_TOL = 0.02, 1.25       # product decisions, written down as numbers
    checks = [
        {"criterion": "answer correctness", "baseline": round(base["score"], 2), "candidate": round(cand["score"], 2),
         "rule": f"≥ baseline − {QUALITY_TOL}", "pass": cand["score"] >= base["score"] - QUALITY_TOL},
        {"criterion": "steps per query", "baseline": round(base["steps"], 1), "candidate": round(cand["steps"], 1),
         "rule": f"≤ baseline × {INFLATION_TOL}", "pass": cand["steps"] <= base["steps"] * INFLATION_TOL},
        {"criterion": "wall ms per query", "baseline": int(base["ms"]), "candidate": int(cand["ms"]),
         "rule": f"≤ baseline × {INFLATION_TOL}", "pass": cand["ms"] <= base["ms"] * INFLATION_TOL},
    ]
    gate = pd.DataFrame([c | {"pass": "PASS" if c["pass"] else "FAIL"} for c in checks])
    show_df(gate, "THE TRAJECTORY GATE — candidate 'always-agentic' vs baseline 'routed'")
    ok = all(c["pass"] for c in checks)
    if ok:
        print(f"  {green('✔ VERDICT: SHIP')} — no quality regression and no path inflation.")
    else:
        failed = [c["criterion"] for c in checks if not c["pass"]]
        print(f"  {red('✘ VERDICT: BLOCK')} — failed: {', '.join(failed)}")
        print(f"  {dim('note WHICH criterion failed: an answer-only gate would have passed this candidate.')}")
    note("a release gate that only reads answer scores is a gate with a hole in it — every "
         "'let's just always run the full loop' change walks straight through. Add two path "
         "criteria and the hole closes. Pick the tolerances deliberately (they are your cost and "
         "latency SLO, same as Lab 3's budget caps), version them next to the golden set, and let "
         "the gate print a verdict rather than throw — a gate nobody can read is a gate people "
         "learn to bypass.")


TUTOR = Tutor(
    title="Lab 3e — Judge the Path, Not Just the Answer",
    tagline="Modern AI Pro · AI Architect · Pillar II · trajectory evaluation",
    mission="""
    Every eval you have run so far grades the ANSWER. Two agents can hand you the same
    answer while one took one step and the other took nine — identical score, wildly
    different cost, latency and blast radius. That gap is where agents rot in production.

    This lab traces Lab 3's agent so every run emits a TRAJECTORY, then grades the
    trajectory four ways: deterministic counters that need no LLM at all, tool-call
    accuracy against the path shape each query deserves, a head-to-head where two agents
    tie on answers and diverge on work, and an LLM judge that reads the path and never
    sees the answer. It ends with a release gate a wasteful agent cannot walk through.
    """,
    stages=[
        Stage("Setup — the catalog, the golden tags, and two kinds of eval", """
            Load the shallow catalog corpus and Lab 3's tagged golden set. The tags did one
            job before (which failure shape a case exposes); here they do a second one —
            each tag DECLARES the path shape the agent ought to take, which is what makes
            path accuracy gradeable without hand-labelling every run. We also draw the line
            this lab lives on: answer eval asks 'is it right?', path eval asks 'was getting
            there sane?'""", s1_setup, "0"),
        Stage("Trace one run — the path becomes an artifact", """
            Run the agent on a multi-hop question with a tracer wrapped around every step,
            then print the trajectory as a table: step, detail, ms, LLM calls, tokens. The
            tracer is a context manager that appends a dict — 30 lines. The point is that
            once the path is DATA, you can count it, diff it, and hand it to a judge.""", s2_trace, "~5"),
        Stage("Deterministic trajectory metrics — five numbers, zero LLM calls", """
            step_count and wall_ms (your cost + latency SLO), redundant_steps (the agent
            re-asked a question it already asked), tool_error_rate (the tool broke vs the
            agent chose not to call it), and loop_detected (a repeated step cycle). We run
            them against a healthy path and a recorded stuck-agent path so you watch every
            counter fire. Not every eval needs a judge — reach for one only where counting
            can't reach.""", s3_counters, "0"),
        Stage("Tool-call accuracy — did it take the right SHAPE of path? ⭐", """
            The headline metric. Per golden tag there is an expected path shape:
            no-retrieval ⇒ route=direct and ZERO retrievals; multi-hop ⇒ decompose plus ≥2
            retrievals; needs-web ⇒ sufficiency fires and a web step happens. Trace every
            golden case, compare expected shape vs actual, score it. A case answered right
            via the wrong path is a latent failure — this table is where you see it.""", s4_shape, "~50"),
        Stage("Same answer, different path — the money stage", """
            Race the routed agent against an 'always-agentic' one (always decompose, always
            web-check) on the same questions. Judge the answers: near-identical. Count the
            paths: not close. The side-by-side ends with score-per-step, the efficiency
            column an answer-only eval structurally cannot produce.""", s5_same_answer, "~45"),
        Stage("LLM-as-judge on the path — what counters can't see", """
            One judge call per case that reads the TRAJECTORY and never the answer: was any
            step unnecessary, was a needed step missing? Returns JSON. Then we put its
            verdicts next to stage 3's counters and find the blind spot: searching a
            document corpus for '17 × 4' is structurally clean — no loops, no redundancy —
            and semantically absurd. Counters catch waste; judges catch WRONGNESS.""", s6_path_judge, "~4"),
        Stage("The trajectory gate — correctness AND path, or no ship", """
            Combine everything into a release rule: a candidate ships only if answer
            correctness doesn't regress AND steps/latency don't inflate past a tolerance you
            chose on purpose. Run the always-agentic agent at it and watch a candidate that
            an answer-only gate would have waved through get blocked. The gate PRINTS its
            verdict — a gate nobody can read is a gate people bypass.""", s7_gate, "0"),
    ],
    outro="""
    The takeaway is a habit, not a metric: when an agent regresses in production, the answer
    score tells you THAT it broke and the trajectory tells you WHERE. Instrument the path on
    day one — the tracer costs 30 lines and buys you every metric in this lab.

    Cheap counters run on every request; the path judge runs on a sample; the gate runs on
    every release. Lab 5 calibrates judges like the one in stage 6 against human labels, and
    Lab 7 puts a human in the loop at the exact steps this trace makes visible.
    """,
)


def main():
    provider = "provider: "
    try:
        provider += llm._provider()
    except Exception:
        provider += "NONE — set OPENAI_API_KEY (class token) in .env"
    web = "web: Tavily ✓" if web_available() else "web: no key (the web step records as skipped)"
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · {provider} · {web}")


if __name__ == "__main__":
    main()
