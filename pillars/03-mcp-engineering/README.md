# Pillar III · MCP Engineering

> **Layer:** Integration · **Time:** ~4 hrs · **70% hands-on**
> **Lab kit:** TypeScript MCP SDK + MCP Inspector (this pillar is Node, not Python).

## Thesis

**Anyone can call an MCP server. Production means building one that authenticates, survives failure, and scales** — and the spec is mid-transition, so you engineer for *today's* stateful model while designing for *tomorrow's* stateless one. The server you build in Module 2 is the fixture; Modules 3–4 harden the *same* server.

## ⚠️ Spec-version note (label every lesson)

- **Stable today:** spec **2025-11-25** — `initialize` handshake, `Mcp-Session-Id` sessions, capability negotiation at init.
- **Coming (RC, not yet shipped):** **stateless-first** (SEP-2575) — handshake removed, session IDs gone, protocol/capabilities in `_meta` per-request, a new **Tasks** primitive for durability. This *is* the scale story.
- Transports: **stdio** (local) + **Streamable HTTP** (remote, single `/mcp`). HTTP+SSE is deprecated.

## Modules

| # | Module | What you build | Lab |
|---|---|---|---|
| 1 | **Architecture & Consume** | register + inspect a server from Claude Code | `.mcp.json` + `npx @modelcontextprotocol/inspector` |
| 2 | **Build a Server** | a Streamable-HTTP server exposing 2–3 tools over the policy corpus | `mcp-sdk-typescript` |
| 3 | **OAuth 2.1 & Security** | 401→PRM→token flow; **audience binding (RFC 8707)**; tool-poisoning defense | local AS + ngrok |
| 4 | **Resilience & Scale** | timeouts, retries+backoff, tool-list cache, capability/version negotiation | load-test stateful vs stateless |

## Key ideas

- **Primitives:** server→client = *tools, resources, prompts*; client→server = *sampling, roots, elicitation*.
- **Auth is OAuth-2.1 resource-server:** PRM discovery (RFC 9728) → AS metadata → PKCE → **audience-bound tokens**. **Token passthrough is forbidden** — a server MUST NOT accept a token not issued for it.
- **The whole tool schema is the LLM's context = attack surface** — tool poisoning, rug-pulls, confused-deputy. Pin by hash, verify schemas in CI.
- **Scale = statelessness:** stateful sessions force sticky routing / shared store; stateless-first lets any request hit any instance.

## Lab setup

```bash
npm i @modelcontextprotocol/sdk
npx @modelcontextprotocol/inspector node ./server.mjs
```
A minimal working server (blackboard read/write + task claiming) ships as the Module 2 worked example. Build, inspect, then harden it.
