# The eval gate

Lab 5 ends with: *"in CI this verdict IS the assert — a red gate blocks the merge,
and no un-evaluated change reaches production."* This directory is that assert.

**The rule, in one line: a red gate blocks the merge.** The candidate ships only if
the headline metric rises beyond the noise floor **and** nothing else regresses.

## What's here

| File | What it does |
|---|---|
| `test_eval_gate.py` | The gate. Two tests that always run keyless + three that need a key. |
| `conftest.py` | Loads `.env` (same as the labs) and puts the repo on `sys.path`. |
| `../.github/workflows/evals.yml` | Runs it on every pull request. |

Two levels, on purpose:

1. **Keyless** — `test_eval_registry_and_deterministic_engines`. Always runs. Proves
   the eval machinery is intact: every engine is registered, `evaluate()` scores a
   hand-built `EvalInput` correctly with deterministic engines (`contains`,
   `exact_match`), inapplicable engines return `None` instead of a phantom `0.0`, and
   `aggregate()` does the arithmetic the gate is built on. Zero model calls, zero cost,
   green on a fork with no secrets.
2. **The real gate** — needs an LLM key. Scores `baseline_system` and
   `candidate_system` on the same golden cases with the same metrics
   (`faithfulness`, `answer_relevancy`), then asserts:
   - `test_gate_measured_every_metric` — every guarded metric actually produced a
     number. An un-guarded metric is how a regression walks into production.
   - `test_no_metric_regresses` — nothing drops by more than `EPS`. The half people
     forget: it's easy to raise faithfulness by refusing everything; answer_relevancy
     catches that trade.
   - `test_headline_metric_improves` — `faithfulness` rises by more than `EPS`.
     "Nothing regressed" is not a reason to merge.

   The pair shipped here makes the course's first claim executable: **baseline** is
   the model answering alone (no retrieval, empty `contexts`), **candidate** is
   Lab 1's naive RAG at `k=4`. Ungrounded generation scores ~0 on faithfulness —
   not a trick, that's what ungrounded means — while staying perfectly fluent.

**With no key the gated tests skip, they do not fail.** A skip is honest ("we didn't
measure"); a red is a claim ("we measured, and it got worse"). Never conflate them.

## Run it locally

```bash
pytest tests/            # or: .venv/bin/python -m pytest tests/ -v
```

Your existing lab `.env` is picked up automatically — no extra setup. Cost with the
default settings: ~24 model calls (4 cases × 3 calls × 2 systems).

## Env vars

| Var | Default | What it does |
|---|---|---|
| `EVAL_GATE_CASES` | `4` | How many golden cases the gate scores. Keeps CI to a handful of calls. Raise it (10–20) for a result you'd bet a release on. |
| `OPENAI_API_KEY` | — | Your class token. Or `GROQ_API_KEY` / `AZURE_OPENAI_API_KEY` (+ `AZURE_OPENAI_ENDPOINT`) / `GEMINI_API_KEY` — whatever `mai_rag.llm` resolves. |
| `OPENAI_BASE_URL` | — | The class LLM proxy. Unset if you bring your own OpenAI key. |
| `MAI_NO_DOTENV` | unset | Ignore the local `.env`. Use it to prove the keyless path really is green: `MAI_NO_DOTENV=1 pytest tests/ -v -p no:deepeval`. (The `-p no:deepeval` matters only if you installed the `deepeval` extra — its pytest plugin loads `.env` behind our back. CI installs no such plugin.) |

## Adapt it to your own app

Copy `test_eval_gate.py` into your repo and change **two functions**:

```python
def baseline_system(store, question) -> dict:   # what's in production today
    ...
def candidate_system(store, question) -> dict:  # what this PR ships
    ...
```

Each returns `{"answer": str, "contexts": list[str]}` — the shape every evaluator
expects. Then point the `golden` fixture at your own golden set (the take-home in
[`BUILD_YOUR_CORPUS.md`](../BUILD_YOUR_CORPUS.md) builds one for your domain). The
gate doesn't care what you changed — only whether the golden set noticed.

Tune at the top of the file: `GATE_METRICS`, `HEADLINE`, `EPS`. `EPS` is the
judge-noise floor — a move smaller than that is not a result. Lab 5 uses `0.02` over
the full gradable golden set; the CI default is `0.05` because noise in a mean scales
with 1/√n and CI scores only 4 cases. Tighten it as you raise `EVAL_GATE_CASES`.

## When the gate goes red

Read the deltas the failure prints before you touch the assert. Three honest outcomes:

- the candidate genuinely isn't better → **fix the candidate, not the gate**;
- too few cases to resolve the difference → raise `EVAL_GATE_CASES`;
- the judge is uncalibrated → Lab 5 stage 5 (Cohen's κ, verbosity + position probes)
  is the fix. An uncalibrated judge is a dashboard, not a control.

Deleting the assert is never one of the outcomes.
