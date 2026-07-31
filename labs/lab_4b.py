# -*- coding: utf-8 -*-
"""Lab 4b — The Memory Stack (interactive CLI tutor)

Modern AI Pro · AI Architect · Agent Memory Architectures — Working · Episodic · Semantic

Run it as a guided walkthrough:   python labs/lab_4b.py
  · each MOVE explains itself, waits for you (Enter), runs, then shows status
  · Enter = run · s = skip · q = quit
Piped / non-interactive input auto-runs every move.

The mission: an LLM has NO memory — everything it "remembers" is something you put in
the prompt. We build the four-layer memory stack real agent systems use, one layer at a
time, WATCHING THE FILES CHANGE ON DISK — then plug the stack into RAG and score it.

  L1 · SHORT-TERM   the transcript in context     (volatile — dies with the process)
  L2 · WORKING      working.yaml                  ("what is happening right now" — rewritten, never appended)
  L3 · EPISODIC     episodic/YYYY-MM-DD-*.md      ("what happened, and why" — append-only, dated)
  L4 · DURABLE      semantic/profile.yaml         ("what is true" — distilled facts, merged)

The design rule that makes it work: LAYERS ARE COMPACTION. Working memory is one
paragraph, an episode is a summary, the durable profile is distilled facts — the raw
transcript never travels forward. Memory ≠ RAG: RAG is retrieval over documents you
LOADED; memory is recall of what HAPPENED. Collapsing them is the most common
modelling error in this space.
"""

# --- repo local-run shim: load .env, work with or without __file__ ----------
import os, pathlib, sys, textwrap, json, shutil, datetime

_here = pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path.cwd()
for _cand in (pathlib.Path(".env"), _here.parent / ".env", _here / ".env"):
    if _cand.exists():
        for _line in _cand.read_text().splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
        break

import yaml
import mai_rag
from mai_rag import corpus, llm

# ── interactive helpers (same pattern as lab_1) ──────────────────────────────
INTERACTIVE = sys.stdin.isatty()
C = {"b": "\033[1m", "d": "\033[2m", "y": "\033[33m", "g": "\033[32m", "c": "\033[36m", "x": "\033[0m"} \
    if sys.stdout.isatty() else {k: "" for k in "bdygcx"}

def banner(n, total, title):
    print(f"\n{C['c']}{'═'*74}{C['x']}")
    print(f"{C['b']}  MOVE {n}/{total} · {title}{C['x']}")
    print(f"{C['c']}{'═'*74}{C['x']}")

def say(text):
    for para in textwrap.dedent(text).strip("\n").split("\n\n"):
        print(textwrap.indent(textwrap.fill(" ".join(para.split()), 84), "  "))
        print()

def note(text):
    print(f"  {C['d']}↳ {text}{C['x']}")

def show_file(path: pathlib.Path, label=None):
    """Print a memory file exactly as it sits on disk — seeing the artifact IS the lesson."""
    print(f"\n  {C['y']}┌─ {label or path} ─{C['x']}")
    body = path.read_text().rstrip() if path.exists() else "(does not exist yet)"
    print(textwrap.indent(body, f"  {C['y']}│{C['x']} "))
    print(f"  {C['y']}└─{C['x']}")

def prompt_next():
    if not INTERACTIVE:
        print(f"  {C['d']}… auto-run{C['x']}")
        return "run"
    try:
        a = input(f"  {C['y']}▶ Enter{C['x']} run  ·  {C['y']}s{C['x']} skip  ·  {C['y']}q{C['x']} quit  › ").strip().lower()
    except EOFError:
        return "run"
    if a in ("q", "quit", "exit"):
        print("\n  Memory persisted to .memory/ — inspect it. 👋\n"); sys.exit(0)
    return "skip" if a in ("s", "skip") else "run"

def est_tokens(s: str) -> int:
    return max(1, len(s) // 4)          # rough chars/4 — good enough for the economics lesson

def ask(prompt, temperature=0.0):
    return llm.complete(prompt, tier="small", temperature=temperature)

def _json(raw):
    return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])

# ── the four-layer memory stack (file-backed, glass-box) ─────────────────────
MEM_ROOT = pathlib.Path(".memory")

class MemoryStack:
    """Working / Episodic / Durable on disk + the in-context transcript in RAM.
    Formats mirror real agent repos: working = YAML (rewritten), episodic = dated
    Markdown with YAML frontmatter (append-only), durable = YAML (merged facts)."""

    def __init__(self, user_id: str, fresh: bool = False):
        self.user = user_id
        self.root = MEM_ROOT / user_id
        if fresh and self.root.exists():
            shutil.rmtree(self.root)
        (self.root / "episodic").mkdir(parents=True, exist_ok=True)
        (self.root / "semantic").mkdir(parents=True, exist_ok=True)
        self.transcript: list[dict] = []            # L1 — short-term, in-context only

    # L2 — working memory: "what is happening RIGHT NOW". Rewritten, never appended.
    @property
    def working_path(self): return self.root / "working.yaml"

    def update_working(self):
        convo = "\n".join(f"{t['role']}: {t['text']}" for t in self.transcript)
        raw = ask(
            "Distill this conversation into WORKING MEMORY — the 'right now' state only.\n"
            'Reply JSON only: {"who": "<one line: who the user is>", '
            '"now": "<one line: what they are working on this session>", '
            '"open": ["<unresolved thread or pending action>", ...]}\n\n' + convo)
        wm = _json(raw)
        self.working_path.write_text(yaml.safe_dump(wm, sort_keys=False, allow_unicode=True))
        return wm

    def read_working(self) -> str:
        return self.working_path.read_text() if self.working_path.exists() else ""

    # L3 — episodic: REM-flush the session into a dated, append-only Markdown entry.
    def rem_flush(self, slug: str, today: str) -> pathlib.Path:
        convo = "\n".join(f"{t['role']}: {t['text']}" for t in self.transcript)
        summary = ask(
            "Summarize this session as 3-5 short markdown bullets: WHAT happened and WHY it "
            "matters for next time. Facts only, no fluff.\n\n" + convo)
        path = self.root / "episodic" / f"{today}-{slug}.md"
        path.write_text(f"---\ntype: session\nuser: {self.user}\ndate: {today}\n---\n\n{summary.strip()}\n")
        # the flush CLOSES the session: short-term + working are cleared — that's the point
        self.transcript = []
        if self.working_path.exists():
            self.working_path.unlink()
        return path

    def recall_episodes(self, n: int = 3) -> str:
        files = sorted((self.root / "episodic").glob("*.md"))[-n:]
        return "\n\n".join(f.read_text() for f in files)

    # L4 — durable/semantic: distill atomic facts (the 4-category taxonomy production
    # systems use) out of an episode, MERGE into profile.yaml. One sentence per fact.
    @property
    def profile_path(self): return self.root / "semantic" / "profile.yaml"

    def distill_semantic(self, episode_text: str):
        raw = ask(
            "Extract DURABLE facts about the user from this session record. Four categories, "
            "each a list of one-sentence strings (empty list if none):\n"
            '{"facts": [...], "preferences": [...], "decisions": [...], "action_items": [...]}\n'
            "Only include what will still matter in a month. Reply JSON only.\n\n" + episode_text)
        new = _json(raw)
        profile = yaml.safe_load(self.profile_path.read_text()) if self.profile_path.exists() else {}
        for cat in ("facts", "preferences", "decisions", "action_items"):
            merged = list(dict.fromkeys((profile.get(cat) or []) + list(new.get(cat) or [])))
            profile[cat] = merged
        self.profile_path.write_text(yaml.safe_dump(profile, sort_keys=False, allow_unicode=True))
        return profile

    def read_semantic(self) -> str:
        return self.profile_path.read_text() if self.profile_path.exists() else ""

    # Assembly — retrieval-INTO-context. Stable prefix (durable + episodic) first,
    # volatile tail (working + transcript) last: the ordering is what makes the prefix
    # prompt-cacheable in production.
    def assemble(self, layers=("durable", "episodic", "working", "short")) -> dict:
        parts, budget = [], {}
        if "durable" in layers and self.read_semantic():
            s = "## Who this user is (durable memory)\n" + self.read_semantic()
            parts.append(s); budget["L4 durable"] = est_tokens(s)
        if "episodic" in layers and self.recall_episodes():
            s = "## Past sessions (episodic memory)\n" + self.recall_episodes()
            parts.append(s); budget["L3 episodic"] = est_tokens(s)
        if "working" in layers and self.read_working():
            s = "## This session right now (working memory)\n" + self.read_working()
            parts.append(s); budget["L2 working"] = est_tokens(s)
        if "short" in layers and self.transcript:
            s = "## Conversation so far\n" + "\n".join(f"{t['role']}: {t['text']}" for t in self.transcript)
            parts.append(s); budget["L1 short-term"] = est_tokens(s)
        return {"context": "\n\n".join(parts), "budget": budget}

    def chat(self, user_msg: str, layers=("durable", "episodic", "working", "short")) -> str:
        asm = self.assemble(layers)
        system = ("You are a helpful assistant. Use the MEMORY below when relevant; "
                  "if it doesn't contain something, say you don't know — never invent memory.\n\n"
                  + (asm["context"] or "(no memory)"))
        answer = ask(f"{system}\n\nuser: {user_msg}\nassistant:")
        self.transcript += [{"role": "user", "text": user_msg}, {"role": "assistant", "text": answer}]
        return answer

TODAY = datetime.date.today().isoformat()
mem = MemoryStack("priya", fresh=True)
store = None                                        # catalog corpus — loaded in Move 7

SESSION_1 = [
    "Hi! I'm Priya — a product manager at a fintech in Mumbai. I don't write code.",
    "We just decided to pilot an AI support bot for our payments app in Q3.",
    "What should I be careful about with a bot answering payment questions?",
    "Good points. Also — remind me to shortlist vendors by Friday.",
]

def judge_pass(question, answer, must):
    v = _json(ask(f'Does the ANSWER satisfy the CHECK? Reply JSON only: {{"pass": true|false, "reason": "<short>"}}.\n'
                  f'QUESTION: {question}\nCHECK: {must}\nANSWER: {answer}'))
    flag = f"{C['g']}PASS{C['x']}" if v.get("pass") else f"{C['y']}FAIL{C['x']}"
    print(f"    [{flag}] {v.get('reason','')[:70]}")
    return bool(v.get("pass"))

# ── the MOVES ────────────────────────────────────────────────────────────────
def m1_amnesiac():
    a1 = ask("user: Hi! I'm Priya — a product manager at a fintech in Mumbai.\nassistant:")
    print(f"  turn 1 → {textwrap.shorten(a1, 90)}")
    a2 = ask("user: What did I just tell you my role was?\nassistant:")   # a FRESH call — nothing carried
    print(f"  turn 2 → {textwrap.shorten(a2, 90)}")
    note("two separate API calls share NOTHING. The model has no memory — every layer we now add "
         "is just a policy for what WE put back into the prompt.")

def m2_short_term():
    print("  replaying the session with the transcript in context (L1 only):\n")
    for msg in SESSION_1:
        a = mem.chat(msg, layers=("short",))
        print(f"  {C['b']}Priya:{C['x']} {msg}")
        print(f"  {C['d']}bot  : {textwrap.shorten(a, 84)}{C['x']}")
        print(f"  {C['d']}       context now ≈ {est_tokens(mem.assemble(('short',))['context'])} tokens{C['x']}\n")
    a = mem.chat("In one line — what have I told you so far?", layers=("short",))
    print(f"  {C['b']}Priya:{C['x']} In one line — what have I told you so far?")
    print(f"  {C['d']}bot  : {textwrap.shorten(a, 84)}{C['x']}")
    note("follow-ups resolve now — but the context GROWS EVERY TURN, and it dies with the process. "
         "Cost curve up, persistence zero. That's why short-term can't be the only layer.")

def m3_working():
    wm = mem.update_working()
    show_file(mem.working_path, "working.yaml — L2, rewritten every update (never appended)")
    slim = mem.assemble(("working",))
    full = mem.assemble(("short",))
    print(f"\n  full transcript ≈ {est_tokens(full['context'])} tokens  →  working memory ≈ {est_tokens(slim['context'])} tokens")
    a = ask("You are a helpful assistant. MEMORY:\n" + slim["context"] +
            "\n\nuser: What's still open on my plate?\nassistant:")
    print(f"\n  {C['b']}Priya:{C['x']} What's still open on my plate?   {C['d']}(answered from working memory ALONE){C['x']}")
    print(f"  {C['d']}bot  : {textwrap.shorten(a, 84)}{C['x']}")
    note('"In Progress" is the only state that belongs here — the blackboard is RIGHT NOW; '
         "history goes elsewhere. This is compaction layer 1: a whole session distilled to a paragraph.")

def m4_episodic():
    path = mem.rem_flush("support-bot-kickoff", TODAY)
    show_file(path, f"episodic/{path.name} — L3, append-only, dated")
    print(f"\n  {C['d']}session CLOSED: transcript wiped, working.yaml deleted — like sleep, the day is archived.{C['x']}")
    print(f"\n  {C['b']}— NEW SESSION (empty context) —{C['x']}")
    a = mem.chat("What did we discuss last time?", layers=("episodic",))
    print(f"  {C['b']}Priya:{C['x']} What did we discuss last time?")
    print(f"  {C['d']}bot  : {textwrap.shorten(a, 84)}{C['x']}")
    note("we called the flush a REM-flush on purpose: raw experience → consolidated summary. The "
         "transcript is GONE; the episode survives. Append-only + dated = an auditable history.")

def m5_durable():
    profile = mem.distill_semantic(mem.recall_episodes(1))
    show_file(mem.profile_path, "semantic/profile.yaml — L4, distilled facts, merged (fact/preference/decision/action_item)")
    print(f"\n  {C['b']}— ANOTHER NEW SESSION —{C['x']}")
    a = mem.chat("Hi again! Anything I should pick back up?", layers=("durable",))
    print(f"  {C['b']}Priya:{C['x']} Hi again! Anything I should pick back up?")
    print(f"  {C['d']}bot  : {textwrap.shorten(a, 90)}{C['x']}")
    note("the 4-category taxonomy (facts / preferences / decisions / action_items) is what real "
         "production systems extract — one sentence, one fact, mergeable. In real repos this tier "
         "is yaml AND md: profiles, decisions.yaml, lessons.md — git-tracked, reviewable truth.")

def m6_assemble_and_prove():
    asm = mem.assemble()
    print("  the assembled context, layer by layer (stable prefix → volatile tail):\n")
    for layer, toks in asm["budget"].items():
        print(f"    {layer:<14} ≈ {toks:>4} tokens")
    print(f"    {'TOTAL':<14} ≈ {sum(asm['budget'].values()):>4} tokens   (vs replaying every raw transcript, forever)")
    print(f"\n  {C['b']}recall test{C['x']} — new session, EMPTY transcript, memory only:")
    a = mem.chat("Quick check — which city am I based in, and do I write code?", layers=("durable", "episodic"))
    print(f"  {C['d']}bot  : {textwrap.shorten(a, 90)}{C['x']}")
    judge_pass("which city / codes?", a, "States Mumbai AND that she does not write code")
    print(f"\n  {C['b']}isolation test{C['x']} — a DIFFERENT user must recall NOTHING:")
    raj = MemoryStack("raj", fresh=True)
    a2 = raj.chat("Which city am I based in?")
    print(f"  {C['d']}bot→raj: {textwrap.shorten(a2, 90)}{C['x']}")
    judge_pass("raj asks his city", a2, "Does NOT claim to know; does NOT mention Mumbai or Priya's details")
    note("that pair — recall for the right user, silence for the wrong one — is THE production "
         "memory eval. Memory that leaks across users is a security incident, not a feature.")

def m7_memory_x_rag():
    global store
    print(f"  {C['d']}loading the catalog corpus (keyless, local embeddings)…{C['x']}")
    store = corpus.load_catalog_corpus("catalog.db")
    q = "Is there a course that fits me?"
    print(f"\n  {C['b']}Priya:{C['x']} {q}\n")
    # WITHOUT memory: retrieval sees only the literal query
    hits = store.search(q, k=3)
    ctx = "\n".join(f"- ({h.title}) {h.content[:150]}" for h in hits)
    a_no = ask(f"Answer from the CATALOG only.\n\nCATALOG:\n{ctx}\n\nQuestion: {q}\nAnswer:")
    print(f"  {C['y']}WITHOUT memory{C['x']} → {textwrap.shorten(a_no, 88)}")
    # WITH memory: rewrite the query from the profile, retrieve with THAT, answer with both
    profile = mem.read_semantic()
    rq = ask("Rewrite this question as a standalone search query using what we know about the "
             f"user. Return ONLY the query.\n\nUSER PROFILE:\n{profile}\n\nQuestion: {q}")
    print(f"\n  {C['d']}memory-rewritten query → {rq.strip()[:80]}{C['x']}")
    hits2 = store.search(rq, k=3)
    ctx2 = "\n".join(f"- ({h.title}) {h.content[:150]}" for h in hits2)
    a_yes = ask("Answer from the CATALOG, personalized with the USER PROFILE.\n\n"
                f"USER PROFILE:\n{profile}\n\nCATALOG:\n{ctx2}\n\nQuestion: {q}\nAnswer:")
    print(f"  {C['g']}WITH memory{C['x']}    → {textwrap.shorten(a_yes, 88)}")
    print()
    judge_pass(q, a_yes, "Recommends a PM-appropriate, non-coding course (e.g. AI for PMs) because the user is a non-coding product manager")
    specific = judge_pass(q, a_no, "Names ONE specific best-fit course for a non-coding PM")
    if not specific:
        print(f"    {C['g']}→ that FAIL is the demonstration:{C['x']} without memory the model can't know who's asking, so it can't be specific.")
    else:
        print(f"    {C['y']}→ unusual — the memoryless answer got specific anyway (retrieval luck). Re-run to see the typical generic answer.{C['x']}")
    note("the boundary, precisely: the CATALOG (RAG) answers 'what is true in the documents'; "
         "MEMORY answers 'what happened with THIS user'. Kept separate, composed at answer time — "
         "collapsing them into one store is the classic modelling error.")

STEPS = [
    ("The amnesiac — an LLM has no memory",
     "Two consecutive API calls share nothing. Everything an agent 'remembers' is something the "
     "harness put back into the prompt — so memory is not a model feature, it's an ARCHITECTURE "
     "you design. We'll build it in four layers, watching the files appear on disk.", m1_amnesiac),
    ("L1 · Short-term — the transcript in context",
     "The simplest layer: replay the conversation into every call. Follow-ups resolve — but watch "
     "the token counter climb every turn, and remember: close the process and it's all gone.", m2_short_term),
    ("L2 · Working memory — working.yaml",
     "Distill the session into a tiny 'right now' state: who / now / open. It's REWRITTEN, never "
     "appended — the blackboard holds only what's in progress. Then answer a question from the "
     "distillate alone and compare token cost.", m3_working),
    ("L3 · Episodic — the REM-flush",
     "Close the session: summarize it into a dated, append-only markdown entry (YAML frontmatter), "
     "wipe the transcript and the working file. Then start a NEW session and recall what happened "
     "— from the episode, not the transcript.", m4_episodic),
    ("L4 · Durable — semantic/profile.yaml",
     "Distill the episode into atomic facts — four categories: facts, preferences, decisions, "
     "action_items — merged into a profile that outlives every session. A brand-new session now "
     "greets Priya knowing who she is, replaying nothing.", m5_durable),
    ("Assemble the stack — and prove it with an eval",
     "Retrieval-into-context: stable prefix (durable + episodic) first, volatile tail (working + "
     "turn) last — the ordering is what makes the prefix cacheable, and the layer budget is the "
     "economics. Then the two evals that matter: RECALL (new session remembers) and ISOLATION "
     "(another user must not).", m6_assemble_and_prove),
    ("Memory × RAG — compose, don't collapse",
     "Plug the stack into retrieval: memory rewrites the query and personalizes the answer; the "
     "corpus supplies the facts. Score with-vs-without. RAG = documents you loaded; memory = what "
     "happened. Separate stores, composed at answer time.", m7_memory_x_rag),
]

def main():
    print(__doc__.split("\n\n", 1)[1] if "\n\n" in __doc__ else __doc__)
    print(f"  {C['d']}mai_rag {mai_rag.__version__} · provider: ", end="")
    try:
        print(f"{llm._provider()}{C['x']}")
    except Exception:
        print(f"NONE — set OPENAI_API_KEY (class token) in .env{C['x']}")
    for i, (title, teach, run) in enumerate(STEPS, 1):
        banner(i, len(STEPS), title)
        say(teach)
        if prompt_next() == "skip":
            note("skipped."); continue
        try:
            run()
        except RuntimeError as e:                 # clean one-liner (key/rate) — no traceback
            print(f"\n  {C['y']}⚠  {e}{C['x']}\n")
            sys.exit(1)
    print(f"\n{C['g']}  ✔ Lab 4b complete.{C['x']} Your agent's whole mind is sitting in .memory/priya/ — open it.")
    print("    Working is a paragraph, episodes are summaries, the profile is distilled truth:")
    print("    layers ARE compaction. Next: Lab 5 turns judges like ours into a calibrated suite.\n")

if __name__ == "__main__":
    main()
