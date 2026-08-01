"""
mai_rag.evals.retrieval — the KEYLESS retrieval engines: recall@k · MRR · hit@1.

Why these belong in the registry (and didn't until now): every other engine in this kit
judges the ANSWER, so a system could regress its retriever — fetch worse documents — and
the gate would never notice as long as the model still wrote something plausible. These
three score the RETRIEVER directly, against the supporting docs your golden set already
labels. No LLM, no judge bias, no cost: pure set + rank arithmetic, deterministic enough
to gate on.

They read two fields on EvalInput:
    retrieved  — doc ids/sources the retriever returned, IN RANK ORDER
    supporting — the doc id(s) the golden case says are needed ("a + b" = multi-hop)

Return None when either is missing, so mixed suites (answer engines + retrieval engines)
run over the same golden set without special-casing.

The metrics, and what each one tells you:
  · recall@k — of the docs the answer NEEDS, how many made the window? This is the FLOOR:
               if it's low, no reranker and no prompt can save the answer.
  · mrr      — 1/rank of the first supporting doc. Rank-SENSITIVE, so a reranker that only
               reorders the window actually shows up (recall@k can't see that).
  · hit@1    — was the right doc ranked first? The legible special case; the clearest read
               on a near-duplicate outranking the document you actually wanted.
"""
from __future__ import annotations

from .base import EvalInput, Score


def _pair(e: EvalInput):
    """(retrieved, supporting) or None when the case carries no retrieval evidence."""
    got = [str(x) for x in (e.retrieved or [])]
    want = [str(x) for x in (e.supporting or [])]
    if not got or not want:
        return None
    return got, want


def recall_at_k(e: EvalInput) -> Score | None:
    """Fraction of supporting docs present anywhere in the retrieved window. The floor."""
    p = _pair(e)
    if not p:
        return None
    got, want = p
    hit = sum(1 for w in want if w in got)
    s = hit / len(want)
    return Score("recall_at_k", s, s >= 0.999,
                 f"{hit}/{len(want)} supporting doc(s) in top-{len(got)}")


def mrr(e: EvalInput) -> Score | None:
    """Reciprocal rank of the FIRST supporting doc: 1.0 at rank 1, 0.5 at rank 2, 0 if absent."""
    p = _pair(e)
    if not p:
        return None
    got, want = p
    ranks = [i + 1 for i, g in enumerate(got) if g in want]
    s = 1.0 / ranks[0] if ranks else 0.0
    where = f"first supporting doc at rank {ranks[0]}" if ranks else "no supporting doc retrieved"
    return Score("mrr", s, s >= 0.5, where)


def hit_at_1(e: EvalInput) -> Score | None:
    """Did the top-ranked doc support the answer? The blunt, legible one."""
    p = _pair(e)
    if not p:
        return None
    got, want = p
    s = 1.0 if got[0] in want else 0.0
    return Score("hit_at_1", s, s == 1.0,
                 f"rank-1 doc {'is' if s else 'is NOT'} a supporting doc ({got[0][:40]})")


def from_golden(question: str, answer: str, contexts: list[str], hits, support: str,
                expected: str = "") -> EvalInput:
    """Convenience: build an EvalInput carrying retrieval evidence.

    `hits` are search results (objects with `.source`, or plain strings) in rank order;
    `support` is the golden case's support field, where " + " separates a multi-hop case's
    several required docs (splitting on it is structural parsing, not classification)."""
    retrieved = [getattr(h, "source", h) for h in (hits or [])]
    supporting = [] if (not support or "none" in support.lower()) else \
        [s.strip() for s in support.split("+")]
    return EvalInput(question=question, answer=answer, contexts=contexts, expected=expected,
                     retrieved=[str(r) for r in retrieved], supporting=supporting)
