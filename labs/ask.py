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
        try:                                     # utf-8-sig eats a Windows Notepad BOM,
            _txt = _cand.read_text(encoding="utf-8-sig")   # which otherwise corrupts the FIRST key
        except (OSError, UnicodeDecodeError):
            _txt = ""                            # an unreadable .env must never crash the import
        for _ln in _txt.splitlines():
            _ln = _ln.strip()
            if _ln.startswith("export "):        # people paste shell-style lines into .env
                _ln = _ln[7:].lstrip()
            if _ln and not _ln.startswith("#") and "=" in _ln:
                _k, _v = _ln.split("=", 1)
                _v = _v.strip()
                if len(_v) > 1 and _v[0] == _v[-1] and _v[0] in ("\'", '"'):
                    _v = _v[1:-1]                # quoted: take it verbatim
                elif " #" in _v:
                    _v = _v.split(" #", 1)[0].strip()   # unquoted: drop a trailing comment
                os.environ.setdefault(_k.strip(), _v)
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

Answer FROM the retrieved help articles attached to the question when they fit — they are the authoritative course fixes, so quote their exact commands. Also use the student's machine snapshot to make the answer specific to them. When a code file is attached (the lab file they asked about, or the file from a pasted traceback), READ it and point at the specific line/function that matters. If nothing retrieved fits, answer from your own knowledge of the course.

Be CONCISE — a few lines. Give the command(s), then a one-line why. Do NOT dump setup checklists or "your key setup looks fine" notes unless asked or clearly the fix. TRUST the student: if they say something already works, don't re-suggest installing it — answer what they actually asked, and don't re-diagnose problems they didn't raise. Never reveal keys.

When a student asks WHICH lab covers a topic (e.g. "which lab for graphRAG / reranking / memory isolation / evals?"), use the LAB MAP below to name the specific lab(s) and the move/technique in them. If the exact topic has no dedicated lab (graphRAG and knowledge-graph RAG are NOT separate labs, for instance), say so plainly and point to the CLOSEST lab — don't invent a lab that doesn't exist.

COMPANY FACTS (use these for "who built this / what company is behind this" questions — do NOT confuse
them with the lab corpus):
- This course, the labs, and the mai_rag kit are built by Modern AI Pro (modernaipro.com), the AI education
  company. The class platform / proxy lives at learn.modernaipro.com.
- Founder & lead instructor: Dr. Balaji Viswanathan — CEO & Lead Instructor, two decades in AI and robotics,
  former CEO of Mitra Robot (AI/robotics deployed in 50+ global organizations), PhD in human-robot
  interaction, earlier at Microsoft and Black Duck (Synopsys).
- Modern AI Pro is the education arm of a three-product family: Modern AI Pro (LEARN — this course),
  Kapi (BUILD — enterprise AI agent platform, app.getkapi.com, ships all 8 agent layers: UI, graph,
  integrations, knowledge, memory, HITL, eval, observability — "Most AI Agents Fail. Yours Won't."), and
  Brahmasumm (DEPLOY — air-gapped enterprise knowledge discovery). The intended journey: learn AI here,
  build agents with Kapi, deploy knowledge systems at work with Brahmasumm.
- DISAMBIGUATION: "Northwind Technologies" is the FICTIONAL company in the lab CORPUS (~131 synthetic
  policy docs engineered to break naive RAG). It did not build anything and is not real. "Which company
  built it?" about the course/labs/kit → Modern AI Pro. Questions about the corpus content → Northwind."""

# ── LAB MAP — what each lab builds, so the TA can route a topic to the right lab ──
# Keep in sync with CLAUDE.md's lab table. Pillars: I Advanced RAG · II Evals · III MCP · IV Trust.
LAB_INDEX = """LAB MAP (Modern AI Pro · AI Architect — four pillars, taught eval-first):
- Lab 1  (lab_1.py) · Pillar II · Evaluation First: build a golden set, open the box on faithfulness,
  BASELINE the naive RAG (retrieve→stuff→answer). The scorecard every later lab must beat.
- Lab 1b (lab_1b.py) · Pillar I · RAG Foundations "The Dials" (100% keyless, no LLM): chunking strategy,
  chunk size, overlap, embedding model (MiniLM vs MPNet), top-k, similarity threshold, phrasing, title-prepending —
  each re-scored on the golden set. Go here for "how does chunking/embeddings/top-k affect retrieval".
- Lab 2  (lab_2.py) · Pillar I · Advanced Retrieval, measured: HYBRID search (BM25/lexical + dense), RRF fusion,
  metadata filtering, CROSS-ENCODER RERANK, contextual retrieval, UMAP maps. Go here for hybrid/reranking/keyword-vs-vector.
- Lab 2c (lab_2c.py) · Pillar I · GraphRAG, Routed: build a knowledge GRAPH from documents (LLM triple extraction),
  traverse it, DUEL graph+chunks vs chunks-alone on relation-shaped questions, and learn WHEN graph loses / how to
  route to it. THIS is the GraphRAG / knowledge-graph lab. Go here for graphRAG, entities/relations, multi-hop over a graph.
- Lab 3  (lab_3.py) · Pillar I · Agentic RAG "The Five Decisions": router (should I retrieve?), HyDE/multi-query,
  DECOMPOSITION (multi-hop), sufficiency + CRAG web fallback, budget caps. Go here for agentic/multi-hop/query-rewriting RAG.
- Lab 3b (lab_3b.py) · Pillar I · Adaptive RAG: a complexity router sends each query to direct/naive/agentic;
  every call metered; quality×cost race. Go here for routing/cost-vs-quality tradeoffs.
- Lab 3c (lab_3c.py) · Pillar I · Agent Architectures "The Authoring Workbench" (LANGGRAPH — needs the agents
  extra: pip install -e ".[agents]"): the four shapes under every framework, hand-built as ~30-line glass-box
  graphs — ReAct tool loop, reflection (generate→critique→revise), plan-and-execute, supervisor+workers — then a
  judged+metered showdown and a compose-your-own workbench. Go here for LangGraph, building agents, ReAct,
  reflection, multi-agent supervisor, "which agent architecture".
- Lab 3d (lab_3d.py) · Pillar I · The Enterprise Stack: GOOGLE ADK (needs the adk extra: pip install -e ".[adk]"):
  the same shapes as framework classes — tools=[...], SequentialAgent, LoopAgent with escalate-exit, sub_agents
  transfer — plus the event stream, session state, callbacks-as-meter, and a DUEL vs the student's own 3c
  LangGraph supervisor. Go here for ADK, Agent Development Kit, enterprise agent frameworks, framework-vs-handrolled.
- Lab 4  (lab_4.py) · Pillar I · Memory: working + long-term memory, user-scoped retrieval, personalization.
- Lab 4b (lab_4b.py) · Pillar I · The Memory Stack: L1 short-term · L2 working · L3 episodic (REM-flush) · L4 durable
  profile; recall + ISOLATION evals; memory × RAG composed. Go here for memory layers / per-user isolation.
- Lab 5  (lab_5.py) · Pillar II · Evals & Benchmarks: the RAGAS triad, an LLM-judge CALIBRATED to human labels
  (Cohen's kappa + bias probes), and the release/eval GATE. Go here for RAGAS/judge-calibration/CI gate.
- Lab 6  (lab_6.py, WIP) · Pillar IV · Guardrails & Security: a 4-gate gauntlet (PII → injection → off-policy → output)
  scored as evaluators, row-level TENANT ACLs, EU AI Act mapping. Go here for guardrails/PII/jailbreak/tenant isolation.
- Lab 7  (lab_7.py) · Pillar IV · Human-in-the-Loop: an action-boundary gate (structural risk-tag · dynamic
  triggers · the real 4-gate guardrails as a safety floor), an atomic pause+approval queue with three resume
  paths (approve / reject / resolve-with-a-human-edit), and the eval→HITL bridge. Go here for HITL/approval
  queues/pause-resume/risk-tagged tools.
- Lab 7b (lab_7b.py) · Pillar IV · Ship Audit-Ready: TRACE one RAG→eval→HITL request (references + timings, never
  payloads), attribute COST per stage, classify the EU AI Act risk TIER (LLM-judged), map SOC2 controls, and GATE
  on a replayable record. Go here for observability/tracing/cost-attribution/EU AI Act/SOC2/audit-ready/compliance.
- Lab 8  (labs/mcp_server/, WIP, TypeScript) · Pillar III · MCP Engineering: build + harden an MCP server over the wire
  (OAuth/audience, tool-poisoning guard, resilience). The one non-Python lab; needs Node 22+.
NOT dedicated labs (name the closest): fine-tuning / model training → out of scope (this course is retrieval + eval +
trust). GraphRAG IS covered — it's Lab 2c (do not say it's missing)."""

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

# The lab package set: core + [evals] + [viz] + the heavy transitive ones students ask about.
LAB_PKGS = ["mai_rag", "openai", "langchain-groq", "rank-bm25", "tavily-python",
            "sentence-transformers", "sqlite-vec", "numpy", "pandas", "matplotlib",
            "ragas", "datasets", "umap-learn", "scikit-learn", "torch", "transformers"]
# Per-lab optional extras: absence only matters for that lab — report with the right fix.
OPT_PKGS = {"langgraph": 'lab 3c only -> pip install -e ".[agents]"',
            "google-adk": 'lab 3d only -> pip install -e ".[adk]"'}

def _find_venv_python():
    for venv in (_repo / ".venv", _repo / "venv", pathlib.Path(".venv"), pathlib.Path("venv")):
        for sub in ("bin/python", "Scripts/python.exe"):
            py = venv / sub
            if py.exists():
                return venv, py
    return None, None

def _venv_probe() -> str:
    """Where the labs actually run: check EVERY lab package in the repo's venv (fast — reads
    installed metadata, no heavy imports). ask.py itself may run on a different interpreter."""
    venv, py = _find_venv_python()
    if not py:
        return "no repo .venv found — create: python3 -m venv .venv && .venv/bin/pip install -e '.[evals,viz]'"
    code = ("import importlib.metadata as m\n"
            "for p in " + repr(LAB_PKGS + list(OPT_PKGS)) + ":\n"
            "    try: print(p + '=' + m.version(p))\n"
            "    except Exception: print(p + '=MISSING')")
    try:
        out = subprocess.run([str(py), "-c", code], capture_output=True, text=True, timeout=12)
        lines = [l for l in out.stdout.splitlines() if "=" in l]
        if not lines:
            return f"{venv.name} found ({py}) but couldn't read installed packages"
        present = [l for l in lines if not l.endswith("=MISSING")]
        missing = [l.split("=")[0] for l in lines if l.endswith("=MISSING")]
        core_missing = [p for p in missing if p not in OPT_PKGS]
        opt_missing = [p for p in missing if p in OPT_PKGS]
        summary = f"{venv.name} ({py})\n  installed: " + ", ".join(present)
        if core_missing:
            summary += "\n  MISSING: " + ", ".join(core_missing) + " -> run `pip install -e \".[evals,viz]\"` in this venv"
        if opt_missing:
            summary += "\n  missing OPTIONAL extras: " + "; ".join(f"{p} ({OPT_PKGS[p]})" for p in opt_missing)
        if not missing:
            summary += "\n  all core + [evals] + [viz] + agent-framework packages present"
        return summary
    except Exception as e:
        return f"{venv.name} found but probe failed: {type(e).__name__}"

def snapshot() -> str:
    L = [
        f"ask.py's interpreter: python {platform.python_version()} ({sys.executable}) — may differ from your lab venv",
        f"os: {platform.system()} {platform.release()} {platform.machine()}",
        f"repo venv (where labs run): {_venv_probe()}",
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

# ── agentic RAG: pull in the CODE FILE(s) the question / traceback is about ──────
CODE_MAX = 12000   # chars per attached file

def _code_refs(text: str) -> set:
    refs = set()
    for m in re.findall(r'File "([^"]+\.py)"', text):               # python tracebacks
        refs.add(m)
    for m in re.findall(r'(?<![\w"])([\w./-]+\.py)\b', text):         # bare .py paths / names
        refs.add(m)
    for n in re.findall(r'\blab[ _-]?(\d+[a-z]?)\b', text.lower()):   # "lab 2" / "lab_2"
        refs.add(f"labs/lab_{n}.py")
    return refs

def gather_code(text: str, limit: int = 3) -> list:
    """Attach the code the question is actually about — the lab file it names, or the file(s)
    in a pasted traceback. Security: only .py files that resolve INSIDE the repo or cwd, never
    arbitrary system paths; each capped at CODE_MAX."""
    roots = []
    for r in (_repo, pathlib.Path.cwd()):
        try:
            roots.append(str(r.resolve()))
        except Exception:
            pass
    out, seen = [], set()
    for ref in _code_refs(text):
        for cand in (pathlib.Path(ref), _repo / ref, _repo / "labs" / pathlib.Path(ref).name,
                     pathlib.Path.cwd() / ref):
            try:
                p = cand.resolve()
            except Exception:
                continue
            if p in seen or p.suffix != ".py" or not p.is_file():
                continue
            if not any(str(p).startswith(root) for root in roots):    # stay inside the repo/cwd
                continue
            try:
                code = p.read_text(errors="ignore")
            except Exception:
                continue
            seen.add(p)
            out.append((p, code[:CODE_MAX] + ("\n… (truncated)" if len(code) > CODE_MAX else "")))
            break
        if len(out) >= limit:
            break
    return out

def _code_block(files: list) -> str:
    return "\n\n".join(f"--- {p.name} ({p}) ---\n{code}" for p, code in files)

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
    system_msg = {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + LAB_INDEX +
                  "\n\nStudent's machine snapshot:\n" + snapshot()}

    if args or piped:  # one-shot
        q = args or "What's going wrong here and how do I fix it, for my setup?"
        hits = retrieve(q + " " + piped)
        files = gather_code(q + "\n" + piped)
        if _TTY and (hits or files):
            bits = []
            if hits:
                bits.append("articles: " + " · ".join(h["title"][:38] for h in hits))
            if files:
                bits.append("code: " + ", ".join(p.name for p, _ in files))
            print(DIM + "↳ retrieved " + " | ".join(bits) + RESET)
        faq_ctx = ("Retrieved help articles:\n" + _faq_block(hits) + "\n\n") if hits else ""
        code_ctx = ("Attached code files:\n" + _code_block(files) + "\n\n") if files else ""
        user = faq_ctx + code_ctx + "Question: " + q + (("\n\nPasted error / output:\n" + piped[:6000]) if piped else "")
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
        files = gather_code(q)
        if hits or files:
            bits = []
            if hits:
                bits.append("articles: " + " · ".join(h["title"][:38] for h in hits))
            if files:
                bits.append("code: " + ", ".join(p.name for p, _ in files))
            print(DIM + "↳ retrieved " + " | ".join(bits) + RESET)
        faq_ctx = ("Retrieved help articles:\n" + _faq_block(hits) + "\n\n") if hits else ""
        code_ctx = ("Attached code files:\n" + _code_block(files) + "\n\n") if files else ""
        req = convo[:-1] + [{"role": "user", "content": faq_ctx + code_ctx + q}]  # augment only the request
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
