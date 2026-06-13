# BUILD_YOUR_CORPUS.md — Build your own adversarial RAG corpus + golden set

> **You (Claude Code) are the build partner for this exercise.** The student is going to
> create a *custom* hard corpus and golden test set on the `mai_rag` kit — modelled on our
> shipped "Hard Pack," but in **their own domain** so it's IP-safe and real to them. Your job
> is to interview them, generate the docs and the golden file, load them, baseline a naive RAG,
> and confirm the corpus is genuinely *hard* (naive recall@5 clearly **below 1.0**). Work
> **one phase at a time**, show output, then move on. Use the cheapest model that works (Haiku).

This produces the **Hard Pack for the student's domain**: ~12–15 markdown docs engineered so
retrieval failure modes are *visible*, plus a ~12-case golden set where **every case is written
to break a naive retriever first.** That golden set becomes the through-line scorecard for the
rest of the course — the number every later technique (hybrid, rerank, contextual, agentic) has
to beat.

---

## Hard rules (state these to the student, honor them in everything you generate)

1. **NO regex for any classification — ever.** This corpus *teaches why regex fails.* Do not
   detect recency, PII, intent, "is this answerable," tier membership, or anything else with a
   pattern like `\d{3}-\d{2}-\d{4}` or a keyword list. Classification is LLM/ML-judged. (Regex is
   fine only for structural parsing — a URL, a file path, a known ID format.)
2. **The corpus is the student's OWN data.** Invent a single fictional org/product *in their
   domain* and write all prose yourself. Never paste a real customer's confidential docs. Synthetic
   = IP-safe by construction. (Our reference does this with a fictional "Northwind Technologies.")
3. **Keep it small enough to re-embed live.** Target **~12–15 docs / ~130–195 chunks**. That
   re-embeds with keyless MiniLM in **~10–20s** in the notebook — which is the whole point: the
   student *runs* the embed step instead of loading a pre-baked DB. Do **not** balloon to hundreds
   of docs; a big corpus saturates naive recall@5 at ≈1.0 and leaves every technique no headroom.
4. **Verify "naive breaks it" before a case earns a place.** A golden case only proves a technique
   has lift if the *baseline genuinely fails it.* A case naive already passes has zero discriminating
   power. The acceptance target is operational: **naive recall@5 must come out clearly < 1.0.**

---

## What you're modelling (the kit contract — obey field names EXACTLY)

The loader reads `---`-delimited **simple `key: value` frontmatter** (no nested YAML — the parser
is a naive partition on `:`). Frontmatter is stripped before embedding, so it's never embedded.

| Frontmatter key | What the loader does with it |
|---|---|
| `doc_id` | → `documents.source`. **This is the ID golden `supporting_doc_ids` must match** against retrieval hits (`hit.source`). Falls back to the **filename stem** if absent — so name files sensibly. |
| `title` | → `documents.title`. Falls back to filename stem. |
| `status` | Written into **each chunk's** metadata as `{"status": ...}` (default `"active"`). Drives the Lab 2 `status=active` metadata-filter move. Use `active` / `superseded`. |
| `last_updated` | → `documents.created_at` (date string, default `""`). |
| `supersedes` / `superseded_by` | Stored on the document row for **your own bookkeeping/readability only — the kit does not read them.** The one field that drives retrieval behavior (the Lab 2 `status=active` filter) is `status`. |

**Chunking** (`_chunk`): boundary-aware greedy packing to **~120 words** with a **~20-word overlap**
tail carried across boundaries (so a fact spanning a boundary stays retrievable). Paragraphs are
split on blank lines; a single paragraph over 120 words is **not** sub-split. `token_count` per
chunk = word count.

**Two golden shapes exist and are NOT interchangeable — use the right one:**

- **Policy / eval-path shape** — fields `question` (REQUIRED, no default → KeyError if missing) /
  `expected_answer` / `supporting_doc_ids` (list) / `criteria` (list) / `tier` / `failure_mode`.
  This is the **only** shape `GoldenSet.from_seed → run_suite → EvalInput` consumes. **Author the
  student's golden set in THIS shape.** (`id`/`doc_id` keys in the seed are ignored.)
- Hard-Pack lab shape — `q` / `expected` / `support` (a *string*, multi-hop joined with `+`,
  unanswerable marked `(none …)`) / `tag`. Read raw by the Lab 2/3/5 harnesses, **never** through
  the evaluator suite. We only mention it so you don't accidentally produce it.

`EvalInput` (what `run_suite` builds per case) carries exactly:
`question`, `answer`, `contexts`, `expected`, `criteria`. So your golden `expected_answer` and
`criteria` are what the evaluators see; `supporting_doc_ids` is what retrieval is scored against.

---

## Step 0 — Add the generic loaders (one-time)

The kit ships three *hardcoded* loaders (policy/hard/catalog), each bound to its own dir resolver
with **no path parameter** — so today a custom dir can only be loaded by hijacking
`MAI_CORPUS_DIR` + `load_policy_corpus(rebuild=True, prebuilt=False)`. We'll skip that hack by
adding a real generic loader. Append the block below to `mai_rag/corpus.py` (it reuses the existing
`_parse_frontmatter`, `_chunk`, `Store`, `embed`, `connect`, `json`, `os`, `Path` already imported
at the top of that file — add nothing else):

```python
# ── Generic loaders — bring-your-own corpus + golden ──
def load_corpus(corpus_dir: str, db_path: str = ":memory:", rebuild: bool = False,
                chunk_meta_key: str = "status") -> Store:
    """Generic sibling of load_hard_corpus: explicit path, live embed, no prebuilt DB.
    Writes per-chunk metadata {chunk_meta_key: meta.get(chunk_meta_key, default)}
    ('status'→'active' default, or 'type'→'topic' for catalog-style)."""
    default = "active" if chunk_meta_key == "status" else "topic"
    conn = connect(db_path)
    store = Store(conn)
    already = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    if already and not rebuild:
        return store
    if rebuild:
        for t in ("documents", "chunks", "vec_chunks", "golden_cases"):
            conn.execute(f"DELETE FROM {t}")
    for p in sorted(Path(corpus_dir).glob("*.md")):
        meta, body = _parse_frontmatter(p.read_text(encoding="utf-8"))
        doc_id = store.add_document(source=meta.get("doc_id", p.stem),
                                    title=meta.get("title", p.stem),
                                    metadata=meta, created_at=meta.get("last_updated", ""))
        chunks = _chunk(body)
        if not chunks:
            continue
        vecs = embed(chunks)
        for i, (text, vec) in enumerate(zip(chunks, vecs)):
            store.add_chunk(doc_id, i, text, vec,
                            metadata={chunk_meta_key: meta.get(chunk_meta_key, default)})
    store.commit()
    return store


def load_golden(path: str) -> list[dict]:
    """Read a custom golden file in the POLICY/eval-path shape (question/
    expected_answer/supporting_doc_ids/criteria/tier/failure_mode). Accepts a
    bare list or {"cases":[...]}. This is the policy shape the eval path consumes."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["cases"] if isinstance(data, dict) and "cases" in data else data
```

> Why a new loader and not the env-var hack: `load_corpus` takes an **explicit path** (no
> `MAI_CORPUS_DIR`, no `prebuilt=False` to remember so the shipped DB isn't restored over your
> data), lets you choose the chunk-metadata key, and `load_golden` pairs an arbitrary golden file —
> unifying the workflow the three hardcoded loaders fragment.

Quick smoke test after adding:

```python
import mai_rag.corpus as corpus
assert hasattr(corpus, "load_corpus") and hasattr(corpus, "load_golden")
```

---

## Step 1 — INTERVIEW the student (do not skip)

You can't engineer adversarial cases for a domain you don't understand. **Ask these, wait for
answers, then reflect back a one-paragraph "corpus brief" for confirmation** before generating
anything:

1. **Domain & fictional org.** "What domain is your RAG for (internal IT/HR knowledge base, a
   product's docs, a medical/legal/finance KB, devtool support, …)? I'll invent a single fictional
   org/product so nothing real leaks — what should I call it, or shall I pick a name?"
2. **Key entities, tiers, numbers.** "What are the named entities, tiers/plans, versions, and
   numeric thresholds that show up in your real docs (e.g. plan tiers, version numbers, dollar/time
   limits, SLAs)? Give me 5–10 — they become the precision and keyword traps."
3. **The questions users actually ask.** "What do users type at this system? Paste 8–12 real
   question shapes. Which feel 'simple lookup' vs. 'requires combining two docs' vs. 'about the
   *current* value of something that changed'?"
4. **Where the current system fails.** "Where does your existing search/RAG embarrass itself —
   returns a stale answer, grabs the wrong tier, confidently makes up a number, or can't say 'I
   don't know'? Those failures are exactly the cases we'll bake in."
5. **What changed recently.** "Name 2–3 policies/values/versions that were **revised** — the old
   value and the new value. These become the recency twins (active vs. superseded)."
6. **A genuine 'no fixed answer'.** "Is there a question users ask that *has no single answer* —
   it's case-by-case, or decided by a person? That's our unanswerable/should-decline case."

Capture the answers as the brief. Everything in Step 2/3 is generated *from this brief.*

---

## Step 2 — GENERATE ~12–15 docs, engineering the adversarial patterns

Write the docs to a fresh dir, e.g. `my_corpus/`. **One coherent fictional universe** — entities,
tiers and cross-refs must interlock so queries feel like real internal-KB questions, not a toy
fact-lookup set. Every doc gets the exact frontmatter above. Deliberately build **each** of these
(this is the menu our Hard Pack ships; map them onto the student's domain):

- **Recency twins (2–3 pairs, REQUIRED).** Ship `*-active.md` + `*-superseded.md` pairs. The active
  doc states the **operative** number; the superseded doc states the **stale** number. Both embed
  near a recency query, so naive top-k surfaces *both* and a generator can answer with the wrong
  one. Set `status: active` on the operative twin and `status: superseded` on the stale one —
  **`status` is the only field the kit acts on.** Optionally add `supersedes`/`superseded_by` for
  your own readability (stored, not read), and an "ARCHIVED — DO NOT RELY" banner in the superseded
  body. *(Our examples: data-retention 24mo active vs 36mo superseded; VPN client version; parental
  leave weeks.)* This is what makes the Lab 2 `status=active` filter visibly win.

- **Bare-reference chunks (the core of why contextual retrieval wins).** State a
  threshold/rule/number under a **generic header that never repeats the subject**, so the chunk
  embeds far from a query that names the subject. *(Our example: the "30-minute idle timeout" and
  "12-hour hard ceiling" live under a generic "Session Behavior and Limits" header that never says
  "VPN.")* These are confirmed to **miss** under naive retrieval — they're the direct headroom for
  the contextual-prepend technique.

- **Colliding headers / near-clone siblings.** Give multiple docs the **same** section headers
  ("Scope", "Exceptions", "Limits") so structurally similar chunks pile into one embedding
  neighborhood. Ship one **near-clone family** (e.g. plan tiers bronze/silver/gold/platinum)
  differing *only in the values* — maximally adversarial for telling which tier a chunk belongs to
  without surrounding context.

- **An acronym/entity defined ONCE, used bare elsewhere.** Bind an entity to its definition in
  exactly one chunk, reference it unlabeled afterward. *(Our example: "CrowdStrike Falcon agent"
  defined once as "the endpoint anti-malware/threat-detection (EDR) layer"; a query phrased as
  "EDR/anti-malware agent" only matches the defining chunk.)* Tests whether retrieval bridges a
  vocabulary gap a single definition creates.

- **A multi-hop chain (REQUIRED).** Make one doc **deliberately refuse to restate** a fact and point
  at another doc for it. *(Our examples: the incident-runbook says responders must pull the
  closed-account retention window *from* data-retention-active and refuses to restate "24 months";
  an expense band requires BOTH a VP approval AND a separate Security review mandated by a different
  doc.)* A single-shot top-k structurally can't assemble both halves — this is the headroom Labs 3+
  exploit.

- **Precision / boundary traps.** Encode exact crossover thresholds with adjacent off-by-one values
  and explicit "no rounding, no grace zone" language. *(Our example: $4,999 = Manager but $5,000 =
  Director; $24,999 = Director but $25,000 = VP.)*

- **Distractors / near-miss decoys (REQUIRED — and add MORE than feels necessary).** Plant
  deprecated-but-named alternatives that must **not** be the answer (a removed older version named
  prominently; the stale superseded figures sitting in-corpus). These are intentional
  wrong-but-adjacent attractors. **Our critic flagged the current Hard Pack as WEAK on
  precision+keyword distractors** — naive already finds those because there aren't enough in-corpus
  decoys. So over-plant: for every precision/keyword answer, seed 1–2 plausible nearby wrong values
  *elsewhere in the corpus* so a sloppy retriever has something to grab.

- **1–2 unanswerable / should-decline cases (REQUIRED).** Include a question whose correct answer is
  that **no answer exists**, and have a doc explicitly say so. *(Our example: the runbook states
  Northwind has no single fixed breach-notification deadline — Legal decides per-incident — so the
  golden expected is to DECLINE and refuse to quote a number.)* This tests calibrated abstention and
  punishes a RAG that hallucinates a plausible deadline.

### Example doc (copy the frontmatter shape exactly — substitute the student's domain)

```markdown
---
title: Acme Cloud — Approved Backup Client (Standard) 
doc_id: backup-client-standard-active
owner: Platform Team
last_updated: 2026-05-18
status: active
classification: internal
supersedes: backup-client-standard-superseded
superseded_by: ""
---

# Acme Cloud — Approved Backup Client (Standard)

This standard defines the single approved backup client ... The numbers in this
document are the values currently in force; where an older edition is cached, this
active edition's figures take precedence.

## Scope
Covers managed workstations connecting to the Acme backup fabric. Personal devices
are out of scope ...

## Session Behavior and Limits      <!-- bare-reference header: never repeats "backup" -->
- If a session carries no traffic for **30 minutes**, the coordinator tears it down.
- Regardless of activity, one session may run at most **12 hours** before a forced restart.
```

And its superseded twin (`backup-client-standard-superseded.md`) carries
`status: superseded`, `superseded_by: backup-client-standard-active`, an "ARCHIVED — DO NOT RELY"
banner, and the **stale** values.

Aim for ~150–400 words of body per doc so you land in the ~130–195 chunk window across 12–15 files.

---

## Step 3 — GENERATE the golden set (POLICY shape — the eval-path schema)

Write `my_corpus/golden_seed.json` as a **bare JSON list** (or `{"cases":[...]}`) of cases in the
**policy shape only**. Target **~12 cases**, tagged by failure mode via `failure_mode`, **each
written to break a naive retriever.** `supporting_doc_ids` must use the **`doc_id`s** you set in
frontmatter (that's what retrieval hits are scored against).

### Tag taxonomy to cover (map onto the student's domain)

| `failure_mode` | What it tests / how to author it |
|---|---|
| `recency` | active-vs-superseded conflict. `expected_answer` names the CURRENT value **and** explicitly calls the stale twin "no longer operative." |
| `contextual` | a fact in a bare-reference chunk meaningless without its parent doc's subject. The query names the subject the chunk omits. (Confirm it MISSES under naive — see Step 4.) |
| `multi-hop` | answer requires 2+ docs, one of which doesn't restate the other. List **both** `doc_id`s in `supporting_doc_ids`. |
| `precision` | exact boundary / off-by-one. Ask for **both sides** of the threshold. |
| `keyword` | answer hinges on an exact named token/version; older versions don't carry forward. (Motivates BM25/hybrid.) |
| `unanswerable` | correct response is to DECLINE; `expected_answer` says no fixed answer exists and to refuse to quote one. `supporting_doc_ids` may be `[]`. |

### Example golden case (EXACT eval-path schema — copy this shape)

```json
[
  {
    "id": "g1-recency-backup-timeout",
    "question": "We're configuring a workstation for backup today. Which backup client/version must we install, and what idle timeout applies?",
    "expected_answer": "Install Acme Backup Client 5.1.4 connecting to the Acme backup fabric. The Standard-tier inactivity cutoff is 30 minutes of no traffic before the session is torn down. (Any older edition naming a different build or timeout is no longer operative.)",
    "supporting_doc_ids": ["backup-client-standard-active"],
    "tier": "blueprint",
    "failure_mode": "recency",
    "criteria": [
      "names Acme Backup Client 5.1.4",
      "states the 30-minute idle timeout",
      "flags any older/superseded value as no longer operative"
    ]
  },
  {
    "question": "What is the fixed regulatory breach-notification deadline (in hours) responders must use for any incident involving customer data?",
    "expected_answer": "There is no fixed deadline to quote. The runbook states Acme does not maintain a single fixed notification deadline; timing is decided by Legal per-incident. Responders must not assume or quote a number.",
    "supporting_doc_ids": [],
    "tier": "blueprint",
    "failure_mode": "unanswerable",
    "criteria": ["declines to give a number", "attributes the decision to Legal per-incident"]
  }
]
```

**Schema gotchas to honor:**
- `question` is **required** (no default — a missing key raises `KeyError`).
- `criteria` must be a **list of strings** (the `contains` evaluator lowercases the answer and
  checks each phrase is a substring — keep phrases short and literally present in `expected_answer`).
  A bare string here can misbehave; always use a list.
- `id`/`doc_id` keys are **ignored** by `from_seed` (the DB assigns its own id) — fine to keep for
  your own readability.
- Use `tier`: `base` (smoke) / `blueprint` (your domain) / `production` (real thumbs-downs). Most
  custom cases are `blueprint`.

---

## Step 4 — LOAD it and BASELINE a naive RAG (confirm naive recall < 1.0)

Now wire it through the generic loaders and the suite. Retrieval is keyless; **only generation/judge
need a key** (Groq's free tier is easiest — set `GROQ_API_KEY` in `.env`).

```python
import mai_rag.corpus as corpus
from mai_rag.golden import GoldenSet, GoldenCase
from mai_rag.baseline import naive_rag
from mai_rag import evals, viz

# 1) Load the custom corpus — live embed (~10-20s). status→chunk metadata for the Lab-2 filter.
store = corpus.load_corpus("my_corpus", db_path=":memory:", rebuild=True)
print(store.stats())            # expect ~12-15 documents, ~130-195 chunks

# 2) Load the golden set in the policy shape and build a GoldenSet (skip from_seed's dir scan).
gs = GoldenSet(store)
for s in corpus.load_golden("my_corpus/golden_seed.json"):
    gs.add(GoldenCase(question=s["question"], expected=s.get("expected_answer", ""),
                      contexts=s.get("supporting_doc_ids", []), criteria=s.get("criteria", []),
                      tier=s.get("tier", "base"),
                      tags=[s["failure_mode"]] if s.get("failure_mode") else []))
gs.save()
print(len(gs), "golden cases loaded")
```

> **Do not call `GoldenSet.from_seed(store)` for your custom set** — `from_seed` scans the resolved
> *policy* corpus dir for `golden_seed.json`, not `my_corpus/`. Always build `GoldenCase` objects
> from `load_golden()` output as shown above.

### The acceptance gate — does naive actually fail?

Before trusting the corpus, **prove naive retrieval misses the right docs.** Compute recall@5
(fraction of `supporting_doc_ids` whose chunks naive top-k surfaces). This is the
eval-design analog of writing a failing test first:

```python
def naive_recall_at_k(store, gs, k=5):
    rows, total_hit, total_need = [], 0, 0
    for c in gs:
        if not c.contexts:          # unanswerable cases have no support docs — skip for recall
            continue
        hits = store.search(c.question, k=k)
        found = {h.source for h in hits}
        need = set(c.contexts)
        hit = len(need & found)
        rows.append((c.question[:60], f"{hit}/{len(need)}", sorted(need - found)))
        total_hit += hit; total_need += len(need)
    print(f"naive recall@{k} = {total_hit/total_need:.2f}  (target: clearly < 1.00)")
    for q, ratio, missed in rows:
        flag = "  <-- MISSED" if missed else ""
        print(f"  {ratio:>5}  {q}{flag}  {missed if missed else ''}")

naive_recall_at_k(store, gs)
```

> **Reading recall:** it's counted over *distinct support docs*. A multi-hop `1/2` can mean both
> docs exist but naive's top-5 chunks all landed in **one** doc — inspect the `MISSED` `doc_id`
> (printed above) rather than just bumping `k`.

- **If recall@5 ≈ 1.0 → the corpus is too easy.** No technique can demonstrate lift. Go back to
  Step 2 and **add more in-corpus distractors / more bare-reference chunks / tighten the colliding
  headers** (this is exactly the WEAK-distractor failure our critic flagged). Re-run until naive
  clearly misses several cases — especially the `contextual` and `multi-hop` ones, which *should*
  miss.
- **If recall@5 is clearly < 1.0 → good.** The corpus has headroom. Now run the full scorecard —
  this is the number every later lab must beat:

```python
run = evals.run_suite(store, gs, naive_rag, label="naive baseline (my corpus)")
viz.scorecard(run["summary"])    # context_precision/recall, faithfulness, relevancy, ...
```

Read the scorecard *with* the student: which evaluator is low, which tag is failing. Low
`context_recall` on `contextual`/`multi-hop` cases is the expected, healthy signal — that's the
headroom Labs 2–3 close.

---

## Step 5 — ITERATE

Adversarial corpus design is a loop, not a one-shot:

1. **Strengthen weak tags.** Any case naive already passes has no discriminating power. For
   `precision`/`keyword` especially, **add in-corpus decoy values** until naive can grab a
   plausible-but-wrong chunk. Re-run Step 4.
2. **Confirm the should-decline case.** Run `naive_rag(store, <unanswerable question>)` and check
   whether the baseline hallucinates a number. If it declines cleanly already, make the corpus
   *tempt* it harder (plant a plausible-looking but wrong figure nearby in a different doc).
3. **Confirm the contextual cases miss.** Re-query each `contextual` case; its support doc should
   **not** be in naive top-k. If it is, your bare-reference chunk still names its subject — rewrite
   the header/body to strip the subject so the chunk truly only makes sense with its parent.
4. **Keep it small.** If you've drifted past ~15 docs / ~200 chunks, cut — re-embed time and
   naive-recall saturation both creep up. Smaller-and-harder beats bigger-and-easier.
5. **Persist when happy.** Swap `db_path=":memory:"` for a file path (e.g.
   `db_path="my_corpus.db"`) so the same seeded store carries into Labs 2–5, where you'll watch
   hybrid → metadata-filter → contextual → agentic each move *this* scorecard.
6. **Re-seed golden after a rebuild.** `load_corpus(rebuild=True)` also clears the `golden_cases`
   table — re-run the `GoldenSet` build + `gs.save()` cell right after, or your `eval_results` will
   reference stale case ids (heatmap/compare joins break).

When naive recall@5 lands clearly below 1.0 and each tag has a case the baseline genuinely fails,
the student has a real adversarial Hard Pack in their own domain — the through-line for the rest of
the course.