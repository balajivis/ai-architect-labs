# -*- coding: utf-8 -*-
"""Lab 2c — GraphRAG, Routed (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · after Lab 2 (retrieval) & Lab 3b (routing)

Run it as a guided walkthrough:   python labs/lab_2c.py
Piped / non-interactive input auto-runs every stage (CI-safe).

The course's stance, tested honestly: "GraphRAG is a niche tool, not a default —
lead with when graph LOSES; the real skill is defending a 'no' with data."

Vector retrieval matches MEANING; a knowledge graph stores RELATIONS. Some questions
are relation-shaped ("what connects X to Y?", multi-hop chains) — and some are
absolutely not. We extract entities/relations with an LLM, build a real graph you can
traverse INTERACTIVELY (the class graph service if it's up, local networkx if not —
same API), race graph-augmented answers against chunks-only, and then show the case
where the graph loses. The verdict comes from the scorecard, not the hype.
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

import mai_rag
from mai_rag import corpus, llm, graph as graphmod
from mai_rag.tutor import Tutor, Stage, Spinner, note, panel, show_df, dim, green, yellow, bold

import pandas as pd

# ── shared state ─────────────────────────────────────────────────────────────
store = None
GOLDEN: list[dict] = []
TRIPLES: list[dict] = []        # shipped pre-extracted [{s,r,o,doc}]
G = None                        # the graph backend (remote class service or local networkx)
ENTITIES: list[str] = []

def ask(prompt, temperature=0.0):
    return llm.complete(prompt, tier="small", temperature=temperature)

def _json(raw):
    """Structural JSON extraction (parsing, not classification). Clear ValueError on non-JSON."""
    m = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if not m:
        raise ValueError(f"model did not return JSON: {(raw or '')[:120]!r}")
    return json.loads(m.group(0))

def grade(q, answer, expected):
    p = ("Grade the ANSWER against EXPECTED. 1.0 fully correct, 0.5 partial, 0.0 wrong/missing. "
         "An honest 'not enough information' is correct when EXPECTED says so.\n"
         'Reply JSON only: {"reason":"<short>","score":<1.0|0.5|0.0>}.\n\n'
         f"QUESTION: {q}\nEXPECTED: {expected}\nANSWER: {answer}")
    try:
        return float(_json(ask(p, temperature=0))["score"])
    except (ValueError, KeyError, TypeError):     # one prose/keyless judge reply must not abort the duel
        return 0.0

def chunks_context(q, k=4):
    hits = store.search(q, k=k)
    return "\n\n".join(f"[{i+1}] ({h.title}) {h.content}" for i, h in enumerate(hits))

def entities_in(q: str) -> list[str]:
    """Entity linking, structurally: which KNOWN graph entities appear in the question?
    (Matching a closed list of known names is structural lookup, not classification.)"""
    ql = q.lower()
    found = [e for e in ENTITIES if len(e) > 3 and e in ql]
    found.sort(key=len, reverse=True)
    return found[:4]

def graph_context(q) -> str:
    lines = []
    for e in entities_in(q):
        for t in (G.subgraph(e, hops=2) or [])[:20]:
            if isinstance(t, (list, tuple)) and len(t) == 3:
                lines.append(f"{t[0]} —{t[1]}→ {t[2]}")
            else:
                lines.append(str(t))
    return "\n".join(dict.fromkeys(lines))

def answer_with(q, ctx):
    return ask("Answer using ONLY the context. If it isn't there, say you don't have enough "
               f"information.\n\nQuestion: {q}\n\nContext:\n{ctx}\n\nAnswer:")

# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_blind_spot():
    global store, GOLDEN, TRIPLES
    with Spinner("embedding the Hard Pack (keyless)"):
        store = corpus.load_hard_corpus(rebuild=True)
    GOLDEN[:] = corpus.load_golden_hard()
    TRIPLES[:] = json.loads((pathlib.Path(corpus.__file__).parent / "data" / "hard_triples.json").read_text())["triples"]
    print(f"  {green('loaded')}: {store.stats().get('documents')} docs · {len(GOLDEN)} golden cases · {len(TRIPLES)} shipped triples\n")
    rows = []
    for c in GOLDEN:
        if "none" in c["support"].lower():
            continue
        wanted = [s.strip() for s in c["support"].split("+")]
        got = [h.source for h in store.search(c["q"], k=3)]
        rows.append({"question": c["q"][:38], "tag": c["tag"],
                     "recall@3": sum(w in got for w in wanted) / len(wanted)})
    df = pd.DataFrame(rows)
    show_df(df[df["tag"] == "multi-hop"], "vector retrieval on the RELATION-shaped questions")
    note("vector search matches meaning chunk-by-chunk — it has no concept of 'X relates to Y "
         "relates to Z'. GraphRAG's bet is that for THESE questions, relations beat similarity. "
         "Let's earn or refute that with a scorecard.")

def s2_extract():
    demo_docs = ["incident-response-runbook", "support-tier-gold"]
    for d in demo_docs:
        body = "\n".join(r[0] for r in store.conn.execute(
            "SELECT content FROM chunks WHERE document_id=(SELECT id FROM documents WHERE source=?) ORDER BY chunk_index", (d,)).fetchall())
        with Spinner(f"LLM-extracting triples from {d}"):
            ts = graphmod.extract_triples(body, max_triples=8)
        panel(f"{d} — extracted live", "\n".join(f"{s} —{r}→ {o}" for s, r, o in ts[:8]))
    print(f"  {dim(f'…the other 12 docs ship pre-extracted ({len(TRIPLES)} triples total) so class never waits.')}")
    note("extraction is the GraphRAG ingestion cost: one LLM pass per document, at ingestion time "
         "(cacheable), and it's classification → always the LLM, never a pattern. Triples are the "
         "atoms: (subject, relation, object).")

def s3_build():
    global G, ENTITIES
    user = os.getenv("MAI_GRAPH_USER", "student")
    with Spinner("connecting (class graph service → local networkx fallback)"):
        G = graphmod.connect(user)
    print(f"  backend: {yellow(G.backend)}")
    with Spinner(f"loading {len(TRIPLES)} triples"):
        G.clear()
        G.add_triples([(t["s"], t["r"], t["o"]) for t in TRIPLES])
    print(f"  {green('graph built')}: {G.stats()}")
    ENTITIES[:] = sorted({t["s"].lower() for t in TRIPLES} | {t["o"].lower() for t in TRIPLES})
    demo = "security team" if "security team" in ENTITIES else ENTITIES[0]
    panel(f"neighbors('{demo}') — one hop of the graph, interactively",
          "\n".join(f"{a} —{r}→ {b}" for a, r, b in
                    [t for t in (G.neighbors(demo) or [])[:10] if isinstance(t, (list, tuple)) and len(t) == 3])
          or "(none)")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import networkx as nx
        g = nx.MultiDiGraph()
        for t in TRIPLES:
            g.add_edge(t["s"].lower()[:24], t["o"].lower()[:24])
        pos = nx.spring_layout(g, k=0.6, seed=42)
        plt.figure(figsize=(11, 8))
        nx.draw_networkx(g, pos, node_size=60, font_size=5, arrows=False, alpha=0.75, edge_color="#bbb")
        plt.axis("off"); plt.title("The Hard Pack as a knowledge graph (168 LLM-extracted triples)")
        out = pathlib.Path("lab2c_graph.png").resolve()
        plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
        print(f"  {green('graph map saved')} → {out}")
    except Exception as e:
        note(f"(graph PNG skipped: {type(e).__name__})")
    note("same primitives either way: neighbors / path / subgraph. If the class service is up you "
         "just built YOUR OWN partition of a real hosted graph DB; offline, networkx — the lab "
         "never dies with the server.")

def s4_duel():
    cases = [c for c in GOLDEN if c["tag"] == "multi-hop"][:3]
    rows = []
    for c in cases:
        with Spinner(f"duel: {c['q'][:44]}"):
            a_vec = answer_with(c["q"], chunks_context(c["q"]))
            gctx = graph_context(c["q"])
            a_gr = answer_with(c["q"], chunks_context(c["q"]) + "\n\nENTITY RELATIONS (from the knowledge graph):\n" + gctx)
            s_vec, s_gr = grade(c["q"], a_vec, c["expected"]), grade(c["q"], a_gr, c["expected"])
        rows.append({"question": c["q"][:36], "chunks only": s_vec, "chunks+graph": s_gr,
                     "graph facts used": len(gctx.splitlines())})
        print(f"  {c['q'][:52]}")
        print(f"    chunks only  : {s_vec}   chunks+graph : {s_gr}   {dim(f'({len(gctx.splitlines())} relations injected)')}")
    df = pd.DataFrame(rows)
    show_df(df, "the duel — relation-shaped questions, judged")
    note("the production GraphRAG recipe is COMPOSITION, not replacement: chunks carry the text, "
         "the subgraph carries the connections, the model gets both. Watch whether the graph "
         "column actually earns its keep — this corpus is small enough that chunks often suffice.")

def s5_where_it_loses():
    c = next((c for c in GOLDEN if c["tag"] == "precision"), None)
    if c is None:                    # empty/oddly-tagged golden set → honest skip, not a raw StopIteration
        note("no 'precision' case in the golden set (did it load? check load_golden_hard) — skipping this demo.")
        return
    with Spinner("precision question: triples-only vs chunks-only"):
        gctx = graph_context(c["q"]) or "(no linked entities)"
        a_graph = answer_with(c["q"], "ENTITY RELATIONS:\n" + gctx)
        a_vec = answer_with(c["q"], chunks_context(c["q"]))
        s_graph, s_vec = grade(c["q"], a_graph, c["expected"]), grade(c["q"], a_vec, c["expected"])
    print(f"  {bold(c['q'][:60])}")
    print(f"    graph triples only : {s_graph}   {dim('relations store connections, not exact numbers')}")
    print(f"    vector chunks only : {s_vec}   {dim('the number is IN the chunk')}\n")
    print(f"  {bold('the cost ledger')}: {len(TRIPLES)} triples took ~14 extraction calls at ingestion; "
          f"chunks took zero.\n")
    show_df(pd.DataFrame([
        {"question shape": "relation-shaped (multi-hop, 'what connects…')", "use": "graph-augmented"},
        {"question shape": "fact lookup (a number, a date, a threshold)", "use": "chunks (vector)"},
        {"question shape": "everything else", "use": "route it — Lab 3b's router prices the rungs"},
    ]), "the verdict — defend the no with data")
    note("this is the course stance made concrete: GraphRAG is a ROUTED strategy for "
         "relation-shaped queries — a rung the Lab 3b router can price — not a default. You now "
         "have the scorecard to say 'no' with.")

TUTOR = Tutor(
    title="Lab 2c — GraphRAG, Routed",
    tagline="Modern AI Pro · AI Architect · Pillar I · graph as a routed strategy",
    mission="""
    Vector retrieval matches meaning; a knowledge graph stores relations. This lab builds
    a real graph from the Hard Pack — LLM-extracted triples, traversable interactively
    through the class graph service (or local networkx, same API) — then races
    graph-augmented answers against chunks-only, INCLUDING the case where the graph loses.
    The course stance is the lab's spine: graph is a routed strategy, not a default, and
    the skill is defending a 'no' with data.
    """,
    stages=[
        Stage("Vector's blind spot — relation-shaped questions", """
            Load the Hard Pack and score plain vector retrieval on the multi-hop golden
            cases. Chunk similarity has no concept of 'X connects to Y connects to Z' —
            these are the questions GraphRAG exists for. Baseline first, always.""", s1_blind_spot, "0"),
        Stage("Extract — documents become triples", """
            The ingestion step: an LLM reads each document and emits (subject, relation,
            object) triples — classification, so always the LLM, never a pattern. Two docs
            extracted live so you see it happen; the rest ship pre-extracted (168 triples)
            so nobody waits.""", s2_extract, "~2"),
        Stage("Build & see — your own traversable graph", """
            Load the triples through mai_rag.graph: the class graph service if it's up
            (your own partition of a real hosted Cosmos graph — zero setup, your class
            token), local networkx if not — identical primitives either way. Then look at
            it: one hop of neighbors, and the whole corpus drawn as a graph PNG.""", s3_build, "0"),
        Stage("The duel — chunks vs chunks+graph, judged", """
            The production recipe is composition: for each multi-hop question, answer once
            with chunks only and once with chunks + the linked entities' subgraph relations
            injected. The judge scores both. The graph column has to EARN its keep.""", s4_duel, "~9"),
        Stage("Where the graph loses — and the routing verdict", """
            A precision question ('how many quotes for $30k?'): triples store connections,
            not exact numbers — the chunk wins. Add the cost ledger (an extraction pass per
            document at ingestion) and the verdict writes itself: graph-augment the
            relation-shaped queries, route everything else past it. Lab 3b's router prices
            the rungs.""", s5_where_it_loses, "~5"),
    ],
    outro="""
    You built a knowledge graph with an LLM, traversed it interactively, measured where it
    wins (relation-shaped questions) and where it loses (fact lookups, plus an ingestion
    cost chunks never pay). GraphRAG's honest home is a rung in the routing ladder — and
    now you have the numbers to defend that architecture in a design review.
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
