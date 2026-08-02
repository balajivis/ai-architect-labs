/**
 * audit.ts — the audit trail (Lab 8, Move 6b). Glass-box: read it, it's stdlib.
 *
 * A DEBUG log is written for the person who wrote the code, to answer "why did
 * this break?". An AUDIT log is written for a stranger who distrusts you, to
 * answer "who did what, when, was it allowed, and what did it cost?" — years
 * later, in a room where you are not present to explain.
 *
 * The tell: a debug log gets MORE useful when you paste in the retrieved
 * document text; an audit log becomes a BREACH when you do. So an audit record
 * stores REFERENCES, never PAYLOADS — `sub`, not the token; document ids, not
 * document bodies; a query digest, not the question; a guard verdict plus the
 * judge's version, not the judge's transcript.
 *
 * And it records the state of the controls at that instant even when —
 * especially when — they were switched OFF. `auth: "disabled"` and
 * `guard: "unavailable"` are fields, not omissions: a log that silently maps a
 * fail-open to "clean" is not a log, it is a cover-up.
 *
 * Two streams, deliberately two files:
 *   · audit/mcp-audit-YYYY-MM-DD.ndjson  — this schema. Append-only, 0600, hash-chained.
 *   · stdout (JSON lines via logJson)    — the ops/debug stream. Noisy, disposable.
 *
 * NDJSON because a JSON array can't be appended to without seeking back to fix
 * the bracket — which is, by definition, not append-only. Records stay small
 * (< 4 KB) so POSIX O_APPEND writes are atomic and concurrent writers can never
 * interleave. That size ceiling is a second, independent reason never to log a
 * document body: the file format itself forbids it.
 */
import { createHash, randomBytes } from "node:crypto";
import { appendFileSync, mkdirSync, readFileSync, existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

export const AUDIT_SCHEMA = "mcp-audit/1";
export const AUDIT_DIR = process.env.MCP_AUDIT_DIR || join(import.meta.dirname, "audit");

/** The W3C trace-id shape: 32 lowercase hex. Not randomUUID() — dashes and a
 *  version nibble make that neither a valid trace-id nor cleanly greppable. */
export const newCorrelationId = () => randomBytes(16).toString("hex");
/** 16 hex — one span per upstream hop. */
export const newSpanId = () => randomBytes(8).toString("hex");

/** Propagate ONE value under TWO headers: `x-correlation-id` is the audit header
 *  (human, greppable, what the record stores); `traceparent` is the tracing
 *  header (machine, standard, what OpenTelemetry/Langfuse pick up for free).
 *  The invariant that makes them one system: the audit record's correlation_id
 *  IS the trace-id inside traceparent. One `grep <cid>` finds both worlds. */
export function traceHeaders(cid: string): Record<string, string> {
  return { "x-correlation-id": cid, traceparent: `00-${cid}-${newSpanId()}-01` };
}

const sha256 = (s: string) => createHash("sha256").update(s).digest("hex");

/** Canonical JSON — keys sorted at every level, so the same record always
 *  hashes to the same value. Without this the chain below is meaningless. */
function canonical(v: unknown): string {
  if (v === null || typeof v !== "object") return JSON.stringify(v) ?? "null";
  if (Array.isArray(v)) return `[${v.map(canonical).join(",")}]`;
  const o = v as Record<string, unknown>;
  return `{${Object.keys(o).sort().map((k) => `${JSON.stringify(k)}:${canonical(o[k])}`).join(",")}}`;
}

/**
 * Which arguments are safe to record verbatim is a decision the TOOL AUTHOR
 * declares — not something a detector guesses. Enumerable args (a doc id, k=5)
 * are the facts an auditor needs and are recorded in full; the args the author
 * marked as free text (a user's question — the highest-density PII in the whole
 * system) collapse to a digest + length. The digest still answers "was this the
 * same call as the one in the incident?" without storing what was asked.
 */
export function safeArgs(args: Record<string, unknown>, freeText: string[] = []): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(args ?? {})) {
    if (freeText.includes(k)) {
      const s = String(v ?? "");
      out[k] = { sha256: sha256(s).slice(0, 16), len: s.length };
    } else {
      out[k] = v;
    }
  }
  return out;
}

/** A stable handle for a credential WITHOUT storing it: the `jti` claim if the
 *  token has one, else a digest prefix. Lets an auditor pivot to "every call
 *  this token made" and hand it to the IdP — while the token itself, in whole
 *  or in part, never touches the file. */
export function tokenId(token: string | undefined, jti?: string): string | null {
  if (jti) return jti;
  if (!token) return null;
  return `sha256:${sha256(token).slice(0, 16)}`;
}

function auditPath(): string {
  mkdirSync(AUDIT_DIR, { recursive: true, mode: 0o700 });
  // Rotate on the UTC day boundary, never by size: retention policy is written
  // in days ("keep 400 days") and auditors ask for "the 14th", not "the third
  // 10 MB chunk".
  return join(AUDIT_DIR, `mcp-audit-${new Date().toISOString().slice(0, 10)}.ndjson`);
}

/** Seed the hash chain from the last record already on disk, so a server
 *  restart continues the chain instead of silently forking it. */
function lastHash(path: string): string | null {
  if (!existsSync(path)) return null;
  const lines = readFileSync(path, "utf-8").trim().split("\n").filter(Boolean);
  if (!lines.length) return null;
  try { return (JSON.parse(lines[lines.length - 1]) as { chain?: { self?: string } }).chain?.self ?? null; }
  catch { return null; }
}

let prevHash: string | null = null;
let chainSeeded = false;

/**
 * Append one audit record. Append-only is a *convention* until an edit is
 * DETECTABLE — so each record carries the previous record's hash. Change any
 * record after the fact and every hash downstream stops matching; deleting a
 * record leaves a hole you can point at. `verifyChain` proves it.
 */
export function appendAudit(record: Record<string, unknown>): Record<string, unknown> {
  const path = auditPath();
  if (!chainSeeded) { prevHash = lastHash(path); chainSeeded = true; }

  const body = {
    schema_version: AUDIT_SCHEMA,
    ts: new Date().toISOString(),          // RFC 3339 UTC, always Z — never local time
    ...record,
    chain: { prev: prevHash },
  };
  const self = sha256(canonical(body));
  const full = { ...body, chain: { prev: prevHash, self } };
  prevHash = self;

  // O_APPEND + 0600: atomic under 4 KB, and unreadable by anyone else on a
  // laptop that will be screen-shared in class.
  appendFileSync(path, JSON.stringify(full) + "\n", { mode: 0o600 });
  return full;
}

/** Recompute every hash and report the first record that doesn't match. ~15
 *  lines is all tamper-evidence costs — ship it with the log or the chain is
 *  decoration. */
export function verifyChain(path?: string): { records: number; ok: boolean; brokenAt: number | null } {
  const file = path ?? auditPath();
  if (!existsSync(file)) return { records: 0, ok: true, brokenAt: null };
  const lines = readFileSync(file, "utf-8").trim().split("\n").filter(Boolean);
  let prev: string | null = null;
  for (let i = 0; i < lines.length; i++) {
    const rec = JSON.parse(lines[i]) as Record<string, unknown> & { chain: { prev: string | null; self: string } };
    const { self, ...rest } = rec.chain;
    const recomputed = sha256(canonical({ ...rec, chain: { prev: rest.prev } }));
    // The FIRST record's `prev` is not checked: with daily rotation it legitimately
    // points at the last record of yesterday's file (the chain crosses files, the
    // verifier is per-file). Demanding prev===null here would report every file
    // "broken at record 1" every day at UTC midnight — a verifier that cries wolf
    // is a verifier nobody runs. Within a file, each link is checked exactly.
    if ((i > 0 && rec.chain.prev !== prev) || recomputed !== self) {
      return { records: lines.length, ok: false, brokenAt: i + 1 };
    }
    prev = self;
  }
  return { records: lines.length, ok: true, brokenAt: null };
}

/** Read today's records back (the tutor and harness use this; so can you —
 *  `cat audit/*.ndjson | jq 'select(.decision != "allow")'`). */
export function readAudit(path?: string): Array<Record<string, unknown>> {
  const file = path ?? auditPath();
  if (!existsSync(file)) return [];
  return readFileSync(file, "utf-8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
}

export function latestAuditFile(): string | null {
  if (!existsSync(AUDIT_DIR)) return null;
  const files = readdirSync(AUDIT_DIR).filter((f) => f.endsWith(".ndjson")).sort();
  return files.length ? join(AUDIT_DIR, files[files.length - 1]) : null;
}

/** The OTHER stream: structured ops logging on stdout. One JSON object per
 *  line, carrying the SAME correlation_id — so `grep <cid>` stitches the ops
 *  view, the audit view, and the Python bridge's own line into one story.
 *  Free-text console.log prose belongs nowhere near either stream. */
export function logJson(fields: Record<string, unknown>): void {
  console.log(JSON.stringify({ ts: new Date().toISOString(), ...fields }));
}
