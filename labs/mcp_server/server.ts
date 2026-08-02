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
      // ── Move 6 (WIP: TODO) — ask the guard BEFORE executing ───────────────
      // WIP: TODO — POST the tool's name + description + args to the bridge's
      //   `/guard` endpoint (Move 6 probed it from the outside; now ENFORCE it
      //   from the inside), and refuse the call when the judge blocks it:
      //
      //     const g = await fetch(`${BRIDGE}/guard`, {
      //       method: "POST",
      //       headers: { "content-type": "application/json", ...traceHeaders(cid) },
      //       body: JSON.stringify({ tool_name: tool, description: TOOL_DESCRIPTIONS[tool], args }),
      //     }).then((r) => r.json());
      //     guard = { verdict: g.blocked === null ? "unavailable" : g.blocked ? "blocked" : "clean",
      //               reason_code: g.blocked ? "guard_blocked" : null, engine: "mai_rag.mcp_guard" };
      //     if (g.blocked) { decision = "deny_guard"; reason = "guard_blocked";
      //                      return textBlock("refused: this tool call was blocked by the poisoning guard"); }
      //
      //   Note the posture: `blocked === null` (no LLM key / judge error) is
      //   "unavailable", NOT "clean" — never let a fail-open be recorded as a pass.
      //   Until you wire this, the audit record says guard.verdict "unavailable"
      //   on every call, and the Move-6b tutor stage tells you so.

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

  // ── TOOL 2 (TODO — you finish this in Move 2): policy_get ──────────────────
  // WIP: TODO — register a `policy_get` tool that returns ONE full policy doc.
  //   It should mirror policy_search above:
  //     • inputSchema: { source: z.string().describe("the policy doc id, e.g. hr-parental-leave-active") }
  //     • handler: fetch `${BRIDGE}/doc/${encodeURIComponent(source)}`, and
  //         - on 200  -> return textBlock(`# ${data.title}\n\n${data.content}`)
  //         - on 404  -> return textBlock(`no policy found for "${source}"`)
  //         - on other non-ok -> throw new Error(...) (surfaces as a -32000)
  //   Until you register it, `tools/list` returns only 1 tool and the Move-2
  //   harness assertion `names == {'policy_search','policy_get'}` FAILS — that
  //   failing assertion is the signal you still have this TODO to finish.
  //
  //   server.registerTool("policy_get", { ...inputSchema... }, async ({ source }) => { ... });
  //
  //   Move 6b adds one more requirement to this same tool: wrap your handler in
  //   auditedTool("policy_get", { risk: "read" }, ...) — see the LIVE
  //   policy_search above — so that EVERY tool call lands in the audit trail.

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

  // ── RESOURCE 2 (TODO — you finish this in Move 2b): a TEMPLATED resource ──
  // WIP: TODO — register a TEMPLATED resource `policy://doc/{source}` that
  //   returns ONE full policy document. Mirror the static resource above:
  //     • first arg:  "policy-doc"
  //     • second arg: new ResourceTemplate("policy://doc/{source}", { list: undefined })
  //         - the `list` key is MANDATORY in this SDK, even when you pass
  //           `undefined` (that means "this template does not enumerate").
  //           Enumerating is the catalog resource's job, above.
  //     • third arg:  { title, description, mimeType: "text/markdown" }
  //     • callback:   async (uri, variables) => { ... }
  //         - `variables.source` is the matched {source} (a string | string[] —
  //           wrap it: String(variables.source))
  //         - fetch `${BRIDGE}/doc/${encodeURIComponent(source)}`
  //         - return { contents: [{ uri: uri.href, mimeType: "text/markdown",
  //                                 text: `# ${data.title}\n\n${data.content}` }] }
  //         - on 404 return a contents block saying no policy was found —
  //           a resource read is a GET, so "missing" is data, not an exception
  //
  //   Until you register it, `resources/templates/list` comes back EMPTY and the
  //   Move-2b stage fails with a pointer at this TODO.
  //
  //   ResourceTemplate is already imported at the top of this file.
  //
  //   server.registerResource("policy-doc", new ResourceTemplate(...), { ... }, async (uri, variables) => { ... });


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
