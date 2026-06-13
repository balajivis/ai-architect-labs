# Lab 8 · `mcp_server/` — your Streamable-HTTP MCP server (the Python→Node seam)

This is the **kit's only non-Python lab artifact**. Labs 1–7 stayed in Python.
Here the policy-RAG capability you built leaves the notebook and becomes *a thing
other agents can call* — an **MCP server**, in TypeScript, on the **same
`@modelcontextprotocol/sdk` version (1.26.0)** Kapi's production client pins.

The corpus, embeddings, and evals stay in **Python** behind a thin keyless HTTP
bridge (`mai_rag.bridge.serve_corpus`). This Node server holds no corpus — it
calls that one upstream. That split *is* the lesson: you stop *calling* tools and
start *being* the thing that's called.

> **Spec label — read every move with this in mind.**
> **CURRENT (2025-11-25):** Streamable HTTP on a single `/mcp`, `initialize`
> handshake + sticky `Mcp-Session-Id` sessions. This is what you build.
> **COMING (2026-07-28 RC, SEP-2575):** stateless-first — any instance serves any
> request, capabilities per-request in `_meta`, a Tasks primitive for durability.
> The RC ships **after this cohort**: you engineer stateful today, design
> stateless. No stateless code path exists in this scaffold yet (documentation
> only); a later `git pull` may add a `server.stateless.ts` variant.

---

## Prerequisite: Node 20+ (NEW for this lab)

The Python labs only needed a venv + `.env`. **This lab also needs Node 20+ and
npm.** If you're a Python-labs student with no Node, install it with nvm:

```bash
nvm install 20        # or: brew install node@20  /  see nodejs.org
node --version        # must print v20.x or newer
```

> **Local VS Code only — NOT Colab.** This lab runs three processes over
> localhost at once (Node server + Python bridge + the notebook kernel). Colab
> cannot host that in one session. **Colab fallback is read-only**: follow along
> via the shipped screenshots + recorded harness output; the notebook's headless
> structural checks run where reachable, but the live build is local.

---

## Run steps

### 1. Install the Node deps (once, in a terminal — not a notebook cell)

```bash
cd labs/mcp_server
npm install            # pulls @modelcontextprotocol/sdk@1.26.0 + express + zod
```

### 2. Start the Python bridge (Move 1) — from the notebook

The bridge is the **one** Python upstream this server calls. Start it as an
explicit background process in the lab so you can *see* the second process:

```python
from mai_rag import bridge, corpus
store = corpus.load_policy_corpus("policy.db")
httpd = bridge.serve_corpus(store, port=8765)   # MCP_BRIDGE_PORT
# ... when you're done: httpd.shutdown()
```

Confirm it: `curl "http://127.0.0.1:8765/search?q=parental+leave&k=3"`.

### 3. Start the MCP server

```bash
cd labs/mcp_server
npm start              # node --experimental-strip-types server.ts -> :9000/mcp
```

It reads ports from your environment (`MCP_BRIDGE_PORT=8765`,
`MCP_SERVER_PORT=9000`). Auth is **off** for Moves 3–4 (`AUTH_ENABLED` unset); at
Move 5 you start it with `AUTH_ENABLED=1` and switch the `.mcp.json` profile.

### 4. Consume it (Move 3)

- **Claude Code / Cursor:** the shipped `.mcp.json` points a host at
  `http://127.0.0.1:9000/mcp` (no-auth profile active).
- **MCP Inspector:** `npx @modelcontextprotocol/inspector` — no install. List
  tools, hand-invoke `policy_search('VPN split tunneling')`, eyeball the content.

---

## What's LIVE vs what you finish (WIP map)

| File | Live now | You complete |
|------|----------|--------------|
| `server.ts` | Streamable-HTTP transport + session wiring + **`policy_search` worked end-to-end** | **`policy_get`** tool — `// WIP: TODO` (Move 2) |
| `auth.ts` | **401 + `WWW-Authenticate` PRM emitter** (RFC 9728) | **RFC 8707 `aud` comparison** — one-line `// WIP: TODO` (Move 5); wrong-audience assertion fails until done |
| `.mcp.json` | no-auth `policy` profile | switch to the bearer profile at Move 5 |
| `package.json`, `tsconfig.json` | pinned deps + TS config | — |

Credentials are **env-only**: `MCP_DEV_TOKEN` / expected `aud` come from `.env`
(git-ignored). Nothing secret is written into a `.ts`/`.json`/`.md` file —
`.mcp.json`'s `${MCP_DEV_TOKEN}` resolves from your shell, never a pasted token.

> **Borrowed shape, not transport.** The tool-handler shape and error-code
> vocabulary (`textBlock` helper, `-32601`/`-32000`/`-32602`) echo workshop-kit
> `mcp/server.mjs`. That file is an OLDER-spec (2024-11-05), stdio, raw-JSON-RPC
> example — its transport/handshake is **replaced** here by `McpServer` +
> Streamable HTTP. Borrow the shape; don't treat it as a same-spec reference.
