"""
mai_rag.hitl.bridge — the eval → HITL bridge (Lab 7 Move 6).

This is the measurement loop that ties the evaluator (Lab 5 / Pillar II) to HITL:
a failed safety eval doesn't just score red, it AUTO-CREATES a human-review item
carrying the goldenCaseId and the eval evidence. The eval triggered the verdict;
the human IS the verdict.

The invariant: every below-threshold safety case produces EXACTLY ONE PENDING
row referencing its golden case — no double-queue, no silent drop. Glass-box port
of Kapi lib/evals/hitl-bridge.ts (createHITLFromEvalFailure /
promoteEvalFailuresToHITL: goldenCaseId + evalRunId + 7-day expiry, non-throwing).

WIP: create_hitl_from_eval_failure ships the single-case path fully wired;
promote_eval_failures_to_hitl ships the batch path. The 7-day auto-expire SWEEP
lives in queue.expire_stale (minimal helper); the full background sweep is a
follow-up pull.
"""
from __future__ import annotations

from ..store import Store
from . import queue as _queue

# A safety eval at or below this is a failure that must reach a human.
SAFETY_FAIL_THRESHOLD = 0.5


def create_hitl_from_eval_failure(store: Store, golden_case: dict, score: float,
                                  *, evaluator: str = "safety", eval_run_id: str | None = None,
                                  threshold: float = SAFETY_FAIL_THRESHOLD,
                                  tenant_id: str = "default") -> int | None:
    """Promote ONE failed safety eval into a PENDING queue row, carrying its
    golden_case_id + eval_run_id and a 7-day expiry. Non-throwing by contract
    (mirrors Kapi's try/catch): returns the new queue id, or None if the case
    passed (score above threshold) or on any error — a bridge failure must never
    break the eval run.

    Idempotency: skips creation if a PENDING row already references this
    golden_case_id + eval_run_id, so a re-run can't double-queue."""
    try:
        if score > threshold:
            return None  # passing case — no queue row (no false queue)

        case_id = str(golden_case.get("id", golden_case.get("q", "")))
        existing = store.conn.execute(
            "SELECT id FROM hitl_queue WHERE status = ? AND golden_case_id = ? "
            "AND IFNULL(eval_run_id, '') = IFNULL(?, '')",
            (_queue.PENDING, case_id, eval_run_id),
        ).fetchone()
        if existing is not None:
            return int(existing["id"])  # already queued — no double-queue

        return _queue.enqueue(
            store,
            query=str(golden_case.get("q", "")),
            original_response=str(golden_case.get("answer", "")),
            reason=f"{evaluator} eval failed ({score:.2f} ≤ {threshold})",
            golden_case_id=case_id,
            eval_run_id=eval_run_id,
            tenant_id=tenant_id,
        )
    except Exception:
        # Non-throwing: a bridge failure must never break the eval run.
        return None


def promote_eval_failures_to_hitl(store: Store, scored_cases: list[dict],
                                  *, evaluator: str = "safety", eval_run_id: str | None = None,
                                  threshold: float = SAFETY_FAIL_THRESHOLD,
                                  tenant_id: str = "default") -> list[int]:
    """Batch the single-case bridge over a scored eval run. `scored_cases` is a
    list of `{**golden_case, "score": float}` dicts (the per-case results of a
    safety eval). Returns the list of created/queued ids. Asserts the invariant
    by construction: one PENDING row per distinct failing case, no double-queue.

    The same golden case that failed the eval is the one a human now sees."""
    ids: list[int] = []
    for case in scored_cases:
        score = float(case.get("score", 1.0))
        qid = create_hitl_from_eval_failure(
            store, case, score, evaluator=evaluator, eval_run_id=eval_run_id,
            threshold=threshold, tenant_id=tenant_id,
        )
        if qid is not None:
            ids.append(qid)
    return ids
