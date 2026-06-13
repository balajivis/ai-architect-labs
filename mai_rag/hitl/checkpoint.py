"""
mai_rag.hitl.checkpoint — the action-boundary gate (Lab 7 Move 1-4).

Autonomy is earned action-by-action: the gate lives at the ACTION boundary,
gated by stakes × reversibility, never by the model's vibe. Every tool call
passes through one `checkpoint(action)` chokepoint before execution.

The gate returns one of four actions, mirroring Kapi lib/hitl/evaluate.ts
HITLEvaluationResult:

    proceed | modify | block | queue

It composes three layers, cheapest first:

  1. STRUCTURAL risk tag (Move 2, free) — a per-tool `risk ∈ read|write|
     destructive` DECLARED at design time. read→proceed, write→proceed+audit,
     destructive→block. The tag is structural metadata (the turn's `tool_risk`
     enum), legitimately NOT a content classification — so reading it is allowed
     under the no-regex rule.
  2. DYNAMIC triggers (Move 3, mid-cost) — escalate(queue) when confidence < 0.7
     OR a safety eval < 0.8. LLM self-confidence is not accuracy, so the
     thresholds are tuned empirically against the golden set.
  3. SAFETY gates (Move 4, non-optional) — mai_rag.evals.safety pii_exposure /
     harmful_intent fire below threshold and FORCE review even in autonomous
     mode: PII → modify(redact), harm/jailbreak → block. These can never be
     configured to zero recall (asserted in Move 4).

WIP: Move 1 ships `checkpoint()` as a PASS-THROUGH STUB (returns proceed for all)
so the autonomy ledger can be drawn first; the risk-tag gate, trigger gate, and
safety gate fill in across Moves 2-4. The flags below let each move turn its
layer on without rewriting the function.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PROCEED, MODIFY, BLOCK, QUEUE = "proceed", "modify", "block", "queue"

# Stakes × reversibility → autonomy zone, for the spectrum ledger.
RISK_READ, RISK_WRITE, RISK_DESTRUCTIVE = "read", "write", "destructive"

CONFIDENCE_FLOOR = 0.7          # Move 3 default; tuned empirically in the sweep
EVAL_FLOOR = 0.8               # Move 3 default
SAFETY_FLOOR = 0.5            # Move 4: system-default safety gates fire below this


@dataclass
class Action:
    """One tool call as it reaches the gate. `risk` is the declared structural
    enum (read|write|destructive); `args` are the tool arguments; `confidence`
    and `text` (the drafted output, if any) feed the dynamic + safety layers."""
    tool: str
    risk: str = RISK_READ
    args: dict[str, Any] = field(default_factory=dict)
    confidence: float | None = None
    text: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    action: str                # proceed | modify | block | queue
    reason: str
    gate: str                  # which layer fired: structural | trigger | safety | none


def _structural(action: Action) -> Decision | None:
    """Move 2 — the free structural gate. read→proceed, write→proceed+audit,
    destructive→ALWAYS block (overrides any per-step autonomy level)."""
    if action.risk == RISK_DESTRUCTIVE:
        return Decision(BLOCK, "destructive tool — structural gate always blocks", "structural")
    return None  # read/write fall through; write is audited by the caller


def _triggers(action: Action, *, confidence_floor: float = CONFIDENCE_FLOOR,
              eval_score: float | None = None, eval_floor: float = EVAL_FLOOR) -> Decision | None:
    """Move 3 — dynamic triggers. Escalate(queue) on low confidence or a low
    safety/relevance eval. Thresholds are tuned against the golden set."""
    if action.confidence is not None and action.confidence < confidence_floor:
        return Decision(QUEUE, f"confidence {action.confidence:.2f} < {confidence_floor} — escalate", "trigger")
    if eval_score is not None and eval_score < eval_floor:
        return Decision(QUEUE, f"eval score {eval_score:.2f} < {eval_floor} — escalate", "trigger")
    return None


def _safety(action: Action, *, safety_floor: float = SAFETY_FLOOR) -> Decision | None:
    """Move 4 — non-optional safety gates, LLM-judged (mai_rag.evals.safety),
    firing EVEN in autonomous mode. PII → modify(redact), harm/jailbreak → block.
    No regex floor (I-25). Only runs when there is drafted `text` to screen."""
    if not action.text:
        return None
    from ..evals import safety as _safety_engine
    from ..evals.base import EvalInput
    e = EvalInput(question=action.tool, answer=action.text, contexts=[])
    harm = _safety_engine.harmful_intent(e)
    if harm.score < safety_floor:
        return Decision(BLOCK, f"safety: harmful content ({harm.reasoning})", "safety")
    pii = _safety_engine.pii_exposure(e)
    if pii.score < safety_floor:
        return Decision(MODIFY, f"safety: PII present → redact ({pii.reasoning})", "safety")
    return None


def checkpoint(action: Action, *, use_structural: bool = True, use_triggers: bool = True,
               use_safety: bool = True, eval_score: float | None = None,
               confidence_floor: float = CONFIDENCE_FLOOR, eval_floor: float = EVAL_FLOOR,
               safety_floor: float = SAFETY_FLOOR) -> Decision:
    """The single chokepoint every tool call passes through before execution.

    Returns a Decision(action ∈ proceed|modify|block|queue). The three layers are
    composed safety-LAST so a safety violation overrides a structural 'proceed'
    even in autonomous mode. Each `use_*` flag lets a move enable its layer
    incrementally (Move 1 calls with all three False → pure pass-through stub).

    WIP: with all use_* flags False this is the Move-1 pass-through stub
    (returns proceed for everything). Moves 2-4 flip them on."""
    # Safety is non-optional and evaluated first so it can override structural
    # proceed — but a destructive structural block still wins if both fire.
    if use_safety:
        d = _safety(action, safety_floor=safety_floor)
        if d is not None:
            return d
    if use_structural:
        d = _structural(action)
        if d is not None:
            return d
    if use_triggers:
        d = _triggers(action, confidence_floor=confidence_floor,
                      eval_score=eval_score, eval_floor=eval_floor)
        if d is not None:
            return d

    reason = "proceed (pass-through stub)" if not (use_structural or use_triggers or use_safety) \
        else ("write — proceed + audit" if action.risk == RISK_WRITE else "read — proceed")
    return Decision(PROCEED, reason, "none")
