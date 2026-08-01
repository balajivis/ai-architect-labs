"""
mai_rag.obs — keyless observability: spans, a per-request Trace, and a cost ledger.

Pillar IV, "Ship audit-ready." An AUDIT trace is REFERENCES + timings + control-state,
never PAYLOADS — the same rule the MCP audit lab teaches, here applied to the whole
RAG -> eval -> HITL request. You build one Trace per request, wrap each hop in
`trace.span(...)`, then read total latency, per-stage COST ATTRIBUTION, and a redacted
`record()` an auditor can replay years later without it becoming a data breach.

Everything here is standard library and keyless — instrumentation must never need a key,
and it must never be the thing that leaks the data it is watching. Prices are illustrative
$/1k-tokens; plug your provider's real card in PRICE_PER_1K.
"""
from __future__ import annotations

import secrets
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

# Illustrative $/1k tokens as (input, output) by tier. NOT a live rate card — the point is
# the SHAPE of the bill (which stage spends), not the cents. Replace with your provider's.
PRICE_PER_1K: dict[str, tuple[float, float]] = {
    "small":  (0.05, 0.40),
    "medium": (0.80, 4.00),
    "large":  (2.50, 10.00),
    "embed":  (0.02, 0.00),
    "none":   (0.00, 0.00),      # keyless work (local retrieval, a structural gate) — real latency, $0
}


def estimate_tokens(text: str) -> int:
    """chars/4 — the same rough proxy the metered labs use. Good enough to attribute the bill;
    swap in your tokenizer for the exact count."""
    return max(0, len(text or "") // 4)


def new_correlation_id() -> str:
    """A greppable 16-hex request id (W3C trace-id shape), minted per request — the thread an
    auditor pulls to reconstruct one call across every stage."""
    return secrets.token_hex(8)


@dataclass
class Span:
    """One traced hop. `refs` are the ids of the documents/resources touched — NEVER their text;
    `tokens_*` are volumes, not content. Both are what an auditor needs and what a breach would
    misuse, which is exactly why the audit record keeps the first and drops the second."""
    name: str
    ms: float
    tier: str = "none"
    tokens_in: int = 0
    tokens_out: int = 0
    refs: list[str] = field(default_factory=list)
    note: str = ""

    def cost(self) -> float:
        c_in, c_out = PRICE_PER_1K.get(self.tier, (0.0, 0.0))
        return (self.tokens_in / 1000) * c_in + (self.tokens_out / 1000) * c_out


@dataclass
class Trace:
    """A per-request trace: the spans, plus derived latency + cost. `record()` is the
    payload-free artifact you persist; `waterfall()` is the human view."""
    correlation_id: str = field(default_factory=new_correlation_id)
    spans: list[Span] = field(default_factory=list)
    controls: dict[str, str] = field(default_factory=dict)   # control-state at request time (e.g. guard verdict, auth)

    @contextmanager
    def span(self, name: str, *, tier: str = "none", tokens_in: int = 0, tokens_out: int = 0,
             refs: list[str] | None = None, note: str = ""):
        """Time a hop. Yields a mutable dict so the body can fill in what it learns
        (output tokens, the doc ids it touched) before the span is recorded:

            with trace.span("retrieve", tier="embed") as sp:
                hits = store.search(q); sp["refs"] = [h.source for h in hits]
        """
        holder = {"tokens_in": tokens_in, "tokens_out": tokens_out,
                  "refs": list(refs or []), "note": note}
        t0 = time.time()
        try:
            yield holder
        finally:
            self.spans.append(Span(name, (time.time() - t0) * 1000.0, tier,
                                   int(holder["tokens_in"]), int(holder["tokens_out"]),
                                   list(holder["refs"]), str(holder["note"])))

    def record_control(self, name: str, state: str) -> None:
        """Record the state of a control AT THIS INSTANT — even (especially) when it was OFF.
        `guard: unavailable` and `auth: disabled` are fields, not omissions: a log that maps a
        fail-open to 'clean' is a cover-up, not evidence."""
        self.controls[name] = state

    @property
    def total_ms(self) -> float:
        return sum(s.ms for s in self.spans)

    @property
    def total_cost(self) -> float:
        return sum(s.cost() for s in self.spans)

    def cost_by_stage(self) -> list[tuple[str, float, float, float]]:
        """(stage, ms, cost_usd, pct_of_cost) per span — the attribution table."""
        total = self.total_cost or 1e-12
        return [(s.name, s.ms, s.cost(), 100.0 * s.cost() / total) for s in self.spans]

    def record(self) -> dict:
        """The audit artifact: references + volumes + timings + cost + control-state, NO text.
        This is what you persist and what an auditor replays."""
        return {
            "correlation_id": self.correlation_id,
            "spans": [{"stage": s.name, "ms": round(s.ms, 1), "tier": s.tier,
                       "tokens": s.tokens_in + s.tokens_out, "refs": s.refs,
                       "cost_usd": round(s.cost(), 6), "note": s.note} for s in self.spans],
            "controls": dict(self.controls),
            "total_ms": round(self.total_ms, 1),
            "total_cost_usd": round(self.total_cost, 6),
        }

    def waterfall(self, width: int = 32) -> str:
        """An in-terminal latency waterfall — one bar per span, scaled to the longest."""
        if not self.spans:
            return "(no spans)"
        longest = max(s.ms for s in self.spans) or 1.0
        rows = []
        for s in self.spans:
            bar = "█" * max(1, round(width * s.ms / longest))
            rows.append(f"  {s.name:<12} {bar} {s.ms:6.0f}ms  ${s.cost():.5f}")
        return "\n".join(rows)


# Fields every audit-ready record must carry — the audit gate asserts none is missing.
REQUIRED_RECORD_FIELDS = ("correlation_id", "spans", "controls", "total_ms", "total_cost_usd")


def audit_complete(record: dict) -> tuple[bool, list[str]]:
    """Is this record replayable evidence? Returns (ok, missing_fields). A record missing any
    required field FAILS the audit gate — the same discipline as the eval gate, one pillar over."""
    missing = [f for f in REQUIRED_RECORD_FIELDS if not record.get(f) and record.get(f) != 0]
    # a span with no refs AND no note is un-auditable (what did it touch?)
    if record.get("spans") and all(not sp.get("refs") and not sp.get("note") for sp in record["spans"]):
        missing.append("span-evidence (refs/notes)")
    return (not missing), missing
