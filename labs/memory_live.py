# -*- coding: utf-8 -*-
"""memory_live.py — a LIVE chat with the memory stack emerging next to it (teaching demo).

Modern AI Pro · AI Architect · Pillar I · Memory (companion to Lab 4 / Lab 4b)

    python labs/memory_live.py

Left half: a real chat (retrieve → answer over the catalog corpus).
Right rail: the memory layers MATERIALIZING as you talk — the point of the demo is that memory
is not an LLM "artifact" you take on faith, it's a THING on disk you watch form:

    L1 · short-term   the rolling window + its token count
    L2 · working      working.yaml  (who / now / open) — rewritten every turn
    L4 · identity     semantic/profile.yaml — durable facts that ACCRETE as you reveal who you are

Type a message and watch the rail update. Commands:
    /flush   REM-flush the session → a dated episodic .md, clears L1+L2 (the NEXT turn still remembers)
    /reset   wipe this demo's memory
    /quit    exit

Everything is written under .memory/live/ (git-ignored) — open the files while you teach; the rail
is just those files, rendered. Needs a key (class token / OpenAI); retrieval is keyless.
"""

# --- repo local-run shim: load .env, work with or without __file__ ----------
import os, pathlib, sys, textwrap, datetime

_here = pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path.cwd()
for _cand in (pathlib.Path(".env"), _here.parent / ".env", _here / ".env"):
    if _cand.exists():
        try:
            _txt = _cand.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            _txt = ""
        for _line in _txt.splitlines():
            _line = _line.strip()
            if _line.startswith("export "):
                _line = _line[7:].lstrip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                _v = _v.strip()
                if len(_v) > 1 and _v[0] == _v[-1] and _v[0] in ("'", '"'):
                    _v = _v[1:-1]
                elif " #" in _v:
                    _v = _v.split(" #", 1)[0].strip()
                os.environ.setdefault(_k.strip(), _v)
        break

import yaml
from mai_rag import corpus, llm
from mai_rag.llm import complete_json

MEM_ROOT = pathlib.Path(".memory") / "live"


def _now_stamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d-%H%M")


class LiveMemory:
    """The four layers, self-contained + file-backed (mirrors Lab 4b's MemoryStack). Every layer
    is a FILE on disk; the right rail just renders these. That's the whole point — tangible, not a
    hidden LLM behaviour."""

    def __init__(self, user_id: str = "guest"):
        self.user = user_id
        self.root = MEM_ROOT / user_id
        (self.root / "episodic").mkdir(parents=True, exist_ok=True)
        (self.root / "semantic").mkdir(parents=True, exist_ok=True)
        self.transcript: list[dict] = []      # L1
        self.working: dict = {}               # L2 (also on disk as working.yaml)
        self.profile: dict = self._load_profile()   # L4

    # ── paths ────────────────────────────────────────────────────────────────
    @property
    def working_path(self): return self.root / "working.yaml"
    @property
    def profile_path(self): return self.root / "semantic" / "profile.yaml"

    def _load_profile(self) -> dict:
        if (self.root / "semantic" / "profile.yaml").exists():
            try:
                return yaml.safe_load((self.root / "semantic" / "profile.yaml").read_text()) or {}
            except Exception:
                return {}
        return {}

    # ── L1 short-term ─────────────────────────────────────────────────────────
    def window(self, n: int = 6) -> str:
        return "\n".join(f"{t['role']}: {t['text']}" for t in self.transcript[-n:])

    def tokens(self) -> int:
        return max(0, len(self.window(999)) // 4)

    # ── L2 working — distilled 'right now' state, rewritten each turn ──────────
    def update_working(self):
        if not self.transcript:
            return
        convo = "\n".join(f"{t['role']}: {t['text']}" for t in self.transcript[-8:])
        try:
            wm = complete_json(
                "Distill this conversation into WORKING MEMORY — the 'right now' state only.\n"
                'Keys: who (one line: who the user is), now (one line: what they are working on), '
                'open (list of unresolved threads / pending questions).\n\n' + convo)
            self.working = {"who": str(wm.get("who", "")), "now": str(wm.get("now", "")),
                            "open": wm.get("open", []) if isinstance(wm.get("open"), list) else []}
            self.working_path.write_text(yaml.safe_dump(self.working, sort_keys=False, allow_unicode=True))
        except Exception:
            pass

    # ── L4 durable — facts that accrete + merge ───────────────────────────────
    def update_profile(self, user_msg: str):
        try:
            r = complete_json(
                "Extract DURABLE facts about the USER from this message — things true across sessions "
                "(role, skills, goals, preferences, constraints). Nothing transient.\n"
                'Keys: facts (list), preferences (list). Empty lists if none.\n\n'
                f'Message: "{user_msg}"')
        except Exception:
            return
        for key in ("facts", "preferences"):
            new = r.get(key, [])
            if not isinstance(new, list):
                continue
            cur = self.profile.setdefault(key, [])
            for item in new:
                item = str(item).strip()
                if item and item not in cur:
                    cur.append(item)
        if self.profile:
            self.profile_path.write_text(yaml.safe_dump(self.profile, sort_keys=False, allow_unicode=True))

    # ── L3 episodic — REM-flush closes the session ────────────────────────────
    def rem_flush(self) -> pathlib.Path | None:
        if not self.transcript:
            return None
        convo = "\n".join(f"{t['role']}: {t['text']}" for t in self.transcript)
        try:
            summary = llm.complete(
                "Summarize this session as 3-5 short markdown bullets: WHAT happened and WHY it "
                "matters next time. Facts only.\n\n" + convo, tier="small")
        except Exception:
            summary = "- (session summary unavailable)"
        path = self.root / "episodic" / f"{_now_stamp()}.md"
        path.write_text(f"---\ntype: session\nuser: {self.user}\ndate: {_now_stamp()}\n---\n\n{summary.strip()}\n")
        self.transcript = []                              # the flush CLOSES the session
        self.working = {}
        if self.working_path.exists():
            self.working_path.unlink()
        return path

    def episode_count(self) -> int:
        return len(list((self.root / "episodic").glob("*.md")))


def profile_hint(mem: LiveMemory) -> str:
    bits = mem.profile.get("facts", []) + mem.profile.get("preferences", [])
    return "; ".join(bits) if bits else "(unknown user)"


def respond(mem: LiveMemory, user_msg: str, store) -> str:
    """One turn: rewrite the message to a standalone query using the window + who-we-know, retrieve,
    answer. The rewrite (resolving 'that'/'it') is where the WINDOW earns its keep."""
    window = mem.window()
    standalone = llm.complete(
        "Rewrite the user's LAST message as a standalone search query, resolving any pronouns "
        f"('that'/'it') using the conversation and what we know about them.\n"
        f"KNOWN USER: {profile_hint(mem)}\nCONVERSATION:\n{window}\nLAST: {user_msg}\n\nStandalone query:",
        tier="small").strip()
    hits = store.search(standalone, k=4)
    ctx = "\n\n".join(f"[{h.title}] {h.content}" for h in hits)
    answer = llm.complete(
        "Answer the user for the catalog. Use the conversation for continuity, the context for facts, "
        "and personalize to the known user when relevant.\n"
        f"KNOWN USER: {profile_hint(mem)}\nCONVERSATION:\n{window}\nUSER: {user_msg}\n\n"
        f"CONTEXT:\n{ctx}\n\nAnswer:", tier="small")
    mem.transcript.append({"role": "User", "text": user_msg})
    mem.transcript.append({"role": "Bot", "text": answer})
    return answer, standalone


# ── rendering (rich if present, else a plain two-column fallback) ─────────────
try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    _RICH = True
    _con = Console()
except Exception:
    _RICH = False
    _con = None


def _yaml_or(text_empty: str, obj) -> str:
    if not obj:
        return f"[dim]{text_empty}[/dim]" if _RICH else text_empty
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True).rstrip()


def render(mem: LiveMemory, last_rewrite: str = ""):
    if not _RICH:
        print("\n" + "═" * 78)
        print("MEMORY  ·  L1 window (%d tok):" % mem.tokens())
        print(textwrap.indent(mem.window() or "(empty)", "  "))
        print("\nL2 working.yaml:\n" + textwrap.indent(_yaml_or("(none yet)", mem.working), "  "))
        print("\nL4 profile.yaml:\n" + textwrap.indent(_yaml_or("(nothing durable yet)", mem.profile), "  "))
        print("═" * 78)
        return
    _con.clear()
    # LEFT — the chat
    chat = Text()
    for t in mem.transcript[-10:]:
        if t["role"] == "User":
            chat.append("you  ", style="bold green"); chat.append(t["text"] + "\n")
        else:
            chat.append("bot  ", style="bold cyan"); chat.append(t["text"][:400] + "\n\n", style="")
    if not mem.transcript:
        chat.append("(say hi — e.g. \"I'm a non-coding PM new to AI\")", style="dim")
    left = Panel(chat, title="[bold]live chat[/bold]", border_style="green")
    # RIGHT — the memory rail (each panel IS a file on disk)
    rail = Group(
        Panel(Text(mem.window() or "(empty)", style="dim"),
              title=f"[bold]L1 · window[/] · {mem.tokens()} tok", border_style="yellow"),
        Panel(Text.from_markup(_yaml_or("(forms after your first turn)", mem.working)),
              title="[bold]L2 · working.yaml[/] · rewritten each turn", border_style="magenta"),
        Panel(Text.from_markup(_yaml_or("(nothing durable yet — tell it who you are)", mem.profile)),
              title="[bold]L4 · profile.yaml[/] · accretes", border_style="blue"),
    )
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=3); grid.add_column(ratio=2)
    grid.add_row(left, rail)
    _con.print(grid)
    foot = f"[dim]rewrite → {last_rewrite[:70]}[/dim]\n" if last_rewrite else ""
    _con.print(foot + f"[dim]{mem.episode_count()} episode(s) on disk · /flush  /reset  /quit · files in {mem.root}[/dim]")


def _input(prompt: str) -> str:
    if _RICH:
        return _con.input(prompt)
    return input(prompt)


def main():
    if _RICH:
        with _con.status("embedding the catalog corpus (keyless, ~20s)…"):
            store = corpus.load_catalog_corpus()
    else:
        print("embedding the catalog corpus (keyless, ~20s)…")
        store = corpus.load_catalog_corpus()
    try:
        llm._provider()
    except Exception:
        print("\n  No LLM key found. Put today's class token in .env as CLASS_LLM_TOKENS "
              "(or OPENAI_API_KEY), then re-run.\n")
        return

    mem = LiveMemory()
    render(mem)
    while True:
        try:
            q = _input("[bold green]you ›[/] " if _RICH else "you › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nmemory persisted in", mem.root, "👋"); return
        if not q:
            continue
        if q.lower() in ("/quit", "/q", "quit", "exit"):
            print("memory persisted in", mem.root, "👋"); return
        if q.lower() == "/reset":
            import shutil
            shutil.rmtree(mem.root, ignore_errors=True)
            mem = LiveMemory(); render(mem)
            continue
        if q.lower() == "/flush":
            if _RICH:
                with _con.status("REM-flush → writing the episode, clearing L1+L2…"):
                    path = mem.rem_flush()
            else:
                print("REM-flush…"); path = mem.rem_flush()
            render(mem, last_rewrite=f"flushed → {path.name if path else 'nothing to flush'}")
            continue
        # a normal turn: answer, then let the memory layers re-form
        status = _con.status("thinking · retrieving · distilling working memory · updating identity…") if _RICH else None
        if status: status.start()
        try:
            answer, rewrite = respond(mem, q, store)
            mem.update_working()
            mem.update_profile(q)
        except RuntimeError as e:
            if status: status.stop()
            print(f"\n  ⚠  {e}\n")
            continue
        if status: status.stop()
        render(mem, last_rewrite=rewrite)


if __name__ == "__main__":
    main()
