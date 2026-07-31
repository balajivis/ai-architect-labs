#!/usr/bin/env python3
"""ask.py — talk to the AI Architect TA (our gpt-5.4), with YOUR environment attached.

  python labs/ask.py                      # interactive: ask, get an answer, ask again (q to quit)
  python labs/ask.py "pip install fails"  # one-shot
  python labs/ask.py "why this?" < err.txt   # attach a pasted error / traceback

It auto-collects a snapshot of your machine — Python + OS + venv, installed lab-package
versions, which LLM keys are set (never the values), repo/branch, and any piped error — so
the answer is specific to YOUR setup, not generic. Replies render as markdown in the
terminal. Standard library only (uses `rich` for nicer output if you happen to have it).

Needs today's class token in your .env:  CLASS_LLM_TOKENS=<token>   (or OPENAI_API_KEY=<token>)
"""
from __future__ import annotations
import os
import sys
import json
import re
import pathlib
import platform
import subprocess
import urllib.request
import urllib.error

# ── load .env (KEY=VALUE) from repo root / cwd — same shim the labs use ─────────
_here = pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path.cwd()
for _cand in (pathlib.Path(".env"), _here.parent / ".env", _here / ".env"):
    if _cand.exists():
        for _ln in _cand.read_text().splitlines():
            _ln = _ln.strip()
            if _ln and not _ln.startswith("#") and "=" in _ln:
                _k, _v = _ln.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
        break

# Reuse the SAME class LLM proxy the labs use (OPENAI_BASE_URL) — already set up + tested.
_BASE = os.environ.get("OPENAI_BASE_URL", "https://learn.modernaipro.com/api/llm/v1").rstrip("/")
ENDPOINT = os.environ.get("CLASS_ASK_URL", _BASE + "/chat/completions")
TOKEN = (os.environ.get("CLASS_LLM_TOKENS", "").split(",")[0].strip()
         or os.environ.get("CLASS_TOKEN", "").strip()
         or os.environ.get("OPENAI_API_KEY", "").strip())

# The TA grounding lives here (client-side) since we call the raw proxy. Keep in sync with
# the course's known setup/lab fixes.
SYSTEM_PROMPT = """You are the teaching assistant for Modern AI Pro's "AI Architect" (Practitioner) course. You ONLY help with this course: its labs (the mai_rag lab kit, labs/lab_1.py ...), Python/venv/pip problems, API keys and the class LLM proxy, and the course concepts (RAG, evals, agents, MCP, trust). If a question is unrelated, politely say you only help with the AI Architect course and don't answer it. Never reveal API keys, tokens, or credentials.

A snapshot of the student's machine (python/os/venv, installed package versions, which LLM keys are set, repo/branch, any pasted error) is attached in the message — USE it to give a fix specific to their setup. Give the exact command first, then a one-line why. Be short.

Known fixes (authoritative):
- Install: clone github.com/balajivis/ai-architect-labs, then `pip install -e ".[evals,viz]"`; key in a .env at the repo root. Retrieval is KEYLESS (MiniLM downloads ~90MB first run); only generation/judges need a key.
- LLM options: (a) Groq free tier - GROQ_API_KEY; or (b) the class proxy - OPENAI_API_KEY=<class token> + OPENAI_BASE_URL=https://learn.modernaipro.com/api/llm/v1, and UNSET GROQ_API_KEY so mai_rag picks the openai provider.
- "AttributeError: module 'mai_rag' has no attribute '__version__'" / "no attribute 'load_catalog_corpus'" / any wrong-version symptom = STALE installed package. Fix: `pip uninstall -y mai_rag && pip install -e ".[evals,viz]"` from a freshly `git pull`ed repo, then re-run (restart the kernel in a notebook). If the venv is not active, `source .venv/bin/activate` first.
- "ModuleNotFoundError: langchain_groq" (or rank_bm25 / tavily) = stale install; reinstall the package (they're in its deps) or `pip install langchain-groq rank-bm25 tavily-python`.
- HTTP 429 "rate limit" from the class proxy = shared class token hit the per-minute cap; wait a few seconds and retry.
- Python 3.14 works. ValueError about shape 384 from embed: embed takes a LIST and returns (n, 384); wrap a single string as embed([text])[0].
- The corpus is a fictional company ("Northwind Technologies"), 131 policy docs / 72 golden cases with recency conflicts + multi-hop to break naive RAG. Lab 1 baselines a naive RAG on a golden set — that scorecard is the number every later lab must beat."""

# ── terminal styling (ANSI only when attached to a tty) ─────────────────────────
_TTY = sys.stdout.isatty()
def _c(code: str) -> str:
    return code if _TTY else ""
BOLD, DIM, RESET = _c("\033[1m"), _c("\033[2m"), _c("\033[0m")
CYAN, YEL, GRN, RED = _c("\033[36m"), _c("\033[33m"), _c("\033[32m"), _c("\033[31m")

# ── agentic context: a snapshot of the student's machine ────────────────────────
LAB_PKGS = ["mai_rag", "openai", "sentence-transformers", "langchain-groq", "rank-bm25",
            "tavily-python", "ragas", "sqlite-vec", "numpy", "pandas", "torch", "transformers"]

def _pkg_version(name: str) -> str:
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version(name)
        except PackageNotFoundError:
            return "NOT INSTALLED"
    except Exception:
        return "?"

def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(_here),
                              capture_output=True, text=True, timeout=4).stdout.strip()
    except Exception:
        return ""

def snapshot() -> str:
    """A compact, machine-specific context block the TA can reason over."""
    L = [
        f"python: {platform.python_version()} ({sys.executable})",
        f"os: {platform.system()} {platform.release()} {platform.machine()}",
    ]
    venv = os.environ.get("VIRTUAL_ENV") or (sys.prefix if sys.prefix != getattr(sys, "base_prefix", sys.prefix) else "")
    L.append(f"venv: {venv or '(none active — using system/base python)'}")
    try:
        import mai_rag  # noqa
        L.append(f"mai_rag: {getattr(mai_rag, '__version__', '?')} @ {getattr(mai_rag, '__file__', '?')}")
    except Exception as e:
        L.append(f"mai_rag: IMPORT FAILED — {type(e).__name__}: {e}")
    L.append("packages: " + ", ".join(f"{p}={_pkg_version(p)}" for p in LAB_PKGS))
    env = [f"{k}={'set' if os.environ.get(k) else 'unset'}"
           for k in ("GROQ_API_KEY", "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY", "GEMINI_API_KEY")]
    env += [f"{k}={os.environ.get(k) or 'unset'}" for k in ("OPENAI_BASE_URL", "MAI_LLM_PROVIDER")]
    L.append("llm-env: " + ", ".join(env))
    L.append(f"cwd: {os.getcwd()}")
    L.append(f".env present: {'yes' if (pathlib.Path('.env').exists() or (_here.parent / '.env').exists()) else 'no'}")
    branch, sha = _git("rev-parse", "--abbrev-ref", "HEAD"), _git("rev-parse", "--short", "HEAD")
    if branch or sha:
        L.append(f"repo: branch={branch or '?'} @ {sha or '?'}")
    return "\n".join(L)

# ── markdown → terminal (rich if available, else a small ANSI renderer) ─────────
def render(text: str) -> None:
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        Console().print(Markdown(text))
        return
    except Exception:
        pass
    out, in_code = [], False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append((DIM + "  ┄┄┄┄┄┄┄┄┄┄" + RESET) if _TTY else line)
            continue
        if in_code:
            out.append(CYAN + "  " + line + RESET)
            continue
        s = line
        if re.match(r"^#{1,6}\s", s):
            s = BOLD + re.sub(r"^#{1,6}\s", "", s) + RESET
        s = re.sub(r"\*\*(.+?)\*\*", BOLD + r"\1" + RESET, s)
        s = re.sub(r"`([^`]+)`", CYAN + r"\1" + RESET, s)
        s = re.sub(r"^(\s*)[-*]\s", r"\1• ", s)
        out.append(s)
    print("\n".join(out))

# ── the call ────────────────────────────────────────────────────────────────────
def ask(question: str, context: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {question}\n\n--- my environment ---\n{context}"},
    ]
    req = urllib.request.Request(
        ENDPOINT, method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        data=json.dumps({"messages": messages, "max_tokens": 700}).encode("utf-8"))
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8"))
        return (data.get("choices") or [{}])[0].get("message", {}).get("content") or "(no answer returned)"

def _explain_http(code: int, body: str) -> str:
    if code == 503:
        return "The class help endpoint isn't turned on right now (the class token is set day-of)."
    if code == 401:
        return "Bad/expired class token — check CLASS_LLM_TOKENS (or OPENAI_API_KEY) in your .env against today's token."
    if code == 429:
        return "Too many requests right now — wait a few seconds and try again."
    return f"[HTTP {code}] {body[:300]}"

def one(question: str, piped: str) -> None:
    context = snapshot() + (("\n\nPasted error / output:\n" + piped[:6000]) if piped else "")
    if _TTY:
        sys.stdout.write(DIM + "  … thinking\r" + RESET)
        sys.stdout.flush()
    try:
        answer = ask(question, context)
        if _TTY:
            sys.stdout.write("           \r")  # clear the spinner line
        print()
        render(answer)
        print()
    except urllib.error.HTTPError as e:
        print(RED + "\n" + _explain_http(e.code, e.read().decode("utf-8", "ignore")) + RESET + "\n")
    except urllib.error.URLError as e:
        print(RED + f"\nCouldn't reach the TA ({e.reason}). Check your connection / CLASS_HELP_URL." + RESET + "\n")
    except Exception as e:  # never crash the student's shell
        print(RED + f"\nSomething went wrong: {type(e).__name__}: {e}" + RESET + "\n")

def main() -> None:
    if not TOKEN:
        print(YEL + "No class token found. Put today's token in your .env:\n"
              "  CLASS_LLM_TOKENS=<the token from class>   (or set OPENAI_API_KEY to it)" + RESET)
        return
    args = " ".join(sys.argv[1:]).strip()
    piped = "" if sys.stdin.isatty() else sys.stdin.read().strip()
    if args:
        one(args, piped)
        return
    if piped:
        one("What's going wrong here and how do I fix it, for my setup?", piped)
        return
    # interactive REPL
    print(f"{BOLD}AI Architect TA{RESET} {DIM}· gpt-5.4 · your environment is attached · ask away, q to quit{RESET}")
    while True:
        try:
            q = input(f"{GRN}TA ›{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("q", "quit", "exit"):
            break
        if not q:
            continue
        one(q, "")
    print(DIM + "bye 👋" + RESET)

if __name__ == "__main__":
    main()
