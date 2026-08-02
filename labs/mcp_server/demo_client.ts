/**
 * demo_client.ts — a REAL MCP client, driving the Lab 8 server over the wire.
 *
 * Nothing here knows about the corpus, Python, or embeddings. It speaks MCP to
 * http://127.0.0.1:9000/mcp and nothing else. Every document you see below
 * travelled: client -> (MCP/Streamable HTTP) -> Node server -> (HTTP) -> Python
 * bridge -> mai_rag corpus, and back.
 */
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const MCP_URL = new URL(process.env.MCP_URL || "http://127.0.0.1:9000/mcp");
const rule = (t: string) => console.log(`\n\x1b[36m── ${t} ${"─".repeat(Math.max(0, 66 - t.length))}\x1b[0m`);
const text = (r: any) => (r.content as Array<{ text?: string }>).map((c) => c.text ?? "").join("");

const client = new Client({ name: "lab8-class-demo", version: "0.1.0" });
const transport = new StreamableHTTPClientTransport(MCP_URL);
await client.connect(transport);

rule("1 · handshake");
console.log(`connected to ${MCP_URL.href}`);
console.log(`server:      ${JSON.stringify(client.getServerVersion())}`);
console.log(`session id:  ${transport.sessionId}   <- Streamable HTTP, stateful (2025-11-25 spec)`);

rule("2 · discovery — what does this server offer?");
const { tools } = await client.listTools();
for (const t of tools) console.log(`TOOL      ${t.name.padEnd(16)} ${t.description?.slice(0, 72)}`);
const { resources } = await client.listResources();
for (const r of resources) console.log(`RESOURCE  ${r.uri.padEnd(16)} ${r.description}`);
const { resourceTemplates } = await client.listResourceTemplates();
for (const r of resourceTemplates) console.log(`TEMPLATE  ${r.uriTemplate.padEnd(16)} ${r.description}`);
const { prompts } = await client.listPrompts();
for (const p of prompts) console.log(`PROMPT    ${p.name.padEnd(16)} ${p.description}`);

rule("3 · MODEL-controlled: policy_search (tool call -> Python bridge)");
const t0 = Date.now();
const hits = await client.callTool({ name: "policy_search", arguments: { query: "how much parental leave do I get?", k: 3 } });
console.log(text(hits));
console.log(`\n(${Date.now() - t0} ms — includes the LLM poisoning guard, which ran BEFORE the tool did)`);

rule("4 · the payoff: policy_get — a FULL policy document, fetched through MCP");
const doc = await client.callTool({ name: "policy_get", arguments: { source: "leave-time-off-policy" } });
const body = text(doc);
console.log(body.split("\n").slice(0, 22).join("\n"));
console.log(`\n… [${body.length} chars total, ${body.split("\n").length} lines] — this text lives in the Python corpus, not in Node.`);

rule("5 · APPLICATION-controlled: the SAME doc as a resource read (no model turn)");
const res = await client.readResource({ uri: "policy://doc/leave-time-off-policy" });
const c0 = (res.contents[0] as { uri: string; mimeType?: string; text?: string });
console.log(`uri:      ${c0.uri}\nmimeType: ${c0.mimeType}\nfirst line: ${(c0.text ?? "").split("\n")[0]}`);
console.log(`identical body as the tool call? ${(c0.text ?? "") === body ? "YES" : "no"}   <- same doc, different control plane`);

rule("6 · a missing doc is DATA, not a crash");
console.log(text(await client.callTool({ name: "policy_get", arguments: { source: "does-not-exist" } })));

rule("7 · the schema is enforced server-side");
try {
  const bad = await client.callTool({ name: "policy_search", arguments: { query: "x", k: "four" as any } });
  console.log(`rejected via isError result: ${(bad as any).isError === true}`);
} catch (e) {
  console.log(`rejected via JSON-RPC error: ${(e as Error).message.slice(0, 90)}`);
}

await client.close();
console.log("\n\x1b[32mdone — session closed.\x1b[0m");
