# -*- coding: utf-8 -*-
"""Lab 1 — Evaluation First (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar I · Module 1

Run it as a guided walkthrough:   python labs/lab_1.py
  · each MOVE explains itself, waits for you (Enter), runs, then shows status
  · Enter = run · s = skip · q = quit
Piped / non-interactive (e.g. `... | python labs/lab_1.py`) auto-runs every move.

The mission: before touching a retriever, build the INSTRUMENT that tells you whether
your RAG is any good — then baseline a naive RAG. That scorecard is the number every
later lab must beat. This is eval-driven development: define "good" first.
"""

# --- repo local-run shim: load .env, make Colab-only names work off-Colab ----
import os, pathlib, sys, textwrap, json, time, re

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

import mai_rag
from mai_rag import corpus, llm
import pandas as pd

# ── the shared tutor kit — same Tutor/Stage/Spinner/menu the other labs use, so the
#    intro screen, stage map, forgiving menu, and failure-recovery are uniform ──────────────
from mai_rag.tutor import Tutor, Stage, note, COLOR

# The move bodies below still use inline `C[...]` color spans; gate the dict on the kit's COLOR
# flag so it honors NO_COLOR / non-tty exactly like the kit's own green()/bold() helpers.
C = {"b": "\033[1m", "d": "\033[2m", "y": "\033[33m", "g": "\033[32m", "c": "\033[36m", "x": "\033[0m"} \
    if COLOR else {k: "" for k in "bdygcx"}

# ── Lab-1 primitives (the actual logic — importable + pokeable) ───────────────
store = None                      # set in Move 1
_rag_cache = {}                   # memoize naive_rag so we don't re-call the LLM every move

def ask(prompt, temperature=0.0):
    """One LLM chokepoint (mai_rag.llm) — provider from your env / the class token.
    Rate-limit retries + friendly key/proxy errors now live in mai_rag.llm.complete()."""
    return llm.complete(prompt, tier="small", temperature=temperature)

def naive_rag(query, k=5):
    """The simplest RAG: retrieve top-k → stuff context → answer. The thing every lab beats."""
    key = (query, k)                  # cache on (query, k) — a re-poke at a new k must not return stale contexts
    if key in _rag_cache:
        return _rag_cache[key]
    hits = store.search(query, k=k)
    context = "\n\n".join(f"[{i+1}] ({h.title}) {h.content}" for i, h in enumerate(hits))
    prompt = ("Answer the question using ONLY the context below. If the answer isn't there, "
              f"say you don't have enough information.\n\nQuestion: {query}\n\nContext:\n{context}\n\nAnswer:")
    out = {"answer": ask(prompt), "contexts": [h.content for h in hits]}
    _rag_cache[key] = out
    return out

# Golden set — HARD, grounded in the real docs. Built to break naive single-shot RAG:
# recency conflicts (active vs superseded), multi-hop (answer spans 2 docs), precise
# thresholds, and an unanswerable (must decline, not invent).
golden = [
    {"q": "How many weeks of paid parental leave do primary caregivers get?",
     "expected": "16 weeks at 100% salary (effective May 1, 2026 — up from the superseded 8-week policy).",
     "support": "hr-parental-leave-active", "tag": "recency"},
    {"q": "How often must employees rotate their account passwords?",
     "expected": "There is no forced periodic rotation — the current NIST-aligned IAM policy removed the legacy 90-day rule.",
     "support": "identity-access-management-policy", "tag": "recency"},
    {"q": "Can I use SMS text codes as my MFA method for VPN access?",
     "expected": "No. SMS is not permitted under the current VPN Client Standard (allowed only under the superseded legacy policy).",
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
     {"q": "What are the use cases for the Enterprise Tier and what is the criterion?",
     "expected": "Use case is: Multi-cloud data integration, compliance mandate. Enterprise contract value $100k-$500k+",
     "support": "cs-sales-playbook", "tag": "precision"},
    {"q": "If both partners work at Northwind, how much parental leave does each receive?",
     "expected": "Each receives 16 weeks independently; the leave may overlap or be staggered.",
     "support": "hr-parental-leave-active", "tag": "precision"},
    {"q": "Is split tunneling allowed on the corporate VPN?",
     "expected": "No — full-tunnel is mandatory (no split tunneling) effective May 1, 2026.",
     "support": "itsec-vpn-client-standard", "tag": "recency"},
    {"q": "What was Northwind's total revenue in fiscal year 2025?",
     "expected": "Not stated in the corpus — the docs define the revenue-recognition method, not the figure; the model should decline.",
     "support": "(none — should decline)", "tag": "unanswerable"},
    # ↓ a worked "blueprint tier" case (authored, multi-hop across two policies) — add your own like this
    {"q": "If an employee loses a laptop with customer data while travelling, what must they do and how is that data handled?",
     "expected": "Report to the Security Team promptly per the incident-response runbook, and handle the customer data at the level the Data Classification policy requires.",
     "support": "incident-response-runbook + data-classification-retention-policy", "tag": "multi-hop"},
]

def _json(raw):
    """Structural JSON extraction (permitted — parsing, not classification). Raises a clear
    ValueError on non-JSON so a weak model's prose reply is a caught error, not a raw traceback."""
    m = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if not m:
        raise ValueError(f"model did not return JSON: {(raw or '')[:120]!r}")
    return json.loads(m.group(0))

def llm_judge(q, answer, expected):          # holistic correctness (the naive judge)
    p = ('Grade the ANSWER against EXPECTED for the QUESTION. Reply JSON only: '
         '{"score": <0..1>, "reason": "<short>"}.\n\n'
         f'QUESTION: {q}\nEXPECTED: {expected}\nANSWER: {answer}')
    return _json(ask(p))

def faithfulness(answer, contexts):          # holistic faithfulness (the naive judge)
    ctx = "\n\n".join(contexts)
    p = ('Is every claim in the ANSWER supported by the CONTEXT? Reply JSON only: '
         '{"score": <0..1>, "reason": "<short>"} (1=grounded, 0=hallucinated).\n\n'
         f'CONTEXT:\n{ctx}\n\nANSWER: {answer}')
    return _json(ask(p))

def grade(q, answer, expected):              # sturdier: anchored rubric, reason-first
    p = ("You are grading a RAG answer. Give a one-sentence reason, THEN a score.\n"
         "Scale: 1.0 fully correct - 0.5 partial/incomplete - 0.0 wrong/missing.\n"
         'Reply JSON only: {"reason": "<one sentence>", "score": <1.0|0.5|0.0>}.\n\n'
         f"QUESTION: {q}\nEXPECTED: {expected}\nANSWER: {answer}")
    return _json(ask(p))

def faithfulness_claims(answer, contexts):   # sturdier: claim-decomposition, not holistic
    ctx = "\n\n".join(contexts)
    p = ("Break the ANSWER into distinct factual claims; for each decide if the CONTEXT supports it. "
         "score = supported/total (1.0 for a refusal like 'not enough information').\n"
         'Reply JSON only: {"reason": "<n claims, m supported>", "score": <0..1>}.\n\n'
         f"CONTEXT:\n{ctx}\n\nANSWER: {answer}")
    return _json(ask(p))

def retrieval_metrics(q, support, k=5):      # NO LLM — isolates the embeddings
    if "none" in support.lower():
        return {"recall": None, "hit@1": None}
    wanted = [s.strip() for s in support.split("+")]
    got = [h.source for h in store.search(q, k=k)]
    return {"recall": sum(w in got for w in wanted) / len(wanted),
            "hit@1": 1.0 if (got and got[0] in wanted) else 0.0}

def completeness(answer, expected):
    p = ("Does the ANSWER cover ALL the points in the EXPECTED answer? "
         "score = fraction covered (1.0 all, 0.0 none). "
         'Reply JSON only: {"reason": "<covered/missing>", "score": <0..1>}.\n\n'
         f"EXPECTED: {expected}\nANSWER: {answer}")
    return _json(ask(p))

def search_docs(keyword):
    return pd.read_sql("SELECT id, title, source FROM documents WHERE title LIKE ? OR source LIKE ?",
                       store.conn, params=(f"%{keyword}%", f"%{keyword}%"))

def read_doc(doc_id):
    d = store.conn.execute("SELECT title, source FROM documents WHERE id=?", (doc_id,)).fetchone()
    body = store.conn.execute("SELECT content FROM chunks WHERE document_id=? ORDER BY chunk_index", (doc_id,)).fetchall()
    print(f"  {d['title']}  ·  {d['source']}\n  {'─'*60}")
    print(textwrap.indent("\n".join(r["content"] for r in body), "  "))

# ── the MOVES (each: run + print status; teaching sits in STEPS below) ─────────
def m1_corpus():
    global store
    store = corpus.load_policy_corpus("policy.db")   # copies the pre-embedded DB (first run pulls MiniLM ~90MB)
    s = store.stats()
    print(f"  {C['g']}corpus loaded{C['x']}: {s.get('documents')} documents · {s.get('chunks')} chunks (keyless — local embeddings)")
    docs = pd.read_sql("SELECT source FROM documents", store.conn)
    depts = docs["source"].str.split("-").str[0].value_counts().head(6)
    print("\n  docs by area:            " + "  ".join(f"{k}:{v}" for k, v in depts.items()))
    ch = pd.read_sql("SELECT token_count FROM chunks", store.conn)["token_count"].describe()
    print(f"  chunk size (tokens):     mean {ch['mean']:.0f} · median {ch['50%']:.0f} · max {ch['max']:.0f}")
    print(f"\n  {C['b']}retrieval demo{C['x']} — 'How much parental leave do I get?' (top 5):")
    for h in store.search("How much parental leave do I get?", k=5):
        print(f"    {h.score:.3f}  {h.title}")
    note("notice: the ACTIVE and the SUPERSEDED parental-leave doc both show up — that's the trap.")

def m2_naive_rag():
    q = "How much parental leave do I get?"
    print(f"  asking the naive RAG:  {C['b']}{q}{C['x']}\n")
    print(textwrap.indent(textwrap.fill(naive_rag(q)["answer"], 84), "  "))
    note("reads fine on ONE question — but 'reads fine' is a vibe, not a measurement. That's the whole problem.")

def m3_golden():
    tags = {t: sum(c["tag"] == t for c in golden) for t in sorted({c["tag"] for c in golden})}
    print(f"  {C['g']}{len(golden)} golden cases{C['x']} — by failure type: " + " · ".join(f"{k}={v}" for k, v in tags.items()))
    print("\n  three that are built to break a naive RAG:")
    for c in [golden[0], golden[5], golden[9]]:
        print(f"    {C['y']}[{c['tag']}]{C['x']} {c['q']}")
        print(f"        expected: {textwrap.shorten(c['expected'], 92)}")
        print(f"        supports: {c['support']}")
    note("each case = a precise question + a known-good answer + the doc(s) that support it. Authoring these is THE skill.")

def _score_table(fn_rows, header):
    rows = fn_rows()
    df = pd.DataFrame(rows)
    pd.set_option("display.max_colwidth", 52); pd.set_option("display.width", 200)
    print(textwrap.indent(df.to_string(index=False), "  "))
    return df

def m4_naive_judge():
    print(f"  {C['d']}scoring {len(golden)} cases × (correctness + faithfulness) — ~{len(golden)*2} LLM calls, please wait…{C['x']}\n")
    def rows():
        r = []
        for c in golden:
            out = naive_rag(c["q"])
            r.append({"question": c["q"][:42], "tag": c["tag"],
                      "correct": llm_judge(c["q"], out["answer"], c["expected"])["score"],
                      "faithful": faithfulness(out["answer"], out["contexts"])["score"]})
        return r
    df = _score_table(rows, None)
    print(f"\n  {C['b']}BASELINE (naive judge){C['x']}: " +
          str(df[["correct", "faithful"]].mean(numeric_only=True).round(3).to_dict()))
    note("you have a number. But look how many faithfulness scores are a suspiciously round 1.0…")

def m5_sturdy_judge():
    print(f"  {C['d']}re-scoring the SAME answers with a claim-based, reason-first judge — ~{len(golden)*2} LLM calls…{C['x']}\n")
    def rows():
        r = []
        for c in golden:
            out = naive_rag(c["q"])          # cached → literally the same answers as Move 4
            g = grade(c["q"], out["answer"], c["expected"])
            f = faithfulness_claims(out["answer"], out["contexts"])
            r.append({"question": c["q"][:34], "tag": c["tag"], "correct": g["score"],
                      "why_correct": g["reason"][:46], "faithful": f["score"], "why_faithful": f["reason"][:40]})
        return r
    df = _score_table(rows, None)
    print(f"\n  {C['b']}BASELINE (sturdier judge){C['x']}: " +
          str(df[["correct", "faithful"]].mean().round(3).to_dict()))
    note("same answers, more honest AND auditable scores — every number now has a reason. THIS noticing is the lesson.")

def m6_whose_fault():
    print(f"  Stage 1 — RETRIEVAL accuracy ({C['g']}no LLM{C['x']}, just the embeddings):\n")
    rdf = pd.DataFrame([{"question": c["q"][:34], "tag": c["tag"], **retrieval_metrics(c["q"], c["support"])} for c in golden])
    print(textwrap.indent(rdf.to_string(index=False), "  "))
    print(f"\n  recall@5 = {rdf['recall'].dropna().mean():.3f}  ·  hit@1 = {rdf['hit@1'].dropna().mean():.3f}")
    print(f"\n  {C['d']}Stage 2 — completeness + verdict (~{len(golden)} LLM calls)…{C['x']}\n")
    rows = []
    for c in golden:
        out = naive_rag(c["q"]); rm = retrieval_metrics(c["q"], c["support"])
        comp = completeness(out["answer"], c["expected"])["score"]
        if rm["recall"] is None:
            # "did the model refuse?" is a classification → LLM-judge it, never a keyword list (course rule)
            try:
                declined = bool(_json(ask(
                    'Did the ANSWER decline to answer — i.e. it says the information is not '
                    'available / not in the documents — rather than giving a factual answer? '
                    'Reply JSON only: {"declined": true|false}.\n\nANSWER: ' + out["answer"]))["declined"])
            except (ValueError, KeyError):
                declined = False
            diag = "OK (declined)" if declined else "LLM — hallucinated"
        elif rm["recall"] < 1.0: diag = "EMBEDDING — doc not retrieved"
        elif comp < 0.75:        diag = "LLM — had docs, answer off"
        else:                    diag = "OK"
        rows.append({"question": c["q"][:30], "tag": c["tag"], "recall": rm["recall"], "complete": comp, "diagnosis": diag})
    ddf = pd.DataFrame(rows)
    print(textwrap.indent(ddf.to_string(index=False), "  "))
    print(f"\n  {C['b']}WHERE IT BREAKS{C['x']}: {ddf['diagnosis'].value_counts().to_dict()}")
    note("now each failure has a verdict — so you know whether Lab 2 must fix RETRIEVAL or GENERATION.")

def m7_read_docs():
    print("  search_docs('leave') — find the real source:\n")
    print(textwrap.indent(search_docs("leave").to_string(index=False), "  "))
    first = search_docs("leave")
    if len(first):
        did = int(first.iloc[0]["id"])
        print(f"\n  read_doc({did}) — the actual policy text (re-ground your `expected` against THIS):\n")
        read_doc(did)
    note("we graded against remembered answers. A golden set you don't re-ground in the source rots — treat it as living code.")

STEPS = [
    ("Look at the corpus (no LLM yet)",
     "Eval-first means: before you touch a retriever, know your data and set up the measuring "
     "instrument. Our corpus is a fictional company, Northwind — 131 policy docs engineered to "
     "break naive RAG (superseded-vs-active twins, multi-hop facts, an unanswerable). Retrieval is "
     "keyless — embeddings run locally.", m1_corpus),
    ("Build a naive RAG and ask it one thing",
     "The simplest possible system: retrieve the top-5 chunks, stuff them into the prompt, answer. "
     "This is the baseline every later technique (hybrid, rerank, agentic) has to beat. First we "
     "just eyeball one answer — the way most teams 'evaluate'.", m2_naive_rag),
    ("Meet the golden set (no LLM)",
     "An evaluator is only as good as the cases you point it at. Ours are deliberately hard and "
     "grounded in the real docs. The transferable skill is authoring your OWN — a precise question, "
     "a known-good answer, and the supporting doc.", m3_golden),
    ("Score it — the naive judge → first baseline",
     "Now define 'good' as two numbers: correctness (an LLM grades the answer vs expected) and "
     "faithfulness (is every claim grounded in the retrieved context?). We score the whole golden "
     "set. Slow — it's real LLM calls.", m4_naive_judge),
    ("The judge IS the lesson → make it sturdier",
     "That first baseline isn't trustworthy: one holistic 'is it grounded?' call rubber-stamps ~1.0, "
     "the scores are round and unauditable. Rebuild it: decompose the answer into claims, use an "
     "anchored rubric, and KEEP the reason. Same model, same answers — honest scores.", m5_sturdy_judge),
    ("Whose fault — retriever or generator?",
     "End-to-end 'correctness' hides WHERE the pipeline broke. Split it: retrieval accuracy "
     "(recall@k / hit@1 vs the supporting doc — no LLM) crossed with completeness. Low recall ⇒ an "
     "embedding problem no prompt can fix; high recall + low completeness ⇒ a generation problem.", m6_whose_fault),
    ("Read the real docs — don't grade against guesses",
     "We wrote those expected answers from memory. If we never opened the source, the baseline is "
     "built on guesses. Browse the corpus, read the real policy, re-ground each case.", m7_read_docs),
]

# rough LLM-call estimate per step, shown on the stage map (13 golden cases → ~26 for a 2-judge pass)
_CALLS = ["0", "~1", "0", "~26", "~26", "~13", "~1"]

TUTOR = Tutor(
    title="Lab 1 — Evaluation First: The Number to Beat",
    tagline="Modern AI Pro · AI Architect · Pillar II · Evals & Benchmarks",
    mission="""
    Eval-first means defining 'good' as NUMBERS before you tune anything. You load a corpus
    engineered to break naive RAG (Northwind — superseded-vs-active twins, multi-hop facts, an
    unanswerable), build the simplest retrieve→stuff→answer baseline, author a golden set, and
    score it. Then you turn the instrument on itself — a holistic judge rubber-stamps ~1.0, so
    you rebuild it claim-by-claim — and split retrieval-vs-generation blame. The scorecard you
    leave with is the number every later lab (hybrid, rerank, agentic) has to beat.
    """,
    stages=[Stage(title, teach, run, calls)
            for (title, teach, run), calls in zip(STEPS, _CALLS)],
    outro="""
    That baseline is the number to beat — Lab 2 adds hybrid search + reranking, and the only
    thing that counts as success is moving these exact numbers. "We tested it" is a vibe; the
    eval suite is the documentation.
    """,
)


def main():
    provider = "provider "
    try:
        provider += llm._provider()
    except Exception:
        provider += "NONE — set OPENAI_API_KEY (class token) in .env"
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · {provider} · eval-first: the number to beat")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
