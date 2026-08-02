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
AUTH_ENABLED=1 MCP_EXPECTED_AUD=http://127.0.0.1:9000/mcp npm start   # Moves 5+ (OAuth on)

# 3) the interactive tutor — the guided walk over all seven moves
npm run lab                              # same tutor UI as labs 1b/3/4b (Enter run · s skip · r retry · q quit)

# …and the raw assertion gate (headless, CI-shaped)
npm test
```

`npm run lab` drives the seven moves **live against the server you're editing**
(`lab_8.ts` + `tutor.ts` — a glass-box TypeScript port of `mai_rag/tutor.py`).
A failing stage is not a crash — it names the `// WIP: TODO` still open: finish
it, restart the server, press `r` to retry. `npm test` (harness.ts) asserts the
same contract headless — same idea as Lab 5's eval gate, but the gate here is a
**protocol contract**, not a score.

---

## The arc — consume → build → harden → scale (10 moves)

| Move | You do | The win | File |
|---|---|---|---|
| **1** | Start the bridge; `curl http://127.0.0.1:8765/search?q=parental+leave` | the corpus is reachable over HTTP — the Python→Node seam | `mai_rag/bridge.py` |
| **2 ⭐** | Register `policy_get` (mirror the worked `policy_search`) with a JSON-Schema `inputSchema` | `tools/list` returns **2** tools; harness Move 4 goes green | `server.ts` (`// WIP: TODO`) |
| **2b ⭐** | Register the templated resource `policy://doc/{source}` (the static `policy://catalog` + the `policy_briefing` prompt ship worked) | all **three** primitives, and the rule that orders them: the MODEL calls tools, the APPLICATION attaches resources, the USER picks prompts | `server.ts` (`// WIP: TODO`) |
| **3** | Point Claude Code at it (`.mcp.json`) and inspect with `npx @modelcontextprotocol/inspector` | you call your own server's tools from a real client | `.mcp.json` |
| **3b** | The consumer arc, interactively: **search** Glama's free keyless registry API (`glama.ai/api/mcp/v1/servers?query=…`) for service types, **consume** an open weather server (hosted NWS — pick a lat/lon, live forecast, zero auth), then meet **Tavily's** authed MCP: read its live **401 + PRM**, and unlock it with the `TAVILY_API_KEY` you already have from Lab 3 | discovery + both auth postures in the wild — and Move 5's handshake, consumed before you build it | `lab_8.ts` (tutor stage; `MCP3B_QUERY` / `MCP3B_PUBLIC_URL` / `MCP3B_AUTH_URL` / `MCP3B_TOKEN` overrides) |
| **3c** | The full **OAuth 2.1 dance** against Sentry's hosted MCP (free throwaway account — deliberately not your Google/GitHub): watch Dynamic Client Registration mint a client_id, approve in the browser, localhost catches the redirect, PKCE trades the code for a token, then call `whoami` | discovery → DCR → consent → scoped token, lived once as a client before you enforce it as a server in Move 5 | `lab_8.ts` (tutor stage; `MCP3C_URL` / `MCP3C_CALLBACK_PORT` overrides; interactive terminal only) |
| **4** | `npm test` — one happy path + one schema violation per tool | a bad arg (`k:"four"`) is rejected `-32602`, not silently run | `harness.ts` |
| **5 ⭐** | Finish the RFC 8707 `aud` comparison; run `AUTH_ENABLED=1 npm start` | no-token → **401 + PRM**; wrong-audience → **403** | `auth.ts` (`// WIP: TODO`) |
| **6 ⭐** | Wire the server's tool handler to call `POST /guard` before executing | a poisoned tool description is **blocked** (LLM-judged, **no regex**) | `server.ts` (`// WIP: TODO` inside `auditedTool`) + `mai_rag/mcp_guard.py` |
| **6b ⭐** | Route `policy_get` through `auditedTool()` too, so **every** tool call is audited | a hash-chained, tamper-evident trail that answers who/what/allowed/cost — storing references, never payloads | `audit.ts` (LIVE) + `server.ts` (`// WIP: TODO`) |
| **7** | Add timeout + retry-with-backoff + a circuit breaker + a `tools/list` cache to the client path | the client survives a transient failure, stops hammering a dead upstream, and refreshes its tool list | guided exercise |

**The teaching insight (Move 2):** a tool's `description` and `inputSchema` *are
the prompt* — a precise schema steers the model to call the tool correctly; a
vague one makes it misfire. Spend time on the descriptions.

---

## What ships LIVE vs WIP (you complete the WIP)

| | Status |
|---|---|
| `policy_search` tool (calls the bridge) | **LIVE** worked example |
| `policy://catalog` resource + `policy_briefing` prompt | **LIVE** worked examples (Move 2b) |
| `audit.ts` — hash-chained NDJSON trail, correlation ids, redaction | **LIVE**, and `verifyChain()` ships with it |
| Streamable-HTTP transport + sessions | **LIVE** |
| 401 + `WWW-Authenticate: …resource_metadata=` (PRM) emitter | **LIVE** (`auth.ts`) |
| no-auth `.mcp.json` profile | **LIVE** |
| `mai_rag.mcp_guard.guard` (tool-poisoning judge, fails closed) | **LIVE**, fail-safe |
| `policy_get` tool | **WIP** — Move 2 TODO |
| `policy://doc/{source}` templated resource | **WIP** — Move 2b TODO |
| RFC 8707 `aud` comparison | **WIP** — Move 5 TODO (`audMismatch = false`) |
| server-side guard enforcement | **WIP** — Move 6 TODO (inside `auditedTool`) |
| auditing `policy_get` | **WIP** — Move 6b TODO |
| client resilience (timeout · retry · breaker · cache) | **WIP** — Move 7, guided |
| stateless-first RC (2026-07-28) | documentation-only by design |

### The audit trail (Move 6b)

`audit.ts` writes `audit/mcp-audit-YYYY-MM-DD.ndjson` — append-only, `0600`,
**git-ignored** (it carries subject identifiers). Each record is hash-chained to
its predecessor, so an edit is *detectable*, not merely discouraged:

```bash
cat audit/*.ndjson | jq 'select(.decision != "allow")'   # every refusal
grep <correlation-id> audit/*.ndjson                     # …and the same id in terminal 1's bridge output
```

One correlation id per `tools/call` travels to the Python bridge as both
`x-correlation-id` and the trace-id inside a W3C `traceparent` — so the trail
graduates to OpenTelemetry or Langfuse later without a migration.

This lab is **work-in-progress shipped via `git pull`** — completing the TODOs
*is* the lab.
