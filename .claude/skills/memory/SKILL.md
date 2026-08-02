---
name: memory
description: "The one memory skill for the portfolio. Capture, flush, park, resume, graduate, and recall agent memory across Kapi and Modern AI Pro using the L1–L4 stack (short-term · working · episodic · semantic). Use when you need to write down a finding, close out an issue, step away from in-progress work, pick it back up, or find out whether we've hit this before. Replaces /post, /park, /resume, /issue-fixed's archive half, and the ad-hoc 'update wm.md' habit."
argument-hint: "<verb> [args] — capture | flush | park | resume | graduate | recall | status"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Memory

> An LLM has no memory. Everything it "remembers" is text someone put back into the
> prompt. So memory is an **architecture you can see** — files on disk — not a claim.
> This skill is the write/read protocol for those files.

The model is `class-resources/ai-architect-labs/labs/lab_4.py` (and 4b): four layers,
each file-backed, each with a different lifetime and a different eviction rule.
Kapi and Modern AI Pro both already implement it — under different filenames. This
skill is the single contract; §1 maps it onto each repo.

---

## 1. The stack (and where each layer lives)

| Layer | Lifetime | Kapi (`kapi-platform/`) | Modern AI Pro (`modernaipro/`) | Portfolio |
|---|---|---|---|---|
| **L1 · short-term** | this session | the context window itself | same | same |
| **L2 · working** | this issue / sprint | `docs/wm.md` + `.kapi/board.md`, `.kapi/entries/` | `docs/wm.md` (+ `status.md`) | `.kapi/blackboard-live.yaml` |
| **L3 · episodic** | permanent, append-only | `docs/episodic/` + `README.md` index | `docs/episodic/` | `.kapi/entries/` |
| **L4 · semantic** | durable, accretes | `CLAUDE.md`, `docs/identity.yaml` rules, `docs/adrs/`, `.kapi/lessons.md` | `CLAUDE.md`, `docs/adrs/` | root `CLAUDE.md`, `~/.claude/projects/-Users-bv-Code-active/memory/` |
| **Backlog funnel** | pre-work | `.kapi/backlog.md` (Inbox) | `ideas.md → park.md → next.md` | — |
| **Parked WIP** | days–weeks | `.kapi/parked/` (+ `_resumed/`) | `docs/park.md` topic sections | — |

**MAI's GTD funnel** is the fuller version and the one to imitate when in doubt:

```
ideas (raw inbox) → park (someday/maybe) → next (committed backlog)
      → wm (today) → episodic (archive)      … with ADRs/lessons peeling off sideways as L4
```

**The load-bearing property** (lab 4's punchline): a flush clears L1+L2 and the system
*still remembers*, because L3 and L4 survive it. If clearing working memory loses
knowledge, you flushed wrong — the knowledge belonged in L3 or L4 and you skipped the
graduation step.

---

## 2. Verbs

Dispatch on the first word of `$ARGUMENTS`. No verb → run `status`.

| Verb | One-liner | Writes to |
|---|---|---|
| `capture` | Fast write of a finding/decision/blocker/idea. <30s, no conversation. | L2 (+ backlog) |
| `flush` | REM-flush: an issue shipped → archive its wm section, reset wm. | L2 → L3 |
| `park` | Stepping away mid-work → snapshot state + next action. | L2 → parked |
| `resume` | Coming back → restore the snapshot and brief the human. | parked → L2 |
| `graduate` | A durable fact/decision/correction escaped its scratchpad → pin it. | L2/L3 → L4 |
| `recall` | "Have we hit this before?" — search all four layers in order. | read-only |
| `status` | What's in flight, what's parked, what's owed. | read-only |

---

### `capture <type> <message>`

Types: `finding` · `decision` · `blocker` · `steer` · `idea`. Missing/unclear → `finding`.

1. Write `.kapi/entries/{YYYY-MM-DD-HHMM}-{role}-{type}-{slug}.md` (Kapi/portfolio) with
   frontmatter `type`, `role`, `timestamp` and a 1–3 sentence body under a short title.
   In MAI, append to the matching `docs/*.md` section instead of minting an entry file.
2. Append one line to the routing target:

| Type | Kapi | MAI |
|---|---|---|
| finding | `.kapi/board.md` → `## Findings` | `docs/wm.md` → current section |
| decision | `## Open Decisions` | `docs/wm.md` (or ADR if ratified → `graduate`) |
| blocker | `## Active Blockers` | `docs/wm.md` → blockers |
| steer | `## Directives` | `docs/wm.md` → directives |
| idea | `.kapi/backlog.md` → `## Inbox` | `docs/ideas.md` (raw one-liner) |

Line format: `- **Human:Balaji** — {message} — {short timestamp}` (use the Human Identity
table in `kapi-platform/CLAUDE.md`; default `Human`). Confirm in one line and stop.

> **Be fast.** The human posted this to avoid losing their train of thought. Don't
> interview them, don't restructure the board, don't start working the finding.

---

### `flush [slug]`

The REM-flush. Working memory is a scratchpad; it must not grow monotonically.
Run when an issue is **shipped, tested, and doc-synced**. Every stage must pass before
the next runs — on failure, STOP and report (a) which stage, (b) the concrete reason
(file/commit/test output), (c) the suggested next action. Never silently continue.

- **Stage 0 — reconcile.** `git log <last-episodic-commit>..HEAD --no-merges`; any commit
  not mentioned in wm.md gets appended as a `commit reconciliation` section, committed
  before proceeding.
- **Stage 1 — tests exist.** For each fix commit, `git show --stat` the touched sources and
  grep `tests/`, `__tests__/`, `*.spec.ts`, `*.test.ts` for coverage. A fix with no test is
  a stop — the human decides: write it, accept-and-document, or abort.
- **Stage 2 — tests pass.** Run the acceptance test recorded in wm.md (`/run-tests` in Kapi).
  Any red is a stop.
- **Stage 3 — docs synced.** Kapi: `npx tsx scripts/build/gen-status.ts`, then walk
  CLAUDE.md / scorecard / recipes / deletions / lessons. Commit doc changes separately.
- **Stage 4 — archive.** Write `docs/episodic/{YYYY-MM-DD}-{slug}.md`:

```markdown
---
date: YYYY-MM-DD
slug: <slug>
title: "<title from working memory>"
agents: [<participants>]
commits: [<SHAs of fix + doc-sync>]
acceptance_test: "<one line>"
result: pass | accepted-failure
related_adrs: [ADR-NNN]
related_lessons: ["YYYY-MM-DD — <title>"]
tags: []
---

# <title>

<the wm.md section VERBATIM — plan, critique, fix report, test output, doc-sync, inline discussion>
```

- **Stage 5 — index + reset.** Append `- [YYYY-MM-DD — <title>](./<file>.md) — <outcome>` to
  `docs/episodic/README.md` under the month heading (create the README if missing). Then
  replace the flushed section of `wm.md` with a "Just flushed" pointer line to the new file
  (MAI style) — carry any still-open threads forward to `next.md` rather than deleting them.
- **Stage 6 — commit.** Pathspec-restricted, never `git add .`:
  `git add -- docs/episodic/ docs/wm.md docs/next.md && git commit -m "episodic-memory: archive <slug>"`.

**Preserve the section verbatim.** Episodic memory's whole value is the unedited record —
future agents grep here when they see a familiar symptom. Summarize and you've destroyed it.

---

### `park <label>`

Setting work aside, **not** closing it. If it's actually done, run `flush` instead.

1. **Reflect state back first** (4–6 lines) from `wm.md`, `git log --oneline -15`,
   `git status --short`, `.kapi/board.md` — so the human corrects rather than dictates.
2. **Ask these six, one at a time, waiting for each answer.** This is the whole value of
   the verb; silently summarizing from git defeats it.
   1. What were you working on?
   2. Current state — done / half-done / blocked / stuck?
   3. First thing future-you should do on return? *(the most valuable line in the file)*
   4. Any half-formed thoughts you don't want to lose? *(capture **verbatim** — the vague
      phrasing is itself the cue that re-anchors thinking)*
   5. Open questions you didn't decide? *(numbered)*
   6. Anything someone else might change while you're away? *(peer agents, crons, deploys)*
3. **Uncommitted changes**: ask "commit as WIP, or note as WIP-on-disk?" If commit, stage by
   pathspec and `wip: parking <label>`. If on-disk, list the files in the park file so
   `resume` can warn if they vanish. **Never `git stash`** (CLAUDE.md rule).
4. **Write** `.kapi/parked/{YYYY-MM-DD}-{label}.md` (MAI: a `## <topic>` section in
   `docs/park.md`) with frontmatter `date, label, title, parked_by, expected_return, branch,
   head_sha, uncommitted_files, related_adrs, related_episodic` and sections: *What was being
   worked on · Current state · First action on return · Open questions · Half-formed thoughts ·
   What might change while away · References · Verbatim snapshot of wm.md* (whole file, fenced).
5. **Reset wm.md** to a pointer so a cold agent doesn't re-engage the thread:
   `> **Currently parked.** State as of <date> is in <path>. Run \`/memory resume <label>\`.`
6. Commit pathspec-restricted (`park: <label> — <title>`). Never push. Report, then **stop working**.

---

### `resume [label]`

No label → list `.kapi/parked/*.md` newest-first as
`<label>  (parked YYYY-MM-DD, branch: <branch>) — <title>` and ask which. **Never auto-pick.**

1. **Read the whole park file** — frontmatter, prose, and the verbatim wm snapshot.
2. **Check for drift**: `git rev-parse --abbrev-ref HEAD`, `git rev-parse --short HEAD`,
   `git log --oneline <head_sha>..HEAD`, `git status --short`.
   - Branch + head unchanged → clean resume.
   - Head advanced → summarize what landed (yours or peers') in the brief.
   - Branch differs → **ask**; never auto-switch.
   - `uncommitted_files` from the park file now missing → **flag loudly**, work may be lost.
3. **Restore wm.md** from the verbatim snapshot. If wm.md is no longer just the parked
   pointer, STOP — show the human the current contents and ask merge / overwrite / abort.
   Never silently overwrite peer-agent work.
4. **Brief the human**: parked date + days ago · branch/head status · what you were working on ·
   state at park · *first action in their own words* · open questions · half-formed thoughts ·
   what landed since. Then ask *"Ready to start with `<first action>`?"* and **wait**.
5. **Move, don't delete**: `git mv` the file into `.kapi/parked/_resumed/`, commit `resume: <label>`.

Edge cases: no match → list, don't fuzzy-match. Duplicate labels → ask. Parked >30 days →
say so and suggest an `/arch-reviewer` pass. Referenced files gone → flag before acting.

---

### `graduate <what>`

The step people skip — and the reason flushes lose knowledge. A fact that will still be
true next month does **not** belong in wm.md or an episodic file. Route it:

| The thing | Goes to | Skill/step |
|---|---|---|
| Architectural decision, ratified | `docs/adrs/NNN-*.md` | Kapi `/adr` — never write ADRs from a doc-sync (I-23) |
| Correction from the founder | `.kapi/lessons.md`, dated, `Mistake / Lesson / Context` | append immediately, not at session end |
| Non-negotiable rule | `docs/identity.yaml` → `rules:` (I-N, with `Enforced by:`) | only if the work surfaced a real error class |
| Load-bearing fact (route, model, convention) | the relevant `CLAUDE.md` | not counts — those are generated into `STATUS.md` |
| Routine done twice | `docs/engineering/recipes/` | write the recipe on the *second* occurrence |
| Deleted code | `docs/engineering/deletions.md` | log **before** deleting; include the restore command |
| A fact about Balaji / how to work with him | `~/.claude/projects/-Users-bv-Code-active/memory/*.md` + `MEMORY.md` line | one fact per file, with frontmatter |

Never invent a graduation to look productive. If nothing is durable, say so and stop.

---

### `recall <symptom or topic>`

Search **in this order** and stop when you have enough — cheapest and freshest first:

1. **L2** — `docs/wm.md`, `.kapi/board.md`, `.kapi/entries/`, `docs/next.md`: is it in flight *right now*?
2. **L3** — `grep -ril "<term>" docs/episodic/` (both repos): have we shipped this before?
   Read the matching file's frontmatter first — `acceptance_test` and `result` tell you fast
   whether it stuck.
3. **L4** — `.kapi/lessons.md`, `docs/adrs/`, `CLAUDE.md`, `~/.claude/.../memory/`: is there a
   standing rule or decision that already settles it?
4. **Parked** — `.kapi/parked/`, `docs/park.md`: was this abandoned mid-flight, and why?

Report as: *what we found · where · what it decided · whether it still holds.* If L4 and L3
disagree, **L4 wins and L3 is history** — say so explicitly rather than averaging them.

---

### `status`

Read-only. Print: current wm.md section titles (both repos) · open blockers and decisions on
the board · parked labels with age · episodic entries in the last 14 days · any lesson added
this week. One screen, no prose padding.

---

## 3. Boundaries (all verbs)

- **Never push.** Kapi invariant I-12. Every verb here commits locally; the human pushes.
- **Never `git stash`, `git reset --hard`, `git restore`, `git checkout -- <file>`, or
  `git clean -fd`.** Peer agents share these trees; their uncommitted work is invisible to you.
- **Pathspec-restricted commits only.** Never `git add .` — you will sweep up another agent's work.
- **Never paraphrase what the human said** in a park file or an episodic archive. Verbatim.
  The exact phrasing is the retrieval cue.
- **Never clear working memory without archiving first.** Flush = archive *then* reset, in that
  order, or the next agent walks in blind.
- **Never delete from `docs/episodic/` or `.kapi/parked/`.** Episodic is append-only; a resumed
  park moves to `_resumed/`. A colliding park label gets a `-v2` suffix and a callout.
- **Never start working from `park`, `resume`, or `recall`.** They restore context; the human starts.
- **Never write an ADR as a side effect.** Ratification is a separate, explicit step (I-23).
- **No regex for classification** anywhere in code this skill causes you to write (portfolio rule).
  Structural parsing of a known format is fine.

## 4. Update wm.md as you go

Between verbs, keep your live per-role status in `wm.md` — peers review, test, and deploy off
it. Don't wait for the flush to tell them what you did.
