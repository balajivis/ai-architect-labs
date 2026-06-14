# Lab 8 · MCP — Build a Server (then harden it)

**This is the one TypeScript/Node lab.** Labs 1–7 hardened a policy-RAG app *in
process* (Python). Here that same capability becomes **a thing other agents can
call** — an MCP server — and crosses a process/network boundary.

> **Why the language switches to Node — and why that's the lesson.** The
> guardrails, ACLs, and HITL gates you built in Labs 6–7 **do not travel across
> the wire.** Once retrieval is exposed as a *tool* an arbitrary client invokes,
> the server must **re-enforce** trust: authenticate the caller (OAuth), reject
> wrong-audience tokens (RFC 8707), and refuse poisoned tool calls. The Node
> switch isn't a tooling accident — it's where "I called my own function" becomes
> "an untrusted client called my tool." Build accordingly.

Spec note on every move: **current = 2025-11-25** (stateful, `Mcp-Session-Id`
sessions, what you build here) vs **coming = 2026-07-28 RC / SEP-2575**
(stateless-first; ships *after* this cohort — design forward, don't build on it).

---

## Prerequisites

- **Node 22+** (`nvm install 22`) — the scaffold runs `.ts` directly via
  `node --experimental-strip-types`, no build step.
- The **Python corpus bridge** — the server holds no corpus; it calls a tiny
  keyless Python HTTP wrapper over the `mai_rag` store (the only Python you run).
  Install the kit once (`pip install -e ".[evals,viz]"` from the repo root) so
  `python -m mai_rag.bridge` works.
- An **LLM key** in `.env` (Groq free tier is fine) — only Move 6's
  tool-poisoning guard reaches a model; everything else is keyless.

## Run it — three terminals

```bash
# 1) the keyless corpus bridge (:8765)
python -m mai_rag.bridge                 # add --corpus catalog if you prefer

# 2) your MCP server (:9000)
cd labs/mcp_server && npm install
npm start                                # Moves 2–4 (auth off)
AUTH_ENABLED=1 npm start                 # Moves 5+ (OAuth on)

# 3) the test harness — your move-by-move to-do list
npm test
```

A failing harness line is the signal you still have that Move's TODO to finish —
same idea as Lab 5's eval gate, but the gate here is a **protocol contract**, not
a score.

---

## The arc — consume → build → harden → scale (7 moves)

| Move | You do | The win | File |
|---|---|---|---|
| **1** | Start the bridge; `curl http://127.0.0.1:8765/search?q=parental+leave` | the corpus is reachable over HTTP — the Python→Node seam | `mai_rag/bridge.py` |
| **2 ⭐** | Register `policy_get` (mirror the worked `policy_search`) with a JSON-Schema `inputSchema` | `tools/list` returns **2** tools; harness Move 4 goes green | `server.ts` (`// WIP: TODO`) |
| **3** | Point Claude Code at it (`.mcp.json`) and inspect with `npx @modelcontextprotocol/inspector` | you call your own server's tools from a real client | `.mcp.json` |
| **4** | `npm test` — one happy path + one schema violation per tool | a bad arg (`k:"four"`) is rejected `-32602`, not silently run | `harness.ts` |
| **5 ⭐** | Finish the RFC 8707 `aud` comparison; run `AUTH_ENABLED=1 npm start` | no-token → **401 + PRM**; wrong-audience → **403** | `auth.ts` (`// WIP: TODO`) |
| **6 ⭐** | Wire the server's tool handler to call `POST /guard` before executing | a poisoned tool description is **blocked** (LLM-judged, **no regex**) | `server.ts` + `mai_rag/mcp_guard.py` |
| **7** | Add a timeout + retry-with-backoff + a `tools/list` cache to the client path | the client survives a transient failure and a tool-list refresh | guided exercise |

**The teaching insight (Move 2):** a tool's `description` and `inputSchema` *are
the prompt* — a precise schema steers the model to call the tool correctly; a
vague one makes it misfire. Spend time on the descriptions.

---

## What ships LIVE vs WIP (you complete the WIP)

| | Status |
|---|---|
| `policy_search` tool (calls the bridge) | **LIVE** worked example |
| Streamable-HTTP transport + sessions | **LIVE** |
| 401 + `WWW-Authenticate: …resource_metadata=` (PRM) emitter | **LIVE** (`auth.ts`) |
| no-auth `.mcp.json` profile | **LIVE** |
| `mai_rag.mcp_guard.guard` (tool-poisoning judge, fails closed) | **LIVE**, fail-safe |
| `policy_get` tool | **WIP** — Move 2 TODO |
| RFC 8707 `aud` comparison | **WIP** — Move 5 TODO (`audMismatch = false`) |
| server-side guard enforcement + resilience | **WIP** — Moves 6–7 |
| stateless-first RC (2026-07-28) | documentation-only by design |

This lab is **work-in-progress shipped via `git pull`** — completing the TODOs
*is* the lab.
