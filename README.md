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

## The labs — index

Run in order; each builds on the prior scorecard. *(interactive = guided CLI tutor: Enter to run each stage, `s` skip, `q` quit)*

| Lab | Name | File | Needs a key? |
|---|---|---|---|
| 1 | **Evaluation First** — golden cases, hand-rolled judges, the baseline to beat | `labs/lab_1.py` | yes · interactive |
| 1b | **RAG Foundations: The Dials** — chunking, size, overlap, embedding model, top-k, threshold, phrasing; live leaderboard + workbench | `labs/lab_1b.py` | **no — 100% keyless** · interactive |
| 2 | **Retrieval, Measured** — hybrid+RRF, metadata (given & LLM-derived), cross-encoder rerank, contextual, UMAP, the answers finale | `labs/lab_2.py` | yes · interactive |
| 2c | **GraphRAG, Routed** — LLM triple extraction (168 shipped), build + traverse your own graph (class Cosmos service or local networkx, same API), chunks-vs-chunks+graph duel, and the case where graph LOSES — the routing verdict | `labs/lab_2c.py` | yes · interactive |
| 3 | **Agentic RAG: The Five Decisions** — router, HyDE/multi-query, decomposition, sufficiency + CRAG web fallback, budget caps | `labs/lab_3.py` | yes · interactive |
| 3b | **Route Smart, Not Slow: Adaptive RAG** — LLM complexity router (with its own eval), the direct/naive/agentic cost ladder, a live LLM-call meter, and the naive-vs-adaptive-vs-agentic showdown | `labs/lab_3b.py` | yes · interactive |
| 3c | **Agent Architectures: The Authoring Workbench** — the four shapes under every framework (ReAct, reflection, plan-execute, supervisor) each built as a ~30-line glass-box LangGraph graph, raced on the golden slice with the call meter, then a free-play workbench to compose your own (needs `pip install -e ".[agents]"`) | `labs/lab_3c.py` | yes · interactive |
| 3d | **The Enterprise Stack: Google ADK** — the same shapes as framework classes (tools=[...], SequentialAgent, LoopAgent with escalate-exit, sub_agents transfer), the event stream read live, sessions/state, the meter moved into `before_model_callback`, and the DUEL: ADK's supervisor vs your 3c LangGraph one, same judge, same slice (needs `pip install -e ".[adk]"`) | `labs/lab_3d.py` | yes · interactive |
| 4 | **Memory & Personalization** — rolling window, summarization, user profile, user-scoped retrieval, decay | `labs/lab_4.py` | yes |
| 4b | **The Memory Stack** — the four layers on disk (short-term · working.yaml · episodic .md · durable profile.yaml), recall/isolation evals, memory × RAG | `labs/lab_4b.py` | yes · interactive |
| 5 | **The Calibrated Judge & the Eval Gate** — RAGAS triad, judge vs human labels (Cohen's κ + bias probes), CI gate | `labs/lab_5.py` | yes |
| 6 | **Guardrails & Security** *(WIP)* — 4-gate gauntlet, tenant ACLs, EU AI Act mapping | `labs/lab_6.py` | yes |
| 7 | **Human-in-the-Loop** *(WIP)* — risk-tagged tools, pause/resume, the eval→HITL bridge | `labs/lab_7.py` | yes |
| 8 | **MCP: Build a Server, Then Harden It** *(WIP · TypeScript/Node 22+)* — build + consume (incl. third-party open & authed servers), OAuth/audience binding, tool-poisoning guard, resilience | `labs/mcp_server/` (`npm run lab`) | yes · interactive |

## Install (Colab)
```python
!pip install -q "mai_rag[evals] @ git+https://github.com/balajivis/ai-architect-labs.git"
```
Retrieval is **keyless** (embeddings run locally via MiniLM). Only generation and
the LLM-judge evaluators need a key. **In-class default: paste the CLASS TOKEN
into `OPENAI_API_KEY`** (`.env.example` presets `OPENAI_BASE_URL` to the class
proxy; leave `GROQ_API_KEY` unset — it takes precedence if set). Or bring your
own: one of `GROQ_API_KEY` / `OPENAI_API_KEY` / `AZURE_OPENAI_API_KEY` /
`GEMINI_API_KEY`.

## Run locally (recommended — clone + editable install)
The labs in [`labs/`](./labs/) are Python files you can run in VS Code (or plain
`python`). Clone the repo and install it **editable**, so a later `git pull`
updates **both** the labs and the `mai_rag` package at once:
```bash
git clone https://github.com/balajivis/ai-architect-labs.git
cd ai-architect-labs
python -m venv .venv && source .venv/bin/activate
pip install -e ".[evals,viz,agents]"
cp .env.example .env        # then paste your CLASS TOKEN into OPENAI_API_KEY (base URL is preset)
                            # — or bring your own key instead (e.g. GROQ_API_KEY; Groq has a free tier)
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
| `evals` | 17 evaluator engines — 8 native + 3 safety + 3 retrieval (recall@k/MRR/hit@1) + 3 perf (latency/token/call budgets); 9 are keyless. Pluggable `native` / `ragas` / `deepeval` backends |
| `golden` | `GoldenSet` — the through-line test fixture |
| `viz` | editorial-styled scorecard / compare / heatmap / UMAP |
| `llm` | one tiered LLM chokepoint (Groq/OpenAI/Azure/Gemini) |

## The corpus
A coherent fictional company ("Northwind Technologies") — 131 policy documents
engineered to exercise real RAG failure modes: multi-hop
facts, distractors, a deliberate **recency conflict** (superseded vs active IAM
policy), acronyms, and paraphrase. Ships with 72 candidate golden cases.

## Notebooks
- `notebooks/01_evaluation_first.ipynb` — build golden cases, open the box on
  faithfulness, baseline the naive RAG.

## Status
Pre-release. Labs 1–5 (plus 1b, 2c, 3b, 4b) are complete and share the same
`store` + `golden` + `viz` spine; Labs 6–8 are WIP — shipped move-by-move with
`WIP:` stubs filled in over the course via `git pull`.
