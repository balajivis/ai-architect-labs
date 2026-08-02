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

        def _get(self):
            parsed = urlparse(self.path)
            if parsed.path == "/docs":
                # The corpus INDEX — what the Lab 8 `policy://catalog` MCP *resource*
                # serves. Resources are application-controlled reference data, so the
                # index is the natural resource: cheap, stable, no query needed.
                rows = store.conn.execute(
                    "SELECT source, title FROM documents ORDER BY source").fetchall()
                self._send(200, {"docs": [{"source": r["source"], "title": r["title"]}
                                          for r in rows]})
                return
            if parsed.path == "/search":
                qs = parse_qs(parsed.query)
                q = (qs.get("q") or [""])[0]
                try:
                    k = int((qs.get("k") or ["5"])[0])
                except ValueError:
                    k = 5
                hits = store.search(q, k=k)
                # Volume + which docs, never the query text or the doc bodies —
                # the same references-not-payloads rule audit.ts follows.
                self._trace("/search", hits=len(hits), k=k)
                self._send(200, {"hits": [
                    {"source": h.source, "title": h.title,
                     "score": round(h.score, 4), "content": h.content}
                    for h in hits
                ]})
                return
            m = _DOC_PATH.match(parsed.path)
            if m:
                doc = _full_doc(store, unquote(m.group("source")))
                self._trace("/doc", source=unquote(m.group("source")), found=doc is not None)
                if doc is None:
                    self._send(404, {"error": "not found", "source": unquote(m.group("source"))})
                else:
                    self._send(200, doc)
                return
            self._send(404, {"error": "unknown route", "path": parsed.path})

        def _post(self):
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
                verdict = guard(payload.get("tool_name", ""),
                                payload.get("description", ""),
                                payload.get("args", {}))
                # The guard is the ONLY paid hop — so it's the only one whose
                # cost an auditor can be asked about. Record the verdict, never
                # the judge's reasoning (it quotes the attacker's payload back).
                self._trace("/guard", tool=payload.get("tool_name", ""),
                            blocked=verdict.get("blocked"), judged=verdict.get("judged"))
                self._send(200, verdict)
            except Exception as e:  # no LLM key / judge error → FAIL CLOSED, don't crash
                # `blocked: None` here was a fail-OPEN at the process boundary: it
                # threw away mcp_guard's fail-closed contract the moment the judge
                # was unreachable — exactly when you least want to execute. A guard
                # that can't judge must refuse. (`judged: false` keeps it honest:
                # this is a refusal for lack of a verdict, not a verdict.)
                self._send(200, {"blocked": True, "judged": False,
                                 "reason": f"fail-closed: guard unavailable: {type(e).__name__}",
                                 "detail": str(e)[:200]})

        def _trace(self, route: str, **fields) -> None:
            """The Python half of Lab 8's correlation seam (Move 6b).

            The Node server mints ONE id per tools/call and sends it on every
            upstream hop as `X-Correlation-Id` (plus the same value as the
            trace-id inside a W3C `traceparent`). Echoing it here is what makes
            a single tool call greppable ACROSS the process boundary:
            `grep <cid>` finds the Node audit record, the Node ops line, and
            this line. Two processes, one story."""
            cid = self.headers.get("X-Correlation-Id")
            if not cid:
                return                       # un-correlated call (curl, browser) — stay quiet
            print(json.dumps({"stream": "bridge", "correlation_id": cid,
                              "route": route, **fields}), flush=True)

        # An unhandled handler exception drops the TCP connection with no HTTP
        # response at all; the Lab 8 Node client then reports "fetch failed", which
        # sends the student debugging their TypeScript instead of this bridge.
        def _guarded(self, fn) -> None:
            try:
                fn()
            except Exception as e:
                try:
                    self._send(500, {"error": f"{type(e).__name__}: {str(e)[:200]}",
                                     "hint": "raised inside the Python corpus bridge, "
                                             "not in your MCP server"})
                except Exception:
                    pass

        def do_GET(self):   # noqa: N802 (http.server API name)
            self._guarded(self._get)

        def do_POST(self):  # noqa: N802 (http.server API name)
            self._guarded(self._post)

        def log_message(self, *args):  # keep the default apache-style noise off
            return

    class _Server(ThreadingHTTPServer):
        allow_reuse_address = True     # re-running the cell shouldn't hit TIME_WAIT

    try:
        httpd = _Server(("127.0.0.1", port), _Handler)
    except OSError as e:
        # Lab 8 says "leave this running", so a second start is the likely path.
        raise RuntimeError(
            f"Port {port} is already in use — the corpus bridge is probably already "
            f"running in another terminal or cell. Reuse it, or start this one on "
            f"another port: python -m mai_rag.bridge --port {port + 1}"
        ) from None
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


if __name__ == "__main__":  # `python -m mai_rag.bridge` — the one command the lab runs
    import argparse
    import pathlib
    import time

    from . import corpus

    # Same .env shim as the labs: /guard is the one LLM-touching endpoint, and the
    # student's key lives in the repo-root .env (never printed, never committed).
    for _cand in (pathlib.Path(".env"), pathlib.Path(__file__).resolve().parent.parent / ".env"):
        if _cand.exists():
            try:                                     # utf-8-sig eats a Windows Notepad BOM,
                _txt = _cand.read_text(encoding="utf-8-sig")   # which otherwise corrupts the FIRST key
            except (OSError, UnicodeDecodeError):
                _txt = ""                            # an unreadable .env must never crash the import
            for _line in _txt.splitlines():
                _line = _line.strip()
                if _line.startswith("export "):        # people paste shell-style lines into .env
                    _line = _line[7:].lstrip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    _v = _v.strip()
                    if len(_v) > 1 and _v[0] == _v[-1] and _v[0] in ("\'", '"'):
                        _v = _v[1:-1]                # quoted: take it verbatim
                    elif " #" in _v:
                        _v = _v.split(" #", 1)[0].strip()   # unquoted: drop a trailing comment
                    os.environ.setdefault(_k.strip(), _v)
            break

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
