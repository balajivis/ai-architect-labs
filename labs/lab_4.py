# -*- coding: utf-8 -*-
"""Lab 4 — Conversational Memory: What Stateless RAG Drops (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · Module 4

Run it as a guided walkthrough:   python labs/lab_4.py
Piped / non-interactive input auto-runs every stage (CI-safe).

A conversation is STATE — and stateless RAG drops it. Every stage of this lab picks up
one thing statelessness loses, and proves the fix on golden conversations:

  · the PRONOUN   — "is there a course for that?" → rewrite to a standalone query
  · the BILL      — a growing window re-sends everything → compact old turns to a summary
  · the PERSON    — durable facts (role, skills, goals) → a profile that personalizes
  · the RETRIEVAL — the same question should fetch DIFFERENT docs per user
  · the ROT       — memory you can't inspect is memory you can't trust → observe + decay
  · the PROOF     — re-score, grading ONLY the turns that depend on memory

Lab 4b builds the full four-layer memory stack on disk (working/episodic/durable);
this lab is the conversational core that stack serves.
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
import textwrap

import pandas as pd

import mai_rag
from mai_rag import corpus, llm
from mai_rag.tutor import Tutor, Stage, Spinner, note, show_df, dim, green, bold, yellow

# ── shared state ─────────────────────────────────────────────────────────────
store = None
mem = None                # the compacting memory carried across stages 3→4→6
profile = None            # the long-term profile built in stage 5

def ask(prompt, temperature=0.0):
    return llm.complete(prompt, tier="small", temperature=temperature)

def _json(raw):
    """Structural JSON extraction (parsing, not classification). Clear ValueError on non-JSON."""
    m = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if not m:
        raise ValueError(f"model did not return JSON: {(raw or '')[:120]!r}")
    return json.loads(m.group(0))

def retrieve(q, k=4):
    return "\n\n".join(f"[{h.source}] {h.content}" for h in store.search(q, k=k))

def est_tokens(s: str) -> int:
    return max(1, len(s) // 4)

# Golden CONVERSATIONS — later turns DEPEND on earlier ones (follow-ups + personalization).
# `needs_memory=True` marks the turns a stateless bot cannot answer.
conversations = [
    {"persona": "PM, non-coder, new to AI",
     "turns": [
        {"user": "I'm a product manager, new to AI, and I don't code.",
         "expect": "Acknowledge the user's context.", "needs_memory": False},
        {"user": "What should I focus on learning first?",
         "expect": "PM-relevant AI skills (prompting, AI-assisted PRDs, evals for product) — tailored to a non-coding PM.", "needs_memory": True},
        {"user": "Is there a course for that?",
         "expect": "AI for PMs — a 1-day course for product managers.", "needs_memory": True},
        {"user": "How long is it and who is it for?",
         "expect": "1 day, for product managers.", "needs_memory": True},
     ]},
    {"persona": "Senior engineer, Python, wants production RAG",
     "turns": [
        {"user": "I'm a senior backend engineer, very comfortable with Python.",
         "expect": "Acknowledge the user's context.", "needs_memory": False},
        {"user": "I want to build production RAG systems — which course should I take?",
         "expect": "AI Practitioner / AI Architect (RAG, evals, MCP, trust).", "needs_memory": True},
        {"user": "How is it different from the vibe coding one?",
         "expect": "Practitioner builds AI systems; Vibe Coding is AI-assisted coding.", "needs_memory": True},
        {"user": "Will it cover evaluations?",
         "expect": "Yes — evaluations are a core layer of the Practitioner course.", "needs_memory": True},
     ]},
]

def stateless_answer(user_msg):
    ctx = retrieve(user_msg)
    return ask(f"Answer the user using the catalog context.\n\nUser: {user_msg}\n\nContext:\n{ctx}\n\nAnswer:")

# ── short-term memory: rolling window + the query-rewrite trick ──────────────
class ShortTermMemory:
    def __init__(self, window=6):
        self.turns, self.window = [], window
    def add(self, role, text): self.turns.append((role, text))
    def context(self): return "\n".join(f"{r}: {t}" for r, t in self.turns[-self.window:])

def chat(user_msg, mem_):
    history = mem_.context()
    standalone = ask("Given the conversation, rewrite the user's LAST message as a standalone question "
                     f"(resolve any pronouns like 'that'/'it').\n\n{history}\nUser: {user_msg}\n\nStandalone question:")
    ctx = retrieve(standalone)
    ans = ask(f"Conversation so far:\n{history}\n\nUser: {user_msg}\n\nCatalog context:\n{ctx}\n\nAnswer:")
    mem_.add("User", user_msg); mem_.add("Bot", ans)
    return ans, standalone

# ── compacting memory: constant-size context ─────────────────────────────────
class CompactingMemory(ShortTermMemory):
    def __init__(self, window=4):
        super().__init__(window=window); self.summary = ""
    def add(self, role, text):
        super().add(role, text)
        if len(self.turns) > self.window * 2:                  # fold oldest turns into a running summary
            old = self.turns[:-self.window]
            self.summary = ask("Update the running summary with these older turns (<=60 words).\n"
                               f"Summary: {self.summary}\nTurns:\n" +
                               "\n".join(f"{r}: {t}" for r, t in old))
            self.turns = self.turns[-self.window:]
    def context(self):
        head = f"[summary] {self.summary}\n" if self.summary else ""
        return head + "\n".join(f"{r}: {t}" for r, t in self.turns[-self.window:])

# ── long-term profile: durable facts ─────────────────────────────────────────
class UserProfile:
    def __init__(self): self.facts = []
    def update(self, user_msg):
        out = ask('Extract DURABLE facts about the user (role, skills, goals) from this message. '
                  'Reply JSON only: {"facts": ["..."]} (empty list if none).\n\n'
                  f'Message: "{user_msg}"')
        for f in _json(out).get("facts", []):
            if f not in self.facts: self.facts.append(f)
    def text(self): return "; ".join(self.facts) or "(unknown user)"

def scoped_search(q, profile_, k=3):
    return [h.source for h in store.search(f"{q} (for: {profile_.text()})", k=k)]

# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_setup():
    global store
    with Spinner("embedding the catalog corpus (keyless, local MiniLM, ~20s)"):
        store = corpus.load_catalog_corpus(rebuild=True)
    s = store.stats()
    n_turns = sum(len(c["turns"]) for c in conversations)
    n_dep = sum(t["needs_memory"] for c in conversations for t in c["turns"])
    print(f"  {green('corpus ready')}: {s.get('documents')} docs · {s.get('chunks')} chunks")
    print(f"  golden CONVERSATIONS: {len(conversations)} personas · {n_turns} turns · "
          f"{bold(str(n_dep))} memory-dependent")
    for c in conversations:
        print(f"    · {c['persona']}: " + dim(" → ".join(t['user'][:28] for t in c['turns'])))
    note("the golden fixture changed shape: not questions — CONVERSATIONS, where later turns "
         "depend on earlier ones. `needs_memory` marks the turns a stateless bot cannot answer; "
         "those are the only turns the finale will grade. Evals follow the failure you care about.")

def s2_stateless():
    print(f"  persona: {bold(conversations[0]['persona'])} — every turn answered with NO memory:\n")
    for t in conversations[0]["turns"]:
        with Spinner("stateless answer"):
            a = stateless_answer(t["user"])
        flag = yellow(" [needs memory]") if t["needs_memory"] else ""
        print(f"  {bold('USER:')} {t['user']}{flag}")
        print(f"  {dim('BOT : ' + a[:140].replace(chr(10), ' '))}\n")
    note("the opening turn works — then 'is there a course for THAT?' and 'how long is IT?' "
         "collapse: the bot has no idea what that/it means. Follow-ups are the heart of real "
         "conversation, and a pronoun is a pointer into state you threw away.")

def s3_rewrite():
    global mem
    mem = ShortTermMemory()
    # the money shot: what retrieval sees BEFORE vs AFTER the rewrite
    lead_in = conversations[0]["turns"][:2]
    for t in lead_in:                                   # seed the window quietly
        with Spinner("seeding the window"):
            chat(t["user"], mem)
    pronoun_q = conversations[0]["turns"][2]["user"]    # "Is there a course for that?"
    raw_docs = [h.source for h in store.search(pronoun_q, k=3)]
    with Spinner("rewrite + retrieve"):
        ans, standalone = chat(pronoun_q, mem)
    new_docs = [h.source for h in store.search(standalone, k=3)]
    print(f"  {bold('USER:')} {pronoun_q}")
    print(f"  rewritten → {green(standalone.strip()[:76])}\n")
    print(f"  retrieval with the RAW pronoun query : {dim(' · '.join(d[:30] for d in raw_docs))}")
    print(f"  retrieval with the REWRITTEN query   : {dim(' · '.join(d[:30] for d in new_docs))}\n")
    print(f"  {dim('BOT : ' + ans[:140].replace(chr(10), ' '))}")
    with Spinner("finishing the conversation"):
        ans2, st2 = chat(conversations[0]["turns"][3]["user"], mem)
    print(f"\n  {bold('USER:')} {conversations[0]['turns'][3]['user']}")
    print(f"  rewritten → {green(st2.strip()[:76])}")
    print(f"  {dim('BOT : ' + ans2[:140].replace(chr(10), ' '))}")
    note("the trick is NOT the window — it's the REWRITE. An embedding can't follow a pronoun, "
         "so before retrieving we rewrite the follow-up into a standalone question using the "
         "window. Look at the two retrieval lines: same user turn, different documents. That's "
         "the whole fix.")

def s4_compaction():
    global mem
    grow = ShortTermMemory(window=999)                  # what NOT to do: keep everything
    mem = CompactingMemory(window=2)
    with Spinner(f"replaying all {sum(len(c['turns']) for c in conversations)} turns through BOTH memories"):
        for c in conversations:
            for t in c["turns"]:
                chat(t["user"], grow)
                chat(t["user"], mem)
    g, m = est_tokens(grow.context()), est_tokens(mem.context())
    print(f"  context size after 8 turns:  growing window ≈ {yellow(str(g))} tokens   "
          f"compacted ≈ {green(str(m))} tokens\n")
    print(f"  {bold('what the compacted memory holds:')}")
    print(textwrap.indent(mem.context()[:600], f"  {dim('│')} "))
    note("a growing window re-sends the WHOLE conversation every turn — the bill climbs turn "
         "over turn, forever. Compaction folds old turns into a running summary and keeps a "
         "short verbatim window: constant-size context, full continuity. This is the difference "
         "between a bot that's cheap at turn 50 and one that isn't.")

def s5_profile():
    global profile
    profile = UserProfile()
    with Spinner("extracting durable facts from the PM conversation"):
        for t in conversations[0]["turns"]:
            profile.update(t["user"])
    print(f"  learned profile: {green(profile.text())}\n")
    q = "What should I focus on learning first?"
    with Spinner("same question, generic vs personalized"):
        generic = ask(f"Q: {q}\nContext:\n{retrieve(q)}\n\nAnswer:")
        personal = ask(f"User profile: {profile.text()}\n\nQ: {q}\nContext:\n{retrieve(q)}\n\n"
                       "Give a recommendation tailored to THIS user:")
    print(f"  {bold('GENERIC :')} {dim(generic[:150].replace(chr(10), ' '))}\n")
    print(f"  {bold('PERSONAL:')} {green(personal[:220].replace(chr(10), ' '))}")
    note("some facts outlive the conversation: who the user is, what they know, what they want. "
         "Extract those DURABLE facts (that's the semantic tier from Lab 4b) and inject them — "
         "the same question now gets a different, better answer per person.")

def s6_scoped():
    q = "which course should I take?"
    pm = UserProfile();  pm.facts = ["product manager", "does not code", "new to AI"]
    eng = UserProfile(); eng.facts = ["senior backend engineer", "knows Python", "wants production RAG"]
    print(f"  Q: {bold(q)}  — three retrievals, no LLM:\n")
    print(f"  generic    : {dim(' · '.join(h.source[:30] for h in store.search(q, 3)))}")
    print(f"  PM-scoped  : {dim(' · '.join(d[:30] for d in scoped_search(q, pm)))}")
    print(f"  eng-scoped : {dim(' · '.join(d[:30] for d in scoped_search(q, eng)))}")
    note("personalization isn't only in the answer — it changes WHAT YOU RETRIEVE. Fold the "
         "profile into the query and the right docs surface first: a non-coding PM and a senior "
         "engineer asking the SAME question get DIFFERENT documents. Retrieval-time beats "
         "generation-time: the model can't cite a doc it never saw.")

def s7_observe():
    print(f"  {bold('what the agent remembers right now')} — memory you can inspect:\n")
    print(f"  {yellow('short-term window:')}")
    print(textwrap.indent((mem.context() if mem else "(none)")[:400], f"  {dim('│')} "))
    print(f"\n  {yellow('running summary:')}")
    print(textwrap.indent((getattr(mem, 'summary', '') or '(none)')[:300], f"  {dim('│')} "))
    print(f"\n  {yellow('long-term profile:')}")
    print(f"  {dim('│')} {(profile.text() if profile else '(none)')}")
    if profile:
        profile.facts = profile.facts[-5:]              # decay: keep the most recent N durable facts
        print(f"\n  profile after decay (keep 5): {green(profile.text())}")
    note("memory you can't inspect is memory you can't trust — and memory that only grows, rots: "
         "stale facts crowd out current ones and personalize answers for a person who no longer "
         "exists. Print it, cap it, drop the oldest. (Production versions: TTLs, per-fact "
         "timestamps, and the decay policies Lab 4b's durable tier needs.)")

def s8_rescore():
    def grade_turn(user, answer, expect):
        p = ('Did the ANSWER correctly handle the user turn, given EXPECTED? 1.0 yes, 0.5 partial, 0.0 confused/wrong. '
             'JSON only: {"score": <1.0|0.5|0.0>}.\n\n'
             f'USER: {user}\nEXPECTED: {expect}\nANSWER: {answer}')
        return float(_json(ask(p))["score"])
    rows = []
    with Spinner("replaying both conversations, stateless vs memory (+ judging)"):
        for conv in conversations:
            m = ShortTermMemory()                        # fresh memory per conversation
            for t in conv["turns"]:
                try:
                    s_ans = stateless_answer(t["user"])
                    m_ans, _ = chat(t["user"], m)
                    if t["needs_memory"]:
                        rows.append({"turn": t["user"][:42],
                                     "stateless": grade_turn(t["user"], s_ans, t["expect"]),
                                     "with_memory": grade_turn(t["user"], m_ans, t["expect"])})
                except (ValueError, KeyError, TypeError):
                    pass                                  # one bad/non-numeric judge reply drops a row, not the run
    if not rows:                                          # every judge reply failed → report honestly, don't KeyError
        note("no memory-dependent turns could be judged this run (the judge replies didn't parse) — "
             "re-run the move; if it persists, check your key/rate.")
        return
    df = pd.DataFrame(rows)
    show_df(df, "the finale — graded on MEMORY-DEPENDENT turns only")
    means = df[["stateless", "with_memory"]].mean().round(3)
    print(f"  MEANS: stateless={means['stateless']}  with_memory={means['with_memory']}")
    note("we grade ONLY the turns that depend on context — that's where the argument lives. "
         "Stateless craters on exactly those turns; memory resolves them. Unlike retrieval "
         "tricks, this win can't be argued away: stateless RAG simply cannot carry state. "
         "Lab 4b turns this into a durable, four-layer architecture on disk.")

TUTOR = Tutor(
    title="Lab 4 — Conversational Memory: What Stateless RAG Drops",
    tagline="Modern AI Pro · AI Architect · Pillar I · Module 4",
    mission="""
    Labs 1–3 treated every query as independent. Real users don't: they say "is there a
    course for THAT?" and "how long is IT?" — pronouns pointing into state your pipeline
    threw away. A conversation is a state machine, and stateless RAG drops the state.

    Each stage picks up one thing statelessness loses — the pronoun, the bill, the
    person, the retrieval, the rot — and the finale grades only the turns that depend on
    memory, because that's where the win is unarguable. (Lab 4b then builds the full
    four-layer memory stack on disk; this lab is the conversational core it serves.)
    """,
    stages=[
        Stage("Setup — the catalog + golden CONVERSATIONS", """
            Same catalog as Lab 3, but the golden fixture changes shape: two personas
            (a non-coding PM, a senior engineer), multi-turn conversations where later
            turns depend on earlier ones, and a needs_memory flag marking exactly the
            turns a stateless bot cannot answer. The eval design IS the lab design.""", s1_setup, "0"),
        Stage("Where stateless RAG breaks — watch the follow-ups collapse", """
            Answer each turn of the PM conversation independently — no memory. The opener
            works fine; then 'is there a course for that?' meets a bot that has no idea
            what THAT means. A pronoun is a pointer into conversation state; stateless RAG
            dereferences it into nothing.""", s2_stateless, "~4"),
        Stage("The pronoun — a rolling window + the query REWRITE", """
            The fix is not the window — it's the rewrite. Before retrieving, rewrite the
            follow-up into a standalone question using recent history. The exhibit shows
            retrieval BEFORE vs AFTER the rewrite on the same turn: different documents.
            An embedding cannot follow a pronoun; a rewrite can.""", s3_rewrite, "~8"),
        Stage("The bill — compact old turns, keep a short window", """
            A growing window re-sends the whole conversation every turn. Compaction folds
            the oldest turns into a running ≤60-word summary and keeps a short verbatim
            window — constant-size context, full continuity. We run BOTH memories through
            all 8 turns and print the token counts side by side.""", s4_compaction, "~20"),
        Stage("The person — durable facts → a profile → personalization", """
            Some facts outlive the conversation: role, skills, goals. Extract them into a
            profile (Lab 4b's durable tier, in miniature) and inject it. The exhibit: the
            SAME question answered generically vs for THIS user — a non-coding PM gets a
            PM answer, not a syllabus dump.""", s5_profile, "~7"),
        Stage("The retrieval — user-scoped search (no LLM)", """
            Personalization at generation time is half the story. Fold the profile into
            the query itself and the right docs surface FIRST: a PM and an engineer asking
            the same question retrieve different documents. The model can't cite a doc it
            never saw — scope the retrieval, not just the reply.""", s6_scoped, "0"),
        Stage("The rot — observability + decay", """
            Print exactly what the agent holds — window, summary, profile — because memory
            you can't inspect is memory you can't trust. Then apply decay: cap the profile,
            drop the oldest facts, so it stays a portrait of who the user IS, not who they
            were eight conversations ago.""", s7_observe, "0"),
        Stage("The proof — re-score on memory-dependent turns only", """
            Replay both golden conversations stateless and with memory, grading ONLY the
            needs_memory turns. Stateless craters exactly there; memory resolves them.
            The gap is the whole lab — and it cannot be argued away, because stateless
            RAG structurally cannot carry state.""", s8_rescore, "~36"),
    ],
    outro="""
    The conversational core is four habits: rewrite before you retrieve, compact before
    you're billed, extract what outlives the session, and inspect what you remember.
    Lab 4b makes those habits an architecture — four layers, on disk, with recall and
    isolation evals. Lab 5 calibrates the judges you've been trusting all day.
    """,
)

def main():
    provider = "provider: "
    try:
        provider += llm._provider()
    except Exception:
        provider += "NONE — set OPENAI_API_KEY (class token) in .env"
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · {provider}")

if __name__ == "__main__":
    main()
