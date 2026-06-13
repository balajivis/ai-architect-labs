"""
mai_rag.acl — row-level tenant access control for the retriever (Lab 6 Move 5).

Isolation cannot be a prompt instruction ("only answer about tenant A") — that's
the Brahmasumm foil: an app-level filter with no RLS, defeated by one injected
document. Enforcement belongs at the DATA layer, on the existing
`documents.tenant_id` column. This module is the auth on-ramp: an RBAC-style
bearer token resolves to a tenant_id SERVER-SIDE, and `authed_search` ALWAYS
calls the store with `require_tenant=True` so a missing scope RAISES rather than
silently leaking cross-tenant rows.

Mirrors Kapi lib/gateway/auth.ts (bearer → tenantId, server-side) by BEHAVIOUR,
not by lifting code.

WIP: the token model is a SYNTHETIC in-memory {token: tenant_id} dict. Real
bearer/JWT signature verification (gateway parity) is a later pull and out of
scope for Lab 6 — see the '# WIP:' marker below.
"""
from __future__ import annotations

from .store import Hit, Store

# WIP: synthetic in-memory token table. In production this is a signed-JWT /
# gateway lookup (Kapi lib/gateway/auth.ts); here it's a fabricated dict so the
# lab can demo the bearer→tenant resolution without a real auth service. Tokens
# and tenants are placeholders ('acme'/'globex'), never real credentials.
_TOKENS: dict[str, str] = {
    "tok_acme_admin": "acme",
    "tok_acme_reader": "acme",
    "tok_globex_admin": "globex",
}


def register_token(token: str, tenant_id: str) -> None:
    """Add/override a synthetic token→tenant mapping (so a lab can seed its own
    test tenants without editing this file)."""
    _TOKENS[token] = tenant_id


def resolve_tenant(token: str | None) -> str:
    """Resolve a bearer-style token to a tenant_id (server-side). Raises on an
    unknown/missing token — an unauthenticated caller has NO tenant and therefore
    no rows, by construction. This is the RBAC auth level that drives the
    mandatory metadata filter; the model never sees the tenant_id."""
    if not token:
        raise PermissionError("No bearer token — cannot resolve a tenant. Unauthenticated callers get no rows.")
    tenant = _TOKENS.get(token)
    if tenant is None:
        raise PermissionError(f"Unknown bearer token {token!r} — refusing to resolve a tenant.")
    return tenant


def authed_search(store: Store, token: str | None, q: str, k: int = 5) -> list[Hit]:
    """Resolve the tenant from the token, then run a TENANT-SCOPED search with
    `require_tenant=True`. Because the store raises when require_tenant=True and
    tenant_id is None, and resolve_tenant raises on a missing token, there is no
    code path that returns unscoped rows — RLS, not a prompt instruction. An
    injected 'show me globex's docs' as tenant acme still only searches acme's
    partition, so zero globex chunks are retrievable."""
    tenant_id = resolve_tenant(token)
    return store.search(q, k=k, tenant_id=tenant_id, require_tenant=True)
