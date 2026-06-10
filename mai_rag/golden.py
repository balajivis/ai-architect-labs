"""
mai_rag.golden — the golden test set, the through-line of the whole pillar.

You author cases in Module 1 (question, expected answer, supporting docs,
criteria, tier). They persist in the `golden_cases` table and every later
module re-runs them. Three tiers: base (smoke test), blueprint (your domain),
production (real thumbs-downs captured from usage).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .corpus import load_golden_seed
from .store import Store


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GoldenCase:
    question: str
    expected: str = ""
    contexts: list[str] = field(default_factory=list)   # supporting doc_ids
    criteria: list[str] = field(default_factory=list)
    tier: str = "base"                                   # base | blueprint | production
    tags: list[str] = field(default_factory=list)
    id: int | None = None


class GoldenSet:
    """A collection of GoldenCases backed by the `golden_cases` table."""

    def __init__(self, store: Store):
        self.store = store
        self.cases: list[GoldenCase] = []

    def __iter__(self):
        return iter(self.cases)

    def __len__(self):
        return len(self.cases)

    def add(self, case: GoldenCase) -> "GoldenSet":
        self.cases.append(case)
        return self

    def save(self) -> "GoldenSet":
        """Persist any unsaved cases, assigning ids."""
        for c in self.cases:
            if c.id is not None:
                continue
            cur = self.store.conn.execute(
                "INSERT INTO golden_cases (question, expected, contexts, criteria, tier, tags, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (c.question, c.expected, json.dumps(c.contexts), json.dumps(c.criteria),
                 c.tier, json.dumps(c.tags), _now()),
            )
            c.id = int(cur.lastrowid)
        self.store.commit()
        return self

    @classmethod
    def from_db(cls, store: Store) -> "GoldenSet":
        gs = cls(store)
        for r in store.conn.execute(
            "SELECT id, question, expected, contexts, criteria, tier, tags FROM golden_cases ORDER BY id"
        ).fetchall():
            gs.cases.append(GoldenCase(
                id=int(r["id"]), question=r["question"], expected=r["expected"],
                contexts=json.loads(r["contexts"] or "[]"),
                criteria=json.loads(r["criteria"] or "[]"),
                tier=r["tier"], tags=json.loads(r["tags"] or "[]"),
            ))
        return gs

    @classmethod
    def from_seed(cls, store: Store, save: bool = True) -> "GoldenSet":
        """Load the shipped candidate cases (`golden_seed.json`) — a starting
        point students extend, not a substitute for authoring their own."""
        gs = cls(store)
        for s in load_golden_seed():
            gs.add(GoldenCase(
                question=s["question"], expected=s.get("expected_answer", ""),
                contexts=s.get("supporting_doc_ids", []),
                criteria=s.get("criteria", []),
                tier=s.get("tier", "base"),
                tags=[s["failure_mode"]] if s.get("failure_mode") else [],
            ))
        if save:
            gs.save()
        return gs
