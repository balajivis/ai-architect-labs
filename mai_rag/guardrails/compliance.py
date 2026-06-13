"""
mai_rag.guardrails.compliance — EU AI Act evidence (Lab 6 Move 7).

Compliance is not paperwork bolted on at the end; it's evidence PRODUCED BY the
evals. This module joins the latest in-notebook pass/fail dicts (from Moves 3-6,
NOT a persisted eval_run) to an Article map, and runs the governance canvas as a
RUNNABLE LLM-judged fixture so Move 7's risk-tier verdict is a printed output.

Mirrors Kapi lib/evals/criteria/compliance (eu-ai-act-transparency /
human-oversight) by behaviour, not by lifting code. Every classification here is
LLM-judged — NO regex (I-25).

WIP: covers Art 13/14/50 + a 5-question canvas only; GDPR/RTBF and the full
Annex-III high-risk checklist arrive with the Observability & Compliance module.
"""
from __future__ import annotations

import json
from pathlib import Path


def _load_data(name: str) -> dict:
    here = Path(__file__).resolve().parent.parent / "data" / name
    if not here.exists():
        alt = Path(__file__).resolve().parent.parent.parent / name
        here = alt if alt.exists() else here
    return json.loads(here.read_text(encoding="utf-8"))


def load_eu_ai_act_map() -> dict:
    """The Article → backing_eval → tier map (eu_ai_act_map.json)."""
    return _load_data("eu_ai_act_map.json")


def load_governance_canvas() -> dict:
    """The five governance questions + LLM-judge rubric (governance_canvas.json)."""
    return _load_data("governance_canvas.json")


def compliance_report(passed: dict[str, bool]) -> list[dict]:
    """Join the latest in-notebook pass/fail dict to the Article map. `passed`
    maps a backing_eval name → bool (e.g. {'output_safety': True, 'hitl_escalate':
    True, 'ai_disclosure': False}). Each Article is marked discharged only if its
    backing eval passed. Returns a list of rows ready to print as a scorecard."""
    amap = load_eu_ai_act_map()
    rows = []
    for art in amap.get("articles", []):
        backing = art.get("backing_eval", "")
        discharged = bool(passed.get(backing, False))
        rows.append({
            "article": art.get("article", ""),
            "title": art.get("title", ""),
            "backing_eval": backing,
            "discharged": discharged,
            "tier": art.get("tier", ""),
            "status": "🟢 discharged" if discharged else "🔴 undischarged",
        })
    return rows


def render_compliance_report(passed: dict[str, bool]) -> str:
    """Plain-text EU AI Act evidence sheet for the notebook."""
    rows = compliance_report(passed)
    out = [f"{'Article':<8} {'status':<16} {'backing eval':<16} title", "-" * 70]
    for r in rows:
        out.append(f"{r['article']:<8} {r['status']:<16} {r['backing_eval']:<16} {r['title']}")
    return "\n".join(out)


def run_governance_canvas(answers: dict[str, str]) -> dict:
    """Feed the student's five canvas answers to an LLM-judge that maps them to an
    EU AI Act risk tier. `answers` maps each question id → the student's answer.
    Returns {tier, reasoning}. LLM-judged, never a regex/keyword classifier."""
    from ..llm import complete_json
    canvas = load_governance_canvas()
    qmap = {q["id"]: q["prompt"] for q in canvas.get("questions", [])}
    filled = "\n".join(f"- {qmap.get(qid, qid)}\n  ANSWER: {ans}"
                       for qid, ans in answers.items())
    r = complete_json(
        "You are classifying an AI system into an EU AI Act risk tier using the "
        "governance-canvas answers below and the rubric.\n\n"
        f"RUBRIC:\n{canvas.get('rubric', '')}\n\n"
        f"ANSWERS:\n{filled}\n\n"
        "Keys: tier (one of unacceptable|high|limited|minimal), reasoning."
    )
    tier = str(r.get("tier", "")).strip().lower()
    if tier not in canvas.get("tiers", ["unacceptable", "high", "limited", "minimal"]):
        tier = "limited"  # safe default for an education-adjacent assistant
    return {"tier": tier, "reasoning": str(r.get("reasoning", ""))}
