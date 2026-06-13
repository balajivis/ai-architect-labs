"""
mai_rag.hitl — the Human-in-the-Loop gate (Lab 7 · Pillar IV Module 3).

The first labs let the agent ANSWER; this package lets it ACT — and asks the
production question every wrapper skips: which actions does a human have to see
before they happen? A glass-box model of Kapi's lib/hitl/evaluate.ts +
lib/evals/hitl-bridge.ts (referenced by behaviour, not forked).

    from mai_rag.hitl import checkpoint, queue, bridge, spectrum
    from mai_rag.hitl.checkpoint import Action, checkpoint

    d = checkpoint(Action(tool="sql", risk="destructive", args={...}))
    # d.action ∈ proceed | modify | block | queue

Submodules:
  * checkpoint — the action-boundary gate (proceed|modify|block|queue)
  * queue      — atomic pause+queue over the hitl_queue table; PENDING/APPROVED/
                 REJECTED/RESOLVED state machine
  * bridge     — the eval→HITL bridge (a failed safety eval queues exactly one row)
  * spectrum   — the autonomy ledger render (Sheridan → 5-tier → 3-zone)

WIP markers live in each submodule (the checkpoint pass-through stub, the
RESOLVED edited-response path, the 7-day auto-expire sweep). Single-tenant for
now; the Module-2 RLS lab enforces tenant_id later.
"""
from __future__ import annotations

from . import bridge, checkpoint, queue, spectrum
from .checkpoint import Action, Decision, checkpoint as run_checkpoint

__all__ = ["bridge", "checkpoint", "queue", "spectrum", "Action", "Decision", "run_checkpoint"]
