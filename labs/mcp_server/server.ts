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
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { oauthResourceServer } from "./auth.ts";

const BRIDGE_PORT = process.env.MCP_BRIDGE_PORT || "8765";
const SERVER_PORT = Number(process.env.MCP_SERVER_PORT || "9000");
const BRIDGE = `http://127.0.0.1:${BRIDGE_PORT}`;
const AUTH_ENABLED = process.env.AUTH_ENABLED === "1"; // OFF for Moves 3–4, ON at Move 5

/** A well-formed MCP text content block. Mirrors server.mjs's `textBlock`. */
const textBlock = (text: string) => ({ content: [{ type: "text" as const, text }] });

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
      description: "Semantic search over the enterprise-policy corpus. Returns the top-k ranked policy citations (source, title, score, snippet).",
      inputSchema: {
        query: z.string().describe("natural-language policy question"),
        k: z.number().int().min(1).max(20).default(5).describe("how many citations to return"),
      },
    },
    async ({ query, k }) => {
      const url = `${BRIDGE}/search?q=${encodeURIComponent(query)}&k=${k}`;
      const resp = await fetch(url);
      if (!resp.ok) {
        // -32000: server-side execution error (bridge unreachable / non-200).
        throw new Error(`bridge /search failed: ${resp.status}`);
      }
      const data = (await resp.json()) as { hits: Array<{ source: string; title: string; score: number; content: string }> };
      const lines = data.hits.map(
        (h, i) => `${i + 1}. [${h.source}] ${h.title} (score ${h.score})\n   ${h.content.slice(0, 240)}`,
      );
      return textBlock(lines.length ? lines.join("\n") : "no matching policy found");
    },
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

app.listen(SERVER_PORT, () => {
  console.log(`lab8 MCP server (Streamable HTTP) on http://127.0.0.1:${SERVER_PORT}/mcp`);
  console.log(`  -> bridging to keyless Python corpus at ${BRIDGE}`);
  console.log(`  -> auth ${AUTH_ENABLED ? "ENABLED (Move 5+)" : "disabled (Moves 3–4)"}`);
});
