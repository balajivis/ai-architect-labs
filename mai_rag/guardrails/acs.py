"""
mai_rag.guardrails.acs — optional Azure Content Safety adapter (Lab 6).

WIP: THIS SHIPS AS A STUB. When AZURE_CONTENT_SAFETY_ENDPOINT +
AZURE_CONTENT_SAFETY_KEY are present in the environment, the real adapter will
call Azure Content Safety `detectPII` (TRUE redaction → redactedText) and Prompt
Shield (`shieldPrompt`) — mirroring Kapi lib/guardrails/content-safety-client.ts.
Until class Azure creds are provisioned, every entrypoint returns
`{"configured": False, "reason": "ACS not configured"}` and the Guardrail
pipeline FALLS THROUGH to the native keyless LLM-judge engines in
mai_rag.evals.safety.

The fall-through is to the LLM judge, NEVER to a regex floor (invariant I-25).
On the native path, Gate-1 'redact' honestly degrades to 'block' because the
native pii_exposure engine only CLASSIFIES (exposed true/false) and has no
redactedText primitive. The lab states this out loud rather than faking a
redaction the kit can't do.

The real calls land via a later git pull once creds exist; the live/stub
boundary is the `is_configured()` check below.
"""
from __future__ import annotations

import os

# The two env vars the real adapter will read. Read from the environment ONLY —
# never hardcode a key (portfolio credentials policy).
_ENDPOINT_VAR = "AZURE_CONTENT_SAFETY_ENDPOINT"
_KEY_VAR = "AZURE_CONTENT_SAFETY_KEY"

_NOT_CONFIGURED = {"configured": False, "reason": "ACS not configured"}


def is_configured() -> bool:
    """True only when BOTH Azure Content Safety creds are present in the env.
    The Guardrail pipeline calls this to decide live-ACS vs native fall-through."""
    return bool(os.getenv(_ENDPOINT_VAR) and os.getenv(_KEY_VAR))


def status() -> dict:
    """A printable one-liner for Move 0's optional ACS block."""
    if is_configured():
        return {"configured": True, "reason": "ACS configured (live adapter)"}
    return dict(_NOT_CONFIGURED)


def detect_pii(text: str) -> dict:
    """Azure Content Safety detectPII with TRUE redaction.

    WIP STUB: returns {configured: False, reason: 'ACS not configured'} so the
    caller falls through to the native pii_exposure judge (which only classifies,
    so 'redact' degrades to 'block'). The real call will return
    {configured: True, exposed: bool, redactedText: str, entities: [...]}.
    """
    if not is_configured():
        return dict(_NOT_CONFIGURED)
    # WIP: live Azure Content Safety detectPII call lands here via a later git
    # pull once class creds are provisioned. Until then this branch is
    # unreachable (is_configured() is False) and we never fake a redaction.
    raise NotImplementedError(
        "ACS creds detected but the live detectPII adapter is not wired yet — "
        "ships in a later git pull. Unset the ACS env vars to use the native path."
    )


def shield_prompt(text: str, contexts: list[str] | None = None) -> dict:
    """Azure Prompt Shield (shieldPrompt) over the input + retrieved docs.

    WIP STUB: returns {configured: False, ...} so the caller falls through to the
    native harmful_intent judge over input+contexts. The real call will return
    {configured: True, attackDetected: bool, ...}.
    """
    if not is_configured():
        return dict(_NOT_CONFIGURED)
    # WIP: live Azure Prompt Shield call lands here via a later git pull.
    raise NotImplementedError(
        "ACS creds detected but the live shieldPrompt adapter is not wired yet — "
        "ships in a later git pull. Unset the ACS env vars to use the native path."
    )
