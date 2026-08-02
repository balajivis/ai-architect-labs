/**
 * tutor.ts — the interactive CLI tutor kit, ported to TypeScript for Lab 8.
 *
 * A faithful glass-box port of `mai_rag/tutor.py` (read them side by side —
 * that's the point). A lab is a sequence of STAGES: each teaches (prose), then
 * runs (code), then shows status. Same UI contract as the Python labs:
 *
 *   · an intro screen — what the lab is about + the full stage map before anything runs
 *   · a live stage rail — ● done · ◉ current · ○ upcoming · ↷ skipped · ✗ failed
 *   · a forgiving menu — Enter run · s skip · r redo · o overview · ? help · q quit
 *   · failure recovery — a crashed stage offers retry / skip / quit (never a stack-trace death)
 *   · spinners with elapsed time for slow beats
 *   · graceful degradation — piped/non-TTY input auto-runs; NO_COLOR strips ANSI
 *
 * Node builtins only (readline) — nothing here is magic; read it top to bottom.
 */
import * as readline from "node:readline";

export const TTY_IN = process.stdin.isTTY === true;
export const TTY_OUT = process.stdout.isTTY === true;
const COLOR = TTY_OUT && process.env.NO_COLOR === undefined;

const c = (code: string, s: string) => (COLOR ? `\x1b[${code}m${s}\x1b[0m` : s);
export const bold = (s: string) => c("1", s);
export const dim = (s: string) => c("2", s);
export const yellow = (s: string) => c("33", s);
export const green = (s: string) => c("32", s);
export const cyan = (s: string) => c("36", s);
export const red = (s: string) => c("31", s);

export function width(): number {
  return Math.min(process.stdout.columns || 100, 100);
}

export function rule(ch = "─"): void {
  console.log(cyan(ch.repeat(width())));
}

/** Greedy word-wrap of one paragraph to `w` columns. */
function fill(text: string, w: number): string[] {
  const words = text.split(/\s+/).filter(Boolean);
  const lines: string[] = [];
  let line = "";
  for (const word of words) {
    if (line && (line + " " + word).length > w) { lines.push(line); line = word; }
    else line = line ? line + " " + word : word;
  }
  if (line) lines.push(line);
  return lines;
}

/** Teaching prose: dedent, reflow to the terminal, paragraph-aware. */
export function say(text: string, indent = "  "): void {
  const paras = text.replace(/^\n+|\n+$/g, "").split(/\n\s*\n/);
  for (const para of paras) {
    for (const line of fill(para, width() - 4)) console.log(indent + line);
    console.log();
  }
}

export function note(text: string): void {
  console.log(`  ${dim("↳ " + text)}`);
}

/** A boxed block — used to frame artifacts (JSON, tool lists) so they read as exhibits. */
export function panel(title: string, body: string): void {
  console.log(`\n  ${yellow("┌─ " + title + " ─")}`);
  for (const line of body.replace(/\s+$/, "").split("\n")) console.log(`  ${yellow("│")} ${line}`);
  console.log(`  ${yellow("└─")}`);
}

/** `const sp = spinner("connecting"); ... sp.stop();` — animated on a TTY. */
export function spinner(label: string): { stop: () => void } {
  const FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏";
  const t0 = Date.now();
  let timer: ReturnType<typeof setInterval> | undefined;
  if (TTY_OUT) {
    let i = 0;
    timer = setInterval(() => {
      const secs = ((Date.now() - t0) / 1000).toFixed(0).padStart(4);
      process.stdout.write(`\r  ${cyan(FRAMES[i % FRAMES.length])} ${label} ${dim(secs + "s")} `);
      i++;
    }, 120);
  } else {
    console.log(`  … ${label}`);
  }
  return {
    stop() {
      if (timer) { clearInterval(timer); process.stdout.write("\r" + " ".repeat(width() - 1) + "\r"); }
      const took = (Date.now() - t0) / 1000;
      if (took >= 1) console.log(`  ${dim(`(${label}: ${took.toFixed(0)}s)`)}`);
    },
  };
}

// ── input (one shared readline; non-TTY auto-runs) ───────────────────────────
let rl: readline.Interface | undefined;
function ask(prompt: string): Promise<string | null> {
  if (!TTY_IN) return Promise.resolve(null);
  if (!rl) rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    const iface = rl!;
    const onClose = () => resolve(null); // EOF / Ctrl-D → caller's default
    iface.once("close", onClose);
    iface.question(prompt, (answer) => { iface.off("close", onClose); resolve(answer); });
  });
}
export function closeInput(): void {
  rl?.close();
  rl = undefined;
}

/** Free-text prompt inside a stage (e.g. "search for…"). Non-TTY returns the
 *  default silently, so piped runs stay fully unattended. */
export async function promptLine(question: string, def = ""): Promise<string> {
  const hint = def ? dim(` (Enter = ${def})`) : "";
  const raw = await ask(`  ${yellow("›")} ${question}${hint}: `);
  const a = (raw ?? "").trim();
  return a || def;
}

export interface Stage {
  title: string;
  teach: string;                       // the prose shown before running
  run: () => Promise<void>;
  calls?: string;                      // rough LLM-call estimate, shown on the map
  status?: "pending" | "done" | "skipped" | "failed";
}

const MARKS = { pending: "○", current: "◉", done: "●", skipped: "↷", failed: "✗" } as const;
const TINT = { pending: dim, current: yellow, done: green, skipped: dim, failed: red } as const;

export class Tutor {
  title: string;
  tagline: string;
  mission: string;
  stages: Stage[];
  outro: string;

  constructor(title: string, tagline: string, mission: string, stages: Stage[], outro = "") {
    this.title = title;
    this.tagline = tagline;
    this.mission = mission;
    this.stages = stages;
    this.outro = outro;
    for (const st of stages) st.status = st.status ?? "pending";
  }

  // ── screens ────────────────────────────────────────────────────────────────
  introScreen(providerLine = ""): void {
    console.log();
    rule("═");
    console.log(`  ${bold(this.title)}`);
    console.log(`  ${dim(this.tagline)}`);
    rule("═");
    console.log();
    say(this.mission);
    this.stageMap();
    if (providerLine) console.log(`  ${dim(providerLine)}`);
    if (TTY_IN) console.log(`\n  ${dim("controls: Enter run · s skip · r redo previous · o overview · ? help · q quit")}`);
    console.log();
  }

  stageMap(current?: number): void {
    console.log(`  ${bold("THE STAGES")}`);
    this.stages.forEach((st, i) => {
      const state = i === current ? "current" : (st.status ?? "pending");
      const mark = TINT[state](MARKS[state]);
      const calls = st.calls && st.calls !== "0" ? dim(`~${st.calls} LLM calls`) : dim("no LLM");
      console.log(`    ${mark} ${i + 1}. ${st.title.padEnd(52)} ${calls}`);
    });
    console.log();
  }

  banner(i: number): void {
    console.log();
    rule();
    console.log(`  ${bold(`STAGE ${i + 1}/${this.stages.length} · ${this.stages[i].title}`)}`);
    rule();
  }

  // ── menus (every input loop validates; junk input never crashes) ───────────
  async menu(i: number): Promise<"run" | "skip" | "redo" | "quit"> {
    if (!TTY_IN) { console.log(`  ${dim("… auto-run")}`); return "run"; }
    for (;;) {
      const raw = await ask(`  ${yellow("▶ Enter")} run · ${yellow("s")} skip · ${yellow("o")} overview · ${yellow("q")} quit ${yellow("›")} `);
      const a = (raw ?? "").trim().toLowerCase();
      if (raw === null || a === "" || a === "run" || a === "y") return "run";
      if (a === "s" || a === "skip") return "skip";
      if (a === "r" || a === "redo") return "redo";
      if (a === "o" || a === "overview" || a === "map") { this.stageMap(i); continue; }
      if (a === "?" || a === "h" || a === "help") {
        console.log(`  ${dim("Enter=run this stage · s=skip it · r=redo the previous stage · o=show the stage map · q=quit")}`);
        continue;
      }
      if (a === "q" || a === "quit" || a === "exit") return "quit";
      console.log(`  ${dim("…didn’t catch that — Enter, s, r, o, ? or q")}`);
    }
  }

  async failMenu(): Promise<"retry" | "skip" | "quit"> {
    if (!TTY_IN) return "skip";        // unattended runs keep going
    for (;;) {
      const raw = await ask(`  ${yellow("r")} retry · ${yellow("s")} skip stage · ${yellow("q")} quit ${yellow("›")} `);
      const a = (raw ?? "q").trim().toLowerCase();
      if (a === "r" || a === "retry" || a === "") return "retry";
      if (a === "s" || a === "skip") return "skip";
      if (a === "q" || a === "quit") return "quit";
    }
  }

  // ── the drive loop ─────────────────────────────────────────────────────────
  async run(providerLine = ""): Promise<void> {
    this.introScreen(providerLine);
    let i = 0;
    outer: while (i < this.stages.length) {
      const st = this.stages[i];
      this.banner(i);
      say(st.teach);
      const action = await this.menu(i);
      if (action === "quit") { console.log(`\n  ${dim("leaving — progress so far:")}`); this.stageMap(); closeInput(); return; }
      if (action === "skip") { st.status = "skipped"; note("skipped."); i++; continue; }
      if (action === "redo") {
        if (i === 0) { note("nothing before this stage."); continue; }
        i--; this.stages[i].status = "pending"; continue;
      }
      for (;;) {                        // run, with failure recovery
        try {
          await st.run();
          st.status = "done";
          break;
        } catch (e) {                   // clean message, never a stack-trace death
          const err = e as Error;
          console.log(`\n  ${yellow("⚠  " + (err.message || String(e)).slice(0, 300))}`);
        }
        const act = await this.failMenu();
        if (act === "retry") continue;
        if (act === "skip") { st.status = "failed"; break; }
        console.log(`\n  ${dim("leaving — progress so far:")}`); this.stageMap(); closeInput(); return;
      }
      i++;
    }
    console.log();
    rule("═");
    const done = this.stages.filter((s) => s.status === "done").length;
    console.log(`  ${green(`✔ ${this.title} complete`)} — ${done}/${this.stages.length} stages run.`);
    if (this.outro) { console.log(); say(this.outro); }
    rule("═");
    console.log();
    closeInput();
  }
}
