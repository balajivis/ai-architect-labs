"""
mai_rag.tutor — the interactive CLI tutor kit the labs share. Glass-box: read it.

A lab is a sequence of STAGES. Each stage teaches (prose), then runs (code), then
shows status. The kit gives every lab the same, robust terminal UI:

  · an intro screen — what the lab is about + the full stage map before anything runs
  · a live stage rail — ● done · ◉ current · ○ upcoming · ↷ skipped · ✗ failed
  · a forgiving menu — Enter run · s skip · r redo · o overview · ? help · q quit
  · failure recovery — a crashed stage offers retry / skip / quit (never a stack-trace death)
  · spinners with elapsed time for slow beats (model downloads, scoring loops)
  · graceful degradation — piped/non-TTY input auto-runs; NO_COLOR strips ANSI

Nothing here is magic: ~200 lines of stdlib you can read top to bottom.
"""
from __future__ import annotations

import os
import shutil
import sys
import textwrap
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

TTY_IN = sys.stdin.isatty()
TTY_OUT = sys.stdout.isatty()
COLOR = TTY_OUT and os.environ.get("NO_COLOR") is None


def _c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if COLOR else s

def bold(s): return _c("1", s)
def dim(s): return _c("2", s)
def yellow(s): return _c("33", s)
def green(s): return _c("32", s)
def cyan(s): return _c("36", s)
def red(s): return _c("31", s)


def width() -> int:
    return min(shutil.get_terminal_size((100, 24)).columns, 100)


def rule(ch: str = "─") -> None:
    print(cyan(ch * width()))


def say(text: str, indent: str = "  ") -> None:
    """Teaching prose: dedent, reflow to the terminal, paragraph-aware."""
    for para in textwrap.dedent(text).strip("\n").split("\n\n"):
        print(textwrap.indent(textwrap.fill(" ".join(para.split()), width() - 4), indent))
        print()


def note(text: str) -> None:
    print(f"  {dim('↳ ' + text)}")


def panel(title: str, body: str) -> None:
    """A boxed block — used to frame artifacts (tables, files) so they read as exhibits."""
    print(f"\n  {yellow('┌─ ' + title + ' ─')}")
    for line in body.rstrip().splitlines():
        print(f"  {yellow('│')} {line}")
    print(f"  {yellow('└─')}")


def show_df(df, title: str) -> None:
    panel(title, df.to_string(index=False))


class Spinner:
    """`with Spinner("scoring hybrid"):` — animated on a TTY, a single line otherwise."""

    FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, label: str):
        self.label = label
        self._stop = threading.Event()
        self._t0 = 0.0
        self._thread: threading.Thread | None = None

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            frame = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(f"\r  {cyan(frame)} {self.label} {dim(f'{time.time() - self._t0:4.0f}s')} ")
            sys.stdout.flush()
            i += 1
            time.sleep(0.12)

    def __enter__(self):
        self._t0 = time.time()
        if TTY_OUT:
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
        else:
            print(f"  … {self.label}")
        return self

    def __exit__(self, *exc):
        self._stop.set()
        if self._thread:
            self._thread.join()
            sys.stdout.write("\r" + " " * (width() - 1) + "\r")
        took = time.time() - self._t0
        if took >= 1:
            print(f"  {dim(f'({self.label}: {took:.0f}s)')}")
        return False


def choice(prompt: str, options: dict[str, str], default: str) -> str:
    """Numbered picker. Non-interactive input returns the default silently."""
    if not TTY_IN:
        return default
    keys = list(options)
    print(f"  {bold(prompt)}")
    for i, k in enumerate(keys, 1):
        mark = dim(" (default)") if k == default else ""
        print(f"    {yellow(str(i))}. {options[k]}{mark}")
    while True:
        try:
            raw = input(f"  {yellow('›')} ").strip()
        except EOFError:
            return default
        if raw == "":
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(keys):
            return keys[int(raw) - 1]
        print(f"  {dim('pick 1–' + str(len(keys)) + ' or Enter for the default')}")


@dataclass
class Stage:
    title: str
    teach: str                      # the prose shown before running
    run: Callable[[], None]
    calls: str = "0"                # rough LLM-call estimate, shown on the map
    status: str = "pending"         # pending | done | skipped | failed


MARKS = {"pending": "○", "current": "◉", "done": "●", "skipped": "↷", "failed": "✗"}
TINT = {"pending": dim, "current": yellow, "done": green, "skipped": dim, "failed": red}


@dataclass
class Tutor:
    title: str
    tagline: str
    mission: str                    # the "what this lab is about" intro prose
    stages: list[Stage] = field(default_factory=list)
    outro: str = ""

    # ── screens ──────────────────────────────────────────────────────────────
    def intro_screen(self, provider_line: str = "") -> None:
        print()
        rule("═")
        print(f"  {bold(self.title)}")
        print(f"  {dim(self.tagline)}")
        rule("═")
        print()
        say(self.mission)
        self.stage_map()
        if provider_line:
            print(f"  {dim(provider_line)}")
        if TTY_IN:
            print(f"\n  {dim('controls: Enter run · s skip · r redo previous · o overview · ? help · q quit')}")
        print()

    def stage_map(self, current: int | None = None) -> None:
        print(f"  {bold('THE STAGES')}")
        for i, st in enumerate(self.stages):
            state = "current" if i == current else st.status
            mark = TINT[state](MARKS[state])
            calls = dim(f"~{st.calls} LLM calls") if st.calls not in ("0", "") else dim("no LLM")
            print(f"    {mark} {i + 1}. {st.title:<52} {calls}")
        print()

    def banner(self, i: int) -> None:
        st = self.stages[i]
        print()
        rule()
        print(f"  {bold(f'STAGE {i + 1}/{len(self.stages)} · {st.title}')}")
        rule()

    # ── menus (every input loop validates; junk input never crashes) ─────────
    def menu(self, i: int) -> str:
        if not TTY_IN:
            print(f"  {dim('… auto-run')}")
            return "run"
        while True:
            try:
                a = input(f"  {yellow('▶ Enter')} run · {yellow('s')} skip · {yellow('o')} overview · {yellow('q')} quit {yellow('›')} ").strip().lower()
            except EOFError:
                return "run"
            except KeyboardInterrupt:
                print(); return "quit"
            if a in ("", "run", "y"):
                return "run"
            if a in ("s", "skip"):
                return "skip"
            if a in ("r", "redo"):
                return "redo"
            if a in ("o", "overview", "map"):
                self.stage_map(current=i); continue
            if a in ("?", "h", "help"):
                print(f"  {dim('Enter=run this stage · s=skip it · r=redo the previous stage · o=show the stage map · q=quit')}")
                continue
            if a in ("q", "quit", "exit"):
                return "quit"
            print(f"  {dim('…didn’t catch that — Enter, s, r, o, ? or q')}")

    def fail_menu(self) -> str:
        if not TTY_IN:
            return "skip"                       # unattended runs keep going
        while True:
            try:
                a = input(f"  {yellow('r')} retry · {yellow('s')} skip stage · {yellow('q')} quit {yellow('›')} ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return "quit"
            if a in ("r", "retry", ""):
                return "retry"
            if a in ("s", "skip"):
                return "skip"
            if a in ("q", "quit"):
                return "quit"

    # ── the drive loop ───────────────────────────────────────────────────────
    def run(self, provider_line: str = "") -> None:
        self.intro_screen(provider_line)
        i = 0
        while i < len(self.stages):
            st = self.stages[i]
            self.banner(i)
            say(st.teach)
            action = self.menu(i)
            if action == "quit":
                print(f"\n  {dim('leaving — progress so far:')}"); self.stage_map(); return
            if action == "skip":
                st.status = "skipped"; note("skipped."); i += 1; continue
            if action == "redo":
                if i == 0:
                    note("nothing before this stage."); continue
                i -= 1; self.stages[i].status = "pending"; continue
            while True:                          # run, with failure recovery
                try:
                    st.run()
                    st.status = "done"
                    break
                except KeyboardInterrupt:
                    print(f"\n  {yellow('interrupted.')}")
                except RuntimeError as e:        # the kit's clean errors (key / rate limit)
                    print(f"\n  {yellow('⚠  ' + str(e))}")
                except Exception as e:           # anything else — still no stack-trace death
                    print(f"\n  {red('✗ ' + type(e).__name__ + ': ' + str(e)[:200])}")
                act = self.fail_menu()
                if act == "retry":
                    continue
                if act == "skip":
                    st.status = "failed"; break
                print(f"\n  {dim('leaving — progress so far:')}"); self.stage_map(); return
            i += 1
        print()
        rule("═")
        done = sum(s.status == "done" for s in self.stages)
        print(f"  {green(f'✔ {self.title} complete')} — {done}/{len(self.stages)} stages run.")
        if self.outro:
            print()
            say(self.outro)
        rule("═")
        print()
