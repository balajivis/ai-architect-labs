"""
mai_rag.hitl.queue — atomic pause + approval queue (Lab 7 Move 5).

A held action isn't a log line — it's a paused run PLUS a queue row written in
ONE transaction. If the run pauses without queuing (or queues without pausing)
you get an orphan. This wraps the additive `hitl_queue` table (added to
store.py's SCHEMA with CREATE TABLE IF NOT EXISTS, so the prebuilt policy.db is
safe and the lab uses its own fresh in-memory store anyway).

State machine mirrors Kapi lib/hitl/resume.ts:
    PENDING → APPROVED (run the original action as-is)
            → RESOLVED (run a PM-edited response)

Kapi has NO explicit REJECTED resume branch — reject is modelled as
'resume-without-executing'. This lab adds a LAB-LOCAL REJECTED status purely to
make the 'side effect never fires' assertion legible (it is a teaching
simplification, NOT Kapi's model — flagged here and in the lab markdown).

WIP: the RESOLVED (edited-response) path and Kapi's dedup/advisory-lock are
stubbed TODO for a later pull; APPROVED re-execution and the lab-local REJECTED
no-execute path ship fully wired.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ..store import Store

PENDING, APPROVED, REJECTED, RESOLVED = "PENDING", "APPROVED", "REJECTED", "RESOLVED"
EXPIRY_DAYS = 7


@dataclass
class QueueRow:
    id: int
    status: str
    query: str
    original_response: str
    reason: str
    golden_case_id: str | None
    eval_run_id: str | None
    tenant_id: str
    created_at: str
    expires_at: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _expiry(days: int = EXPIRY_DAYS) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def enqueue(store: Store, query: str, original_response: str = "", reason: str = "",
            golden_case_id: str | None = None, eval_run_id: str | None = None,
            tenant_id: str = "default", expiry_days: int = EXPIRY_DAYS) -> int:
    """Insert one PENDING hitl_queue row. Returns its id. Pair this with pausing
    the run inside the SAME transaction (see pause_and_queue) so the two are
    atomic — no orphan run, no orphan row."""
    cur = store.conn.execute(
        "INSERT INTO hitl_queue (status, query, original_response, reason, "
        "golden_case_id, eval_run_id, tenant_id, created_at, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (PENDING, query, original_response, reason, golden_case_id, eval_run_id,
         tenant_id, _now(), _expiry(expiry_days)),
    )
    return int(cur.lastrowid)


@dataclass
class AgentRun:
    """A tiny in-memory model of a paused agent run. Real frameworks persist the
    paused node + state; here it's plain Python + the queue row, no framework.
    The `executed` spy counter is what Move 5 asserts stays 0 after a reject."""
    status: str = "running"          # running | paused | done
    queue_id: int | None = None
    executed: int = 0                # how many times the held side-effect ran


def pause_and_queue(store: Store, run: AgentRun, query: str, original_response: str = "",
                    reason: str = "", golden_case_id: str | None = None,
                    eval_run_id: str | None = None, tenant_id: str = "default") -> int:
    """ATOMIC pause+queue: inside one transaction, flip the run to `paused` AND
    write the PENDING queue row. Mirrors Kapi executor.ts:1755's
    prisma.$transaction pause-and-queue. Returns the queue id.

    The side effect (the destructive tool) is NOT run here — it only runs on an
    explicit APPROVED resume. That's the whole point: the unsafe action waits
    behind a human."""
    try:
        qid = enqueue(store, query, original_response, reason,
                      golden_case_id, eval_run_id, tenant_id)
        run.status = "paused"
        run.queue_id = qid
        store.conn.commit()
        return qid
    except Exception:
        store.conn.rollback()
        raise


def get(store: Store, queue_id: int) -> QueueRow | None:
    row = store.conn.execute("SELECT * FROM hitl_queue WHERE id = ?", (queue_id,)).fetchone()
    if row is None:
        return None
    return QueueRow(**{k: row[k] for k in row.keys()})


def pending(store: Store) -> list[QueueRow]:
    rows = store.conn.execute(
        "SELECT * FROM hitl_queue WHERE status = ? ORDER BY id", (PENDING,)
    ).fetchall()
    return [QueueRow(**{k: r[k] for k in r.keys()}) for r in rows]


def resume(store: Store, run: AgentRun, queue_id: int, decision: str,
           execute_fn=None, edited_response: str | None = None) -> dict:
    """Drive a held run to a terminal state.

      APPROVED → run the original action as-is (calls execute_fn) and resume.
      REJECTED → (lab-local) resume WITHOUT executing — the side effect provably
                 never fires; assert run.executed stays 0.
      RESOLVED → run a PM-edited response (WIP stub: marks resolved, does not
                 re-run the tool).

    Returns {status, executed} so the lab can assert the call-count."""
    row = get(store, queue_id)
    if row is None:
        raise ValueError(f"no queue row {queue_id}")

    if decision == APPROVED:
        if execute_fn is not None:
            execute_fn()
            run.executed += 1
        _set_status(store, queue_id, APPROVED)
        run.status = "done"
    elif decision == REJECTED:
        # Lab-local: reject = resume WITHOUT executing. The DELETE never runs.
        _set_status(store, queue_id, REJECTED)
        run.status = "done"
    elif decision == RESOLVED:
        # WIP: run an edited response. Stubbed — marks resolved, does not re-run
        # the original tool. The full RESOLVED path lands via a later git pull.
        _set_status(store, queue_id, RESOLVED)
        run.status = "done"
    else:
        raise ValueError(f"unknown resume decision {decision!r} "
                         f"(expected {APPROVED}|{REJECTED}|{RESOLVED})")
    return {"status": decision, "executed": run.executed}


def _set_status(store: Store, queue_id: int, status: str) -> None:
    store.conn.execute("UPDATE hitl_queue SET status = ? WHERE id = ?", (status, queue_id))
    store.conn.commit()


def expire_stale(store: Store) -> int:
    """WIP: 7-day auto-expire sweep. Marks PENDING rows past expires_at as
    RESOLVED so they don't linger. The batch sweep is a follow-up pull; this is
    the minimal helper. Returns the number expired."""
    now = _now()
    cur = store.conn.execute(
        "UPDATE hitl_queue SET status = ? WHERE status = ? AND expires_at < ?",
        (RESOLVED, PENDING, now),
    )
    store.conn.commit()
    return cur.rowcount
