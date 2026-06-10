"""
mai_rag.corpus — load the bundled enterprise-policy corpus into the data layer.

`load_policy_corpus()` is the one call that makes the lab ready to go: it finds
the shipped policy docs, chunks them, embeds them locally (MiniLM, keyless), and
populates the SQL + vector tables. First call builds the DB (~seconds); pass a
`db_path` to persist it.
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


def load_policy_corpus(db_path: str = ":memory:", rebuild: bool = False) -> Store:
    """Build (or open) the data layer seeded with the policy corpus.
    Returns a ready-to-query `Store`."""
    conn = connect(db_path)
    store = Store(conn)

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
