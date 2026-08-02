/**
 * server.ts — Lab 8, Move 2: the MCP SERVER you build.
 *
 * The BUILD beat of the consume -> build -> harden spine. Labs 1–7 stayed in
 * Python; here the same policy-RAG capability becomes *a thing other agents can
 * call* — an MCP server, in TypeScript, on the SAME `@modelcontextprotocol/sdk`
 * version (1.26.0) Kapi's production client pins (`^1.26.0`).
 *
 * Transport: **Streamable HTTP** on a single `/mcp` endpoint (the CURRENT
 * 2025-11-25 spec). stdio is the local fallback; the old HTTP+SSE transport is
 * DEPRECATED — do not build new servers on it. The COMING RC (2026-07-28,
 * SEP-2575) is stateless-first; this scaffold is stateful (sessioned) by design
 * and labels where that changes.
 *
 * The seam: this Node server holds NO corpus. It calls the keyless Python bridge
 * from Move 1 (`mai_rag.bridge.serve_corpus`) over HTTP — exactly one Python
 * upstream. Retrieval stays in Python; the server is just the MCP envelope.
 *
 * Shape note: the tool-handler SHAPE and error-code vocabulary (textBlock helper,
 * -32601/-32000/-32602) are borrowed from workshop-kit `mcp/server.mjs` — but
 * that file is an OLDER-spec (2024-11-05), stdio, raw-JSON-RPC example. Its
 * transport/handshake is REPLACED here by McpServer + Streamable-HTTP. Borrow the
 * shape, not the transport.
 */
import { randomUUID } from "node:crypto";
import express from "express";
import { z } from "zod";
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { oauthResourceServer } from "./auth.ts";
import { appendAudit, logJson, newCorrelationId, safeArgs, tokenId, traceHeaders } from "./audit.ts";

const BRIDGE_PORT = process.env.MCP_BRIDGE_PORT || "8765";
const SERVER_PORT = Number(process.env.MCP_SERVER_PORT || "9000");
const BRIDGE = `http://127.0.0.1:${BRIDGE_PORT}`;
const AUTH_ENABLED = process.env.AUTH_ENABLED === "1"; // OFF for Moves 3–4, ON at Move 5
const SERVER_ID = `lab8-policy-mcp@0.1.0/${process.pid}`;

/** A well-formed MCP text content block. Mirrors server.mjs's `textBlock`. */
const textBlock = (text: string) => ({ content: [{ type: "text" as const, text }] });

// ── Move 6b: the audited tool path ───────────────────────────────────────────
// EVERY tool call goes through here. The wrapper owns the four things a tool
// handler must never be trusted to remember: mint a correlation id, ask the
// guard, time the call, and write exactly one audit record — including when the
// call FAILS or is REFUSED (those are the records an auditor actually reads).
type ToolCtx = { cid: string; resourceIds: string[]; bytes: number; count: number };

function auditedTool(
  tool: string,
  opts: { freeText?: string[]; risk: "read" | "write" },
  handler: (args: Record<string, any>, ctx: ToolCtx) => Promise<ReturnType<typeof textBlock>>,
) {
  return async (args: Record<string, any>, extra: any) => {
    const cid = newCorrelationId();               // one id per tools/call — not per HTTP request
    const t0 = Date.now();
    const ctx: ToolCtx = { cid, resourceIds: [], bytes: 0, count: 0 };
    const auth = extra?.authInfo;                 // set by auth.ts middleware → req.auth
    let decision = "allow";
    let reason = "ok";
    let guard: Record<string, unknown> = { verdict: "unavailable", reason_code: null, engine: null };

    try {
      // ── Move 6 — ask the guard BEFORE executing ───────────────────────────
      // Move 6 probed POST /guard from the OUTSIDE; this is the same judge
      // ENFORCED from the inside, on the path every tool call has to take.
      // Both surfaces the attacker controls go over: the tool's advertised
      // description AND the caller's args.
      let g: { blocked?: boolean; judged?: boolean; reason?: string };
      try {
        const resp = await fetch(`${BRIDGE}/guard`, {
          method: "POST",
          headers: { "content-type": "application/json", ...traceHeaders(cid) },
          body: JSON.stringify({ tool_name: tool, description: TOOL_DESCRIPTIONS[tool] ?? "", args }),
        });
        if (!resp.ok) throw new Error(`bridge /guard failed: ${resp.status}`);
        g = (await resp.json()) as typeof g;
      } catch (e) {
        // The guard being unreachable is not permission to run. A control that
        // disappears when the network hiccups is not a control.
        g = { blocked: true, judged: false, reason: `fail-closed: guard unreachable: ${(e as Error).message.slice(0, 80)}` };
      }

      // Three states, never two. `judged: false` means we never got a verdict —
      // recording that as "clean" would be logging a fail-open as a pass.
      const verdict = g.judged === false ? "fail_closed" : g.blocked ? "blocked" : "clean";
      guard = {
        verdict,
        reason_code: g.blocked ? (g.judged === false ? "guard_unavailable" : "guard_blocked") : null,
        engine: "mai_rag.mcp_guard",
      };
      if (g.blocked) {
        decision = g.judged === false ? "deny_guard_unavailable" : "deny_guard";
        reason = String(guard.reason_code);
        return textBlock(
          g.judged === false
            ? `refused: the poisoning guard could not judge this call, so it refused it (${g.reason ?? "no verdict"})`
            : "refused: this tool call was blocked by the poisoning guard",
        );
      }

      const out = await handler(args, ctx);
      return out;
    } catch (e) {
      decision = "error_upstream";
      reason = (e as Error).message.slice(0, 60);
      throw e;
    } finally {
      // ONE record per call, written on every path — success, refusal, throw.
      appendAudit({
        event: "mcp.tool.call",
        correlation_id: cid,
        session_id: extra?.sessionId ?? null,
        server: SERVER_ID,
        auth: AUTH_ENABLED ? "oauth2.1" : "disabled",   // the honesty field
        actor: {
          sub: auth?.extra?.sub ?? null,
          aud: auth?.extra?.aud ?? null,                // RFC 8707 evidence, after the fact
          client_id: auth?.clientId ?? null,
          token_id: tokenId(auth?.token, auth?.extra?.jti as string | undefined),
        },
        tool,
        risk: opts.risk,
        args_safe: safeArgs(args, opts.freeText),      // references, never payloads
        resource_ids: ctx.resourceIds,                 // WHICH documents this subject touched
        result: { count: ctx.count, bytes: ctx.bytes },// volume, not content — exfiltration shows up here
        decision,
        decision_reason: reason,                       // stable code, not prose
        guard,
        duration_ms: Date.now() - t0,
      });
      logJson({ stream: "ops", correlation_id: cid, tool, decision, ms: Date.now() - t0 });
    }
  };
}

// A tool's DESCRIPTION is part of the model's context — which is exactly why
// Move 6's guard judges it. Keeping them in one table means the server can hand
// the same text to the guard that it advertises in `tools/list`.
const TOOL_DESCRIPTIONS: Record<string, string> = {
  policy_search: "Semantic search over the enterprise-policy corpus. Returns the top-k ranked policy citations (source, title, score, snippet).",
  policy_get: "Return one full enterprise-policy document by its source id.",
};

// ── Build the server + register tools ────────────────────────────────────────
function buildServer(): McpServer {
  const server = new McpServer({ name: "lab8-policy-mcp", version: "0.1.0" });

  // ── TOOL 1 (WORKED EXAMPLE): policy_search ────────────────────────────────
  // Calls the Move-1 Python bridge `GET /search`, returns ranked citations as a
  // single text block. This one is DONE end-to-end — study it, then mirror it
  // for policy_get below.
  server.registerTool(
    "policy_search",
    {
      title: "Search the enterprise policy corpus",
      description: TOOL_DESCRIPTIONS.policy_search,
      inputSchema: {
        query: z.string().describe("natural-language policy question"),
        k: z.number().int().min(1).max(20).default(5).describe("how many citations to return"),
      },
    },
    // Move 6b: wrapped. `query` is declared FREE TEXT — the tool author decides
    // what is sensitive, not a detector — so the audit log stores its digest,
    // never the user's actual question.
    auditedTool("policy_search", { freeText: ["query"], risk: "read" }, async ({ query, k }, ctx) => {
      const url = `${BRIDGE}/search?q=${encodeURIComponent(query)}&k=${k}`;
      const resp = await fetch(url, { headers: traceHeaders(ctx.cid) });  // stitch Node → Python
      if (!resp.ok) {
        // -32000: server-side execution error (bridge unreachable / non-200).
        throw new Error(`bridge /search failed: ${resp.status}`);
      }
      const data = (await resp.json()) as { hits: Array<{ source: string; title: string; score: number; content: string }> };
      const lines = data.hits.map(
        (h, i) => `${i + 1}. [${h.source}] ${h.title} (score ${h.score})\n   ${h.content.slice(0, 240)}`,
      );
      const text = lines.length ? lines.join("\n") : "no matching policy found";
      ctx.resourceIds = [...new Set(data.hits.map((h) => h.source))];   // WHICH docs were served
      ctx.count = data.hits.length;
      ctx.bytes = text.length;
      return textBlock(text);
    }),
  );

  // ── TOOL 2: policy_get ─────────────────────────────────────────────────────
  // Mirrors policy_search: one bridge hop, one text block, audited by the same
  // wrapper. `source` is a document ID, not free text — so it is logged in the
  // clear (that is the WHICH-doc evidence an auditor needs), unlike `query`.
  server.registerTool(
    "policy_get",
    {
      title: "Fetch one policy document",
      description: TOOL_DESCRIPTIONS.policy_get,
      inputSchema: {
        source: z.string().describe("the policy doc id, e.g. hr-parental-leave-active"),
      },
    },
    auditedTool("policy_get", { risk: "read" }, async ({ source }, ctx) => {
      const resp = await fetch(`${BRIDGE}/doc/${encodeURIComponent(source)}`, { headers: traceHeaders(ctx.cid) });
      if (resp.status === 404) {
        // A missing doc is an ANSWER, not a server fault — don't spend a -32000
        // on it, and don't let the model read a transport error as "no policy".
        const text = `no policy found for "${source}"`;
        ctx.bytes = text.length;
        return textBlock(text);
      }
      if (!resp.ok) throw new Error(`bridge /doc failed: ${resp.status}`);   // -32000: execution error
      const data = (await resp.json()) as { source: string; title: string; content: string };
      const text = `# ${data.title}\n\n${data.content}`;
      ctx.resourceIds = [data.source];
      ctx.count = 1;
      ctx.bytes = text.length;
      return textBlock(text);
    }),
  );

  // ══ MOVE 2b · THE OTHER TWO PRIMITIVES ══════════════════════════════════════
  // A server is not just tools. MCP has three primitives, and the difference
  // between them is WHO IS IN CONTROL:
  //
  //   TOOLS      — MODEL-controlled.       The model decides to call it. Side effects live here.
  //   RESOURCES  — APPLICATION-controlled. The client app decides what to attach as context. Like GET: no side effects.
  //   PROMPTS    — USER-controlled.        The human picks it (a slash command, a menu item).
  //
  // Get this wrong and the model does the app's job: exposing "read the corpus
  // index" as a TOOL invites the model to burn a turn deciding to call it, when
  // the app should simply have attached it.

  // ── RESOURCE 1 (WORKED EXAMPLE): a STATIC resource ────────────────────────
  // The corpus index — stable, cheap, no query needed. Exactly the kind of
  // reference data an application attaches without asking the model first.
  server.registerResource(
    "policy-catalog",
    "policy://catalog",
    {
      title: "Policy corpus catalog",
      description: "The index of every policy document: source id + title.",
      mimeType: "application/json",
    },
    async (uri) => {                                  // uri is a WHATWG URL, not a string
      const resp = await fetch(`${BRIDGE}/docs`);
      if (!resp.ok) throw new Error(`bridge /docs failed: ${resp.status}`);
      const data = (await resp.json()) as { docs: Array<{ source: string; title: string }> };
      return {
        contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify(data.docs, null, 2) }],
      };
    },
  );

  // ── RESOURCE 2: a TEMPLATED resource ──────────────────────────────────────
  // Same document as policy_get, reached the other way round. That duplication
  // is the POINT of Move 2b: when the app already knows which doc it wants, it
  // ATTACHES this — no model turn spent deciding to call a tool. The tool exists
  // for when the MODEL has to make that choice.
  server.registerResource(
    "policy-doc",
    // `list: undefined` = this template does not enumerate. Enumerating is the
    // catalog resource's job above. The key is mandatory even when undefined.
    new ResourceTemplate("policy://doc/{source}", { list: undefined }),
    {
      title: "One policy document",
      description: "Read a single enterprise-policy document by its source id.",
      mimeType: "text/markdown",
    },
    async (uri, variables) => {
      const source = String(variables.source);           // string | string[] on the wire
      const resp = await fetch(`${BRIDGE}/doc/${encodeURIComponent(source)}`);
      if (resp.status === 404) {
        // A read is a GET: "missing" is data the app can render, not an exception.
        return {
          contents: [{ uri: uri.href, mimeType: "text/markdown", text: `no policy found for "${source}"` }],
        };
      }
      if (!resp.ok) throw new Error(`bridge /doc failed: ${resp.status}`);
      const data = (await resp.json()) as { source: string; title: string; content: string };
      return {
        contents: [{ uri: uri.href, mimeType: "text/markdown", text: `# ${data.title}\n\n${data.content}` }],
      };
    },
  );


  // ── PROMPT (WORKED EXAMPLE): a USER-controlled template ───────────────────
  // This is what appears as a slash command in a client. Note what it is NOT:
  // it does not call the corpus, it does not answer anything. A prompt returns
  // MESSAGES — a starting position for the conversation, with the house style
  // already baked in so every analyst gets the same rigour.
  server.registerPrompt(
    "policy_briefing",
    {
      title: "Policy briefing",
      description: "Draft a cited briefing on a policy topic for a given audience.",
      argsSchema: {
        // MCP prompt arguments are Record<string,string> ON THE WIRE — every
        // argument must be a string schema. Take a string, coerce inside.
        topic: z.string().describe("the policy topic, e.g. parental leave"),
        audience: z.string().optional().describe("who the briefing is for, e.g. new managers"),
      },
    },
    async ({ topic, audience }) => ({
      description: `Policy briefing on ${topic}`,
      messages: [
        {
          role: "user" as const,
          content: {
            type: "text" as const,
            text:
              `Write a briefing on "${topic}" for ${audience ?? "the whole company"}.\n\n` +
              `Rules: use policy_search to gather citations first. Cite every claim as [source-id]. ` +
              `If the corpus does not cover something, say so plainly instead of filling the gap. ` +
              `Where two policies conflict, name both and flag which is active.`,
          },
        },
      ],
    }),
  );

  return server;
}

// ── Streamable-HTTP transport on a single `/mcp` endpoint ─────────────────────
// CURRENT (2025-11-25): the client `initialize`s once, gets an `Mcp-Session-Id`,
// and reuses it. Sessions force a shared store / sticky routing — the COMING RC
// (2026-07-28, SEP-2575) drops this for stateless-first. We keep a per-session
// transport map here; swap to stateless `new StreamableHTTPServerTransport({})`
// per request once the RC ships (out of scope for this lab — documentation-only).
const transports: Record<string, StreamableHTTPServerTransport> = {};

const app = express();
app.use(express.json());

// Move 5: flip auth on with AUTH_ENABLED=1. OFF for Moves 3–4 (pre-auth server).
if (AUTH_ENABLED) {
  app.use("/mcp", oauthResourceServer);
}

app.post("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  let transport = sessionId ? transports[sessionId] : undefined;

  if (!transport && isInitializeRequest(req.body)) {
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
      onsessioninitialized: (sid) => { transports[sid] = transport!; },
    });
    transport.onclose = () => {
      if (transport!.sessionId) delete transports[transport!.sessionId];
    };
    await buildServer().connect(transport);
  }

  if (!transport) {
    res.status(400).json({
      jsonrpc: "2.0",
      error: { code: -32000, message: "no valid session — send an initialize request first" },
      id: null,
    });
    return;
  }
  await transport.handleRequest(req, res, req.body);
});

// GET (server->client SSE stream) and DELETE (session teardown) reuse the session.
const reuse = async (req: express.Request, res: express.Response) => {
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  const transport = sessionId ? transports[sessionId] : undefined;
  if (!transport) { res.status(400).send("unknown or missing Mcp-Session-Id"); return; }
  await transport.handleRequest(req, res);
};
app.get("/mcp", reuse);
app.delete("/mcp", reuse);

app.listen(SERVER_PORT, "127.0.0.1", () => {   // bind loopback ONLY — match the URL we advertise, don't expose /mcp to the LAN
  console.log(`lab8 MCP server (Streamable HTTP) on http://127.0.0.1:${SERVER_PORT}/mcp`);
  console.log(`  -> bridging to keyless Python corpus at ${BRIDGE}`);
  console.log(`  -> auth ${AUTH_ENABLED ? "ENABLED (Move 5+)" : "disabled (Moves 3–4)"}`);
});
