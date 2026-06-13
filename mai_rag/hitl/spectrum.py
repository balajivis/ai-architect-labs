"""
mai_rag.hitl.spectrum — the autonomy spectrum + ledger (Lab 7 Move 1).

Sheridan's ten levels, compressed to the five working tiers the lessons use,
then folded to the three production ZONES:

    HITL  — human approves every action
    HOTL  — human monitors, can intervene
    HOOTL — human reviews aggregates after the fact

Autonomy is earned action-by-action; the PRD that says 'the agent operates
autonomously' has already lost. The gate lives at the action boundary, gated by
stakes × reversibility, never by the model's vibe.

This renders the autonomy LEDGER: action category → current tier → promote/demote
criteria, so the spectrum is a data structure, not a slide. Sourced from the MAS
hitl-design.tsx six-pattern set (not the four-pattern explainer).

WIP: the ledger TABLE renders; the earned-autonomy promote/demote AUTOMATION
(circuit-breaker, random-audit, two-key approval from hitl-design.tsx) is
described here in prose, code stubbed for a later pull.
"""
from __future__ import annotations

from .checkpoint import RISK_DESTRUCTIVE, RISK_READ, RISK_WRITE

# Sheridan (10) → 5 working tiers → 3 production zones.
SHERIDAN_TO_ZONE = [
    ("L1-2 · human does it / asks", "manual", "HITL"),
    ("L3-4 · agent suggests, human selects", "suggest", "HITL"),
    ("L5-6 · agent acts after approval", "approve", "HITL"),
    ("L7-8 · agent acts, then informs / can be vetoed", "monitor", "HOTL"),
    ("L9-10 · agent acts, human reviews aggregates", "autonomous", "HOOTL"),
]

# Default tier by structural risk — the stakes × reversibility heuristic.
RISK_TO_ZONE = {
    RISK_READ: "HOOTL",          # read-only: review aggregates
    RISK_WRITE: "HOTL",          # write: monitor, can intervene
    RISK_DESTRUCTIVE: "HITL",    # destructive: approve every one
}

# Tag (from the ACTION golden) → recommended zone.
TAG_TO_ZONE = {
    "safe-autonomous": "HOOTL",
    "needs-escalate": "HOTL",
    "needs-redact": "HITL",
    "needs-approval": "HITL",
}

PROMOTE_DEMOTE = {
    "HOOTL": "promote← when error-rate stays low over N audits; demote→ on any safety miss",
    "HOTL":  "promote← after a clean monitoring window; demote→ on a near-miss the human caught",
    "HITL":  "promote← only after sustained correct approvals; never auto-promote destructive tools",
}


def zone_for(*, risk: str | None = None, tag: str | None = None) -> str:
    """Place an action on the spectrum by structural risk and/or its tag. The
    MORE restrictive of the two wins (a destructive read-tag still lands HITL)."""
    order = {"HOOTL": 0, "HOTL": 1, "HITL": 2}
    zones = []
    if risk is not None:
        zones.append(RISK_TO_ZONE.get(risk, "HITL"))
    if tag is not None:
        zones.append(TAG_TO_ZONE.get(tag, "HITL"))
    if not zones:
        return "HITL"
    return max(zones, key=lambda z: order.get(z, 2))


def ledger(turns: list[dict]) -> list[dict]:
    """Build the autonomy ledger from ACTION-golden turns: one row per turn with
    its category, the zone it lands in, and the promote/demote criteria. `turns`
    are the load_action_golden() dicts (`tag` + `tool_risk`)."""
    rows = []
    for t in turns:
        zone = zone_for(risk=t.get("tool_risk"), tag=t.get("tag"))
        rows.append({
            "action": t.get("q", "")[:60],
            "tool_risk": t.get("tool_risk", ""),
            "tag": t.get("tag", ""),
            "zone": zone,
            "criteria": PROMOTE_DEMOTE.get(zone, ""),
        })
    return rows


def render_ledger(turns: list[dict]) -> str:
    """Plain-text autonomy ledger for the notebook (display()/print). Keeps viz
    thin — this is a table of strings, not a chart."""
    rows = ledger(turns)
    width = max((len(r["action"]) for r in rows), default=6)
    out = [f"{'action':<{width}}  {'risk':<11} {'tag':<16} {'zone':<6}  promote/demote",
           "-" * (width + 50)]
    for r in rows:
        out.append(f"{r['action']:<{width}}  {r['tool_risk']:<11} {r['tag']:<16} "
                   f"{r['zone']:<6}  {r['criteria']}")
    return "\n".join(out)


def render_spectrum() -> str:
    """The Sheridan → 5-tier → 3-zone mapping table (Move 1's spine)."""
    out = ["Sheridan level                              tier         zone", "-" * 60]
    for level, tier, zone in SHERIDAN_TO_ZONE:
        out.append(f"{level:<42}  {tier:<10}  {zone}")
    return "\n".join(out)
