#!/usr/bin/env python3
"""ask.py — get unstuck fast: ask the Modern AI Pro AI Architect TA (our GPT-5.4).

It reads your .env for the class token, gathers a little context about YOUR setup
(python + mai_rag version, which provider keys are set, plus any error you paste),
and asks our course endpoint. No extra packages — standard library only.

    python labs/ask.py "pip install is failing on sentence-transformers"
    python labs/ask.py                       # then type your question
    python labs/ask.py "why this error?" < traceback.txt   # pipe an error in

Needs the class token in your .env:  CLASS_LLM_TOKENS=<today's class token>
(or OPENAI_API_KEY set to the class token, if that's how you configured the proxy).
"""
import os
import sys
import json
import pathlib
import platform
import urllib.request
import urllib.error

# --- load .env (KEY=VALUE) from repo root / cwd, same shim as the labs ----------
_here = pathlib.Path(__file__).resolve().parent
for _cand in (pathlib.Path(".env"), _here.parent / ".env", _here / ".env"):
    if _cand.exists():
        for _line in _cand.read_text().splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
        break

ENDPOINT = os.environ.get("CLASS_HELP_URL", "https://learn.modernaipro.com/api/class-help")
# The class token: from CLASS_LLM_TOKENS, or CLASS_TOKEN, or the OPENAI_API_KEY you set for the proxy.
TOKEN = (os.environ.get("CLASS_LLM_TOKENS", "").split(",")[0].strip()
         or os.environ.get("CLASS_TOKEN", "").strip()
         or os.environ.get("OPENAI_API_KEY", "").strip())


def gather_context() -> str:
    parts = [
        f"python={platform.python_version()}",
        f"os={platform.system()} {platform.machine()}",
        f"cwd={os.getcwd()}",
    ]
    try:
        import mai_rag  # noqa
        parts.append(f"mai_rag={getattr(mai_rag, '__version__', '?')}")
    except Exception as e:  # import failure IS useful context
        parts.append(f"mai_rag import FAILED: {type(e).__name__}: {e}")
    for k in ("GROQ_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL",
              "AZURE_OPENAI_API_KEY", "GEMINI_API_KEY", "MAI_LLM_PROVIDER"):
        v = os.environ.get(k)
        # never send the secret value — just whether it's set (base_url/provider are safe to show)
        parts.append(f"{k}={v if k in ('OPENAI_BASE_URL', 'MAI_LLM_PROVIDER') and v else ('set' if v else 'unset')}")
    return " | ".join(parts)


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        try:
            question = input("Ask the AI Architect TA › ").strip()
        except EOFError:
            question = ""
    if not question:
        print("Nothing asked. Try:  python labs/ask.py \"your question\"")
        return

    piped = "" if sys.stdin.isatty() else sys.stdin.read().strip()
    context = gather_context() + (("\n\nPasted error / output:\n" + piped[:6000]) if piped else "")

    if not TOKEN:
        print("No class token found. Put today's token in your .env:\n"
              "  CLASS_LLM_TOKENS=<the token from class>\n"
              "(or set OPENAI_API_KEY to it, if you used the class proxy).")
        return

    req = urllib.request.Request(
        ENDPOINT, method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        data=json.dumps({"question": question, "context": context}).encode("utf-8"),
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            print("\n" + json.loads(r.read().decode("utf-8")).get("answer", "(no answer returned)") + "\n")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:300]
        if e.code == 503:
            print("\nThe class help endpoint isn't enabled right now (the class token is set day-of).")
        elif e.code == 401:
            print("\nBad/expired class token — check CLASS_LLM_TOKENS in your .env against today's token.")
        elif e.code == 429:
            print("\nToo many requests right now — wait a few seconds and try again.")
        else:
            print(f"\n[HTTP {e.code}] {detail}")
    except Exception as e:
        print(f"\nCouldn't reach the TA: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
