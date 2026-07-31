#!/usr/bin/env python3
"""ask.py — talk to the AI Architect TA (gpt-5.4), with your environment attached + memory.

  python labs/ask.py                      # interactive REPL — remembers the conversation
  python labs/ask.py "pip install fails"  # one-shot
  python labs/ask.py "why this?" < err.txt   # attach a pasted error / traceback

Attaches a snapshot of your setup — Python/OS, whether mai_rag is installed in your repo
.venv (where the labs actually run), which LLM keys are set, repo/branch, any piped error —
so answers fit YOUR machine. In the REPL it keeps the chat in memory so it doesn't repeat
itself. Renders markdown. Standard library only (uses `rich` if present).

Token: put today's class token in your .env as CLASS_LLM_TOKENS=<token> (or OPENAI_API_KEY).
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
_repo = _here.parent
for _cand in (pathlib.Path(".env"), _repo / ".env", _here / ".env"):
    if _cand.exists():
        for _ln in _cand.read_text().splitlines():
            _ln = _ln.strip()
            if _ln and not _ln.startswith("#") and "=" in _ln:
                _k, _v = _ln.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
        break

_BASE = os.environ.get("OPENAI_BASE_URL", "https://learn.modernaipro.com/api/llm/v1").rstrip("/")
ENDPOINT = os.environ.get("CLASS_ASK_URL", _BASE + "/chat/completions")
TOKEN = (os.environ.get("CLASS_LLM_TOKENS", "").split(",")[0].strip()
         or os.environ.get("CLASS_TOKEN", "").strip()
         or os.environ.get("OPENAI_API_KEY", "").strip())
# Cloudflare (in front of learn.modernaipro.com) 403s the default python-urllib UA.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) mai-architect-ask/1.0")

SYSTEM_PROMPT = """You are the TA for Modern AI Pro's "AI Architect" (Practitioner) course. Help ONLY with this course: its labs (the mai_rag kit, labs/lab_1.py ...), Python/venv/pip, API keys / the class proxy, and course concepts (RAG, evals, agents, MCP, trust). If a question is off-topic, say briefly that you only help with this course.

Answer FROM the retrieved help articles attached to the question when they fit — they are the authoritative course fixes, so quote their exact commands. Also use the student's machine snapshot to make the answer specific to them. If nothing retrieved fits, answer from your own knowledge of the course.

Be CONCISE — a few lines. Give the command(s), then a one-line why. Do NOT dump setup checklists or "your key setup looks fine" notes unless asked or clearly the fix. TRUST the student: if they say something already works, don't re-suggest installing it — answer what they actually asked, and don't re-diagnose problems they didn't raise. Never reveal keys."""

# ── terminal styling (ANSI only on a tty) ───────────────────────────────────────
_TTY = sys.stdout.isatty()
def _c(code: str) -> str:
    return code if _TTY else ""
BOLD, DIM, RESET = _c("\033[1m"), _c("\033[2m"), _c("\033[0m")
CYAN, YEL, GRN, RED = _c("\033[36m"), _c("\033[33m"), _c("\033[32m"), _c("\033[31m")

# ── agentic snapshot — probes the repo .venv (where the labs run), not just ask.py's python ──
def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(_here),
                              capture_output=True, text=True, timeout=4).stdout.strip()
    except Exception:
        return ""

def _venv_mai_rag() -> str:
    """Where the labs actually run: check mai_rag in the repo's venv (fast — reads installed
    metadata, doesn't import torch). ask.py itself may run on a different interpreter."""
    for venv in (_repo / ".venv", _repo / "venv", pathlib.Path(".venv"), pathlib.Path("venv")):
        py = venv / "bin" / "python"
        if not py.exists():
            py = venv / "Scripts" / "python.exe"   # windows
        if py.exists():
            try:
                out = subprocess.run(
                    [str(py), "-c", "import importlib.metadata as m; print(m.version('mai_rag'))"],
                    capture_output=True, text=True, timeout=8)
                if out.returncode == 0 and out.stdout.strip():
                    return f"{venv.name}: mai_rag {out.stdout.strip()} INSTALLED (run labs with {py})"
                return f"{venv.name}: mai_rag NOT installed (run: {py} -m pip install -e '.[evals,viz]')"
            except Exception:
                return f"{venv.name}: found but couldn't probe"
    return "no repo .venv found — create one: python3 -m venv .venv && .venv/bin/pip install -e '.[evals,viz]'"

def snapshot() -> str:
    L = [
        f"ask.py's interpreter: python {platform.python_version()} ({sys.executable}) — may differ from your lab venv",
        f"os: {platform.system()} {platform.release()} {platform.machine()}",
        f"repo venv (where labs run): {_venv_mai_rag()}",
    ]
    env = [f"{k}={'set' if os.environ.get(k) else 'unset'}"
           for k in ("GROQ_API_KEY", "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY", "GEMINI_API_KEY")]
    env += [f"{k}={os.environ.get(k) or 'unset'}" for k in ("OPENAI_BASE_URL", "MAI_LLM_PROVIDER")]
    L.append("llm-env: " + ", ".join(env))
    L.append(f"cwd: {os.getcwd()} · .env present: {'yes' if (pathlib.Path('.env').exists() or (_repo / '.env').exists()) else 'no'}")
    branch, sha = _git("rev-parse", "--abbrev-ref", "HEAD"), _git("rev-parse", "--short", "HEAD")
    if branch or sha:
        L.append(f"repo: branch={branch or '?'} @ {sha or '?'}")
    return "\n".join(L)

# ── FAQ knowledge base + lexical retrieval — the RAG course's own help tool does RAG ──
_STOP = {"the", "a", "an", "is", "how", "do", "i", "to", "my", "in", "it", "of", "and",
         "for", "on", "this", "what", "why", "that", "with", "you", "we", "are", "get",
         "when", "can", "if", "not", "am", "run", "me"}

def _load_faq() -> list:
    for path in (_here / "FAQ.md", _repo / "FAQ.md", _repo / "labs" / "FAQ.md", pathlib.Path("labs/FAQ.md")):
        if path.exists():
            faq = []
            for b in re.split(r"\n##\s+", "\n" + path.read_text())[1:]:  # [0] is the intro
                title, _, body = b.strip().partition("\n")
                if not title:
                    continue
                faq.append({
                    "title": title.strip(), "body": body.strip(),
                    "toks": set(re.findall(r"[a-z0-9_]+", (title + " " + body).lower())),
                    "ttoks": set(re.findall(r"[a-z0-9_]+", title.lower())),
                })
            return faq
    return []

FAQ = _load_faq()

def retrieve(query: str, k: int = 3) -> list:
    """Lexical retrieval over FAQ.md — title matches weighted higher. (Keyword, not
    embeddings, so it works even when the student's install/torch is broken.)"""
    q = set(re.findall(r"[a-z0-9_]+", query.lower())) - _STOP
    if not q or not FAQ:
        return []
    scored = [(len(q & e["toks"]) + 2 * len(q & e["ttoks"]), e) for e in FAQ]
    scored = [(s, e) for s, e in scored if s > 0]
    scored.sort(key=lambda x: -x[0])
    return [e for _, e in scored[:k]]

def _faq_block(entries: list) -> str:
    return "\n\n".join(f"[{e['title']}]\n{e['body']}" for e in entries)

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
def call(messages: list) -> str:
    req = urllib.request.Request(
        ENDPOINT, method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": UA},
        data=json.dumps({"messages": messages, "max_tokens": 500}).encode("utf-8"))
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.loads(r.read().decode("utf-8"))
        return (d.get("choices") or [{}])[0].get("message", {}).get("content") or "(no answer returned)"

def _explain_http(code: int, body: str) -> str:
    if code == 503:
        return "The class proxy isn't turned on right now (the class token is set day-of)."
    if code == 401:
        return "Bad/expired class token — check CLASS_LLM_TOKENS (or OPENAI_API_KEY) in your .env against today's token."
    if code == 429:
        return "Rate-limited right now — wait a few seconds and try again."
    if code == 403:
        return "Blocked at the edge (403). If this persists, tell the instructor."
    return f"[HTTP {code}] {body[:300]}"

def _spin(on: bool) -> None:
    if not _TTY:
        return
    sys.stderr.write((DIM + "…thinking" + RESET) if on else "\r\033[2K")
    sys.stderr.flush()

def send(messages: list):
    """Returns the answer text, or None (and prints why) on failure."""
    _spin(True)
    try:
        ans = call(messages)
        _spin(False)
        return ans
    except urllib.error.HTTPError as e:
        _spin(False)
        print(RED + _explain_http(e.code, e.read().decode("utf-8", "ignore")) + RESET)
    except urllib.error.URLError as e:
        _spin(False)
        print(RED + f"Couldn't reach the TA ({e.reason}). Check your connection / CLASS_ASK_URL." + RESET)
    except Exception as e:  # never crash the student's shell
        _spin(False)
        print(RED + f"Something went wrong: {type(e).__name__}: {e}" + RESET)
    return None

def main() -> None:
    if not TOKEN:
        print(YEL + "No class token found. Put today's token in your .env:\n"
              "  CLASS_LLM_TOKENS=<the token from class>   (or set OPENAI_API_KEY to it)" + RESET)
        return
    args = " ".join(sys.argv[1:]).strip()
    piped = "" if sys.stdin.isatty() else sys.stdin.read().strip()
    system_msg = {"role": "system", "content": SYSTEM_PROMPT + "\n\nStudent's machine snapshot:\n" + snapshot()}

    if args or piped:  # one-shot
        q = args or "What's going wrong here and how do I fix it, for my setup?"
        hits = retrieve(q + " " + piped)
        if hits and _TTY:
            print(DIM + "↳ retrieved: " + " · ".join(h["title"][:46] for h in hits) + RESET)
        faq_ctx = ("Retrieved help articles:\n" + _faq_block(hits) + "\n\n") if hits else ""
        user = faq_ctx + "Question: " + q + (("\n\nPasted error / output:\n" + piped[:6000]) if piped else "")
        ans = send([system_msg, {"role": "user", "content": user}])
        if ans:
            print()
            render(ans)
            print()
        return

    # interactive REPL — with memory
    print(f"{BOLD}AI Architect TA{RESET} {DIM}· gpt-5.4 · your env attached · remembers this chat · q to quit{RESET}")
    convo = [system_msg]
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
        convo.append({"role": "user", "content": q})   # clean question — this is the memory
        hits = retrieve(q)
        if hits:
            print(DIM + "↳ retrieved: " + " · ".join(h["title"][:46] for h in hits) + RESET)
        faq_ctx = ("Retrieved help articles:\n" + _faq_block(hits) + "\n\n") if hits else ""
        req = convo[:-1] + [{"role": "user", "content": faq_ctx + q}]  # augment only the request
        ans = send(req)
        if ans is None:
            convo.pop()            # drop the failed turn so memory stays clean
            continue
        convo.append({"role": "assistant", "content": ans})
        if len(convo) > 9:         # keep the system msg + last ~4 exchanges
            convo = [convo[0]] + convo[-8:]
        print()
        render(ans)
        print()
    print(DIM + "bye 👋" + RESET)

if __name__ == "__main__":
    main()
