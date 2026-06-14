"""
mai_rag.bridge — the Python→Node seam (Lab 8, Move 1).

The MCP server you build in Lab 8 is **Node**; the corpus, embeddings, and
evals are **Python**. You do not rewrite retrieval in TypeScript — you put a
thin, *keyless* HTTP wrapper in front of `mai_rag.store.Store` so the Node
server has exactly **one** Python upstream to call.

Glass box: this is ~30 lines of stdlib `http.server`, no extra dependency. Read
it. Two endpoints, both keyless (the bridge never reaches an LLM — retrieval is
local MiniLM, the same keyless path Labs 1–5 used):

    GET  /search?q=<query>&k=<n>  → JSON {"hits": [ {source, title, score, content}, ... ]}  (keyless)
    GET  /doc/<source>           → JSON {"source", "title", "content"} (full doc)            (keyless)
    POST /guard {tool_name, description, args}
                                 → JSON {"blocked", "reason", ...}  — the ONLY endpoint that
                                   reaches an LLM (Lab 8 Move 6 tool-poisoning check). Needs an
                                   LLM key; returns {"blocked": null} when none is set.

Run it as a SEPARATE terminal process — the seam is the lesson, the Node MCP
server is the star. One command, no notebook:

    python -m mai_rag.bridge                 # serves the policy corpus on :8765
    python -m mai_rag.bridge --corpus catalog --port 8765

Then build/run the Node MCP server in labs/mcp_server/ against it. (You can also
call serve_corpus(store, port) directly if you want it in-process.)
"""
from __future__ import annotations

import json
import os
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

        def do_POST(self):  # noqa: N802 (http.server API name)
            # /guard — the one LLM-touching endpoint (Move 6 tool-poisoning check).
            # Keyless retrieval stays on GET; this folds mai_rag.evals.safety judges
            # (NO regex) over the tool description + args. Server-side enforcement
            # (server.ts calling this before running a tool) is the Move-6 exercise.
            if urlparse(self.path).path != "/guard":
                self._send(404, {"error": "unknown route", "path": self.path})
                return
            length = int(self.headers.get("Content-Length", 0))
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                self._send(400, {"error": "invalid JSON body"})
                return
            try:
                from .mcp_guard import guard
                self._send(200, guard(payload.get("tool_name", ""),
                                      payload.get("description", ""),
                                      payload.get("args", {})))
            except Exception as e:  # no LLM key / judge error → report, don't crash
                self._send(200, {"blocked": None,
                                 "reason": f"guard unavailable: {type(e).__name__}",
                                 "detail": str(e)[:200]})

        def log_message(self, *args):  # keep the terminal output quiet
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


if __name__ == "__main__":  # `python -m mai_rag.bridge` — the one command the lab runs
    import argparse
    import time

    from . import corpus

    ap = argparse.ArgumentParser(
        description="Serve the mai_rag corpus over HTTP for the Lab 8 Node MCP server.")
    ap.add_argument("--port", type=int, default=int(os.getenv("MCP_BRIDGE_PORT", "8765")))
    ap.add_argument("--corpus", default="policy", choices=["policy", "catalog", "hard"],
                    help="which bundled corpus to serve (default: policy)")
    args = ap.parse_args()

    if args.corpus == "policy":
        store = corpus.load_policy_corpus("policy.db")        # prebuilt → instant
    elif args.corpus == "catalog":
        store = corpus.load_catalog_corpus()                  # live embed ~15-25s
    else:
        store = corpus.load_hard_corpus()                     # live embed ~10-20s

    serve_corpus(store, port=args.port)
    print(f"mai_rag bridge · '{args.corpus}' corpus · http://127.0.0.1:{args.port}")
    print("  GET /search?q=...&k=5   GET /doc/<source>   POST /guard {tool_name,description,args}")
    print("  leave this running; build/run the Node server in labs/mcp_server/. Ctrl-C to stop.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\nbridge stopped.")
