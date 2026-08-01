# -*- coding: utf-8 -*-
"""Lab 7b — Ship Audit-Ready: Trace, Cost, and Compliance (interactive CLI tutor)

Modern AI Pro · AI Architect · Pillar IV · Trust & Production · after Lab 6 (guardrails) & Lab 7 (HITL)

Run it as a guided walkthrough:   python labs/lab_7b.py
Piped / non-interactive input auto-runs every stage (CI-safe).

An auditor does not trust your dashboard — they REPLAY your evidence. "Ship audit-ready"
means every production request leaves a trace a stranger who distrusts you can reconstruct
years later: who, what, how much it cost, which controls were on, and what risk tier the
SYSTEM sits in — WITHOUT the trace itself becoming the breach.

  · TRACE     — one RAG→eval→HITL request, a span per hop: references + timings, never payloads
  · COST      — attribute the bill per stage; your eval suite is a line item, not free
  · EU AI ACT — classify the SYSTEM's purpose into a risk tier + obligations (LLM-judged, no keywords)
  · SOC2      — map the trace artifacts to Trust Service Criteria; evidence, not promises
  · GATE      — a request with an incomplete record FAILS the audit, the same way a regression fails the eval gate

Observability must be keyless and must never leak what it watches: the trace stores doc
IDs and token COUNTS, never the question, the answer, or a document body.
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

import pandas as pd

import mai_rag
from mai_rag import corpus, llm, obs
from mai_rag.evals import native
from mai_rag.evals.base import EvalInput
from mai_rag.hitl import checkpoint
from mai_rag.llm import complete_json
from mai_rag.tutor import (Tutor, Stage, Spinner, note, panel, show_df,
                           dim, green, yellow, bold, red)

# ── shared state (lazy so every stage is skip-safe) ──────────────────────────
store = None
GOLDEN: list[dict] = []
LAST_RECORD: dict = {}          # the audit record from the traced request, reused by later stages

_ANSWER_PROMPT = ("Answer the question using ONLY the context. If it isn't there, say you don't "
                  "have enough information.\n\nQuestion: {q}\n\nContext:\n{ctx}\n\nAnswer:")


def ensure_setup():
    global store, GOLDEN
    if store is not None:
        return
    with Spinner("embedding the catalog corpus (keyless, local MiniLM)"):
        store = corpus.load_catalog_corpus()
    GOLDEN[:] = corpus.load_golden_catalog()


def traced_request(q: str, tier: str = "small") -> tuple:
    """Run ONE real request — retrieve → generate → judge → HITL gate — with every hop wrapped
    in a span. Retrieval and the gate are keyless ($0, real latency); generation and the judge
    are the LLM line items. Returns (trace, answer, judge_score, decision)."""
    tr = obs.Trace()

    with tr.span("retrieve", tier="embed") as sp:          # local embeddings — keyless
        hits = store.search(q, k=4)
        sp["refs"] = [h.source for h in hits]              # doc IDs, NOT the doc text
        sp["tokens_in"] = obs.estimate_tokens(q)
        sp["note"] = f"{len(hits)} chunks"

    ctx = "\n\n".join(f"[{i + 1}] ({h.title}) {h.content}" for i, h in enumerate(hits))
    prompt = _ANSWER_PROMPT.format(q=q, ctx=ctx)
    with tr.span("generate", tier=tier) as sp:
        answer = llm.complete(prompt, tier=tier)
        sp["tokens_in"] = obs.estimate_tokens(prompt)
        sp["tokens_out"] = obs.estimate_tokens(answer)
        sp["refs"] = [h.source for h in hits]

    with tr.span("judge", tier=tier) as sp:                # the eval is a first-class, billed hop
        j = native.llm_judge(EvalInput(question=q, answer=answer, contexts=[h.content for h in hits]))
        sp["tokens_in"] = obs.estimate_tokens(q + answer)
        sp["tokens_out"] = obs.estimate_tokens(j.reasoning)
        sp["note"] = f"score={j.score:.2f}"

    with tr.span("hitl-gate", tier="none") as sp:          # structural + trigger — keyless Python
        d = checkpoint.checkpoint(
            checkpoint.Action(tool="answer", risk="read", text=answer, confidence=j.score),
            use_structural=True, use_triggers=True, use_safety=False, eval_score=j.score)
        sp["note"] = f"{d.action} ({d.gate})"

    # Record the state of every control AT REQUEST TIME — including when off.
    tr.record_control("auth", "disabled (lab-local, single-tenant)")
    tr.record_control("guardrails", "not-run (screened at draft, not here)")
    tr.record_control("hitl_gate", f"{d.action}/{d.gate}")
    tr.record_control("judge_version", f"native.llm_judge · {tier}")
    return tr, answer, j.score, d


# ── EU AI Act risk tier — classify the SYSTEM's purpose, LLM-judged (never keywords) ──
_AI_ACT_RUBRIC = (
    "You classify an AI SYSTEM into its EU AI Act risk tier from its DEPLOYMENT PURPOSE "
    "(the use case), not from any single message. Tiers:\n"
    "  prohibited — social scoring, manipulative or exploitative systems, untargeted "
    "biometric scraping (banned outright).\n"
    "  high-risk  — safety components or systems used for hiring/CV-screening, credit, "
    "education admissions/grading, essential services, law enforcement, biometric ID "
    "(allowed with conformity assessment, logging, human oversight, risk management).\n"
    "  limited    — systems that interact with people or generate content: chatbots, "
    "Q&A assistants, generators (transparency obligations — disclose it's AI, label output).\n"
    "  minimal    — spam filters, search ranking, most internal tooling (no specific obligation).\n"
    "Judge the PURPOSE by meaning. Reply JSON only: "
    '{"tier": "prohibited|high-risk|limited|minimal", "obligations": ["<short>", ...], "why": "<short>"}.'
)


def classify_ai_act(purpose: str) -> dict:
    try:
        r = complete_json(_AI_ACT_RUBRIC + f"\n\nDEPLOYMENT PURPOSE: {purpose}")
        return {"tier": str(r.get("tier", "?")),
                "obligations": r.get("obligations", []) if isinstance(r.get("obligations"), list) else [],
                "why": str(r.get("why", ""))}
    except (ValueError, KeyError):
        return {"tier": "?", "obligations": [], "why": "classifier reply did not parse"}


# ── SOC2 — which Trust Service Criteria does this trace's evidence support? (LLM-judged) ──
_SOC2_CONTROLS = [
    ("CC6.1", "Logical access — requests carry an authenticated, audience-scoped identity"),
    ("CC7.2", "System monitoring — every request emits a tamper-evident, payload-free audit record"),
    ("CC7.3", "Incident evidence — traces let you reconstruct who touched which resource, and the cost"),
    ("CC8.1", "Change management — a versioned judge + an eval gate block un-evaluated releases"),
    ("CC3.2", "Risk assessment — per-request eval scores + a human-in-the-loop gate on low confidence"),
]


def soc2_coverage(record: dict) -> list[dict]:
    """LLM-judge, per control, whether THIS trace record is evidence for it. Structural facts
    (the record's fields) are the input; the judgement 'does this evidence the control?' is the LLM's."""
    controls_txt = "\n".join(f"  {cid}: {desc}" for cid, desc in _SOC2_CONTROLS)
    try:
        r = complete_json(
            "For each SOC2 control, decide whether the AUDIT RECORD below is genuine evidence the "
            "control is operating (covered=true) or whether the record leaves it unproven (covered=false). "
            "Judge by what the record actually contains; do not credit a control the evidence doesn't show.\n\n"
            f"CONTROLS:\n{controls_txt}\n\nAUDIT RECORD:\n{json.dumps(record)[:1800]}\n\n"
            'Reply JSON only: {"controls": [{"id": "CC6.1", "covered": true|false, "evidence": "<short>"}, ...]}.')
        by_id = {str(c.get("id")): c for c in r.get("controls", []) if isinstance(c, dict)}
    except (ValueError, KeyError):
        by_id = {}
    out = []
    for cid, desc in _SOC2_CONTROLS:
        c = by_id.get(cid, {})
        out.append({"control": cid, "criterion": desc[:46],
                    "covered": bool(c.get("covered")), "evidence": str(c.get("evidence", "—"))[:44]})
    return out


# ── THE STAGES ───────────────────────────────────────────────────────────────
def s1_trace():
    ensure_setup()
    global LAST_RECORD
    q = next((c["q"] for c in GOLDEN if c["tag"] in ("site", "topic", "multi-hop")), GOLDEN[0]["q"])
    print(f"  tracing one request: {dim(q[:72])}\n")
    with Spinner("retrieve → generate → judge → HITL gate (2 LLM calls)"):
        tr, answer, score, d = traced_request(q)
    LAST_RECORD = tr.record()
    print(bold("  latency waterfall") + f"  ·  correlation_id {tr.correlation_id}")
    print(tr.waterfall())
    print(f"\n  total: {tr.total_ms:.0f}ms · ${tr.total_cost:.5f} · gate → {d.action}")
    panel("the AUDIT record you persist (payload-free — replay this, not the transcript)",
          json.dumps(tr.record(), indent=1)[:900])
    note("read what ISN'T there: no question text, no answer text, no document bodies — only doc IDs, "
         "token COUNTS, timings, and control-state. A debug log gets better when you paste the payload "
         "in; an audit log becomes a BREACH. Same request, two logs, opposite rules.")


def s2_cost():
    ensure_setup()
    if not LAST_RECORD:
        s1_trace()
    with Spinner("re-tracing to attribute the bill across stages"):
        tr, _a, _s, _d = traced_request(next(c["q"] for c in GOLDEN if c["tag"] in ("site", "topic", "multi-hop")))
    rows = [{"stage": n, "ms": round(ms), "cost_usd": round(c, 6), "pct_of_$": f"{pct:.0f}%"}
            for n, ms, c, pct in tr.cost_by_stage()]
    show_df(pd.DataFrame(rows), "cost attribution — where the request's money actually goes")
    gen = next((c for n, _m, c, _p in tr.cost_by_stage() if n == "generate"), 0.0)
    jud = next((c for n, _m, c, _p in tr.cost_by_stage() if n == "judge"), 0.0)
    print(f"\n  generate ${gen:.5f}   ·   judge ${jud:.5f}   "
          f"({green('the eval costs ~as much as the answer')})")
    note("retrieve and the HITL gate are $0 — keyless local work — but they still cost LATENCY, which "
         "the waterfall shows. The line that surprises teams on the invoice is the JUDGE: running evals "
         "in production is a real line item, not a free conscience. Attribute it, or it hides.")


def s3_ai_act():
    examples = [
        ("an internal assistant that answers employees' HR-policy questions from the handbook", "OURS"),
        ("an AI that screens and ranks job applicants' CVs to shortlist candidates for hiring", ""),
        ("a system that scores citizens' trustworthiness from their behaviour for access to services", ""),
        ("a spam filter that ranks incoming support email by priority", ""),
    ]
    rows = []
    with Spinner(f"classifying {len(examples)} deployment purposes into EU AI Act tiers"):
        for purpose, tag in examples:
            r = classify_ai_act(purpose)
            rows.append({"deployment purpose": (("★ " if tag else "") + purpose)[:52],
                         "EU AI Act tier": r["tier"],
                         "top obligation": (r["obligations"][0] if r["obligations"] else "—")[:40]})
    show_df(pd.DataFrame(rows), "classify the SYSTEM, not the message — tier drives the obligations")
    ours = classify_ai_act(examples[0][0])
    print(f"\n  {bold('★ our system')} (policy Q&A) → {green(ours['tier'])}: "
          f"{dim(', '.join(ours['obligations'][:3]) or ours['why'][:60])}")
    note("the tier is a property of the USE CASE, not the model or the prompt — the same LLM is minimal "
         "in a spam filter and high-risk in a hiring screen. That's why this is LLM-judged over the "
         "purpose, never a keyword match. High-risk pulls in exactly the logging + human-oversight + "
         "risk-management this pillar already built (Labs 5–7): the tier tells you which obligations bind.")


def s4_soc2():
    ensure_setup()
    if not LAST_RECORD:
        s1_trace()
    with Spinner("judging which SOC2 controls this trace's evidence supports"):
        cov = soc2_coverage(LAST_RECORD)
    rows = [{"control": c["control"], "criterion": c["criterion"],
             "covered": "✓" if c["covered"] else "gap", "evidence": c["evidence"]} for c in cov]
    show_df(pd.DataFrame(rows), "SOC2 coverage — the trace IS the evidence (or the gap is honest)")
    covered = sum(c["covered"] for c in cov)
    print(f"\n  {covered}/{len(cov)} Trust Service Criteria evidenced by this pipeline's artifacts.")
    note("evidence, not promises: a control is 'covered' only when the RECORD shows it operating — the "
         "audit trail evidences monitoring (CC7), the eval gate evidences change management (CC8), the "
         "HITL gate evidences risk assessment (CC3). Gaps (auth is lab-disabled here) are flagged, not "
         "faked — an auditor trusts the log that admits what's off far more than the one that claims green.")


def s5_gate():
    ensure_setup()
    if not LAST_RECORD:
        s1_trace()
    ok, missing = obs.audit_complete(LAST_RECORD)
    print(f"  audit gate on the real record → {green('🟢 COMPLETE') if ok else red('🔴 INCOMPLETE')}"
          + (f"  (missing: {missing})" if missing else ""))
    assert ok, f"a shipped request must leave a replayable record — missing {missing}"

    # Now prove the gate BITES: drop the references and re-check.
    crippled = json.loads(json.dumps(LAST_RECORD))
    for sp in crippled["spans"]:
        sp["refs"] = []
        sp["note"] = ""
    bad_ok, bad_missing = obs.audit_complete(crippled)
    print(f"  same request with the evidence stripped → "
          f"{green('🟢 COMPLETE') if bad_ok else red('🔴 INCOMPLETE')}  (missing: {bad_missing})")
    assert not bad_ok, "a record whose spans touched nothing traceable must FAIL the audit gate."
    print(f"\n  {bold('the audit gate')}: a request that can't be replayed doesn't ship — the same hard "
          f"rule as the eval gate (Lab 5), one pillar over. Wire it where you wire your tests.")
    note("this is the sentence the whole pillar earns: you don't PROMISE you're compliant, you EMIT the "
         "evidence, per request, and gate on it. Trace + cost + tier + control-state = an artifact an "
         "auditor replays without you in the room. That is what 'ship audit-ready' means.")


TUTOR = Tutor(
    title="Lab 7b — Ship Audit-Ready: Trace, Cost, and Compliance",
    tagline="Modern AI Pro · AI Architect · Pillar IV · observability, cost & compliance",
    mission="""
    The syllabus promises 'ship audit-ready: traces, cost attribution, EU AI Act tier
    classification, SOC2 controls.' This lab earns that sentence on ONE real request. You
    instrument a RAG→eval→HITL call span-by-span (references + timings, never payloads),
    attribute the bill across stages, classify the SYSTEM into its EU AI Act risk tier
    (LLM-judged, not keywords), map the trace to SOC2 criteria as evidence, and gate on a
    complete, replayable record — the same discipline as the eval gate, one pillar over.
    """,
    stages=[
        Stage("The trace — one request, every hop, no payloads", """
            Run a real retrieve→generate→judge→gate request with each hop wrapped in a span.
            Read the latency waterfall and the payload-free audit record: doc IDs and token
            counts, never the question, answer, or document text. An audit log that stores the
            payload isn't a log, it's a breach.""", s1_trace, "~2"),
        Stage("Cost — attribute the bill, find the eval line item", """
            Sum tokens×price per stage. Retrieve and the gate are $0 (keyless) but cost latency;
            the surprise on the invoice is the JUDGE — running evals in production costs about as
            much as the answer. Attribute it or it hides.""", s2_cost, "~2"),
        Stage("EU AI Act — classify the SYSTEM, not the message", """
            The risk tier is a property of the USE CASE: the same model is minimal in a spam filter
            and high-risk in a hiring screen. Classify four deployment purposes (and ours) into
            prohibited / high-risk / limited / minimal, LLM-judged over the purpose — never a
            keyword rule — and read the obligations each tier binds.""", s3_ai_act, "~5"),
        Stage("SOC2 — the trace as evidence, gaps kept honest", """
            Map this pipeline's artifacts to Trust Service Criteria: the audit trail evidences
            monitoring (CC7), the eval gate evidences change management (CC8), the HITL gate
            evidences risk assessment (CC3). A control is covered only when the RECORD shows it —
            lab-disabled auth is flagged as a gap, not faked green.""", s4_soc2, "~1"),
        Stage("The audit gate — replayable evidence or it doesn't ship", """
            Assert the record is complete and replayable, then strip its evidence and watch the
            gate BITE. A request that can't be reconstructed fails the audit the same way a
            regression fails the eval gate. You emit evidence and gate on it — you don't promise.
            """, s5_gate, "0"),
    ],
    outro="""
    Audit-ready is not a dashboard, it's a discipline: every request emits references + timings +
    cost + control-state + a risk tier, and a request that can't be replayed doesn't ship. That
    artifact — payload-free, per request, gated — is what an auditor (and a breach investigator, and
    finance) actually reads. Pillar IV, closed: guardrails BLOCK, HITL PAUSES, and this is how you
    PROVE both were operating.
    """,
)


def main():
    provider = "provider "
    try:
        provider += llm._provider()
    except Exception:
        provider += "NONE — set OPENAI_API_KEY (class token) in .env"
    TUTOR.run(provider_line=f"mai_rag {mai_rag.__version__} · {provider} · traces are keyless, judges billed")


if __name__ == "__main__":
    main()
