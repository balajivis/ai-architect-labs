"""
mai_rag.bridge — the Python→Node seam (Lab 8, Move 1).

The MCP server you build in Lab 8 is **Node**; the corpus, embeddings, and
evals are **Python**. You do not rewrite retrieval in TypeScript — you put a
thin, *keyless* HTTP wrapper in front of `mai_rag.store.Store` so the Node
server has exactly **one** Python upstream to call.

Glass box: this is ~30 lines of stdlib `http.server`, no extra dependency. Read
it. Two endpoints, both keyless (the bridge never reaches an LLM — retrieval is
local MiniLM, the same keyless path Labs 1–5 used):

    GET /search?q=<query>&k=<n>   → JSON {"hits": [ {source, title, score, content}, ... ]}
    GET /doc/<source>            → JSON {"source", "title", "content"} (full doc)

Start it as an EXPLICIT background process from the lab (not auto-spawned) so
you can *see* the second process — the seam is the lesson. In the notebook:

    from mai_rag import bridge, corpus
    store = corpus.load_policy_corpus("policy.db")
    httpd = bridge.serve_corpus(store, port=8765)   # returns a started server
    # ... curl http://localhost:8765/search?q=parental+leave ...
    httpd.shutdown()                                # stop it when done
"""
from __future__ import annotations

import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from .store import Store

# Structural ID parse only (a known `/doc/<source>` path shape) — NOT
# classification. The hard no-regex rule is about deciding "is this a kind of
# thing"; pulling a path segment out of a fixed URL format is allowed.
_DOC_PATH = re.compile(r"^/doc/(?P<source>.+)$")


def _full_doc(store: Store, source: str) -> dict | None:
    """Reassemble a full document from its chunks, by `source` id. Reads the
    same SQLite data layer `Store.search` does — no LLM, no key."""
    doc = store.conn.execute(
        "SELECT id, source, title FROM documents WHERE source = ? LIMIT 1", (source,)
    ).fetchone()
    if doc is None:
        return None
    rows = store.conn.execute(
        "SELECT content FROM chunks WHERE document_id = ? ORDER BY chunk_index",
        (doc["id"],),
    ).fetchall()
    return {"source": doc["source"], "title": doc["title"],
            "content": "\n\n".join(r["content"] for r in rows)}


def serve_corpus(store: Store, port: int = 8765) -> ThreadingHTTPServer:
    """Start a keyless HTTP wrapper over `store` on `port` and return the
    running server. Call `.shutdown()` to stop it. Glass-box and dependency-free
    (stdlib `http.server`) so the Node server has exactly one upstream surface."""

    class _Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802 (http.server API name)
            parsed = urlparse(self.path)
            if parsed.path == "/search":
                qs = parse_qs(parsed.query)
                q = (qs.get("q") or [""])[0]
                try:
                    k = int((qs.get("k") or ["5"])[0])
                except ValueError:
                    k = 5
                hits = store.search(q, k=k)
                self._send(200, {"hits": [
                    {"source": h.source, "title": h.title,
                     "score": round(h.score, 4), "content": h.content}
                    for h in hits
                ]})
                return
            m = _DOC_PATH.match(parsed.path)
            if m:
                doc = _full_doc(store, unquote(m.group("source")))
                if doc is None:
                    self._send(404, {"error": "not found", "source": unquote(m.group("source"))})
                else:
                    self._send(200, doc)
                return
            self._send(404, {"error": "unknown route", "path": parsed.path})

        def log_message(self, *args):  # keep the notebook output quiet
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd
