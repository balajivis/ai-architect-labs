# AI Architect — Labs (`mai_rag`)

Lab kit for Modern AI Pro's **AI Architect** course (Pillar I · Advanced RAG). A
**glass-box facade** over the RAG ecosystem with a **ready-to-go SQL + vector
data layer** — so notebooks stay thin and focused on the concept, not the
plumbing.

## Why it exists
Teaching notebooks fail two ways: drowning in boilerplate, or hiding everything
behind magic. `mai_rag` does neither. The concept a module teaches stays inline
and visible; corpus loading, the baseline RAG, the database, and **all
visualization** are one-liner imports you can still read (`mai_rag.evals.native`
is meant to be opened).

## The four pillars
The full Architect Programme is four production layers + a capstone. Each has a
spine you can read right after cloning — see [`pillars/`](./pillars/):

| # | Pillar | Layer |
|---|---|---|
| I | [Advanced RAG](./pillars/01-advanced-rag/) | Input |
| II | [Evals & Benchmarks](./pillars/02-evals-and-benchmarks/) | Quality |
| III | [MCP Engineering](./pillars/03-mcp-engineering/) | Integration |
| IV | [Trust & Production](./pillars/04-trust-and-production/) | Operations |

## Install (Colab)
```python
!pip install -q "mai_rag[evals] @ git+https://github.com/balajivis/ai-architect-labs.git"
```
Retrieval is **keyless** (embeddings run locally via MiniLM). Only generation and
the LLM-judge evaluators need a key — set one of `GROQ_API_KEY` /
`OPENAI_API_KEY` / `AZURE_OPENAI_API_KEY` / `GEMINI_API_KEY`.

## Run locally (recommended — clone + editable install)
The labs in [`labs/`](./labs/) are Python files you can run in VS Code (or plain
`python`). Clone the repo and install it **editable**, so a later `git pull`
updates **both** the labs and the `mai_rag` package at once:
```bash
git clone https://github.com/balajivis/ai-architect-labs.git
cd ai-architect-labs
python -m venv .venv && source .venv/bin/activate
pip install -e ".[evals,viz]"
cp .env.example .env        # then put your GROQ key in .env (Groq has a free tier)
python labs/lab_1.py        # or step through it in VS Code's interactive window
```

## Getting updates
We ship fixes and new labs over the course. To pull them:
```bash
git pull        # updates labs/ AND mai_rag (because you installed -e from the clone)
```
- Installed the **Colab git-URL** way instead of `-e`? `git pull` on a clone
  updates only the lab files — run `pip install -U "mai_rag[...] @ git+...` to move
  the package.
- **Before you edit a lab, copy it** — `cp labs/lab_2.py my_lab_2.py` (or work on a
  branch). Editing `labs/*.py` in place will cause a merge conflict on the next
  `git pull`. Your `.env` is safe — it's git-ignored, so pulls never touch your key.

## Quickstart — baseline a naive RAG (Module 1)
```python
from mai_rag import corpus, evals, viz, golden
from mai_rag.baseline import naive_rag

store = corpus.load_policy_corpus("policy.db")     # pre-seeded, ready to go
gs    = golden.GoldenSet.from_seed(store)          # candidate golden cases
run   = evals.run_suite(store, gs, naive_rag, label="naive baseline")
viz.scorecard(run["summary"])                      # the number every module must beat
```

## The data layer (`mai_rag.store`)
One SQLite file holds the whole RAG state — `documents`, `chunks`, a `vec0`
embedding table (via `sqlite-vec`), `golden_cases`, and every `eval_run` /
`eval_result`. It deliberately mirrors the **pgvector** mental model so concepts
port to production (real pgvector on Azure Postgres Flexible Server). Because
runs persist, Module 1's baseline lives in the DB and every later module just
**appends a run** — `viz.compare_runs(store, "naive baseline", "hybrid+rerank")`
is a query, not a re-run.

## What's inside
| Module | Role |
|---|---|
| `corpus` | load + chunk + embed the bundled enterprise-policy corpus |
| `store` | SQL + vector data layer (sqlite-vec; pgvector-shaped) |
| `baseline` | `naive_rag()` — the thing every module beats |
| `evals` | 9 evaluator engines (mirrors Kapi) + pluggable RAGAS backend |
| `golden` | `GoldenSet` — the through-line test fixture |
| `viz` | editorial-styled scorecard / compare / heatmap / UMAP |
| `llm` | one tiered LLM chokepoint (Groq/OpenAI/Azure/Gemini) |

## The corpus
A coherent fictional company ("Northwind Technologies") — 13 interlinked policy
docs (~12.5k words) engineered to exercise real RAG failure modes: multi-hop
facts, distractors, a deliberate **recency conflict** (superseded vs active IAM
policy), acronyms, and paraphrase. Ships with 10 candidate golden cases.

## Notebooks
- `notebooks/01_evaluation_first.ipynb` — build golden cases, open the box on
  faithfulness, baseline the naive RAG.

## Status
Pre-release (`v0.1.0`). Module 1 complete; Modules 2–5 (retrieval, agentic,
routing, memory) build on the same `store` + `golden` + `viz` spine.
