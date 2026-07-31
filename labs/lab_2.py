# -*- coding: utf-8 -*-
"""Lab 2 — Retrieval, Measured (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · Module 2

Run it as a guided walkthrough:   python labs/lab_2.py
Piped / non-interactive input auto-runs every stage (CI-safe).

Goal: BEAT THE LAB 1 BASELINE. Four escalating retrieval fixes — hybrid, metadata,
rerank, contextual — proved on the same golden set, through one harness. A technique
earns its place only if it moves the scorecard.
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
from mai_rag.tutor import Tutor, Stage, Spinner, note, show_df, choice, dim, green

# ── shared state across stages (set lazily so any stage can be skipped) ──────
store = None
golden: list[dict] = []
USE_HARD_PACK = True
RETRIEVE_K = 3       # tight context budget — retrieval quality has to EARN a top-3 slot
RESULTS: dict[str, pd.DataFrame] = {}
ANS: dict[str, float] = {}

_bm25 = None         # built in the hybrid stage (or on demand)
_chunk_src: list = []
_chunk_txt: list = []
_status_of: dict = {}
_ce = None           # cross-encoder, loaded on demand (~80MB first download)


def ask(prompt, temperature=0.0):
    return llm.complete(prompt, tier="small", temperature=temperature)

def _json(raw):
    return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])

def tok(s):                                    # structural tokenization (NOT classification)
    return re.findall(r"\w+", s.lower())

def dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x); out.append(x)
    return out

# ── the measuring instrument (every technique goes through THIS) ─────────────
def retrieval_eval(search_fn, k=RETRIEVE_K):
    """Per-case MRR@k (headline) + recall@k (floor) + hit@1. Keyless — no LLM."""
    rows = []
    for c in golden:
        sup = c["support"]
        if "none" in sup.lower():
            rows.append({"question": c["q"][:34], "tag": c["tag"], "mrr": None,
                         "recall": None, "hit@1": None, "verdict": "n/a"})
            continue
        wanted = [s.strip() for s in sup.split("+")]
        got = [h.source for h in search_fn(c["q"], k)]
        recall = sum(w in got for w in wanted) / len(wanted)
        ranks = [i + 1 for i, g in enumerate(got) if g in wanted]
        mrr = 1.0 / ranks[0] if ranks else 0.0
        hit1 = 1.0 if (got and got[0] in wanted) else 0.0
        verdict = "OK" if hit1 == 1.0 else (
                  "RANKING (twin outranks)" if recall == 1.0 else "EMBEDDING (missed)")
        rows.append({"question": c["q"][:34], "tag": c["tag"], "mrr": round(mrr, 3),
                     "recall": recall, "hit@1": hit1, "verdict": verdict})
    return pd.DataFrame(rows)

def score(search_fn, label, k=RETRIEVE_K, quiet=False):
    df = retrieval_eval(search_fn, k)
    RESULTS[label] = df
    mrr = df["mrr"].dropna().mean(); r = df["recall"].dropna().mean(); h = df["hit@1"].dropna().mean()
    rank_f = df["verdict"].str.startswith("RANKING").sum()
    embed_f = df["verdict"].str.startswith("EMBEDDING").sum()
    if not quiet:
        print(f"  {label:30s} MRR@{k}={mrr:.3f}  recall@{k}={r:.2f}  hit@1={h:.2f}  | EMBED miss: {embed_f}  RANK fails: {rank_f}")
    return df

def naive_search(q, k=5):
    return store.search(q, k=k)

# lazy builders so stages stay skip-safe -------------------------------------
def ensure_bm25():
    global _bm25, _chunk_src, _chunk_txt
    if _bm25 is not None:
        return
    from rank_bm25 import BM25Okapi
    rows = store.conn.execute(
        "SELECT c.id, d.source, c.content FROM chunks c JOIN documents d ON d.id = c.document_id").fetchall()
    _chunk_src = [r[1] for r in rows]
    _chunk_txt = [r[2] for r in rows]
    with Spinner(f"building BM25 over {len(_chunk_txt)} chunks"):
        _bm25 = BM25Okapi([tok(t) for t in _chunk_txt])

def hybrid_search(q, k=5, K=60):
    ensure_bm25()
    from types import SimpleNamespace
    N = 20
    dense = dedupe([h.source for h in store.search(q, k=N)])
    sparse = dedupe([_chunk_src[i] for i in np.argsort(_bm25.get_scores(tok(q)))[::-1][:N * 3]])
    fused = {}
    for rank, d in enumerate(dense):  fused[d] = fused.get(d, 0) + 1.0 / (K + rank + 1)
    for rank, d in enumerate(sparse): fused[d] = fused.get(d, 0) + 1.0 / (K + rank + 1)
    ranked = sorted(fused, key=fused.get, reverse=True)[:k]
    return [SimpleNamespace(source=d) for d in ranked]

def ensure_status():
    global _status_of
    if not _status_of:
        _status_of = {s: ((json.loads(m) if m else {}) or {}).get("status", "active")
                      for s, m in store.conn.execute("SELECT source, metadata FROM documents")}

def filter_active(search_fn):
    """Composable: wrap ANY retriever, over-fetch, drop superseded docs, return top-k."""
    ensure_status()
    def wrapped(q, k=5):
        hits = search_fn(q, k * 4)
        return [h for h in hits if _status_of.get(h.source, "active") == "active"][:k]
    return wrapped

def ensure_ce():
    global _ce
    if _ce is None:
        from sentence_transformers import CrossEncoder
        with Spinner("loading cross-encoder (ms-marco-MiniLM, ~80MB on first use)"):
            _ce = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(search_fn, N=20):
    """Composable: over-fetch N candidates (with .content), score (q,passage) pairs together,
       re-order, dedupe chunks→docs. Base must be store-backed (carries passage text)."""
    def wrapped(q, k=5):
        ensure_ce()
        cands = search_fn(q, N)
        scores = _ce.predict([(q, h.content) for h in cands])
        ranked = [cands[i] for i in np.argsort(scores)[::-1]]
        seen, out = set(), []
        for h in ranked:
            if h.source not in seen:
                seen.add(h.source); out.append(h)
            if len(out) == k:
                break
        return out
    return wrapped

def doc_body(doc_id, n=2500):
    rows = store.conn.execute(
        "SELECT content FROM chunks WHERE document_id=(SELECT id FROM documents WHERE source=?) "
        "ORDER BY chunk_index", (doc_id,)).fetchall()
    return "\n".join(r[0] for r in rows)[:n]

def first_chunk(doc_id):
    row = store.conn.execute(
        "SELECT content FROM chunks WHERE document_id=(SELECT id FROM documents WHERE source=?) "
        "ORDER BY chunk_index LIMIT 1", (doc_id,)).fetchone()
    return row[0] if row else ""

def cos(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

# The SAME golden cases from Lab 1 — the through-line (used on the policy corpus).
POLICY_GOLDEN = [
    {"q": "How many weeks of paid parental leave do primary caregivers get?",
     "expected": "16 weeks at 100% salary (effective May 1, 2026 — up from the superseded 8-week policy).",
     "support": "hr-parental-leave-active", "tag": "recency"},
    {"q": "How often must employees rotate their account passwords?",
     "expected": "There is no forced periodic rotation — the current NIST-aligned IAM policy removed the legacy 90-day rotation rule.",
     "support": "identity-access-management-policy", "tag": "recency"},
    {"q": "Can I use SMS text codes as my MFA method for VPN access?",
     "expected": "No. SMS is not permitted under the current VPN Client Standard (it was allowed only under the superseded legacy policy).",
     "support": "itsec-vpn-client-standard", "tag": "recency"},
    {"q": "Is the Juniper Pulse VPN client still supported?",
     "expected": "No — Juniper Pulse is deprecated; migrate to Cisco AnyConnect (5.1+) or OpenVPN (2.6+).",
     "support": "itsec-vpn-client-standard", "tag": "recency"},
    {"q": "Malware is detected on an employee laptop — what incident severity is it, and how fast must it be escalated?",
     "expected": "Sev-2 (High): report to the Security Team immediately, with exec team + affected customers notified within 2 hours.",
     "support": "incident-response-runbook", "tag": "multi-hop"},
    {"q": "I want to buy a $60,000 tool from a single vendor — what bidding is required AND who must approve the spend?",
     "expected": "$25K–$99,999 requires 3 competitive quotes (a sole-vendor waiver needs VP Procurement approval); the purchase itself must be approved by CFO + VP Procurement.",
     "support": "fin-procurement-thresholds-competitive-bidding + fin-purchase-approval-matrix", "tag": "multi-hop"},
    {"q": "For a $30,000 purchase, how many competitive quotes are required?",
     "expected": "Three quotes (the $25,000–$99,999 band).",
     "support": "fin-procurement-thresholds-competitive-bidding", "tag": "precision"},
    {"q": "If both partners work at Northwind, how much parental leave does each receive?",
     "expected": "Each receives 16 weeks independently; the leave may overlap or be staggered.",
     "support": "hr-parental-leave-active", "tag": "precision"},
    {"q": "Is split tunneling allowed on the corporate VPN?",
     "expected": "No — full-tunnel is mandatory (no split tunneling) effective May 1, 2026.",
     "support": "itsec-vpn-client-standard", "tag": "recency"},
    {"q": "What was Northwind's total revenue in fiscal year 2025?",
     "expected": "Not stated in the corpus — the documents define the revenue-recognition method, not the actual figure. The model should say it doesn't have enough information.",
     "support": "(none — should decline)", "tag": "unanswerable"},
]

# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_setup():
    global store, USE_HARD_PACK
    pick = choice("Which corpus? (the flow is data-agnostic — same ladder, swap the data)", {
        "hard": "Hard Pack — small adversarial corpus, embeds live (~15s); recall<1.0 so every fix has room to win",
        "policy": "Policy corpus — 131 docs, pre-embedded (instant); recall is saturated, so only RANKING fixes show",
    }, default="hard")
    USE_HARD_PACK = pick == "hard"
    if USE_HARD_PACK:
        with Spinner("embedding the Hard Pack (keyless, local MiniLM)"):
            store = corpus.load_hard_corpus(rebuild=True)
        golden[:] = corpus.load_golden_hard()
    else:
        with Spinner("copying the pre-embedded policy corpus"):
            store = corpus.load_policy_corpus("policy.db")
        golden[:] = POLICY_GOLDEN
    s = store.stats()
    print(f"  {green('corpus ready')}: {s.get('documents')} docs · {s.get('chunks')} chunks · golden cases: {len(golden)}")
    tags = {t: sum(c['tag'] == t for c in golden) for t in sorted({c['tag'] for c in golden})}
    print("  cases by failure type: " + " · ".join(f"{k}={v}" for k, v in tags.items()))
    note("same kit as Lab 1 — keyless retrieval, and the golden set as the through-line.")

def s2_baseline():
    base = score(naive_search, "naive baseline")
    show_df(base, f"the harness — MRR@{RETRIEVE_K} (headline) · recall@{RETRIEVE_K} (floor) · hit@1 · verdict")
    fails = base[base["verdict"].str.startswith(("RANKING", "EMBEDDING"))]
    if len(fails):
        show_df(fails[["question", "tag", "verdict"]], "the cases Lab 2 exists to fix")
    note("MRR is the headline (rank-sensitive), recall is the floor (if the doc isn't in the top-k, "
         "no reranker can save it), hit@1 is the legible special case. This baseline is the number to beat.")

def s3_hybrid():
    ensure_bm25()
    q = "Is the Juniper Pulse VPN client still supported?"
    top = np.argsort(_bm25.get_scores(tok(q)))[::-1][:5]
    print(f"  BM25 top docs for the Juniper query: {dedupe([_chunk_src[i] for i in top])[:3]}\n")
    with Spinner("scoring naive vs hybrid on the golden set"):
        score(naive_search, "naive baseline", quiet=True)
        score(hybrid_search, "hybrid+rrf", quiet=True)
    score(naive_search, "naive baseline")
    score(hybrid_search, "hybrid+rrf")
    show_df(RESULTS["hybrid+rrf"][["question", "tag", "mrr", "hit@1", "verdict"]], "hybrid+rrf — which verdicts flipped?")
    note("honest expectation held? hybrid lifts keyword/multi-hop cases, but the recency twins share "
         "near-identical wording — BM25 can't tell them apart either. That gap is the next stage's job.")

def s4_metadata():
    ensure_status()
    print("  status counts:", pd.Series(_status_of).value_counts().to_dict())
    dropped = [s for s, st in _status_of.items() if st != "active"]
    print(f"  docs a WHERE status='active' drops: {dropped}\n")
    with Spinner("scoring the metadata filter (composed over naive AND hybrid)"):
        score(naive_search, "naive baseline", quiet=True)
        score(filter_active(naive_search), "naive + metadata", quiet=True)
        score(filter_active(hybrid_search), "hybrid + metadata", quiet=True)
    score(naive_search, "naive baseline")
    score(filter_active(naive_search), "naive + metadata")
    score(filter_active(hybrid_search), "hybrid + metadata")
    show_df(RESULTS["naive + metadata"][["question", "tag", "mrr", "hit@1", "verdict"]],
            "naive + metadata — did the recency twins flip to OK?")
    note("no model, no re-embed — a WHERE clause. The caveat: it's free only because ingestion "
         "captured `status`. When it didn't, you derive it — next stage.")

def s5_derive():
    ensure_status()
    superseded = [s for s, st in _status_of.items() if st != "active"]
    active_twins = [a for a in ["hr-parental-leave-active", "identity-access-management-policy",
                                "itsec-vpn-client-standard"] if a in _status_of]
    slice_docs = superseded + active_twins
    if not slice_docs:
        note("this corpus has no recency twins with a status field — nothing to derive. Skipping.")
        return
    def derive_status(doc_id):                 # classification → LLM, never a keyword rule
        p = ("Read this internal policy excerpt. Is it the CURRENTLY ACTIVE version, or a "
             "SUPERSEDED / legacy / archived one? Extract the effective date if stated.\n"
             'Reply JSON only: {"status": "active"|"superseded", "effective_date": "<YYYY-MM-DD|unknown>", "why": "<short>"}\n\n'
             + doc_body(doc_id))
        return _json(ask(p, temperature=0))
    with Spinner(f"deriving status for {len(slice_docs)} docs from their TEXT alone"):
        derived = {d: derive_status(d) for d in slice_docs}
    ddf = pd.DataFrame([{"doc": d[:44], "true": _status_of[d], "derived": derived[d]["status"],
                         "effective_date": derived[d].get("effective_date", "?"),
                         "match": _status_of[d] == derived[d]["status"]} for d in slice_docs])
    show_df(ddf, "LLM-derived status vs the ground truth we secretly held")
    print(f"  derivation accuracy: {ddf['match'].mean():.3f}\n")
    derived_map = {s: "active" for s in _status_of}
    for d in slice_docs:
        derived_map[d] = derived[d]["status"]
    def filter_on(mapping, search_fn=naive_search):
        def wrapped(q, k=5):
            return [h for h in search_fn(q, k * 4) if mapping.get(h.source, "active") == "active"][:k]
        return wrapped
    score(filter_active(naive_search), "metadata (given)")
    score(filter_on(derived_map), "metadata (derived)")
    note("if those two lines match, the field you EARNED with one LLM pass at ingestion is as good as "
         "the one the pipeline handed you. Deciding 'is this superseded?' is classification → always "
         "the LLM, never a keyword rule; extracting the date is structural → regex is fine.")

def s6_rerank():
    with Spinner("scoring the cost ladder (free → mid → stacked)"):
        score(naive_search, "naive baseline", quiet=True)
        score(filter_active(naive_search), "naive + metadata (free)", quiet=True)
        score(rerank(naive_search), "naive + rerank (mid)", quiet=True)
        score(rerank(filter_active(naive_search)), "metadata + rerank (stacked)", quiet=True)
    for lbl in ("naive baseline", "naive + metadata (free)", "naive + rerank (mid)", "metadata + rerank (stacked)"):
        print(f"  {lbl:30s} MRR@{RETRIEVE_K}={RESULTS[lbl]['mrr'].dropna().mean():.3f}  "
              f"hit@1={RESULTS[lbl]['hit@1'].dropna().mean():.2f}")
    show_df(RESULTS["naive + rerank (mid)"][["question", "tag", "mrr", "hit@1", "verdict"]],
            "naive + rerank — did the MODEL fix what the embeddings got wrong?")
    note("a cross-encoder reads query+passage TOGETHER — precise but slow, so production over-fetches "
         "cheap then reranks. Watch the recency rows: if the free metadata filter beat the paid "
         "reranker on the case that matters, that's the lesson about cost ladders.")

def s7_contextual():
    from mai_rag.store import embed
    def ev(t):
        return embed([t])[0]
    def contextualize(doc_id, chunk):
        p = (f"<document>\n{doc_body(doc_id, 2000)}\n</document>\n\n"
             f"Here is a chunk from that document:\n<chunk>\n{chunk}\n</chunk>\n\n"
             "In <=25 words, give context situating this chunk within the document — explicitly note "
             "whether the policy is CURRENT or SUPERSEDED and its effective date if stated. "
             "Reply with the context sentence only.")
        return ask(p, temperature=0).strip()
    act_id, sup_id = "hr-parental-leave-active", "hr-parental-leave-superseded"
    act_chunk, sup_chunk = first_chunk(act_id), first_chunk(sup_id)
    if act_chunk and sup_chunk:
        q = "How many weeks of paid parental leave do primary caregivers get?"
        qv = ev(q)
        naive_gap = cos(qv, ev(act_chunk)) - cos(qv, ev(sup_chunk))
        with Spinner("contextualizing the parental-leave twins (2 LLM calls)"):
            act_ctx = contextualize(act_id, act_chunk)
            sup_ctx = contextualize(sup_id, sup_chunk)
        print(f"  active  context: {act_ctx[:88]}")
        print(f"  super.  context: {sup_ctx[:88]}\n")
        ctx_gap = cos(qv, ev(act_ctx + "\n" + act_chunk)) - cos(qv, ev(sup_ctx + "\n" + sup_chunk))
        print("  sim(query, ACTIVE) − sim(query, SUPERSEDED)")
        print(f"    naive embeddings      : {naive_gap:+.4f}   (near 0 / negative = twins confusable)")
        print(f"    contextual embeddings : {ctx_gap:+.4f}   (larger positive = active pulls ahead)")
        print(f"    separation gained     : {ctx_gap - naive_gap:+.4f}\n")
    else:
        note("no parental-leave twin in this corpus — going straight to the mini-corpus proof.")
    # the tiny corpus where contextual OBVIOUSLY wins — same sentence, topic word only in the title
    mini = {
        "Health Insurance Plan":  "Members are reimbursed 80% of costs after the annual deductible is met.",
        "Dental Insurance Plan":  "Members are reimbursed 50% of costs after the annual deductible is met.",
        "Vision Insurance Plan":  "Members are reimbursed 70% of costs after the annual deductible is met.",
        "Prescription Drug Plan": "Members are reimbursed 90% of costs after the annual deductible is met.",
    }
    titles = list(mini); chunks = [mini[t] for t in titles]
    mini_gold = [("What share does the dental plan reimburse?", 1),
                 ("How much does the vision plan cover?", 2),
                 ("What is reimbursed under the prescription drug plan?", 3),
                 ("What does the health insurance plan reimburse?", 0)]
    def ctx_mini(title, chunk):
        p = (f"Document title: {title}\nChunk: {chunk}\n"
             "In <=12 words, name which plan this chunk describes. Context only.")
        return ask(p, temperature=0).strip()
    with Spinner("mini-corpus: embed naive vs contextual (4 LLM calls)"):
        Xn = embed(chunks)
        Xc = embed([ctx_mini(t, c) + "  " + c for t, c in zip(titles, chunks)])
    def top1(X, q):
        return int(np.argmax(X @ embed([q])[0]))
    rows = []
    for q, target in mini_gold:
        n, c = top1(Xn, q), top1(Xc, q)
        rows.append({"query": q[:42], "naive top-1": titles[n].split()[0], "naive ok": n == target,
                     "ctx top-1": titles[c].split()[0], "ctx ok": c == target})
    out = pd.DataFrame(rows)
    show_df(out, "four plans, identical sentences — the plan type lives ONLY in the title")
    print(f"  naive hit@1: {out['naive ok'].mean():.2f}   →   contextual hit@1: {out['ctx ok'].mean():.2f}")
    note("contextual retrieval fixes the EMBEDDINGS themselves — prepend LLM-written context, re-embed. "
         "The catch: one call per chunk + a full re-embed. Heaviest fix on the ladder; save it for when "
         "recall (not ranking) is the problem.")

def s8_umap():
    try:
        import umap
    except ImportError:
        note('umap not installed — run  pip install -e ".[viz]"  and redo this stage. Skipping.')
        return
    import matplotlib
    matplotlib.use("Agg")                       # never block the terminal on a GUI window
    import matplotlib.pyplot as plt
    from mai_rag.store import embed
    ensure_bm25()                               # reuse its chunk lists
    with Spinner(f"embedding {len(_chunk_txt)} chunks + UMAP to 2-D"):
        X = embed(_chunk_txt)
        reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric="cosine", random_state=42)
        XY = reducer.fit_transform(X)
        QXY = reducer.transform(embed([c["q"] for c in golden]))
    meta = {s: ((json.loads(m) if m else {}) or {}) for s, m in store.conn.execute("SELECT source, metadata FROM documents")}
    super_ids = {s for s in meta if meta[s].get("status", "active") != "active"}
    active_twin = {meta[s].get("superseded_by") for s in super_ids if meta[s].get("superseded_by")}
    src = np.array(_chunk_src)
    is_super = np.array([s in super_ids for s in src])
    is_active = np.array([s in active_twin for s in src])
    plt.figure(figsize=(9, 7))
    plt.scatter(XY[:, 0], XY[:, 1], s=5, c="lightgrey", label="all chunks")
    if is_active.any():
        plt.scatter(XY[is_active, 0], XY[is_active, 1], s=30, c="tab:green", label="active twin")
    if is_super.any():
        plt.scatter(XY[is_super, 0], XY[is_super, 1], s=30, c="tab:red", label="superseded twin")
    plt.scatter(QXY[:, 0], QXY[:, 1], s=160, marker="*", c="tab:blue",
                edgecolor="black", linewidth=0.5, label="golden queries")
    plt.legend(loc="best"); plt.title("Embedding neighborhood — active vs superseded twins sit together")
    plt.xlabel("UMAP-1"); plt.ylabel("UMAP-2"); plt.tight_layout()
    out = pathlib.Path("lab2_umap.png").resolve()
    plt.savefig(out, dpi=140); plt.close()
    print(f"  {green('map saved')} → {out}")
    note("open it: green (active) and red (superseded) chunks cluster TOGETHER — same meaning, "
         "different recency — with a blue query star between them. That picture IS the RANKING "
         "verdict from the baseline: dense retrieval has no way to prefer the active twin.")

def s9_finale():
    def rag_answer(search_fn, q, k=5):
        hits = search_fn(q, k)
        ctx = "\n\n".join(f"[{i+1}] ({h.source}) {h.content}" for i, h in enumerate(hits))
        p = ("Answer the question using ONLY the context. "
             "If it isn't there, say you don't have enough information.\n\n"
             f"Question: {q}\n\nContext:\n{ctx}\n\nAnswer:")
        return ask(p, temperature=0)
    def grade(q, answer, expected):
        p = ("Grade the ANSWER against EXPECTED. 1.0 fully correct, 0.5 partial, 0.0 wrong/missing.\n"
             'Reply JSON only: {"reason":"<short>","score":<1.0|0.5|0.0>}.\n\n'
             f"QUESTION: {q}\nEXPECTED: {expected}\nANSWER: {answer}")
        return _json(ask(p, temperature=0))["score"]
    ladder = [("naive baseline", naive_search),
              ("metadata", filter_active(naive_search)),
              ("metadata + rerank", rerank(filter_active(naive_search)))]
    for lbl, fn in ladder:
        with Spinner(f"answers via {lbl} ({len(golden)} cases × answer+judge)"):
            scores = []
            for c in golden:
                try:
                    scores.append(grade(c["q"], rag_answer(fn, c["q"]), c["expected"]))
                except (ValueError, KeyError):
                    pass                        # a malformed judge reply drops the case, not the run
        ANS[lbl] = float(np.mean(scores)) if scores else float("nan")
        print(f"  {lbl:26s} answer correctness: {ANS[lbl]:.3f}")
        score(fn, lbl, quiet=True)              # refresh retrieval numbers under matching labels
    final = pd.DataFrame({
        f"retrieval MRR@{RETRIEVE_K}": {k: round(RESULTS[k]["mrr"].dropna().mean(), 3) for k in ANS},
        "answer correctness": {k: round(ANS[k], 3) for k in ANS},
    })
    show_df(final.reset_index(names="technique"), "the one table that matters: retrieval quality → answer quality")
    note("read the right column against the baseline row: better retrieval only counts if it changes "
         "what the model SAYS. A technique earns its place only if this number moves — that's the "
         "whole lab, and the whole course.")

TUTOR = Tutor(
    title="Lab 2 — Retrieval, Measured",
    tagline="Modern AI Pro · AI Architect · Pillar I · Module 2",
    mission="""
    Lab 1 left you a baseline and a diagnosis: retrieval fetches the right docs but RANKS
    them wrong (the stale twin outranks the active policy), and misses some multi-hop docs
    entirely. Lab 2 is the fix ladder — four techniques at four price points: hybrid+RRF
    (cheap), metadata filtering (free), cross-encoder rerank (mid), contextual retrieval
    (heavy) — every one scored through the SAME harness on the SAME golden set.

    The arc to watch: three of the fixes attack the same recency bug, and the cheapest one
    wins it. A technique earns its place only if it moves the scorecard.
    """,
    stages=[
        Stage("Setup — pick the corpus, load the golden set", """
            Same kit as Lab 1. You choose the data: the small adversarial Hard Pack (embeds
            live, recall < 1.0, every fix has room to win) or the 131-doc policy corpus
            (instant, but saturated — only ranking fixes show). The flow is data-agnostic:
            same ladder, same harness, swap the corpus and everything re-scores.""", s1_setup, "0"),
        Stage("Baseline — the number to beat", """
            Retrieval measured DIRECTLY — keyless, deterministic, instant: MRR@k (the
            rank-sensitive headline), recall@k (the floor), hit@1 (the legible case). Each
            failing case gets a verdict — RANKING (right doc retrieved, wrong order) vs
            EMBEDDING (not retrieved at all) — because the fix for each is different.""", s2_baseline, "0"),
        Stage("Hybrid + RRF — dense ∪ sparse, fused", """
            Dense embeddings blur exact tokens — product names, versions, dollar amounts.
            BM25 nails them. Run both, fuse by Reciprocal Rank Fusion (Σ 1/(K+rank), K=60 —
            no score calibration, just rank orders). Honest expectation: lifts keyword and
            multi-hop cases; does NOT fix the recency twins.""", s3_hybrid, "0"),
        Stage("Metadata filtering — the free fix", """
            The recency landmine isn't a semantics problem, so no embedding trick fixes it.
            But ingestion captured a status field — so drop superseded docs with a WHERE
            clause. No model, no re-embed, composable over any retriever. Watch the RANKING
            verdicts flip.""", s4_metadata, "0"),
        Stage("When metadata isn't free — derive it", """
            That filter was free only because the pipeline captured `status`. Real corpora
            don't. So manufacture the field once, at ingestion, with an LLM: read each doc,
            emit status + effective date, validate against the ground truth we secretly
            hold. Rule check: 'is this superseded?' is classification → LLM. The date is
            structural → regex is fine.""", s5_derive, "~7"),
        Stage("Cross-encoder rerank — the mid-cost fix", """
            Dense and BM25 score query and doc separately — fast, approximate. A cross-
            encoder reads them TOGETHER — precise, slow. So production over-fetches top-N
            cheap and reranks to top-k. We stack it on naive and on metadata, and let the
            scorecard say whether the paid model beats the free WHERE clause.""", s6_rerank, "0"),
        Stage("Contextual retrieval — the heavy fix (+ a corpus where it wins)", """
            Fix the embeddings themselves: prepend a short LLM-written context to each chunk
            ('from the SUPERSEDED 2024 policy…'), then re-embed — the twins finally separate
            in vector space. Cost: one call per chunk + a full re-embed. We prove the twin
            separation live, then run a tiny engineered corpus where contextual goes from
            guessing to perfect in seconds.""", s7_contextual, "~6"),
        Stage("Seeing retrieval — the UMAP map", """
            You can't picture 384 dimensions; UMAP projects the chunks to 2-D preserving
            neighborhoods. The bug becomes visible: active and superseded twins land on top
            of each other with the golden queries between them. Saves lab2_umap.png —
            requires the [viz] extra; skips gracefully without it.""", s8_umap, "0"),
        Stage("The finale — do better retrievals mean better ANSWERS?", """
            Everything so far measured retrieval — a proxy. Close the loop: for each rung of
            the ladder, retrieve → generate → judge the answer against the golden expected.
            One table at the end: retrieval MRR next to answer correctness. Better retrieval
            only counts if it changes what the model says.""", s9_finale, "~72"),
    ],
    outro="""
    The scorecard is the take-home: the FREE fix (metadata) usually beats the paid ones on
    the case that matters, hybrid earns its keep on keywords, and contextual is waiting for
    a corpus where recall — not ranking — is the bottleneck. Next, Lab 3: agentic RAG —
    routing, HyDE, decomposition, and a web fallback, judged by the same harness.
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
