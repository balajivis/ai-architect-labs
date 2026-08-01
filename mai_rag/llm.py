"""
mai_rag.llm — one small LLM chokepoint for generation and LLM-judge evals.

Auto-detects a provider from the environment so a Colab student sets a single
key and everything works:

    GROQ_API_KEY        → Groq            (OpenAI-compatible, fast + free tier)
    OPENAI_API_KEY      → OpenAI
    AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT → Azure OpenAI (course parity)
    GEMINI_API_KEY      → Google Gemini

Pass a `tier` (small | medium | large) — never a hardcoded model name — so the
mapping lives in one place, mirroring Kapi's tier convention. Retrieval needs no
key (embeddings are local); only generation + judge evals reach an LLM.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from typing import Any

# Per-provider tier → model maps. Edit here, not in notebooks.
_TIER_MODELS = {
    "groq":   {"small": "llama-3.1-8b-instant", "medium": "llama-3.3-70b-versatile", "large": "llama-3.3-70b-versatile"},
    "openai": {"small": "gpt-4o-mini",          "medium": "gpt-4o-mini",             "large": "gpt-4o"},
    "azure":  {"small": "gpt-5.4",              "medium": "gpt-5.4",                 "large": "gpt-5.5"},
    "gemini": {"small": "gemini-2.0-flash",     "medium": "gemini-2.0-flash",        "large": "gemini-2.5-flash"},
}


def _provider() -> str:
    forced = os.getenv("MAI_LLM_PROVIDER")
    if forced:
        return forced
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    if os.getenv("AZURE_OPENAI_API_KEY"):
        return "azure"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    raise RuntimeError(
        "No LLM key found. Set one of GROQ_API_KEY / OPENAI_API_KEY / "
        "AZURE_OPENAI_API_KEY / GEMINI_API_KEY (e.g. via Colab `userdata`)."
    )


def model_for(tier: str = "small", provider: str | None = None) -> str:
    provider = provider or _provider()
    return _TIER_MODELS[provider].get(tier, _TIER_MODELS[provider]["small"])


# The two failures a student actually hits — turned into a clear next step instead of a
# raw traceback. A rotated/disabled class key surfaces as 401/403 or a 503 "not enabled".
_KEY_HINT = (
    "Your class LLM key isn't working — it may have been rotated, or the class proxy is "
    "turned off right now. Ask the instructor for a fresh class token and put it in your "
    ".env as OPENAI_API_KEY."
)
_RATE_HINT = (
    "The class LLM is rate-limited — wait a minute and re-run this step, or ask the "
    "instructor to raise the limit."
)

# Marker returned when the PROVIDER's own content filter refuses a prompt (a guardrail we
# didn't write). Security labs check for this prefix and score it as the refusal it is.
PLATFORM_BLOCK = "[BLOCKED by the platform content filter]"


class _Meter:
    """Counts LLM calls + tokens through this chokepoint, so cost/latency can be SCORED
    (mai_rag.evals.perf) instead of guessed. Usage comes from the provider's own `usage`
    block when it ships one; otherwise tokens are estimated at ~4 chars/token so the
    number is never silently zero. Reset it around a run, snapshot it after."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.estimated = False

    def record(self, resp=None, prompt: str = "", output: str = ""):
        self.calls += 1
        usage = getattr(resp, "usage", None)
        pt = getattr(usage, "prompt_tokens", None) if usage else None
        ct = getattr(usage, "completion_tokens", None) if usage else None
        if pt is None and ct is None:
            pt, ct = len(prompt) // 4, len(output) // 4
            self.estimated = True
        self.prompt_tokens += int(pt or 0)
        self.completion_tokens += int(ct or 0)

    @property
    def tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def snapshot(self) -> dict:
        return {"calls": self.calls, "tokens": self.tokens,
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "estimated": self.estimated}


METER = _Meter()


def complete(prompt: str, tier: str = "small", temperature: float = 0.0,
             max_tokens: int = 800, system: str | None = None, retries: int = 6) -> str:
    """Single-prompt completion. Returns text.

    Retries a rate-limit (429) with exponential backoff, and turns the failures a student
    actually hits — a rotated/disabled key (401/403/503) or a persistent rate-limit — into
    one clear line instead of a raw openai traceback. Every lab + eval engine calls this.
    """
    provider = _provider()
    model = model_for(tier, provider)
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]

    def _once() -> str:
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            gm = genai.GenerativeModel(model, system_instruction=system)
            return gm.generate_content(
                prompt, generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
            ).text

        # OpenAI-compatible path covers openai / groq / azure
        from openai import OpenAI, AzureOpenAI
        if provider == "azure":
            client: Any = AzureOpenAI(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            )
            # gpt-5.x on Azure needs max_completion_tokens + only the default temperature
            resp = client.chat.completions.create(model=model, messages=messages, max_completion_tokens=max_tokens)
        else:
            client = (OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
                      if provider == "groq" else OpenAI(api_key=os.environ["OPENAI_API_KEY"]))
            resp = client.chat.completions.create(model=model, messages=messages,
                                                  temperature=temperature, max_tokens=max_tokens)
        out = resp.choices[0].message.content or ""
        METER.record(resp, prompt=prompt, output=out)
        return out

    for attempt in range(retries):
        try:
            return _once()
        except Exception as e:
            status = getattr(e, "status_code", None)
            m = str(e).lower()
            name = type(e).__name__
            is_rate = status == 429 or name == "RateLimitError" or "rate limit" in m
            is_key = (status in (401, 403) or name in ("AuthenticationError", "PermissionDeniedError")
                      or "not enabled" in m or "invalid or missing class token" in m or "invalid api key" in m)
            if is_rate and attempt < retries - 1:
                wait = min(2 ** attempt * 2, 30)      # 2 → 4 → 8 → 16 → 30 → 30
                print(f"[mai_rag.llm] rate-limited — backing off {wait}s (retry {attempt + 1}/{retries - 1})",
                      file=sys.stderr, flush=True)
                time.sleep(wait)
                continue
            # The PROVIDER's own content filter refused the prompt (Azure 400). That is a
            # guardrail we didn't write — surface it as an explicit block marker instead of
            # crashing, so security labs can score it as the refusal it is.
            if ("content management policy" in m or "content_filter" in m
                    or ("filtered" in m and "400" in m)):
                return PLATFORM_BLOCK + (" The provider's own content filter refused this "
                                         "prompt; no answer was generated.")
            if is_key:
                raise RuntimeError(_KEY_HINT) from None
            if is_rate:
                raise RuntimeError(_RATE_HINT) from None
            raise RuntimeError(f"LLM call failed ({name}{' ' + str(status) if status else ''}): {str(e)[:160]}") from None


def complete_json(prompt: str, tier: str = "small", **kw) -> dict:
    """Completion that must return a JSON object. Robust to ```json fences and
    leading prose — structural parsing only (allowed), never classification.

    Note the token budget: JSON replies (claim lists, per-chunk verdicts) run far longer
    than prose answers, and a reply truncated mid-object is invalid JSON. Default higher
    than complete()'s, and say so plainly when a reply still gets cut off."""
    kw.setdefault("max_tokens", 2500)
    raw = complete(prompt + "\n\nRespond with a single JSON object and nothing else.",
                   tier=tier, **kw)
    # Provider-filtered prompt (see complete): there is no output to judge. Report it as a
    # clean, explicit verdict so safety evaluators score the refusal instead of crashing.
    if raw.startswith(PLATFORM_BLOCK):
        return {"blocked": True, "exposed": False, "harmful": False, "score": 1.0,
                "reasoning": "provider content filter blocked the prompt; nothing was generated"}
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON object found in model output: {raw[:200]}")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        # Almost always a truncated reply (the model hit max_tokens mid-object).
        raise ValueError(
            f"model returned invalid/truncated JSON ({e.msg}). Raise max_tokens for this "
            f"call, or ask for fewer items. Tail: …{raw[-120:]!r}"
        ) from None
