# -*- coding: utf-8 -*-
"""Lab 3c — Agent Architectures: The Authoring Workbench (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · after Lab 3b (adaptive RAG)

Run it as a guided walkthrough:   python labs/lab_3c.py
Piped / non-interactive input auto-runs every stage (CI-safe).
Needs the agents extra:           pip install -e ".[evals,viz,agents]"

The mission: every agent framework — CrewAI, AutoGen, LangGraph's own prebuilts —
sells you the same four or five SHAPES: a tool-calling loop, a self-critique loop,
a planner over an executor, a supervisor over workers. This lab strips the branding
off. You build each shape yourself as a ~30-line LangGraph graph (state + nodes +
edges — nothing else), watch it think in a live trace, race the shapes on the same
golden set with a call meter running, and finish in a free-play workbench where you
compose your OWN agent — architecture × tools × caps — and fight for the
leaderboard. After this lab a framework is a convenience, not a mystery.
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

import ast
import json
import time
from typing import TypedDict

import mai_rag
from mai_rag import corpus, llm
from mai_rag.tutor import Tutor, Stage, Spinner, note, panel, choice, dim, green, yellow, bold

# ── shared state ─────────────────────────────────────────────────────────────
store = None
GOLDEN: list[dict] = []
LEADERBOARD: list[dict] = []         # every scored agent config lands here
VERBOSE = True                       # live trace on demo runs; off during the showdown

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
    """Structural JSON extraction (parsing, not classification): decode the FIRST valid object,
    ignoring any prose around it. Clear ValueError when there is no JSON at all."""
    s = raw or ""
    i = s.find("{")
    while i != -1:
        try:
            obj, _ = json.JSONDecoder().raw_decode(s[i:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
        i = s.find("{", i + 1)
    raise ValueError(f"model did not return JSON: {s[:120]!r}")

def trace(role, text):
    if VERBOSE:
        print(f"    {yellow(role):<24} {dim(str(text)[:88])}")

def _graphs():
    """One import chokepoint with a clean hint — the lab dies helpfully, not with a traceback."""
    try:
        from langgraph.graph import StateGraph, START, END
        return StateGraph, START, END
    except ImportError:
        raise RuntimeError('LangGraph is not installed — run: pip install -e ".[evals,viz,agents]" '
                           "(or just: pip install langgraph) and restart the lab.") from None

# ── ONE state schema for every architecture (glass-box: read it, it's a dict) ─
class S(TypedDict, total=False):
    q: str            # the question (every graph starts here)
    answer: str       # the final answer (every graph ends here)
    action: dict      # react: the tool call the agent just chose
    obs: list         # react: tool observations so far
    hops: int         # react / supervisor: loop counter the cap checks
    draft: str        # reflection: current answer attempt
    critique: str     # reflection: the critic's objection
    rounds: int       # reflection: revision counter
    plan: list        # plan-execute: remaining steps
    results: list     # plan-execute: finished step answers
    facts: list       # supervisor: what the researcher gathered
    next: str         # supervisor: who works next

# ── the tools (retrieval is keyless; calc parses structurally via ast) ───────
def tool_search(query: str) -> str:
    hits = store.search(str(query), k=3)
    return " | ".join(f"({h.title}) {h.content[:160]}" for h in hits) or "no hits"

def tool_calc(expr: str) -> str:
    """Arithmetic only — ast parse + whitelist (structural parsing, not classification)."""
    ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub,
               ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.USub, ast.UAdd)
    try:
        tree = ast.parse(str(expr), mode="eval")
        if not all(isinstance(n, ALLOWED) for n in ast.walk(tree)):
            return "calc error: numbers and + - * / // % ** only"
        return str(eval(compile(tree, "<calc>", "eval")))
    except Exception as e:
        return f"calc error: {e}"

TOOLBOX = {"search_corpus": (tool_search, "search the course-catalog corpus; input = a search query"),
           "calc":          (tool_calc, "arithmetic; input = an expression like (12*4)+3")}

# ═════════════════════════════════════════════════════════════════════════════
# THE FOUR SHAPES — each builder returns (compiled graph, topology string).
# Every one is state + nodes + edges and nothing else. Read them; that's the lab.
# ═════════════════════════════════════════════════════════════════════════════

def build_react(tools=("search_corpus", "calc"), cap=4):
    """SHAPE 1 · the tool-calling loop: agent ⇄ tools until it answers (or the cap fires)."""
    StateGraph, START, END = _graphs()
    menu = "\n".join(f'  "{t}" — {TOOLBOX[t][1]}' for t in tools)

    def agent(st: S):
        seen = "\n".join(st.get("obs", [])) or "(none yet)"
        raw = ask(
            "You are a tool-calling agent. Decide ONE next move.\nTOOLS:\n" + menu +
            '\nReply JSON only — either {"tool": "<name>", "input": "<input>"} to act, '
            'or {"answer": "<final answer>"} when the observations are enough.\n\n'
            f"QUESTION: {st['q']}\nOBSERVATIONS SO FAR:\n{seen}")
        try:
            d = _json(raw)
        except ValueError:             # prose instead of JSON = the model already answered
            d = {"answer": raw.strip()}
        if d.get("answer"):
            trace("agent → answer", d["answer"]); return {"answer": d["answer"]}
        trace("agent → tool", f"{d.get('tool')}({str(d.get('input'))[:50]})")
        return {"action": {"tool": d.get("tool", ""), "input": d.get("input", "")}}

    def tools_node(st: S):
        a = st["action"]
        fn = TOOLBOX.get(a["tool"], (None,))[0]
        out = fn(a["input"]) if fn else f"unknown tool: {a['tool']}"
        trace("  ↳ observation", out)
        return {"obs": st.get("obs", []) + [f"{a['tool']}({a['input']}) → {out}"],
                "hops": st.get("hops", 0) + 1}

    def force_answer(st: S):   # the budget cap from Lab 3, as a NODE — the loop cannot run away
        trace("cap fired", f"{cap} hops — answering from what we have")
        return {"answer": ask("Answer the question now from these observations only; say what's "
                              f"missing if they fall short.\n\nQUESTION: {st['q']}\n\n" +
                              "\n".join(st.get("obs", [])))}

    def decide(st: S):
        if st.get("answer"):
            return "done"
        return "force" if st.get("hops", 0) >= cap else "act"

    g = StateGraph(S)
    g.add_node("agent", agent); g.add_node("tools", tools_node); g.add_node("force", force_answer)
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", decide, {"act": "tools", "force": "force", "done": END})
    g.add_edge("tools", "agent"); g.add_edge("force", END)
    return g.compile(), f"START → agent ⇄ tools (cap {cap} → force) → END"

def build_reflect(rounds=2):
    """SHAPE 2 · the self-critique loop: generate → critique → revise until the critic passes."""
    StateGraph, START, END = _graphs()

    def generate(st: S):
        ctx = tool_search(st["q"])
        d = ask("Answer using ONLY the context. If the answer isn't there, say you don't have "
                f"enough information.\n\nQuestion: {st['q']}\n\nContext:\n{ctx}\n\nAnswer:")
        trace("generate", d); return {"draft": d, "rounds": 0}

    def critique(st: S):
        try:
            d = _json(ask('You are a strict reviewer. Does the DRAFT actually answer the QUESTION — '
                          'complete, specific, no waffle? Reply JSON only: '
                          '{"verdict": "pass"|"revise", "objection": "<one concrete fix, or empty>"}\n\n'
                          f"QUESTION: {st['q']}\nDRAFT: {st['draft']}"))
        except ValueError:             # an unparseable critique must not kill the loop — pass the draft
            d = {"verdict": "pass"}
        trace("critique", f"{d.get('verdict')} — {d.get('objection', '')}")
        return {"critique": d.get("objection", "") if d.get("verdict") == "revise" else ""}

    def revise(st: S):
        d = ask(f"Rewrite the DRAFT to fix the OBJECTION. Keep what was right.\n\n"
                f"QUESTION: {st['q']}\nDRAFT: {st['draft']}\nOBJECTION: {st['critique']}\n\nRevised answer:")
        trace("revise", d); return {"draft": d, "rounds": st.get("rounds", 0) + 1}

    def decide(st: S):
        return "revise" if st.get("critique") and st.get("rounds", 0) < rounds else "done"

    def finish(st: S):
        return {"answer": st["draft"]}

    g = StateGraph(S)
    for n, f in (("generate", generate), ("critique", critique), ("revise", revise), ("finish", finish)):
        g.add_node(n, f)
    g.add_edge(START, "generate"); g.add_edge("generate", "critique")
    g.add_conditional_edges("critique", decide, {"revise": "revise", "done": "finish"})
    g.add_edge("revise", "critique"); g.add_edge("finish", END)
    return g.compile(), f"START → generate → critique ⇄ revise (≤{rounds}) → END"

def build_plan(max_steps=3):
    """SHAPE 3 · plan-and-execute: a planner writes the steps, an executor loop runs them."""
    StateGraph, START, END = _graphs()

    def plan(st: S):
        try:
            d = _json(ask(f"Write the minimal research plan (1-{max_steps} steps, each ONE corpus "
                          'lookup). Reply JSON only: {"steps": ["...", ...]}\n\n'
                          f"QUESTION: {st['q']}"))
        except ValueError:             # no plan parsed → the question is its own one-step plan
            d = {}
        steps = [s for s in d.get("steps", [st["q"]]) if isinstance(s, str)][:max_steps] or [st["q"]]
        trace("plan", " · ".join(steps)); return {"plan": steps, "results": []}

    def step(st: S):
        s = st["plan"][0]
        ctx = tool_search(s)
        a = ask(f"Answer from the context only; say so if it isn't there.\n\nQuestion: {s}\n\n"
                f"Context:\n{ctx}\n\nAnswer:")
        trace(f"step {len(st['results']) + 1}", f"{s} → {a}")
        return {"plan": st["plan"][1:], "results": st["results"] + [f"Q: {s}\nA: {a}"]}

    def synthesize(st: S):
        return {"answer": ask("Synthesize ONE final answer to the ORIGINAL question from the step "
                              "answers. If they show the information isn't available, say so.\n\n"
                              f"Original question: {st['q']}\n\n" + "\n\n".join(st["results"]) +
                              "\n\nFinal answer:")}

    g = StateGraph(S)
    g.add_node("plan", plan); g.add_node("step", step); g.add_node("synthesize", synthesize)
    g.add_edge(START, "plan")
    g.add_conditional_edges("plan", lambda st: "step" if st["plan"] else "synth",
                            {"step": "step", "synth": "synthesize"})
    g.add_conditional_edges("step", lambda st: "step" if st["plan"] else "synth",
                            {"step": "step", "synth": "synthesize"})
    g.add_edge("synthesize", END)
    return g.compile(), f"START → plan → step ⟳ (≤{max_steps}) → synthesize → END"

def build_supervisor(cap=6):
    """SHAPE 4 · supervisor + workers: a boss LLM routes between a researcher and a writer."""
    StateGraph, START, END = _graphs()

    def supervisor(st: S):
        try:
            d = _json(ask('You supervise two workers. "researcher" gathers facts from the corpus; '
                          '"writer" composes the final answer from gathered facts (send the writer only '
                          'when the facts suffice). Reply JSON only: '
                          '{"next": "researcher"|"writer", "instruction": "<what they should do>"}\n\n'
                          f"QUESTION: {st['q']}\nFACTS GATHERED:\n" +
                          ("\n".join(st.get("facts", [])) or "(none)")))
        except ValueError:             # an unparseable routing call defaults to shipping what we have
            d = {"next": "writer"}
        nxt = d.get("next") if d.get("next") in ("researcher", "writer") else "writer"
        trace("supervisor", f"→ {nxt}: {d.get('instruction', '')}")
        return {"next": nxt, "hops": st.get("hops", 0) + 1}

    def researcher(st: S):
        ctx = tool_search(st["q"] if not st.get("facts") else
                          ask(f"One short corpus search query for what's still MISSING to answer: "
                              f"{st['q']}\nAlready known:\n" + "\n".join(st["facts"]) + "\nQuery:"))
        fact = ask(f"Extract the facts relevant to the question, one per line, from:\n{ctx}\n\n"
                   f"Question: {st['q']}\nFacts:")
        trace("researcher", fact)
        return {"facts": st.get("facts", []) + [fact]}

    def writer(st: S):
        a = ask("Write the final answer from these gathered facts only; say what's missing if they "
                f"fall short.\n\nQUESTION: {st['q']}\nFACTS:\n" + "\n".join(st.get("facts", [])) +
                "\n\nAnswer:")
        trace("writer", a); return {"answer": a}

    def decide(st: S):
        if st.get("hops", 0) >= cap:       # the boss is also on a budget
            return "writer"
        return st["next"]

    g = StateGraph(S)
    g.add_node("supervisor", supervisor); g.add_node("researcher", researcher); g.add_node("writer", writer)
    g.add_edge(START, "supervisor")
    g.add_conditional_edges("supervisor", decide, {"researcher": "researcher", "writer": "writer"})
    g.add_edge("researcher", "supervisor"); g.add_edge("writer", END)
    return g.compile(), f"START → supervisor ⇄ researcher (cap {cap}) → writer → END"

ARCHITECTURES = {
    "react":      ("the tool-calling loop (ReAct)", lambda: build_react()),
    "reflect":    ("generate → critique → revise", lambda: build_reflect()),
    "plan":       ("plan the steps, then execute them", lambda: build_plan()),
    "supervisor": ("a boss routing researcher + writer", lambda: build_supervisor()),
}

def run_agent(app, q: str) -> str:
    out = app.invoke({"q": q})
    return out.get("answer", "")

def naive(q: str) -> str:
    """The Lab-1 baseline every architecture must beat — retrieve once, answer once."""
    ctx = tool_search(q)
    return ask("Answer using ONLY the context. If the answer isn't there, say you don't have "
               f"enough information.\n\nQuestion: {q}\n\nContext:\n{ctx}\n\nAnswer:")

def grade(q, answer, expected):
    p = ("Grade the ANSWER against EXPECTED. 1.0 fully correct, 0.5 partial, 0.0 wrong/missing. "
         "An honest 'I don't have enough information' is CORRECT when EXPECTED says the "
         "information isn't in the corpus.\n"
         'Reply JSON only: {"reason":"<short>","score":<1.0|0.5|0.0>}.\n\n'
         f"QUESTION: {q}\nEXPECTED: {expected}\nANSWER: {answer}")
    try:
        return float(_json(ask(p, temperature=0))["score"])
    except (ValueError, KeyError, TypeError):        # one prose judge reply must not kill a race
        return 0.0

def score_agent(label, runner, cases, quiet=False):
    """Run an agent over golden cases; quality × calls × seconds → one leaderboard row."""
    global VERBOSE
    VERBOSE, was = False, VERBOSE
    scores, t0 = [], time.time()
    meter_reset()
    for c in cases:
        a = runner(c["q"])
        calls_so_far = METER["calls"]
        scores.append(grade(c["q"], a, c["expected"]))
        METER["calls"] = calls_so_far + 1            # count the judge call explicitly
    calls, _ = meter_read()
    VERBOSE = was
    row = {"config": label, "quality": round(sum(scores) / len(scores), 2),
           "calls": calls - len(cases), "judge": len(cases), "secs": round(time.time() - t0, 1)}
    if not any(r["config"] == label for r in LEADERBOARD):
        LEADERBOARD.append(row)
    if not quiet:
        print(f"  {label:<30} quality={row['quality']:.2f}  {yellow(str(row['calls']) + ' calls')}  {dim(str(row['secs']) + 's')}")
    return row

def show_leaderboard(top=10):
    rows = sorted(LEADERBOARD, key=lambda r: (-r["quality"], r["calls"]))[:top]
    body = "\n".join(f"{i+1:>2}. {r['config']:<30} quality={r['quality']:.2f}  {r['calls']:>3} calls  {r['secs']:>6}s"
                     for i, r in enumerate(rows))
    panel("LEADERBOARD — quality first, cheapest wins ties", body)

def golden_slice():
    """One case per shape of difficulty — same slice for every architecture, so rows compare."""
    out = []
    for tag in ("no-retrieval", "topic", "multi-hop"):
        c = next((c for c in GOLDEN if c["tag"] == tag), None)
        if c:
            out.append(c)
    return out

# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_primitive():
    global store, GOLDEN
    with Spinner("loading catalog corpus (embeds on first run)"):
        store = corpus.load_catalog_corpus("catalog.db")
    GOLDEN[:] = corpus.load_golden_catalog()
    print(f"  {green('loaded')}: {store.stats().get('documents')} docs · {len(GOLDEN)} golden cases\n")
    StateGraph, START, END = _graphs()

    # A whole agent runtime in 10 lines — keyless, so you see the MACHINE, not the model.
    def fetch(st: S):     return {"obs": [tool_search(st["q"])]}
    def too_long(st: S):  return "trim" if len(st["obs"][0]) > 300 else "keep"
    def trim(st: S):      return {"obs": [st["obs"][0][:300] + " …"]}
    def present(st: S):   return {"answer": f"[{len(st['obs'][0])} chars of context ready]"}
    g = StateGraph(S)
    g.add_node("fetch", fetch); g.add_node("trim", trim); g.add_node("present", present)
    g.add_edge(START, "fetch")
    g.add_conditional_edges("fetch", too_long, {"trim": "trim", "keep": "present"})
    g.add_edge("trim", "present"); g.add_edge("present", END)
    app = g.compile()

    panel("the entire LangGraph API this lab uses", "\n".join([
        "state    a TypedDict — nodes read it, return the keys they change",
        'node     g.add_node("fetch", fetch)          # any plain function',
        'edge     g.add_edge("trim", "present")       # always-go-here',
        'branch   g.add_conditional_edges("fetch", too_long, {...})   # a function picks',
        "run      g.compile().invoke({'q': ...})      # returns the final state"]))
    q = golden_slice()[1]["q"] if len(golden_slice()) > 1 else GOLDEN[0]["q"]
    out = app.invoke({"q": q})
    print(f"  ran START → fetch → {'trim → ' if out['obs'][0].endswith(' …') else ''}present → END on: {dim(q[:60])}")
    print(f"  final state answer: {green(out['answer'])}\n")
    note("that is ALL an agent framework is: shared state, plain functions, and edges that pick "
         "the next function. Every architecture in this lab — and inside CrewAI or AutoGen — is "
         "this primitive, composed. From here on the nodes call the LLM.")

def s2_react():
    c = next((c for c in GOLDEN if c["tag"] == "multi-hop"), GOLDEN[0])
    app, topo = build_react()
    print(f"  topology: {bold(topo)}\n  question: {dim(c['q'])}\n")
    meter_reset()
    a = run_agent(app, c["q"])
    calls, toks = meter_read()
    print(f"\n  {bold('final answer')} ({yellow(str(calls) + ' calls')} · ≈{toks} tok): {a[:200]}")
    note("the agent CHOSE each lookup — nobody scripted the sequence. The conditional edge is the "
         "whole trick: answer present → END; cap hit → forced answer (Lab 3's budget cap, now a "
         "node you can point at); otherwise → tools and around again.")

def s3_reflect():
    c = next((c for c in GOLDEN if c["tag"] == "multi-hop"), GOLDEN[-1])
    app, topo = build_reflect()
    print(f"  topology: {bold(topo)}\n  question: {dim(c['q'])}\n")
    meter_reset()
    out = app.invoke({"q": c["q"]})
    calls, _ = meter_read()
    g0 = grade(c["q"], out.get("draft", ""), c["expected"])   # the surviving draft IS the answer
    print(f"\n  {bold('final')} ({yellow(str(calls) + ' calls')}): {out['answer'][:180]}")
    print(f"  judge score: {green(f'{g0:.1f}')}")
    note("reflection buys quality with calls: the critic is the same model wearing a different "
         "prompt, which is exactly the LLM-judge move from Lab 1 — pointed at the agent's own "
         "draft before the user ever sees it. The rounds cap keeps perfectionism billable.")

def s4_plan():
    c = next((c for c in GOLDEN if c["tag"] == "multi-hop"), GOLDEN[0])
    app, topo = build_plan()
    print(f"  topology: {bold(topo)}\n  question: {dim(c['q'])}\n")
    meter_reset()
    a = run_agent(app, c["q"])
    p_calls, _ = meter_read()
    meter_reset()
    b = naive(c["q"])
    print(f"\n  {bold('plan-execute')} ({yellow(str(p_calls) + ' calls')}): {a[:160]}")
    print(f"  {bold('naive (1 call)')}: {b[:160]}")
    ga, gb = grade(c["q"], a, c["expected"]), grade(c["q"], b, c["expected"])
    print(f"  judge: plan-execute {green(f'{ga:.1f}')} vs naive {green(f'{gb:.1f}')}")
    note("plan-execute is Lab 3's decomposition wearing a graph: the plan is STATE you can log, "
         "show a human (Lab 7 pauses exactly here), and cap. When naive ties it on your corpus, "
         "that's not a failure of the architecture — that's the 3b routing lesson again.")

def s5_supervisor():
    c = next((c for c in GOLDEN if c["tag"] == "multi-hop"), GOLDEN[0])
    app, topo = build_supervisor()
    print(f"  topology: {bold(topo)}\n  question: {dim(c['q'])}\n")
    meter_reset()
    a = run_agent(app, c["q"])
    calls, _ = meter_read()
    print(f"\n  {bold('final answer')} ({yellow(str(calls) + ' calls')}): {a[:200]}")
    note("this is the 'multi-agent crew' pattern with the branding removed: the supervisor is one "
         "LLM call that picks the next worker, workers share state instead of sending messages, "
         "and the hop cap is the payroll. Kapi's Graph layer draws this same picture on a canvas.")

def s6_showdown():
    cases = golden_slice()
    print(f"  {len(cases)} cases (one per difficulty) × naive + all four shapes · judged on quality, "
          f"billed by the meter:\n")
    score_agent("naive baseline", naive, cases)
    for key, (blurb, make) in ARCHITECTURES.items():
        app, _ = make()
        with Spinner(f"{key}: {len(cases)} cases (answer + judge)"):
            r = score_agent(key, lambda q, a=app: run_agent(a, q), cases, quiet=True)
        print(f"  {r['config']:<30} quality={r['quality']:.2f}  {yellow(str(r['calls']) + ' calls')}  {dim(str(r['secs']) + 's')}  {dim(blurb)}")
    show_leaderboard(6)
    note("read the table the 3b way: on a 'hi'-shaped case every architecture is pure waste; on "
         "multi-hop the loops earn their calls. No shape wins everywhere — which is why production "
         "systems ROUTE between architectures instead of crowning one. Architecture is a dial.")

def _pick_int(prompt, options, default, lo=1, hi=20):
    """choice() where the student can ALSO type a custom whole-number value (a real dial, not just
    presets). Returns an int. Out-of-range / non-numeric falls back to the default with a note."""
    pick = choice(prompt, {**options, "custom": "type my own…"}, default)
    if pick == "custom":
        try:
            raw = input(f"  {yellow('value ›')} ").strip()
        except (EOFError, KeyboardInterrupt):
            return int(default)
        if raw.isdigit() and lo <= int(raw) <= hi:
            return int(raw)
        note(f"using {default} — need a whole number {lo}–{hi}.")
    return int(pick)

def s7_workbench():
    cases = golden_slice()
    if not sys.stdin.isatty():
        note("workbench needs a keyboard — auto-running two preset compositions instead.")
        app, _ = build_react(tools=("search_corpus",), cap=2)
        score_agent("preset: react·corpus-only·cap2", lambda q, a=app: run_agent(a, q), cases)
        app, _ = build_supervisor(cap=3)
        score_agent("preset: supervisor·cap3", lambda q, a=app: run_agent(a, q), cases)
        show_leaderboard(8)
        return
    print(f"  {bold('free play')} — compose an agent, watch it think, score it, fight for the top.\n")
    while True:
        arch = choice("architecture?", {k: f"{k} — {v[0]}" for k, v in ARCHITECTURES.items()}, "react")
        if arch == "react":
            tools = choice("toolbox?", {"both": "search_corpus + calc", "corpus": "search_corpus only"}, "both")
            cap = _pick_int("hop cap?", {"2": "2 — tight budget", "4": "4 — default", "6": "6 — generous"}, "4")
            app, topo = build_react(tools=("search_corpus", "calc") if tools == "both" else ("search_corpus",),
                                    cap=cap)
            label = f"you: react·{tools}·cap{cap}"
        elif arch == "reflect":
            rounds = _pick_int("max revisions?", {"1": "1", "2": "2", "3": "3"}, "2")
            app, topo = build_reflect(rounds=rounds)
            label = f"you: reflect·r{rounds}"
        elif arch == "plan":
            steps = _pick_int("max plan steps?", {"2": "2", "3": "3", "4": "4"}, "3")
            app, topo = build_plan(max_steps=steps)
            label = f"you: plan·s{steps}"
        else:
            cap = _pick_int("handoff cap?", {"3": "3", "6": "6", "9": "9"}, "6")
            app, topo = build_supervisor(cap=cap)
            label = f"you: supervisor·cap{cap}"
        print(f"  topology: {bold(topo)}")
        mode = choice("run it on…", {"score": "the golden slice (scored → leaderboard)",
                                     "ask": "one question of your own (live trace, unscored)"}, "score")
        if mode == "ask":
            try:
                q = input(f"  {yellow('your question ›')} ").strip()
            except (EOFError, KeyboardInterrupt):
                q = ""
            if q:
                meter_reset()
                a = run_agent(app, q)
                calls, toks = meter_read()
                print(f"\n  {bold('answer')} ({yellow(str(calls) + ' calls')} · ≈{toks} tok): {a[:300]}\n")
        else:
            with Spinner(f"scoring {label}"):
                score_agent(label, lambda q, a=app: run_agent(a, q), cases, quiet=True)
            show_leaderboard(8)
        again = choice("another agent?", {"yes": "compose another", "no": "done — wrap up"}, "yes")
        if again == "no":
            break
    best = sorted(LEADERBOARD, key=lambda r: (-r["quality"], r["calls"]))[0]
    print(f"  {green('top of the board')}: {best['config']}  (quality {best['quality']:.2f}, {best['calls']} calls)")
    note("that board is the take-home: architectures, honestly raced. When a framework hands you a "
         "'crew' or a 'graph' now, you know the state, the nodes, and the edges underneath — and "
         "you know to demand the meter and the judge before believing any of it.")

TUTOR = Tutor(
    title="Lab 3c — Agent Architectures: The Authoring Workbench",
    tagline="Modern AI Pro · AI Architect · Pillar I · the shapes under every framework",
    mission="""
    CrewAI, AutoGen, LangGraph prebuilts — every agent framework sells the same few SHAPES:
    a tool-calling loop, a self-critique loop, a planner over an executor, a supervisor over
    workers. This lab strips the branding off. You build each shape yourself as a ~30-line
    LangGraph graph — shared state, plain functions, edges that pick the next function — and
    watch it think in a live trace.

    Then the shapes race: the same golden slice, an LLM judge on quality, and the Lab-3b call
    meter on cost. The finale is an authoring workbench — compose architecture × tools × caps,
    run it on the corpus or your own question, and fight for the leaderboard.
    """,
    stages=[
        Stage("The primitive — state, nodes, edges (keyless)", """
            Load the corpus, then build and run a complete LangGraph agent with ZERO LLM
            calls — a fetch → branch → trim pipeline — so the machine is visible before any
            model magic arrives. The five-line API panel is everything the lab uses.""", s1_primitive, "0"),
        Stage("SHAPE 1 · the tool-calling loop (ReAct)", """
            An agent node picks a tool (corpus search, calculator) or answers; a conditional
            edge loops it through the toolbox until it answers — or the hop cap fires a
            forced answer. Live trace: you watch it choose every lookup.""", s2_react, "~4"),
        Stage("SHAPE 2 · reflection — generate, critique, revise", """
            The draft meets a strict reviewer (the same model, different prompt — the Lab-1
            judge move turned inward) and revises until the critic passes or the rounds cap
            fires. Quality bought with calls, and the judge scores whether it paid.""", s3_reflect, "~5"),
        Stage("SHAPE 3 · plan-and-execute", """
            A planner writes the minimal step list; an executor loop runs the steps; a
            synthesizer joins them. The plan is inspectable STATE — loggable, cappable,
            pausable (Lab 7 pauses exactly there). Raced against naive on the same case.""", s4_plan, "~8"),
        Stage("SHAPE 4 · the supervisor and its workers", """
            The 'multi-agent crew', de-branded: a supervisor LLM routes between a researcher
            (gathers facts) and a writer (composes), workers share state, a handoff cap is
            the payroll. The trace shows every delegation decision.""", s5_supervisor, "~6"),
        Stage("The SHOWDOWN — five systems, one golden slice", """
            Naive baseline + all four shapes on the same three cases (chit-chat, single-fact,
            multi-hop), LLM-judged on quality, billed by the meter. No shape wins everywhere —
            the table proves architecture is a routed choice, not a religion.""", s6_showdown, "~35"),
        Stage("The AUTHORING WORKBENCH — compose your own", """
            Free play: pick an architecture, dial its tools and caps, then either score it on
            the golden slice for the leaderboard or fire your own question at it and watch
            the live trace. Your best composition is the take-home.""", s7_workbench, "varies"),
    ],
    outro="""
    Four shapes, one state dict, one meter, one judge. You have now BUILT what the frameworks
    sell — which means you can read any of them, extend any of them, and demand evidence from
    all of them. Next: Lab 4 gives your agents memory; Lab 7 puts a human inside these same
    graphs, at exactly the nodes you just wrote.
    """,
)

def main():
    try:
        _graphs()
    except RuntimeError as e:
        print(f"\n  ⚠  {e}\n"); return
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · every LLM call metered · retrieval keyless")

if __name__ == "__main__":
    main()
