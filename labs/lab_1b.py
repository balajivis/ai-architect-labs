# -*- coding: utf-8 -*-
"""Lab 1b — RAG Foundations: The Dials (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · between Module 1 (the instrument) and
Module 2 (the fix ladder)

Run it as a guided walkthrough:   python labs/lab_1b.py
Piped / non-interactive input auto-runs every stage (CI-safe).

The mission: BEFORE you reach for fancy fixes, master the foundation dials every RAG
pipeline is built on — chunking strategy, chunk size, overlap, the embedding model,
top-k, phrasing, thresholds. Every twist of a dial is SCORED on the same golden set
and drawn as a bar you can see move. 100% keyless: retrieval only, no LLM, no token.
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

import re
import time

import numpy as np
import pandas as pd

import mai_rag
from mai_rag import corpus
from mai_rag.tutor import Tutor, Stage, Spinner, note, panel, show_df, choice, dim, green, yellow, bold

# ── raw docs + golden set (loaded in stage 1) ────────────────────────────────
DOCS: dict[str, dict] = {}      # source -> {"title":…, "body":…, "meta":…}
GOLDEN: list[dict] = []
LEADERBOARD: list[dict] = []    # every scored config lands here

# ── embedding models (encoders cached; chunk-matrix cache keyed by config) ───
MODELS = {
    "minilm": ("all-MiniLM-L6-v2", "22M params · 384 dims · ~80MB"),
    "mpnet":  ("all-mpnet-base-v2", "110M params · 768 dims · ~420MB"),
}
_encoders: dict[str, object] = {}
_matrix_cache: dict[tuple, tuple] = {}   # cfg key -> (X, sources, n_chunks, encode_s)

def encoder(model_key: str):
    if model_key not in _encoders:
        from sentence_transformers import SentenceTransformer
        name, blurb = MODELS[model_key]
        with Spinner(f"loading {name} ({blurb.split('·')[-1].strip()} download on first use)"):
            _encoders[model_key] = SentenceTransformer(name)
    return _encoders[model_key]

def encode(model_key: str, texts: list[str]) -> np.ndarray:
    X = encoder(model_key).encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(X)

# ── the chunkers (each returns list[(source, chunk_text)]) ───────────────────
def sentences_of(body: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n{2,}", body) if s.strip()]   # structural split

def chunk_fixed(body: str, size: int, overlap: float) -> list[str]:
    """Fixed WORD windows (word-count as the class's token proxy) with fractional overlap."""
    words = body.split()
    step = max(1, int(size * (1 - overlap)))
    return [" ".join(words[i:i + size]) for i in range(0, max(len(words) - int(size * overlap), 1), step)]

def chunk_sentence(body: str, size: int) -> list[str]:
    """Accumulate whole sentences up to ~size words — a fact is never cut mid-sentence."""
    out, cur, n = [], [], 0
    for s in sentences_of(body):
        w = len(s.split())
        if cur and n + w > size:
            out.append(" ".join(cur)); cur, n = [], 0
        cur.append(s); n += w
    if cur:
        out.append(" ".join(cur))
    return out

def chunk_structure(body: str, size: int) -> list[str]:
    """Split on markdown headers, keep each heading WITH its body, merge tiny sections."""
    sections, cur = [], []
    for line in body.splitlines():
        if line.startswith("#") and cur:
            sections.append("\n".join(cur)); cur = []
        cur.append(line)
    if cur:
        sections.append("\n".join(cur))
    out, buf, n = [], [], 0
    for sec in sections:
        w = len(sec.split())
        if buf and n + w > size:
            out.append("\n".join(buf)); buf, n = [], 0
        buf.append(sec); n += w
    if buf:
        out.append("\n".join(buf))
    return out

def chunk_semantic(body: str, size: int, model_key: str = "minilm") -> list[str]:
    """Break where MEANING shifts: embed sentences, split at cosine dips, merge to ~size."""
    sents = sentences_of(body)
    if len(sents) < 3:
        return [" ".join(sents)] if sents else []
    V = encode(model_key, sents)
    sims = np.array([float(V[i] @ V[i + 1]) for i in range(len(V) - 1)])
    cut = sims < (sims.mean() - 0.5 * sims.std())          # a dip = a topic shift
    out, cur, n = [], [], 0
    for i, s in enumerate(sents):
        cur.append(s); n += len(s.split())
        if (i < len(cut) and cut[i] and n >= size // 2) or n >= size:
            out.append(" ".join(cur)); cur, n = [], 0
    if cur:
        out.append(" ".join(cur))
    return out

STRATEGIES = {"fixed": "hard word windows (cuts mid-sentence)",
              "sentence": "whole sentences packed to size",
              "structure": "markdown sections (heading stays with body)",
              "semantic": "break where the MEANING shifts (embedding dips)"}

def build_chunks(strategy: str, size: int, overlap: float, title_prepend: bool) -> list[tuple[str, str]]:
    pairs = []
    for src, d in DOCS.items():
        if strategy == "fixed":
            chs = chunk_fixed(d["body"], size, overlap)
        elif strategy == "sentence":
            chs = chunk_sentence(d["body"], size)
        elif strategy == "structure":
            chs = chunk_structure(d["body"], size)
        else:
            chs = chunk_semantic(d["body"], size)
        for c in chs:
            pairs.append((src, (d["title"] + " — " + c) if title_prepend else c))
    return pairs

# ── config → scored retrieval (the whole pipeline, in-memory + glass-box) ────
def cfg_key(strategy, size, overlap, model_key, title_prepend):
    return (strategy, size, round(overlap, 2), model_key, title_prepend)

def build_index(strategy="sentence", size=180, overlap=0.0, model_key="minilm", title_prepend=False):
    key = cfg_key(strategy, size, overlap, model_key, title_prepend)
    if key in _matrix_cache:
        return _matrix_cache[key]
    pairs = build_chunks(strategy, size, overlap, title_prepend)
    texts = [t for _, t in pairs]
    t0 = time.time()
    X = encode(model_key, texts)
    took = time.time() - t0
    _matrix_cache[key] = (X, [s for s, _ in pairs], len(texts), took)
    return _matrix_cache[key]

def retrieve(index, q: str, k: int, model_key: str) -> list[tuple[str, float]]:
    X, sources, _, _ = index
    qv = encode(model_key, [q])[0]
    sims = X @ qv
    order = np.argsort(sims)[::-1]
    seen, out = set(), []
    for i in order:                              # dedupe chunk hits -> ranked DOC list
        if sources[i] not in seen:
            seen.add(sources[i]); out.append((sources[i], float(sims[i])))
        if len(out) == k:
            break
    return out

def score_config(label, strategy="sentence", size=180, overlap=0.0, model_key="minilm",
                 title_prepend=False, k=3, quiet=False):
    index = build_index(strategy, size, overlap, model_key, title_prepend)
    _, _, n_chunks, took = index
    mrrs, recalls, hit1s = [], [], []
    for c in GOLDEN:
        sup = c["support"]
        if "none" in sup.lower():
            continue
        wanted = [s.strip() for s in sup.split("+")]
        got = [s for s, _ in retrieve(index, c["q"], k, model_key)]
        recalls.append(sum(w in got for w in wanted) / len(wanted))
        ranks = [i + 1 for i, g in enumerate(got) if g in wanted]
        mrrs.append(1.0 / ranks[0] if ranks else 0.0)
        hit1s.append(1.0 if (got and got[0] in wanted) else 0.0)
    row = {"config": label, "MRR": round(float(np.mean(mrrs)), 3),
           "recall": round(float(np.mean(recalls)), 2), "hit@1": round(float(np.mean(hit1s)), 2),
           "chunks": n_chunks, "embed_s": round(took, 1),
           "_cfg": dict(strategy=strategy, size=size, overlap=overlap, model=model_key,
                        title=title_prepend, k=k)}
    if not any(r["config"] == label for r in LEADERBOARD):
        LEADERBOARD.append(row)
    if not quiet:
        print(f"  {label:34s} {sparkbar(row['MRR'])} MRR={row['MRR']:.3f}  recall={row['recall']:.2f}  hit@1={row['hit@1']:.2f}  {dim(f'({n_chunks} chunks)')}")
    return row

def sparkbar(v: float, vmax: float = 1.0, width: int = 18) -> str:
    filled = int(round((v / vmax) * width))
    return green("█" * filled) + dim("░" * (width - filled))

def show_leaderboard(top=10):
    rows = sorted(LEADERBOARD, key=lambda r: (-r["MRR"], -r["recall"]))[:top]
    body = "\n".join(f"{i+1:>2}. {r['config']:<34} {sparkbar(r['MRR'])} MRR={r['MRR']:.3f}  recall={r['recall']:.2f}"
                     for i, r in enumerate(rows))
    panel("LEADERBOARD — best configs so far (by MRR@3)", body)

# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_anatomy():
    global DOCS, GOLDEN
    hard_dir = corpus._find_hard_corpus_dir()
    for p in sorted(hard_dir.glob("*.md")):
        meta, body = corpus._parse_frontmatter(p.read_text(encoding="utf-8"))
        src = meta.get("doc_id", p.stem)
        DOCS[src] = {"title": meta.get("title", p.stem), "body": body, "meta": meta}
    GOLDEN[:] = corpus.load_golden_hard()
    print(f"  {green('loaded')}: {len(DOCS)} raw docs · {len(GOLDEN)} golden cases · retrieval is 100% keyless\n")
    demo = "hr-parental-leave-active"
    body = DOCS[demo]["body"]
    for name, chs in (("fixed@60 words", chunk_fixed(body, 60, 0.0)),
                      ("sentence@60", chunk_sentence(body, 60)),
                      ("structure@120", chunk_structure(body, 120))):
        first = chs[0].replace("\n", " ")[:100]
        print(f"  {yellow(name):<28} → {len(chs):>2} chunks   first: {dim(first + '…')}")
    cut = chunk_fixed(body, 60, 0.0)
    if len(cut) >= 2:
        boundary = cut[0].split()[-6:] + ["‖"] + cut[1].split()[:6]
        panel("a fact, cut in half by a fixed boundary (the ‖ is the chunk break)", " ".join(boundary))
    else:
        note("this demo doc fits in a single 60-word chunk — nothing to cut here; the size dial (next) "
             "is where the tension shows.")
    note("every dial downstream exists to manage one tension: chunks small enough to be precise, "
         "big enough to carry their meaning. You just watched 'fixed' cut a sentence mid-thought.")

def s2_size():
    print(f"  strategy fixed · overlap 0 · MiniLM · k=3 — sweeping SIZE:\n")
    rows = []
    for size in (60, 120, 240, 480):
        with Spinner(f"chunk+embed+score @ {size} words"):
            rows.append(score_config(f"fixed@{size}", "fixed", size, 0.0, quiet=True))
        r = rows[-1]
        print(f"  {r['config']:<12} {sparkbar(r['MRR'])} MRR={r['MRR']:.3f}  recall={r['recall']:.2f}  {dim(str(r['chunks']) + ' chunks · ' + str(r['embed_s']) + 's')}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xs = [60, 120, 240, 480]
        plt.figure(figsize=(7, 4))
        plt.plot(xs, [r["MRR"] for r in rows], "o-", label="MRR@3")
        plt.plot(xs, [r["recall"] for r in rows], "s--", label="recall@3")
        plt.xlabel("chunk size (words)"); plt.ylabel("score"); plt.legend()
        plt.title("The chunk-size curve — precision vs dilution"); plt.tight_layout()
        out = pathlib.Path("lab1b_size_sweep.png").resolve()
        plt.savefig(out, dpi=140); plt.close()
        print(f"\n  {green('curve saved')} → {out}")
    except Exception:
        note("(matplotlib unavailable — bars above tell the story)")

    # ── YOUR TURN: dial a size and watch the score move. The sweep above is the map; this is the
    #    steering wheel — pick sizes (or type your own) and find the sweet spot yourself.
    #    (Auto-run / CI / Colab-non-tty skips straight past, so the lab stays runnable headless.)
    from mai_rag.tutor import TTY_IN
    if TTY_IN:
        print(f"\n  {bold('your turn')} — dial a chunk size and see it re-score live:")
        while True:
            pick = choice("chunk size to try (words)?",
                          {"30": "30 — tiny fragments", "90": "90", "180": "180 (a common default)",
                           "360": "360", "720": "720 — one vector per section",
                           "custom": "type my own…", "done": "done — on to the next dial"}, "done")
            if pick == "done":
                break
            if pick == "custom":
                raw = input("    size in words › ").strip()
                if not (raw.isdigit() and int(raw) >= 1):
                    note("give a whole number of words, e.g. 150."); continue
                pick = raw
            size = int(pick)
            with Spinner(f"chunk+embed+score @ {size} words"):
                r = score_config(f"fixed@{size}", "fixed", size, 0.0, quiet=True)
            rows.append(r)
            best = max(rows, key=lambda x: x["MRR"])
            tag = green("← best so far") if r is best else dim(f"(best is {best['_cfg']['size']}w @ MRR {best['MRR']:.3f})")
            print(f"  fixed@{size:<4} {sparkbar(r['MRR'])} MRR={r['MRR']:.3f}  recall={r['recall']:.2f}  "
                  f"{dim(str(r['chunks']) + ' chunks')}  {tag}")

    note("too small: fragments lose their meaning (and the doc explodes into chunks). Too big: one "
         "vector averages many topics — dilution. The sweet spot is a CURVE you measure, not a rule "
         "you memorize.")

def s3_strategy():
    print("  size ~180 words · MiniLM · k=3 — the strategy shootout:\n")
    for strat in STRATEGIES:
        with Spinner(f"{strat}: chunk+embed+score"):
            r = score_config(f"{strat}@180", strat, 180, 0.0, quiet=True)
        print(f"  {strat:<10} {dim(STRATEGIES[strat][:44]):<46}")
        print(f"             {sparkbar(r['MRR'])} MRR={r['MRR']:.3f}  recall={r['recall']:.2f}  {dim(str(r['chunks']) + ' chunks')}")
    show_leaderboard(6)
    note("same docs, same model, same golden set — only the BOUNDARIES moved. Sentence/structure "
         "chunking usually wins because a retrieved chunk arrives whole: no half-facts, and the "
         "heading travels with its body.")

def s4_overlap():
    print("  strategy fixed@120 · MiniLM · k=3 — does OVERLAP rescue cut facts?\n")
    base_chunks = None
    for ov in (0.0, 0.15, 0.30):
        with Spinner(f"overlap {int(ov*100)}%"):
            r = score_config(f"fixed@120+ov{int(ov*100)}", "fixed", 120, ov, quiet=True)
        if base_chunks is None:
            base_chunks = r["chunks"]
        growth = (r["chunks"] / base_chunks - 1) * 100
        print(f"  overlap {int(ov*100):>2}%  {sparkbar(r['MRR'])} MRR={r['MRR']:.3f}  recall={r['recall']:.2f}   {dim(f'index size {growth:+.0f}%')}")
    note("overlap is insurance against boundary cuts — paid for in index size and embed cost. If "
         "sentence-aware chunking already avoids the cuts, overlap buys much less. Compare stage 3.")

def s5_model():
    print("  best chunking so far · k=3 — swap the EMBEDDING MODEL:\n")
    for mk, (name, blurb) in MODELS.items():
        try:
            with Spinner(f"{name}: encode all chunks"):
                r = score_config(f"sentence@180·{mk}", "sentence", 180, 0.0, model_key=mk, quiet=True)
            print(f"  {mk:<8} {dim(blurb):<40}")
            print(f"           {sparkbar(r['MRR'])} MRR={r['MRR']:.3f}  recall={r['recall']:.2f}   {dim('encode ' + str(r['embed_s']) + 's')}")
        except Exception as e:
            note(f"{name} unavailable ({type(e).__name__}) — likely offline; the download is {blurb.split('·')[-1].strip()}. Skipping.")
    note("5× the parameters, 2× the dimensions, ~10× the download — measure whether the bigger model "
         "EARNS its cost on YOUR corpus. On easy corpora they tie; the gap opens on subtle "
         "distinctions (the support-tier siblings). Model choice is a dial, not dogma.")

def s6_topk():
    print("  sentence@180 · MiniLM — sweep k (the context budget), plus a threshold:\n")
    index = build_index("sentence", 180, 0.0, "minilm", False)
    for k in (1, 3, 5, 8):
        r = score_config(f"sentence@180·k={k}", "sentence", 180, 0.0, k=k, quiet=True)
        est_tokens = k * 180
        print(f"  k={k}   {sparkbar(r['recall'])} recall={r['recall']:.2f}  MRR={r['MRR']:.3f}   {dim(f'≈{est_tokens} prompt tokens of context')}")
    una = next((c for c in GOLDEN if "none" in c["support"].lower()), None)
    ans = next(c for c in GOLDEN if "none" not in c["support"].lower())
    if una:
        top_u = retrieve(index, una["q"], 1, "minilm")[0]
        top_a = retrieve(index, ans["q"], 1, "minilm")[0]
        print(f"\n  {bold('the threshold dial')} — top similarity per query:")
        print(f"    answerable   : {top_a[1]:.3f}  ({top_a[0]})")
        print(f"    unanswerable : {top_u[1]:.3f}  ({top_u[0]})  ← retrieval ALWAYS returns something")
        if top_a[1] > top_u[1]:
            print(f"    a cutoff between them (~{(top_u[1] + top_a[1]) / 2:.2f}) lets the system say “I don't know”")
        else:
            print(f"    {yellow('no clean gap on this pair')}: the unanswerable query scored ≥ the answerable one "
                  f"— a single cosine cutoff would misfire here (why a threshold needs calibrating, not guessing)")
    note("recall rises with k, but every extra chunk costs prompt tokens and adds noise the model "
         "must ignore. And a score THRESHOLD is the cheapest guardrail you'll ever ship: below it, "
         "don't answer.")

def s7_phrasing():
    base = next((c for c in GOLDEN if "hr-parental-leave" in c["support"]), GOLDEN[0])
    paras = [base["q"],
             "How long is paid leave for a primary caregiver?",
             "What's the parental leave allowance for new parents?",
             "wks of leave for caregivers??"]
    index = build_index("sentence", 180, 0.0, "minilm", False)
    print(f"  one fact, four phrasings — support doc: {dim(base['support'])}\n")
    for q in paras:
        got = [s for s, _ in retrieve(index, q, 3, "minilm")]
        wanted = [s.strip() for s in base["support"].split("+")]
        ranks = [i + 1 for i, g in enumerate(got) if g in wanted]
        mrr = 1.0 / ranks[0] if ranks else 0.0
        print(f"  {sparkbar(mrr)} MRR={mrr:.3f}   {dim(q[:64])}")
    r_off = score_config("sentence@180 (no title)", "sentence", 180, 0.0, quiet=True)
    r_on = score_config("sentence@180 + title", "sentence", 180, 0.0, title_prepend=True, quiet=True)
    print(f"\n  {bold('the title dial')} — prepend the doc title to every chunk before embedding:")
    print(f"    without title  {sparkbar(r_off['MRR'])} MRR={r_off['MRR']:.3f}")
    print(f"    with title     {sparkbar(r_on['MRR'])} MRR={r_on['MRR']:.3f}")
    note("embeddings are not robust to phrasing — the same fact scores differently per wording "
         "(Lab 3's HyDE attacks exactly this). And title-prepending is contextual retrieval in "
         "miniature: give each chunk a hint of where it came from, watch the number move.")

def s8_workbench():
    show_leaderboard(8)
    if not sys.stdin.isatty():
        note("workbench needs a keyboard — auto-running two preset combos instead.")
        score_config("preset: structure@240·k=5", "structure", 240, 0.0, k=5)
        score_config("preset: semantic@180+title", "semantic", 180, 0.0, title_prepend=True)
        show_leaderboard(8)
        return
    print(f"  {bold('free play')} — dial a config, score it, fight for the top. Empty answer = done.\n")
    while True:
        strat = choice("chunking strategy?", {k: f"{k} — {v}" for k, v in STRATEGIES.items()}, "sentence")
        size = choice("chunk size (words)?", {"90": "90", "180": "180", "300": "300", "480": "480"}, "180")
        model = choice("embedding model?", {k: f"{v[0]} ({v[1]})" for k, v in MODELS.items()}, "minilm")
        k = choice("top-k?", {"1": "1", "3": "3", "5": "5", "8": "8"}, "3")
        title = choice("prepend doc titles?", {"no": "no", "yes": "yes (contextual-in-miniature)"}, "no")
        label = f"you: {strat}@{size}·{model}·k={k}{'+title' if title == 'yes' else ''}"
        with Spinner(f"scoring {label}"):
            score_config(label, strat, int(size), 0.0, model_key=model, k=int(k),
                         title_prepend=(title == "yes"), quiet=True)
        show_leaderboard(8)
        again = choice("another run?", {"yes": "dial another config", "no": "done — wrap up"}, "yes")
        if again == "no":
            break
    best = sorted(LEADERBOARD, key=lambda r: (-r["MRR"], -r["recall"]))[0]
    print(f"  {green('your best config')}: {best['config']}  (MRR {best['MRR']:.3f}, recall {best['recall']:.2f})")
    note("that leaderboard IS the lab: foundation dials, honestly measured, visibly compared. "
         "Carry the winning config into Lab 2 — the fix ladder starts where these dials stop.")

TUTOR = Tutor(
    title="Lab 1b — RAG Foundations: The Dials",
    tagline="Modern AI Pro · AI Architect · Pillar I · the foundation variables",
    mission="""
    Every RAG pipeline is a stack of quiet decisions made before any 'technique' shows up:
    how you cut documents into chunks, how big, with what overlap, embedded by which model,
    retrieving how many, refusing when. Most teams inherit defaults and never look again.

    This lab puts every one of those dials in your hand. You twist one at a time, the SAME
    golden set re-scores, and the impact is drawn right in the terminal — bars, curves, and
    a running leaderboard. Everything is keyless (local embeddings, no LLM): pure retrieval
    physics, measured.
    """,
    stages=[
        Stage("Anatomy — raw docs, and what a chunk boundary does", """
            Load the 14 raw Hard Pack docs and chunk ONE of them three different ways. Same
            text, different boundaries — including watching a fixed-size window cut a fact
            in half mid-sentence. That half-fact is the original sin every later dial tries
            to manage.""", s1_anatomy, "0"),
        Stage("Chunk SIZE — the precision-vs-dilution curve", """
            Sweep 60 → 480 words with everything else pinned. Small chunks are precise but
            amnesiac; big chunks remember everything and match nothing sharply. Scores drawn
            as bars + the curve saved as a PNG. The sweet spot is measured, not memorized.""", s2_size, "0"),
        Stage("Chunking STRATEGY — where the boundaries fall", """
            Fixed windows vs whole sentences vs markdown structure vs semantic breakpoints
            (split where the meaning shifts — embeddings find the dips). Same size budget,
            only the boundaries move. The leaderboard starts filling.""", s3_strategy, "0"),
        Stage("OVERLAP — insurance against cut facts", """
            0% vs 15% vs 30% overlap on fixed windows: does re-covering the boundaries buy
            back what fixed chunking cut? And what does it cost in index size and embed
            time? Insurance has a premium.""", s4_overlap, "0"),
        Stage("The EMBEDDING MODEL — does bigger earn its keep?", """
            MiniLM (22M params, 384 dims) vs MPNet (110M, 768 dims, ~420MB download): same
            chunks, same golden set. Bigger is slower and heavier — the question is whether
            it separates the cases YOUR corpus actually confuses. Skips gracefully offline.""", s5_model, "0"),
        Stage("TOP-K and the THRESHOLD — budget and refusal", """
            Sweep k = 1/3/5/8: recall climbs, but every chunk costs prompt tokens and adds
            noise. Then the most underrated dial: a similarity threshold — retrieval always
            returns SOMETHING, and the cutoff is what lets a system say 'I don't know'.""", s6_topk, "0"),
        Stage("PHRASING sensitivity — and the title dial", """
            The same fact asked four ways scores four different MRRs — embeddings are not
            robust to wording (Lab 3's HyDE exists for this). Then one cheap fix: prepend
            each chunk's doc TITLE before embedding — contextual retrieval in miniature.""", s7_phrasing, "0"),
        Stage("The WORKBENCH — free play, one leaderboard", """
            Dial any combination — strategy × size × model × k × titles — score it, and
            fight for the top of the leaderboard. Your best config is the take-home, and
            it's the starting point Lab 2's fix ladder builds on.""", s8_workbench, "0"),
    ],
    outro="""
    Eight dials, one instrument, zero API keys. The foundation isn't glamorous, but you have
    now SEEN each variable move the number — which means in production you'll tune them by
    measurement, not folklore. Next: Lab 2 stacks the fixes (hybrid, metadata, rerank,
    contextual) on top of whatever your best config was.
    """,
)

def main():
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · fully keyless — no LLM, no token needed")

if __name__ == "__main__":
    main()
