"""
mai_rag.store — the bundled SQL + vector data layer.

One SQLite file holds the whole RAG state: documents, chunks, a `vec0`
embedding table (via sqlite-vec), the golden test cases, and every eval run +
result. This deliberately mirrors the *pgvector mental model* — vectors living
in a relational DB, KNN expressed in SQL — so what you learn here ports straight
to Kapi's `ContentEmbedding` table and the pgvector you target in production.

Glass box: read this file. Nothing here is magic.

Embeddings are produced locally with a small sentence-transformers model
(MiniLM, 384-dim, normalized) so retrieval needs no API key. The same `Store`
API can later be pointed at a real pgvector backend for the deployment act.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import numpy as np

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBED_DIM = 384

# ── Local embedding model (lazy, cached) ──────────────────────────────────────
_embedder = None


def get_embedder():
    """Load the MiniLM encoder once. Keyless and local."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(EMBED_MODEL_NAME)
    return _embedder


def embed(texts: Sequence[str]) -> np.ndarray:
    """Embed a list of texts → (n, 384) float32, L2-normalized."""
    model = get_embedder()
    vecs = model.encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vecs, dtype=np.float32)


# ── Schema ────────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id          INTEGER PRIMARY KEY,
    source      TEXT,
    title       TEXT,
    metadata    TEXT,                         -- JSON
    tenant_id   TEXT DEFAULT 'default',
    created_at  TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_index INTEGER,
    content     TEXT,
    token_count INTEGER,
    metadata    TEXT                           -- JSON
);

CREATE TABLE IF NOT EXISTS golden_cases (
    id          INTEGER PRIMARY KEY,
    question    TEXT,
    expected    TEXT,
    contexts    TEXT,                          -- JSON: supporting doc_ids
    criteria    TEXT,                          -- JSON: list[str]
    tier        TEXT,                          -- base | blueprint | production
    tags        TEXT,                          -- JSON: list[str]
    created_at  TEXT
);

CREATE TABLE IF NOT EXISTS eval_runs (
    id          INTEGER PRIMARY KEY,
    label       TEXT,                          -- "naive baseline", "hybrid+rerank", ...
    module      TEXT,
    config      TEXT,                          -- JSON
    created_at  TEXT
);

CREATE TABLE IF NOT EXISTS eval_results (
    id          INTEGER PRIMARY KEY,
    run_id      INTEGER REFERENCES eval_runs(id),
    case_id     INTEGER REFERENCES golden_cases(id),
    evaluator   TEXT,
    score       REAL,
    passed      INTEGER,
    reasoning   TEXT
);

CREATE TABLE IF NOT EXISTS feedback (
    id          INTEGER PRIMARY KEY,
    question    TEXT,
    answer      TEXT,
    verdict     TEXT,                          -- thumbs_down etc. → Tier-3 golden cases
    created_at  TEXT
);

-- HITL escalate/approval queue (Lab 7 · Pillar IV Module 3). Additive: a held
-- action is a paused run + a queue row written together. A failed safety eval
-- promotes into exactly one PENDING row carrying its golden_case_id + eval_run_id
-- (the eval→HITL bridge). CREATE ... IF NOT EXISTS makes this safe for the
-- prebuilt policy.db too — opening an old DB just adds the empty table.
CREATE TABLE IF NOT EXISTS hitl_queue (
    id                INTEGER PRIMARY KEY,
    status            TEXT DEFAULT 'PENDING',  -- PENDING | APPROVED | REJECTED | RESOLVED
    query             TEXT,
    original_response TEXT,
    reason            TEXT,
    golden_case_id    TEXT,                    -- the case that failed the eval (bridge)
    eval_run_id       TEXT,                    -- the run that produced the failure
    tenant_id         TEXT DEFAULT 'default',  -- single-tenant for now; RLS lab enforces later
    created_at        TEXT,
    expires_at        TEXT                     -- 7-day expiry, mirrors Kapi hitl-bridge.ts
);
"""

VEC_SCHEMA = (
    f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks "
    f"USING vec0(chunk_id INTEGER PRIMARY KEY, embedding float[{EMBED_DIM}])"
)


def connect(path: str = ":memory:") -> sqlite3.Connection:
    """Open the DB, load sqlite-vec, ensure the schema exists."""
    import sqlite_vec

    # check_same_thread=False so the same store can be read from a worker thread
    # (e.g. mai_rag.bridge's threaded HTTP server in Lab 8). The labs drive the
    # connection single-threaded, so disabling the ownership guard is safe.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.executescript(SCHEMA)
    conn.execute(VEC_SCHEMA)
    conn.commit()
    return conn


@dataclass
class Hit:
    chunk_id: int
    content: str
    document_id: int
    source: str
    title: str
    distance: float
    score: float  # cosine similarity in [0,1]-ish (normalized vectors)


class Store:
    """Thin handle over the connection: embed, index, search — in SQL."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---- writes -------------------------------------------------------------
    def add_document(self, source: str, title: str, metadata: dict | None = None,
                     tenant_id: str = "default", created_at: str = "") -> int:
        cur = self.conn.execute(
            "INSERT INTO documents (source, title, metadata, tenant_id, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (source, title, json.dumps(metadata or {}), tenant_id, created_at),
        )
        return int(cur.lastrowid)

    def add_chunk(self, document_id: int, chunk_index: int, content: str,
                  embedding: Sequence[float], metadata: dict | None = None) -> int:
        import sqlite_vec

        cur = self.conn.execute(
            "INSERT INTO chunks (document_id, chunk_index, content, token_count, metadata) "
            "VALUES (?, ?, ?, ?, ?)",
            (document_id, chunk_index, content, len(content.split()), json.dumps(metadata or {})),
        )
        chunk_id = int(cur.lastrowid)
        self.conn.execute(
            "INSERT INTO vec_chunks (chunk_id, embedding) VALUES (?, ?)",
            (chunk_id, sqlite_vec.serialize_float32(list(map(float, embedding)))),
        )
        return chunk_id

    def commit(self) -> None:
        self.conn.commit()

    # ---- read: vector search ------------------------------------------------
    def search(self, query: str, k: int = 5, tenant_id: str | None = None,
               require_tenant: bool = False) -> list[Hit]:
        """KNN over the vector table, then join back for content. The two-step
        shape keeps the SQL legible — KNN first, hydrate second.

        `require_tenant=True` makes the tenant scope MANDATORY: a call with no
        tenant_id RAISES rather than returning rows. This is row-level security
        enforced at the DATA layer, not a prompt instruction (Lab 6 · mirrors
        Kapi lib/knowledge/vector-store.ts which throws tenantId-required). It is
        a permanent PER-CALL opt-in defaulting False, so Labs 1–5's keyless
        `store.search(q)` calls are untouched — there is no plan to flip the
        default (that would retroactively break already-shipped labs)."""
        import sqlite_vec

        if require_tenant and tenant_id is None:
            raise ValueError(
                "require_tenant=True but tenant_id is None — refusing to run an "
                "unscoped query. Resolve the tenant from the auth layer first "
                "(see mai_rag.acl.authed_search). RLS belongs in the retriever, "
                "not the prompt."
            )

        qv = embed([query])[0]
        # sqlite-vec KNN: use the `k = ?` constraint, NOT `LIMIT ?`. A bound
        # LIMIT isn't seen by the vec0 query planner on some sqlite-vec/SQLite
        # builds (e.g. Colab's), which then raises OperationalError. `k = ?`
        # is the portable form. Over-fetch when tenant filtering so the
        # post-join filter still has k survivors.
        fetch_k = k if tenant_id is None else max(k * 4, k + 20)
        rows = self.conn.execute(
            "SELECT chunk_id, distance FROM vec_chunks "
            "WHERE embedding MATCH ? AND k = ? ORDER BY distance",
            (sqlite_vec.serialize_float32(list(map(float, qv))), fetch_k),
        ).fetchall()

        hits: list[Hit] = []
        for r in rows:
            c = self.conn.execute(
                "SELECT c.content, c.document_id, d.source, d.title, d.tenant_id "
                "FROM chunks c JOIN documents d ON d.id = c.document_id WHERE c.id = ?",
                (r["chunk_id"],),
            ).fetchone()
            if c is None:
                continue
            if tenant_id is not None and c["tenant_id"] != tenant_id:
                continue
            dist = float(r["distance"])
            # normalized vectors → cosine_sim = 1 - L2^2 / 2
            score = max(0.0, 1.0 - (dist * dist) / 2.0)
            hits.append(Hit(
                chunk_id=int(r["chunk_id"]), content=c["content"],
                document_id=int(c["document_id"]), source=c["source"],
                title=c["title"], distance=dist, score=score,
            ))
            if len(hits) >= k:
                break
        return hits

    # ---- read: counts (handy in the notebook) -------------------------------
    def stats(self) -> dict[str, int]:
        q = lambda t: int(self.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
        return {t: q(t) for t in ("documents", "chunks", "golden_cases", "eval_runs", "eval_results")}
