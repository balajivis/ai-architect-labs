"""
mai_rag.corpus — load the bundled enterprise-policy corpus into the data layer.

`load_policy_corpus()` is the one call that makes the lab ready to go. By
default it copies a **pre-embedded `policy.db`** into place — first load is
seconds, no embedding. `rebuild=True` embeds from the raw docs instead (chunk +
MiniLM, keyless) so the lab can show the build once. Pass a `db_path` to persist.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .store import Store, connect, embed

CHUNK_TARGET_WORDS = 120
CHUNK_OVERLAP_WORDS = 20


def _find_corpus_dir() -> Path:
    """Locate the `policy/` corpus dir across layouts: env override → packaged
    data (after `pip install`) → repo-root `corpus/` (dev clone)."""
    env = os.getenv("MAI_CORPUS_DIR")
    if env and Path(env).exists():
        return Path(env)
    here = Path(__file__).resolve()
    candidates = [
        here.parent / "data" / "policy",                    # mai_rag/data/policy (packaged)
        here.parent.parent / "corpus" / "policy",           # repo-root corpus/policy (dev)
        Path.cwd() / "corpus" / "policy",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "Could not find the policy corpus. Set MAI_CORPUS_DIR, or run from the "
        "ai-architect-labs repo, or reinstall mai_rag with its packaged data."
    )


def _find_prebuilt_db() -> Path | None:
    """Locate the shipped pre-embedded `policy.db` so first load skips the
    ~1900-chunk embedding pass. Returns None if it isn't bundled (dev builds)."""
    env = os.getenv("MAI_PREBUILT_DB")
    if env and Path(env).exists():
        return Path(env)
    here = Path(__file__).resolve()
    for c in (here.parent / "data" / "policy.db",            # mai_rag/data/policy.db (packaged)
              here.parent.parent / "policy.db"):             # repo-root (dev)
        if c.exists():
            return c
    return None


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a `---`-delimited YAML-ish frontmatter block from the body.
    Parses simple `key: value` lines (no nested YAML) to avoid a PyYAML dep."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    meta: dict = {}
    for line in block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"')
    return meta, body


def _chunk(body: str, target: int = CHUNK_TARGET_WORDS,
           overlap: int = CHUNK_OVERLAP_WORDS) -> list[str]:
    """Boundary-aware greedy chunking: pack paragraphs to ~target words, with a
    small word overlap so a fact split across a boundary is still retrievable."""
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    chunks: list[str] = []
    cur: list[str] = []
    count = 0
    for p in paras:
        w = len(p.split())
        if count + w > target and cur:
            chunks.append("\n\n".join(cur))
            tail = " ".join("\n\n".join(cur).split()[-overlap:]) if overlap else ""
            cur = [tail] if tail else []
            count = len(tail.split())
        cur.append(p)
        count += w
    if cur:
        chunks.append("\n\n".join(cur))
    return [c for c in chunks if c.strip()]


def load_policy_corpus(db_path: str = ":memory:", rebuild: bool = False,
                       prebuilt: bool = True) -> Store:
    """Build (or open) the data layer seeded with the policy corpus.
    Returns a ready-to-query `Store`.

    Fast path (default): if a pre-embedded `policy.db` ships, it's copied into
    place (or restored into `:memory:`) so the first load is **seconds, not
    minutes** — no re-embedding. Pass `rebuild=True` to embed from the raw docs
    (the lab can show this once), or `prebuilt=False` to ignore the bundle.
    """
    pre = _find_prebuilt_db() if (prebuilt and not rebuild) else None

    # Fast path A — persistent file: copy the prebuilt DB in if the target is new.
    if pre is not None and db_path != ":memory:" and not Path(db_path).exists():
        import shutil
        shutil.copy(pre, db_path)

    conn = connect(db_path)
    store = Store(conn)

    # Fast path B — :memory: db: restore the prebuilt file into the connection.
    already = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    if pre is not None and db_path == ":memory:" and not already:
        import sqlite3
        src = sqlite3.connect(str(pre))
        src.backup(conn)
        src.close()
        already = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]

    if already and not rebuild:
        return store
    if rebuild:
        for t in ("documents", "chunks", "vec_chunks", "golden_cases"):
            conn.execute(f"DELETE FROM {t}")

    corpus_dir = _find_corpus_dir()
    manifest_path = corpus_dir / "manifest.json"
    if manifest_path.exists():
        entries = json.loads(manifest_path.read_text())
        paths = [corpus_dir / Path(e["path"]).name for e in entries]
    else:
        paths = sorted(corpus_dir.glob("*.md"))

    for p in paths:
        meta, body = _parse_frontmatter(p.read_text(encoding="utf-8"))
        doc_id = store.add_document(
            source=meta.get("doc_id", p.stem),
            title=meta.get("title", p.stem),
            metadata=meta,
            created_at=meta.get("last_updated", ""),
        )
        chunks = _chunk(body)
        if not chunks:
            continue
        vecs = embed(chunks)
        for i, (text, vec) in enumerate(zip(chunks, vecs)):
            store.add_chunk(doc_id, i, text, vec, metadata={"status": meta.get("status", "active")})
    store.commit()
    return store


def load_golden_seed() -> list[dict]:
    """Read the shipped candidate golden cases (`golden_seed.json`). Tolerant of
    the file living next to the docs (`policy/`) or one level up (`corpus/`)."""
    corpus_dir = _find_corpus_dir()
    for seed in (corpus_dir / "golden_seed.json", corpus_dir.parent / "golden_seed.json"):
        if seed.exists():
            return json.loads(seed.read_text(encoding="utf-8"))
    return []


# ── Hard Pack — the small, adversarial corpus (one corpus, the hard one) ────────

def _find_hard_corpus_dir() -> Path:
    """Locate the `hard/` corpus dir: env override → packaged data → dev clone."""
    env = os.getenv("MAI_HARD_CORPUS_DIR")
    if env and Path(env).exists():
        return Path(env)
    here = Path(__file__).resolve()
    for c in (here.parent / "data" / "hard",            # mai_rag/data/hard (packaged)
              here.parent.parent / "corpus" / "hard"):  # repo-root corpus/hard (dev)
        if c.exists():
            return c
    raise FileNotFoundError(
        "Could not find the hard corpus (mai_rag/data/hard). Set MAI_HARD_CORPUS_DIR "
        "or reinstall mai_rag with its packaged data."
    )


def load_hard_corpus(db_path: str = ":memory:", rebuild: bool = False) -> Store:
    """Build the data layer seeded with the **Hard Pack** — a small (~14-doc /
    ~130-chunk) adversarial corpus engineered so retrieval failure modes are
    *visible*: recency twins (active/superseded), a near-identical support-tier
    sibling family (the contextual sweet spot), multi-hop cross-references, and
    an unanswerable case.

    Embeds **live** with keyless MiniLM in ~10–20s — small enough to re-embed in
    class (the whole point of the Hard Pack), so there's no prebuilt DB. Pass
    `db_path` to persist; `rebuild=True` to re-seed an existing connection.
    """
    conn = connect(db_path)
    store = Store(conn)
    already = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    if already and not rebuild:
        return store
    if rebuild:
        for t in ("documents", "chunks", "vec_chunks", "golden_cases"):
            conn.execute(f"DELETE FROM {t}")

    for p in sorted(_find_hard_corpus_dir().glob("*.md")):
        meta, body = _parse_frontmatter(p.read_text(encoding="utf-8"))
        doc_id = store.add_document(
            source=meta.get("doc_id", p.stem),
            title=meta.get("title", p.stem),
            metadata=meta,
            created_at=meta.get("last_updated", ""),
        )
        chunks = _chunk(body)
        if not chunks:
            continue
        vecs = embed(chunks)
        for i, (text, vec) in enumerate(zip(chunks, vecs)):
            store.add_chunk(doc_id, i, text, vec, metadata={"status": meta.get("status", "active")})
    store.commit()
    return store


def load_golden_hard() -> list[dict]:
    """The 12-case Hard Pack golden set (`q / expected / support / tag`), the
    through-line fixture for the Hard Pack — adversarially verified to break a
    naive retriever on the recency / contextual / multi-hop / unanswerable cases."""
    here = Path(__file__).resolve()
    for seed in (here.parent / "data" / "golden_seed_hard.json",
                 here.parent.parent / "golden_seed_hard.json"):
        if seed.exists():
            data = json.loads(seed.read_text(encoding="utf-8"))
            return data["cases"] if isinstance(data, dict) and "cases" in data else data
    return []


# ── Catalog corpus — the synthetic "Modern AI Pro" knowledge/site catalog (Lab 3) ──

def _find_catalog_dir() -> Path:
    """Locate the `catalog/` corpus dir: env override → packaged data → dev clone."""
    env = os.getenv("MAI_CATALOG_DIR")
    if env and Path(env).exists():
        return Path(env)
    here = Path(__file__).resolve()
    for c in (here.parent / "data" / "catalog",
              here.parent.parent / "corpus" / "catalog"):
        if c.exists():
            return c
    raise FileNotFoundError(
        "Could not find the catalog corpus (mai_rag/data/catalog). Set MAI_CATALOG_DIR "
        "or reinstall mai_rag with its packaged data."
    )


def load_catalog_corpus(db_path: str = ":memory:", rebuild: bool = False) -> Store:
    """Build the data layer seeded with the **catalog corpus** — ~136 synthetic,
    deliberately *shallow* overview docs modelled on the Modern AI Pro platform
    (AI topics + course/site catalog). The shallowness is the point: depth
    questions can't be answered from the catalog, which is what motivates the
    agentic web-search fallback in Lab 3. Embeds live with keyless MiniLM
    (~15–25s). All prose is synthetic — no proprietary course content."""
    conn = connect(db_path)
    store = Store(conn)
    already = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    if already and not rebuild:
        return store
    if rebuild:
        for t in ("documents", "chunks", "vec_chunks", "golden_cases"):
            conn.execute(f"DELETE FROM {t}")

    for p in sorted(_find_catalog_dir().glob("*.md")):
        meta, body = _parse_frontmatter(p.read_text(encoding="utf-8"))
        doc_id = store.add_document(
            source=meta.get("doc_id", p.stem),
            title=meta.get("title", p.stem),
            metadata=meta,
            created_at=meta.get("last_updated", ""),
        )
        chunks = _chunk(body)
        if not chunks:
            continue
        vecs = embed(chunks)
        for i, (text, vec) in enumerate(zip(chunks, vecs)):
            store.add_chunk(doc_id, i, text, vec, metadata={"type": meta.get("type", "topic")})
    store.commit()
    return store


def load_golden_catalog() -> list[dict]:
    """The Lab 3 golden set over the catalog corpus (`q / expected / support / tag`).
    Tags drive the agentic moves: `site`/`topic` (in-corpus), `multi-hop`
    (decompose), `needs-web` (catalog too shallow → web fallback), `no-retrieval`
    (router answers directly)."""
    here = Path(__file__).resolve()
    for seed in (here.parent / "data" / "golden_seed_catalog.json",
                 here.parent.parent / "golden_seed_catalog.json"):
        if seed.exists():
            data = json.loads(seed.read_text(encoding="utf-8"))
            return data["cases"] if isinstance(data, dict) and "cases" in data else data
    return []


# ── Adversarial + action golden sets (Labs 6 & 7) ───────────────────────────────

def load_golden_attacks() -> list[dict]:
    """The Lab 6 ADVERSARIAL golden set (`golden_attacks.json`) — the inverse of a
    correctness golden: each case is an attack and PASS = the system REFUSED /
    REDACTED / ESCALATED. Cases are plain dicts shaped
    `{q, attack_class, expected_behavior, notContains}` with an optional
    `injected_doc` for indirect (OWASP-LLM01) prompt-injection cases. Four classes
    — jailbreak / prompt-injection / pii-leak / off-policy — mirror Kapi
    lib/evals/golden/safety/*. All synthetic and IP-safe (reuses lab_5's invented
    'Asha Menon / 4471 / 14 Oak Lane' PII fixture). Includes ≥1 off-policy-only
    case so Move 4's gate-toggle can prove Gate 3 is load-bearing.

    WIP: ships ~12 cases now; the adversarial-robustness class grows toward Kapi's
    10-case parity by git pull."""
    here = Path(__file__).resolve()
    for seed in (here.parent / "data" / "golden_attacks.json",
                 here.parent.parent / "golden_attacks.json"):
        if seed.exists():
            data = json.loads(seed.read_text(encoding="utf-8"))
            return data["cases"] if isinstance(data, dict) and "cases" in data else data
    return []


def load_action_golden() -> list[dict]:
    """The Lab 7 ACTION golden set (`golden_seed_action.json`) — synthetic agent
    turns the HITL gate is graded against (distinct from the catalog golden, which
    stays the retrieval substrate). Cases use the catalog key schema
    `{q, expected, tag}` with `tag ∈ {needs-approval | needs-redact |
    safe-autonomous | needs-escalate}` PLUS a structural `tool_risk ∈
    {read | write | destructive}` enum (declared metadata, not a content
    classification) and an optional `confidence` for the Move-3 trigger sweep.
    All synthetic and IP-safe.

    WIP: ships ~10 base cases; tier=production turns (promoted from queue rejects)
    are empty until Move 7's promotion demo, then grow class-to-class."""
    here = Path(__file__).resolve()
    for seed in (here.parent / "data" / "golden_seed_action.json",
                 here.parent.parent / "golden_seed_action.json"):
        if seed.exists():
            data = json.loads(seed.read_text(encoding="utf-8"))
            return data["cases"] if isinstance(data, dict) and "cases" in data else data
    return []


# ── Bring-your-own corpus — generic loaders (see BUILD_YOUR_CORPUS.md) ──────────

#
# Unlike load_policy/hard/catalog_corpus, these take an EXPLICIT path (no env
# var, no prebuilt DB, no manifest dance). They mirror load_hard_corpus exactly:
# live keyless MiniLM embed, the same _parse_frontmatter + _chunk pipeline, and
# the same per-chunk metadata shape. Use these for a student's own domain corpus.

def load_corpus(corpus_dir: str, db_path: str = ":memory:", rebuild: bool = False,
                chunk_meta_key: str = "status") -> Store:
    """Build the data layer from ANY directory of frontmattered ``*.md`` docs.

    The generic sibling of ``load_hard_corpus`` — same chunking, same live embed
    (~10–20s for ~130 chunks, keyless MiniLM), same frontmatter parsing — but it
    takes an explicit ``corpus_dir`` path instead of an env-var/dev-clone resolver
    and ships no prebuilt DB, so the embed step always runs in-notebook.

    Frontmatter read (naive ``key: value`` lines, ``---`` delimited): ``doc_id``
    (→ ``documents.source``, falls back to filename stem), ``title`` (→
    ``documents.title``, falls back to stem), ``last_updated`` (→
    ``documents.created_at``). The FULL frontmatter dict is stored on the
    ``documents`` row. Per CHUNK, one metadata key is written:

      * ``chunk_meta_key="status"`` (default) → ``{"status": meta.get("status","active")}``
        — matches the policy/hard loaders and drives the Lab 2 metadata filter
        (``status=active``) for recency twins.
      * ``chunk_meta_key="type"``  → ``{"type": meta.get("type","topic")}``
        — matches the catalog loader.

    Files are globbed in sorted order (no manifest). Empty/whitespace-only chunks
    are dropped. Pass ``db_path`` to persist; ``rebuild=True`` to re-seed an
    existing connection.
    """
    default = "active" if chunk_meta_key == "status" else "topic"
    conn = connect(db_path)
    store = Store(conn)
    already = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    if already and not rebuild:
        return store
    if rebuild:
        for t in ("documents", "chunks", "vec_chunks", "golden_cases"):
            conn.execute(f"DELETE FROM {t}")

    for p in sorted(Path(corpus_dir).glob("*.md")):
        meta, body = _parse_frontmatter(p.read_text(encoding="utf-8"))
        doc_id = store.add_document(
            source=meta.get("doc_id", p.stem),
            title=meta.get("title", p.stem),
            metadata=meta,
            created_at=meta.get("last_updated", ""),
        )
        chunks = _chunk(body)
        if not chunks:
            continue
        vecs = embed(chunks)
        for i, (text, vec) in enumerate(zip(chunks, vecs)):
            store.add_chunk(doc_id, i, text, vec,
                            metadata={chunk_meta_key: meta.get(chunk_meta_key, default)})
    store.commit()
    return store


def load_golden(path: str) -> list[dict]:
    """Read a custom golden file in the **policy/eval-path shape** so
    the eval path (``run_suite`` / ``EvalInput``) can consume it.

    Expects either a bare JSON list of case dicts, or ``{"cases": [...]}``. Each
    case should use the policy fields ``question`` (required) /
    ``expected_answer`` / ``supporting_doc_ids`` / ``criteria`` / ``tier`` /
    ``failure_mode`` — the ONLY shape ``GoldenSet.from_seed`` maps. (The
    ``q``/``expected``/``support``/``tag`` Hard-Pack shape is NOT consumed here;
    that one is read raw by the lab harnesses, not the evaluator suite.)

    Returns the raw list of dicts; feed it into a GoldenSet (see the lab guide)
    rather than relying on the dir-scanning ``load_golden_seed`` resolver.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["cases"] if isinstance(data, dict) and "cases" in data else data