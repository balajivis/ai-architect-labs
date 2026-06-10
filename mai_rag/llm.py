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


def complete(prompt: str, tier: str = "small", temperature: float = 0.0,
             max_tokens: int = 800, system: str | None = None) -> str:
    """Single-prompt completion. Returns text."""
    provider = _provider()
    model = model_for(tier, provider)
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]

    if provider == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        gm = genai.GenerativeModel(model, system_instruction=system)
        resp = gm.generate_content(
            prompt,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
        )
        return resp.text

    # OpenAI-compatible path covers openai / groq / azure
    from openai import OpenAI, AzureOpenAI

    if provider == "azure":
        client: Any = AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        )
    elif provider == "groq":
        client = OpenAI(api_key=os.environ["GROQ_API_KEY"],
                        base_url="https://api.groq.com/openai/v1")
    else:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    resp = client.chat.completions.create(
        model=model, messages=messages,
        temperature=temperature, max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def complete_json(prompt: str, tier: str = "small", **kw) -> dict:
    """Completion that must return a JSON object. Robust to ```json fences and
    leading prose — structural parsing only (allowed), never classification."""
    raw = complete(prompt + "\n\nRespond with a single JSON object and nothing else.",
                   tier=tier, **kw)
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON object found in model output: {raw[:200]}")
    return json.loads(m.group(0))
