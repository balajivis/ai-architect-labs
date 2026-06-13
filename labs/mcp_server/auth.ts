/**
 * auth.ts — OAuth 2.1 resource-server middleware for the Lab 8 MCP server.
 *
 * Spine: consume -> build -> HARDEN. This is Move 5. Your server is an OAuth 2.1
 * *resource server*. Two obligations the spec puts on you:
 *
 *   1. RFC 9728 (Protected Resource Metadata): an unauthenticated request gets a
 *      401 carrying `WWW-Authenticate: Bearer ... resource_metadata="<PRM URL>"`
 *      so a client (e.g. Kapi's `oauth-discovery.ts probeServerForAuth`) can
 *      discover where to get a token. This emitter is LIVE below.
 *
 *   2. RFC 8707 (audience binding): token passthrough is FORBIDDEN. You MUST
 *      reject a token whose `aud` names a *different* server — otherwise a token
 *      minted for some other resource can be replayed at yours. This check is the
 *      one-line `// WIP:` TODO you complete in Move 5.
 *
 * Reference (read, don't rebuild): Kapi builds the CLIENT side that probes this
 * (`lib/integrations/oauth-discovery.ts`); you build the SERVER side it probes.
 *
 * Spec label: bearer-token + 401/PRM is CURRENT (2025-11-25). The COMING RC
 * (2026-07-28, SEP-2575) is stateless-first; the resource-server obligations here
 * are unchanged by it — only session handling changes.
 *
 * IP-safe / credentials policy: the dev bearer token and the expected audience
 * are read from `process.env` (MCP_DEV_TOKEN, MCP_EXPECTED_AUD) — NEVER inlined.
 * `.env` is git-ignored; `.env.example` ships placeholders only.
 */
import type { Request, Response, NextFunction } from "express";

/** Where the Protected Resource Metadata document lives (RFC 9728). For the lab
 *  this is a well-known path on the same origin; a real deployment serves the
 *  JSON document there too. */
function prmUrl(req: Request): string {
  const base = `${req.protocol}://${req.get("host")}`;
  return `${base}/.well-known/oauth-protected-resource`;
}

/** Emit the RFC 9728 challenge. This is the handshake `probeServerForAuth`
 *  parses with its structural `resource_metadata="..."` header regex. LIVE. */
function send401(req: Request, res: Response): void {
  res
    .status(401)
    .set(
      "WWW-Authenticate",
      `Bearer resource_metadata="${prmUrl(req)}", error="invalid_token"`,
    )
    .json({ error: "unauthorized", detail: "bearer token required (RFC 9728 PRM)" });
}

/** Decode a bearer token's `aud` claim. The lab mints a synthetic HS256 fixture
 *  token (pyjwt, dev secret from .env) with a genuine `aud`, so this read is real.
 *  Structural base64url/JSON parse only — NOT classification, so no judge needed. */
function decodeAud(token: string): string | string[] | undefined {
  const parts = token.split(".");
  if (parts.length !== 3) return undefined;
  try {
    const payload = JSON.parse(
      Buffer.from(parts[1].replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf-8"),
    );
    return payload.aud;
  } catch {
    return undefined;
  }
}

/**
 * Express middleware: 401+PRM when unauthenticated (LIVE), 403 when the token's
 * audience binds a *different* server (RFC 8707 — the WIP one-liner below).
 *
 * Wire this in front of the `/mcp` route in server.ts (Move 5) by setting
 * AUTH_ENABLED=1. Moves 3–4 run with it OFF (pre-auth server).
 */
export function oauthResourceServer(req: Request, res: Response, next: NextFunction): void {
  const header = req.get("authorization") || "";
  const token = header.toLowerCase().startsWith("bearer ") ? header.slice(7).trim() : "";

  // (1) No credentials -> 401 with the PRM discovery pointer. LIVE.
  if (!token) {
    send401(req, res);
    return;
  }

  const aud = decodeAud(token);
  const expected = process.env.MCP_EXPECTED_AUD || ""; // never inlined — from .env

  // (2) RFC 8707 audience binding. Reject a token minted for a DIFFERENT server.
  //
  // WIP: TODO (Move 5) — replace `false` with the real audience comparison so a
  //      token whose `aud` is NOT this server's expected audience is rejected.
  //      `aud` may be a string OR a string[] per the JWT spec; handle both.
  //      Hint: const audOk = Array.isArray(aud) ? aud.includes(expected) : aud === expected;
  //            then reject when `!audOk`.
  //      Until you complete this, EVERY token (even a cross-server one) is
  //      accepted — so the Move-5 wrong-audience assertion FAILS until you fix it.
  const audMismatch = false; // <-- WIP: TODO replace with `!audOk` (see hint above)

  if (audMismatch) {
    res
      .status(403)
      .json({ error: "forbidden", detail: `token audience does not bind this server (expected ${expected})` });
    return;
  }

  next();
}
