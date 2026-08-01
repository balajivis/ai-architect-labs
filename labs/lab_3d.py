# -*- coding: utf-8 -*-
"""Lab 3d — The Enterprise Stack: Google ADK (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · after Lab 3c (agent architectures)

Run it as a guided walkthrough:   python labs/lab_3d.py
Piped / non-interactive input auto-runs every stage (CI-safe).
Needs the adk extra:              pip install -e ".[adk]"

The mission: in Lab 3c you BUILT the four agent shapes by hand — so a framework
can never be magic to you again. This lab hands you the framework enterprises
actually standardized on in 2026: Google's Agent Development Kit. Same corpus,
same golden slice, same meter — but now the ReAct loop is `tools=[...]`, the
plan is a SequentialAgent, reflection is a LoopAgent, the supervisor is
`sub_agents=[...]`, and every run emits a full EVENT STREAM you didn't have to
print yourself. The finale is a duel: ADK's supervisor vs the one you wrote in
3c, judged and billed on the same cases. You end knowing exactly what a
framework buys, what it costs, and how to read the next one in an afternoon.
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
import asyncio
import json
import logging
import time
import warnings

warnings.filterwarnings("ignore", message=".*EXPERIMENTAL.*")   # ADK feature-flag chatter
os.environ.setdefault("LITELLM_LOG", "ERROR")
logging.getLogger("LiteLLM").setLevel(logging.ERROR)

import mai_rag
from mai_rag import corpus, llm
from mai_rag.tutor import Tutor, Stage, Spinner, note, panel, choice, dim, green, yellow, bold

# ── shared state ─────────────────────────────────────────────────────────────
store = None
GOLDEN: list[dict] = []
LEADERBOARD: list[dict] = []
VERBOSE = True

# The meter — in 3c every call went through ask(); in ADK the model is called BY the
# framework, so we meter where a framework wants you to: a before_model CALLBACK.
METER = {"calls": 0}

def _meter_cb(callback_context=None, llm_request=None, **_):
    METER["calls"] += 1
    return None                     # returning None lets the real model call proceed

def meter_reset():
    METER["calls"] = 0

def ask(prompt, temperature=0.0):   # judge + graders stay on the Lab-1 chokepoint
    METER["calls"] += 1
    return llm.complete(prompt, tier="small", temperature=temperature)

def _json(raw):
    """Structural JSON extraction (parsing, not classification)."""
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

def _adk():
    """One import chokepoint with a clean hint."""
    try:
        from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
        from google.adk.runners import InMemoryRunner
        from google.adk.tools import ToolContext
        from google.genai import types
        return LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, InMemoryRunner, ToolContext, types
    except ImportError:
        raise RuntimeError('Google ADK is not installed — run: pip install -e ".[adk]" '
                           "(or: pip install 'google-adk[extensions]') and restart the lab.") from None

# ── the model: ONE resolver, same key precedence as mai_rag.llm ──────────────
def pick_model():
    """Glass-box: how ADK reaches YOUR provider. Gemini keys go native; everything
    else rides ADK's LiteLLM adapter — including the class proxy via OPENAI_BASE_URL."""
    if os.getenv("GROQ_API_KEY"):
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model="groq/" + llm.model_for("small", "groq"),
                       num_retries=6), "groq (LiteLLM)"
    if os.getenv("OPENAI_API_KEY"):
        from google.adk.models.lite_llm import LiteLlm
        base = os.getenv("OPENAI_BASE_URL")
        name = "gpt-5.4" if base else llm.model_for("small", "openai")   # class proxy serves gpt-5.4
        # num_retries: the class proxy rate-limits per token — back off like mai_rag.llm does
        return LiteLlm(model="openai/" + name, api_base=base, api_key=os.environ["OPENAI_API_KEY"],
                       num_retries=6), ("class proxy (LiteLLM)" if base else "openai (LiteLLM)")
    if os.getenv("GEMINI_API_KEY"):
        os.environ.setdefault("GOOGLE_API_KEY", os.environ["GEMINI_API_KEY"])
        return llm.model_for("small", "gemini"), "gemini (ADK-native)"
    raise RuntimeError("No LLM key found. Set OPENAI_API_KEY (class token), GROQ_API_KEY, or GEMINI_API_KEY.")

MODEL = None            # resolved once in stage 1
def model():
    global MODEL
    if MODEL is None:
        MODEL = pick_model()
    return MODEL[0]

# ── the tools — SAME two as Lab 3c, now as plain typed functions ─────────────
def search_corpus(query: str) -> str:
    """Search the course-catalog corpus. Input: a search query. Returns the top passages."""
    hits = store.search(str(query), k=3)
    return " | ".join(f"({h.title}) {h.content[:160]}" for h in hits) or "no hits"

def calc(expression: str) -> str:
    """Evaluate an arithmetic expression like (12*4)+3. Numbers and + - * / // % ** only."""
    ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Add, ast.Sub,
               ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.USub, ast.UAdd)
    try:
        tree = ast.parse(str(expression), mode="eval")
        if not all(isinstance(n, ALLOWED) for n in ast.walk(tree)):
            return "calc error: numbers and + - * / // % ** only"
        return str(eval(compile(tree, "<calc>", "eval")))
    except Exception as e:
        return f"calc error: {e}"

# ── run any ADK agent tree, narrating the event stream ───────────────────────
def run_adk(root, q: str, state: dict | None = None, turns: list | None = None):
    """Invoke an agent (or agent tree) and return (final_text, session). The event
    stream — every author change, tool call, tool result — is printed when VERBOSE:
    in 3c you wrote trace(); here the runtime IS the trace."""
    *_, InMemoryRunner, _tc, types = _adk()
    async def _go():
        runner = InMemoryRunner(agent=root, app_name="lab3d")
        s = await runner.session_service.create_session(app_name="lab3d", user_id="u",
                                                        state=state or {})
        final = ""
        for turn in (turns or [q]):
            msg = types.Content(role="user", parts=[types.Part(text=turn)])
            if turns and VERBOSE:
                print(f"    {bold('user ›')} {turn}")
            async for ev in runner.run_async(user_id="u", session_id=s.id, new_message=msg):
                for c in (ev.get_function_calls() or []):
                    if VERBOSE:
                        print(f"    {yellow(ev.author):<22} {dim('tool call → ' + c.name + ' ' + json.dumps(c.args)[:60])}")
                for r in (ev.get_function_responses() or []):
                    if VERBOSE:
                        print(f"    {yellow(ev.author):<22} {dim('tool result ← ' + str(r.response)[:70])}")
                text = ev.content.parts[0].text if (ev.content and ev.content.parts and ev.content.parts[0].text) else ""
                if text:
                    if VERBOSE:
                        print(f"    {yellow(ev.author):<22} {dim(text.strip()[:88])}")
                    final = text.strip()
        s = await runner.session_service.get_session(app_name="lab3d", user_id="u", session_id=s.id)
        return final, s
    return asyncio.run(_go())

# ── the four shapes, ADK-native (compare each to its 3c hand-rolled twin) ────
def make_tool_agent(tools=None, name="agent"):
    """3c SHAPE 1 (ReAct) ≙ ADK: the loop is BUILT IN — you only declare the tools."""
    LlmAgent, *_ = _adk()
    return LlmAgent(name=name, model=model(), tools=list(tools or [search_corpus, calc]),
                    instruction="Answer using your tools when they help. Search the corpus "
                                "for course facts; say what's missing if the tools fall short.",
                    before_model_callback=_meter_cb)

def make_pipeline():
    """3c SHAPE 3 (plan-execute) ≙ ADK SequentialAgent: state flows via output_key."""
    LlmAgent, SequentialAgent, *_ = _adk()
    researcher = LlmAgent(name="researcher", model=model(), tools=[search_corpus],
                          instruction="Gather the facts needed to answer the user's question. "
                                      "Search the corpus (multiple searches are fine). Output "
                                      "ONLY the facts found, one per line.",
                          output_key="notes", before_model_callback=_meter_cb)
    writer = LlmAgent(name="writer", model=model(),
                      instruction="Write the final answer to the user's question using ONLY "
                                  "these researched notes — say what's missing if they fall "
                                  "short:\n{notes}",
                      output_key="answer", before_model_callback=_meter_cb)
    return SequentialAgent(name="pipeline", sub_agents=[researcher, writer])

def make_reflect(max_rounds=2):
    """3c SHAPE 2 (reflection) ≙ ADK LoopAgent: the critic exits by ESCALATING."""
    LlmAgent, SequentialAgent, _pa, LoopAgent, _r, ToolContext, _t = _adk()

    def approve(tool_context: ToolContext) -> str:
        """Call ONLY when the current draft fully and specifically answers the question."""
        tool_context.actions.escalate = True        # escalate = the loop's exit door
        return "approved — loop ends"

    generate = LlmAgent(name="generate", model=model(), tools=[search_corpus],
                        instruction="Draft an answer to the user's question from corpus facts.",
                        output_key="draft", before_model_callback=_meter_cb)
    critic = LlmAgent(name="critic", model=model(), tools=[approve],
                      instruction="You are a strict reviewer of this draft:\n{draft}\n"
                                  "If it fully answers the user's question, call approve(). "
                                  "Otherwise output ONE concrete objection.",
                      output_key="objection", before_model_callback=_meter_cb)
    reviser = LlmAgent(name="reviser", model=model(),
                       instruction="Rewrite the draft to fix the objection. Keep what was right."
                                   "\nDRAFT:\n{draft}\nOBJECTION:\n{objection}",
                       output_key="draft", before_model_callback=_meter_cb)
    return SequentialAgent(name="reflect", sub_agents=[
        generate, LoopAgent(name="review_loop", sub_agents=[critic, reviser],
                            max_iterations=max_rounds)])

def make_supervisor():
    """3c SHAPE 4 (supervisor) ≙ ADK sub_agents: delegation is a built-in transfer tool
    the model calls — you write DESCRIPTIONS, not routing code."""
    LlmAgent, *_ = _adk()
    researcher = LlmAgent(name="researcher", model=model(), tools=[search_corpus],
                          description="Looks up facts about courses and topics in the catalog corpus.",
                          instruction="Search the corpus and answer with the facts found.",
                          before_model_callback=_meter_cb)
    calculator = LlmAgent(name="calculator", model=model(), tools=[calc],
                          description="Does arithmetic with the calc tool.",
                          instruction="Compute the requested arithmetic with calc.",
                          before_model_callback=_meter_cb)
    return LlmAgent(name="supervisor", model=model(), sub_agents=[researcher, calculator],
                    instruction="Answer directly when no lookup is needed; otherwise transfer "
                                "to the sub-agent whose description fits the task.",
                    before_model_callback=_meter_cb)

def grade(q, answer, expected):
    p = ("Grade the ANSWER against EXPECTED. 1.0 fully correct, 0.5 partial, 0.0 wrong/missing. "
         "An honest 'I don't have enough information' is CORRECT when EXPECTED says the "
         "information isn't in the corpus.\n"
         'Reply JSON only: {"reason":"<short>","score":<1.0|0.5|0.0>}.\n\n'
         f"QUESTION: {q}\nEXPECTED: {expected}\nANSWER: {answer}")
    try:
        return float(_json(ask(p, temperature=0))["score"])
    except (ValueError, KeyError, TypeError):
        return 0.0

def score_system(label, runner_fn, cases, quiet=False):
    global VERBOSE
    was, VERBOSE = VERBOSE, False
    scores, t0 = [], time.time()
    meter_reset()
    for c in cases:
        a = runner_fn(c["q"])
        n = METER["calls"]
        scores.append(grade(c["q"], a, c["expected"]))
        METER["calls"] = n + 1
    VERBOSE = was
    row = {"config": label, "quality": round(sum(scores) / len(scores), 2),
           "calls": METER["calls"] - len(cases), "secs": round(time.time() - t0, 1)}
    if not any(r["config"] == label for r in LEADERBOARD):
        LEADERBOARD.append(row)
    if not quiet:
        print(f"  {label:<32} quality={row['quality']:.2f}  {yellow(str(row['calls']) + ' calls')}  {dim(str(row['secs']) + 's')}")
    return row

def show_leaderboard(top=10):
    rows = sorted(LEADERBOARD, key=lambda r: (-r["quality"], r["calls"]))[:top]
    body = "\n".join(f"{i+1:>2}. {r['config']:<32} quality={r['quality']:.2f}  {r['calls']:>3} calls  {r['secs']:>6}s"
                     for i, r in enumerate(rows))
    panel("LEADERBOARD — quality first, cheapest wins ties", body)

def golden_slice():
    out = []
    for tag in ("no-retrieval", "topic", "multi-hop"):
        c = next((c for c in GOLDEN if c["tag"] == tag), None)
        if c:
            out.append(c)
    return out

# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_anatomy():
    global store, GOLDEN
    with Spinner("loading catalog corpus"):
        store = corpus.load_catalog_corpus("catalog.db")
    GOLDEN[:] = corpus.load_golden_catalog()
    m, provider = pick_model()
    print(f"  {green('loaded')}: {store.stats().get('documents')} docs · {len(GOLDEN)} golden cases · "
          f"ADK model → {bold(provider)}\n")
    if provider.startswith("class proxy"):
        # The whole lab is native function calling — probe that the proxy forwards `tools`
        # before the student watches agents NARRATE searches instead of doing them.
        from openai import OpenAI
        METER["calls"] += 1
        r = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ["OPENAI_BASE_URL"]) \
            .chat.completions.create(
                model="gpt-5.4", max_completion_tokens=40,
                messages=[{"role": "user", "content": "Call the ping tool."}],
                tools=[{"type": "function", "function": {"name": "ping", "description": "ping",
                                                         "parameters": {"type": "object", "properties": {}}}}])
        if not r.choices[0].message.tool_calls:
            print(f"  {yellow('⚠  this class proxy does not forward tool calls yet')} — agents will "
                  f"TALK about using tools instead of using them.\n     Fix: ask the instructor to "
                  f"update the proxy, or put your own GROQ_API_KEY / GEMINI_API_KEY in .env "
                  f"(and comment out OPENAI_API_KEY) for this lab.\n")
    panel("the entire ADK API this lab uses", "\n".join([
        "agent      LlmAgent(name, model, instruction, tools=[...], sub_agents=[...])",
        "workflow   SequentialAgent / ParallelAgent / LoopAgent(sub_agents=[...])",
        "state      output_key='draft' writes it; '{draft}' in an instruction reads it",
        "meter      before_model_callback — one hook, every model call counted",
        "run        InMemoryRunner(...).run_async(...) → a stream of EVENTS"]))
    LlmAgent, *_ = _adk()
    hello = LlmAgent(name="hello", model=model(), before_model_callback=_meter_cb,
                     instruction="Answer in one short sentence.")
    meter_reset()
    q = "In one line: what is an AI agent?"
    print(f"  question: {dim(q)}\n")
    run_adk(hello, q)
    print(f"\n  meter: {yellow(str(METER['calls']) + ' model call')} — counted by the callback, "
          f"not by our own ask() wrapper.")
    note("in 3c you wrote the state dict, the trace, and the meter. ADK ships all three: a "
         "session, an event stream, and callbacks. That's the trade every framework offers — "
         "less code you own, more behavior you must READ. This lab reads it.")

def s2_tools():
    c = next((c for c in GOLDEN if c["tag"] == "multi-hop"), GOLDEN[0])
    agent = make_tool_agent()
    print(f"  the whole ReAct loop, declared: {bold('tools=[search_corpus, calc]')}\n"
          f"  question: {dim(c['q'])}\n")
    meter_reset()
    a, _ = run_adk(agent, c["q"])
    print(f"\n  {bold('final')} ({yellow(str(METER['calls']) + ' calls')}): {a[:200]}")
    note("compare stage 2 of 3c: there YOU wrote the agent node, the JSON action parse, the "
         "conditional edge, and the cap. Here the loop is invisible — ADK converts your typed "
         "Python functions to declarations and re-invokes the model after each tool result. "
         "Faster to author; but notice what you LOST: our 3c force-node cap. Magic has a price.")

def s3_workflows():
    c = next((c for c in GOLDEN if c["tag"] == "multi-hop"), GOLDEN[0])
    print(f"  {bold('SequentialAgent')} — 3c's plan-execute as a class · researcher → writer via output_key\n"
          f"  question: {dim(c['q'])}\n")
    meter_reset()
    a, s = run_adk(make_pipeline(), c["q"])
    print(f"\n  session.state keys now: {green(str([k for k in s.state if not k.startswith('_')]))}")
    print(f"  {bold('pipeline answer')} ({yellow(str(METER['calls']) + ' calls')}): {a[:160]}\n")
    print(f"  {bold('LoopAgent')} — 3c's reflection as a class · critic exits by ESCALATING (approve tool)\n")
    meter_reset()
    a2, _ = run_adk(make_reflect(), c["q"])
    print(f"\n  {bold('reflect answer')} ({yellow(str(METER['calls']) + ' calls')}): {a2[:160]}")
    note("the graph you drew edge-by-edge in 3c is a CLASS here: Sequential = your plan spine, "
         "Loop = your critique cycle (max_iterations = the rounds cap; escalate = the exit "
         "edge), Parallel = fan-out we didn't need. State flows through output_key → {placeholder} "
         "— the same shared-dict idea, templated.")

def s4_supervisor():
    c = next((c for c in GOLDEN if c["tag"] == "multi-hop"), GOLDEN[0])
    print(f"  supervisor + researcher + calculator — routing = {bold('descriptions')}, not code\n"
          f"  question: {dim(c['q'])}\n")
    meter_reset()
    a, _ = run_adk(make_supervisor(), c["q"])
    print(f"\n  {bold('final')} ({yellow(str(METER['calls']) + ' calls')}): {a[:200]}")
    note("watch the authors change in the trace — that's ADK's transfer_to_agent tool firing, "
         "the same decision your 3c supervisor node made with a JSON reply. You wrote routing "
         "logic; here you write job DESCRIPTIONS and the model routes on them. Enterprise "
         "teams love this (declarative, auditable events) and pay for it (less control).")

def s5_state():
    LlmAgent, *_ = _adk()
    agent = LlmAgent(name="tutor", model=model(), tools=[search_corpus],
                     instruction="You are a course advisor for {user_name}, who is interested in "
                                 "{interest}. Personalize your answers and use the corpus.",
                     output_key="last_answer", before_model_callback=_meter_cb)
    print(f"  seeded session.state: {dim(str({'user_name': 'Balaji', 'interest': 'agents'}))}\n")
    meter_reset()
    _, s = run_adk(agent, "", state={"user_name": "Balaji", "interest": "agents"},
                   turns=["Which course should I take?", "What was my previous question?"])
    keep = {k: str(v)[:60] for k, v in s.state.items() if not k.startswith("_")}
    panel("session.state after two turns", "\n".join(f"{k}: {v}" for k, v in keep.items()))
    print(f"  ({yellow(str(METER['calls']) + ' calls')})")
    note("turn 2 worked because the SESSION carried the history — no query rewrite, no manual "
         "window (Lab 4's whole first stage, absorbed by the runtime). state seeds are Lab 4's "
         "durable profile; output_key is working memory. Same layers, framework-shaped: ADK "
         "gives you the slots, Lab 4b taught you what belongs in each.")

def s6_duel():
    cases = golden_slice()
    print(f"  the same {len(cases)}-case slice, judged by the same judge, billed by each side's meter:\n")
    with Spinner(f"ADK supervisor: {len(cases)} cases (answer + judge)"):
        r = score_system("ADK supervisor", lambda q: run_adk(make_supervisor(), q)[0], cases, quiet=True)
    print(f"  {r['config']:<32} quality={r['quality']:.2f}  {yellow(str(r['calls']) + ' calls')}  {dim(str(r['secs']) + 's')}")
    try:
        import lab_3c                                    # your OWN lab, imported as a library
        lab_3c.store, lab_3c.VERBOSE = store, False
        app, _ = lab_3c.build_supervisor()
        with Spinner(f"3c LangGraph supervisor: {len(cases)} cases"):
            meter_reset()
            scores, t0 = [], time.time()
            for c in cases:
                lab_3c.meter_reset()
                a = lab_3c.run_agent(app, c["q"])
                METER["calls"] += lab_3c.METER["calls"]  # their meter, folded into ours
                scores.append(grade(c["q"], a, c["expected"]))
                METER["calls"] -= 1                      # judge call not billed to the agent
        row = {"config": "3c LangGraph supervisor (yours)", "quality": round(sum(scores) / len(scores), 2),
               "calls": METER["calls"], "secs": round(time.time() - t0, 1)}
        LEADERBOARD.append(row)
        print(f"  {row['config']:<32} quality={row['quality']:.2f}  {yellow(str(row['calls']) + ' calls')}  {dim(str(row['secs']) + 's')}")
    except Exception as e:
        note(f"couldn't import lab_3c for the duel ({type(e).__name__}: {str(e)[:60]}) — "
             "install the agents extra and run from labs/. Racing the tool-agent instead.")
        score_system("ADK tool-agent", lambda q: run_adk(make_tool_agent(), q)[0], cases)
    show_leaderboard(6)
    note("this table is the enterprise decision in miniature: the framework's shape and your "
         "hand-rolled shape score alike — what differs is calls, latency, and who owns the "
         "code. In 2026 LangGraph leads production and ADK owns the GCP estate; you now hold "
         "the only durable position: you can read, meter, and judge BOTH.")

def s7_workbench():
    cases = golden_slice()
    if not sys.stdin.isatty():
        note("workbench needs a keyboard — auto-running two preset compositions instead.")
        score_system("preset: adk tool-agent", lambda q: run_adk(make_tool_agent(), q)[0], cases)
        score_system("preset: adk pipeline", lambda q: run_adk(make_pipeline(), q)[0], cases)
        show_leaderboard(8)
        return
    print(f"  {bold('free play')} — compose an ADK agent, watch its events, score it.\n")
    while True:
        kind = choice("root agent?", {"tools": "LlmAgent + tools (the ReAct loop)",
                                      "pipeline": "SequentialAgent researcher → writer",
                                      "reflect": "generate + LoopAgent(critic ⇄ reviser)",
                                      "supervisor": "supervisor + sub_agents"}, "tools")
        if kind == "tools":
            tb = choice("toolbox?", {"both": "search_corpus + calc", "corpus": "search_corpus only"}, "both")
            root = make_tool_agent([search_corpus, calc] if tb == "both" else [search_corpus])
            label = f"you: adk·tools·{tb}"
        elif kind == "reflect":
            r = choice("max review rounds?", {"1": "1", "2": "2", "3": "3"}, "2")
            root, label = make_reflect(int(r)), f"you: adk·reflect·r{r}"
        elif kind == "pipeline":
            root, label = make_pipeline(), "you: adk·pipeline"
        else:
            root, label = make_supervisor(), "you: adk·supervisor"
        mode = choice("run it on…", {"score": "the golden slice (scored → leaderboard)",
                                     "ask": "one question of your own (live events, unscored)"}, "score")
        if mode == "ask":
            try:
                q = input(f"  {yellow('your question ›')} ").strip()
            except (EOFError, KeyboardInterrupt):
                q = ""
            if q:
                meter_reset()
                a, _ = run_adk(root, q)
                print(f"\n  {bold('answer')} ({yellow(str(METER['calls']) + ' calls')}): {a[:300]}\n")
        else:
            with Spinner(f"scoring {label}"):
                score_system(label, lambda q, r=root: run_adk(r, q)[0], cases, quiet=True)
            show_leaderboard(8)
        if choice("another agent?", {"yes": "compose another", "no": "done — wrap up"}, "yes") == "no":
            break
    note("two labs, two stacks, one meter and one judge. Frameworks will keep shipping; your "
         "golden slice doesn't care. Whatever the next one is called, you know the drill: find "
         "the state, find the loop, hook the meter, run the slice.")

TUTOR = Tutor(
    title="Lab 3d — The Enterprise Stack: Google ADK",
    tagline="Modern AI Pro · AI Architect · Pillar I · the framework, after you built one",
    mission="""
    Lab 3c made you build the four agent shapes by hand. This lab hands you 2026's enterprise
    framework — Google's Agent Development Kit — and the shapes come as classes: the ReAct
    loop is tools=[...], plan-execute is a SequentialAgent, reflection is a LoopAgent with an
    escalate exit, the supervisor is sub_agents with job descriptions. Every run emits a full
    event stream, sessions carry state between turns, and the meter moves into a callback —
    the hook real observability lives on.

    The finale is a duel — ADK's supervisor vs the LangGraph one YOU wrote — on the same
    golden slice, same judge, same meter. Then a workbench to compose your own.
    """,
    stages=[
        Stage("Anatomy — Agent, Runner, and the EVENT STREAM", """
            Load the corpus, resolve the model (class proxy / Groq / Gemini — one glass-box
            resolver), run a bare LlmAgent and read the event stream ADK narrates for free.
            The meter moves into before_model_callback — count every call, own no wrapper.""", s1_anatomy, "~1"),
        Stage("Tools — the ReAct loop you didn't have to write", """
            The 3c tool loop was ~30 lines of yours; here it's tools=[search_corpus, calc] —
            typed Python functions become declarations, and the loop is the framework's. Watch
            the tool-call events on a multi-hop question, and notice what the magic costs.""", s2_tools, "~3"),
        Stage("Workflow classes — Sequential, Loop (and Parallel)", """
            3c's plan-execute spine as a SequentialAgent (state flows output_key → {placeholder})
            and reflection as a LoopAgent whose critic EXITS BY ESCALATING via an approve()
            tool — max_iterations is the rounds cap you hand-rolled. Same shapes, now classes.""", s3_workflows, "~8"),
        Stage("The supervisor — sub_agents and transfer", """
            A supervisor with researcher + calculator sub-agents: routing is written as job
            DESCRIPTIONS and the model transfers on them — the built-in version of the JSON
            routing node you wrote. The authors changing in the trace ARE the delegations.""", s4_supervisor, "~4"),
        Stage("Sessions and STATE — memory the runtime carries", """
            Seed session.state with a user profile, template it into the instruction, run two
            turns — the follow-up works because the session carries history (Lab 4's rewrite
            stage, absorbed). Then read the state dict the run left behind.""", s5_state, "~3"),
        Stage("The DUEL — ADK vs the supervisor you built in 3c", """
            Same three cases, same judge: ADK's supervisor against your hand-rolled LangGraph
            one — your own lab imported as a library. Quality, calls, seconds, side by side.
            This table is the build-vs-adopt decision, measured instead of argued.""", s6_duel, "~20"),
        Stage("The WORKBENCH — compose an ADK agent", """
            Free play: pick a root (tool-agent, pipeline, reflect-loop, supervisor), dial it,
            then score it on the golden slice or fire your own question and watch the events.
            The shared leaderboard now holds hand-rolled AND framework agents together.""", s7_workbench, "varies"),
    ],
    outro="""
    You built the shapes in 3c; today a major framework handed them back as classes and you
    read every event it emitted. That is the durable skill: not ADK, not LangGraph, but the
    drill — find the state, find the loop, hook the meter, run YOUR golden slice. Next: Lab 4
    gives agents memory by hand, and you'll recognize ADK's session slots when you get there.
    """,
)

def main():
    try:
        _adk()
    except RuntimeError as e:
        print(f"\n  ⚠  {e}\n"); return
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · ADK metered via before_model_callback · "
                            "retrieval keyless")

if __name__ == "__main__":
    main()
