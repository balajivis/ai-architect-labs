# AI Architect — Common Questions & Fixes

The `ask.py` TA does RAG over this file: it retrieves the entries most relevant to your
question and answers from them. Instructors: edit/extend this list — each `##` heading is
one retrievable article. Phrase headings the way a stuck student would (symptoms + keywords).

## AttributeError: module 'mai_rag' has no attribute '__version__' (or load_catalog_corpus, or a wrong-version error)
Your installed `mai_rag` package is stale — older than your lab file. Reinstall it from a fresh pull:
`git pull && pip uninstall -y mai_rag && pip install -e ".[evals,viz]"`, then re-run. In a notebook, restart the kernel afterward. If your venv isn't active, `source .venv/bin/activate` first.

## ModuleNotFoundError: No module named 'langchain_groq' (or rank_bm25, tavily, ragas)
A stale install missing deps. Reinstall the package (these are in its dependencies now): `pip install -e ".[evals,viz]"`. As a one-off you can also `pip install langchain-groq rank-bm25 tavily-python`.

## No LLM key found / how do I set an API key
Two options. (a) Groq free tier: put `GROQ_API_KEY=gsk_...` in your `.env`. (b) The class proxy (no key of your own): put `OPENAI_API_KEY=<class token>` and `OPENAI_BASE_URL=https://learn.modernaipro.com/api/llm/v1` in `.env`, and UNSET `GROQ_API_KEY` so `mai_rag` picks the OpenAI-compatible provider. Retrieval is keyless — only generation/judges need a key.

## 429 / rate limit — slow down
The shared class token hit its per-minute cap. Wait ~10–30 seconds and re-run the cell. `mai_rag.llm` already retries with backoff. If it keeps happening during a live burst, ask the instructor to raise the limit.

## How do I run a lab?
From the repo root, in your venv: `python labs/lab_1.py` (each move explains itself; Enter to run, s to skip, q to quit). If you're not set up yet: `python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[evals,viz]"`, add your key to `.env`, then run.

## How does Lab 1 work / what is it doing
Lab 1 is "Evaluation First." It loads the fictional Northwind policy corpus, builds a naive single-shot RAG (retrieve top-k → stuff context → answer), writes a golden test set, and scores the naive RAG on it. That baseline scorecard is the number every later lab (hybrid retrieval, reranking, agentic RAG…) has to beat. You define "good" before you tune anything.

## ValueError about shape 384 from embed
`embed` takes a LIST and returns an `(n, 384)` array. Wrap a single string: `embed([text])[0]`, not `embed(text)`.

## First run is slow / it's downloading something
On first use, retrieval downloads the local MiniLM embedding model (~90 MB) from Hugging Face. That's expected and one-time — retrieval stays keyless after that.

## pip and python disagree / it says not installed but I installed it
You installed into one environment and are running another. Activate the venv first (`source .venv/bin/activate`) and install there, then run labs with the SAME python: `.venv/bin/python labs/lab_1.py`. Check with `.venv/bin/python -c "import mai_rag; print(mai_rag.__version__)"`.

## RAGAS install is slow or conflicts
RAGAS is heavy. Use a clean venv, or just run the native eval backend (`backend="native"`), which needs no extra install and mirrors the same metrics.

## Which corpus is this / what is Northwind
A fictional company ("Northwind Technologies"): ~131 policy docs engineered to break naive RAG — recency conflicts (an active policy plus its superseded twin), multi-hop questions that span two docs, precise thresholds, and an unanswerable one the model must decline. It ships with candidate golden cases. Northwind is NOT real and did not build this course — the course and the mai_rag kit are built by Modern AI Pro (see "Who built this course").

## Who built this course / which company made this / who is the instructor
The course, labs, and mai_rag kit are built by Modern AI Pro (modernaipro.com), the AI education company — the class platform and proxy run at learn.modernaipro.com. Founder & lead instructor: Dr. Balaji Viswanathan (CEO & Lead Instructor; two decades in AI/robotics, former CEO of Mitra Robot, PhD in human-robot interaction, earlier at Microsoft and Black Duck/Synopsys). Modern AI Pro is the LEARN arm of a three-product family with Kapi (BUILD — enterprise AI agent platform, app.getkapi.com) and Brahmasumm (DEPLOY — air-gapped enterprise knowledge discovery). Not to be confused with Northwind Technologies, the fictional company in the lab corpus.

## How do I add my own golden test case
Append to the `golden` list in the lab (or the golden set), same dict shape: `{"q": ..., "expected": ..., "support": "<doc-id>", "tag": "blueprint"}`. Multi-hop support is two doc ids joined with " + ". Re-ground your `expected` in the real doc using the read_doc/search helpers.

## Groq vs the class proxy — which provider does it use
`mai_rag.llm` auto-detects: `GROQ_API_KEY` → Groq; else `OPENAI_API_KEY` (+ `OPENAI_BASE_URL`) → OpenAI/proxy; else Azure; else Gemini. To force the class proxy, set `OPENAI_API_KEY`+`OPENAI_BASE_URL` and unset `GROQ_API_KEY` (or set `MAI_LLM_PROVIDER=openai`).

## Colab or local — where should I run the labs
Both work. Local in VS Code with an editable install (`pip install -e`) is recommended: `git pull` then updates both the labs and the package at once, no disconnects, and state persists across labs. Colab is the fallback — the notebook is one `!pip install` + a secret.

## git pull says merge conflict on a lab file
You edited `labs/*.py` in place. Copy the lab before editing (`cp labs/lab_2.py my_lab_2.py`) or work on a branch. To recover: move your edits into a copy, then `git checkout -- labs/<file>` for just that file and pull again. Your `.env` is git-ignored, so pulls never touch your key.

## What are the four pillars of the course
I · Advanced RAG (retrieval that's measured, agentic RAG, memory) · II · Evals & Benchmarks (RAGAS, calibrated LLM-judge, the release gate) · III · MCP Engineering (build a server, OAuth, ship it) · IV · Trust & Production (guardrails, access control, HITL, compliance). Taught eval-first: Lab 1 is the instrument, the pillars are the deep dives.

## How do I know retrieval is actually working / recall
Score it, don't eyeball it — and you no longer have to hand-roll it. The suite ships three KEYLESS retrieval engines: `recall_at_k` (fraction of the needed docs retrieved — the floor), `mrr` (1/rank of the first supporting doc — rank-sensitive, so a reranker shows up) and `hit_at_1`. Build the input with `from mai_rag.evals.retrieval import from_golden` → `from_golden(q, answer, contexts, hits, case["support"])`, then `evals.evaluate(e, evaluators=["recall_at_k","mrr","hit_at_1"])`. Low recall means the right chunk never made it into the window — no prompt will save you; fix the retriever (that's Lab 2).

## How do I measure cost and latency / is my agent too expensive
They're eval dimensions like any other. `mai_rag.llm.METER` counts calls + tokens through the chokepoint (real provider usage when available): `llm.METER.reset()`, run your system, then `meta={"ms": elapsed_ms, **llm.METER.snapshot()}` on the `EvalInput`. The keyless `latency_budget` / `token_budget` / `call_budget` engines score it against a budget (1.0 inside, decaying to 0 at 2x). Without these, every technique looks free and the ladder always argues for more.

## RAGAS vs DeepEval vs native — which metric backend should I use
All three compute the same four RAG metrics and return the same `Score`, so nothing downstream changes: `evals.evaluate(e, evaluators=[...], backend="native"|"ragas"|"deepeval")`. Class default is `native` (no extra install). Install the others with `pip install -e ".[evals]"` (RAGAS) or `".[deepeval]"`. DeepEval is routed through `mai_rag.llm`, so it uses the key you already have instead of demanding an OpenAI one. Lab 5 runs all three side by side — the DISAGREEMENT is the point: a metric you've never diffed against a second implementation is faith, not data.

## How do I wire the eval gate into CI
Copy `tests/test_eval_gate.py` into your repo and change two functions — `baseline_system` and `candidate_system` — to point at your app. Run it with `pytest tests/`. It asserts the gate rule (headline metric rises beyond EPS, nothing regresses), skips cleanly when no LLM key is configured (so a fork with no secrets is green, not red), and caps cost via `EVAL_GATE_CASES` (default 4). `.github/workflows/evals.yml` is the matching GitHub Action. A red gate blocks the merge — that rule, not a dashboard, is eval-driven development.

## How do I evaluate the agent's PATH, not just its answer
That's Lab 3e (`python labs/lab_3e.py`). Two agents can return the same answer having taken 1 step or 9 — identical answer score, wildly different cost and reliability. It traces each run into a trajectory and scores it: deterministic counters (step_count, wall_ms, redundant_steps, tool_error_rate, loop_detected), tool-call accuracy (does the path SHAPE match what the query needs — direct for arithmetic, decompose for multi-hop, web for depth), routed vs always-agentic on score-per-step, and an LLM judge that reads the trajectory instead of the answer.

## Are all the packages installed / how do I check my environment
Your machine snapshot (attached to this question) already lists every lab package in your repo `.venv` with its version, and flags any that are MISSING. To check yourself: `.venv/bin/pip list` (or `pip list` with the venv active). If anything's missing or you're unsure, just reinstall the full set — it's idempotent: `pip install -e ".[evals,viz]"`. That installs core (mai_rag, openai, sentence-transformers, numpy, pandas, sqlite-vec) plus the eval (ragas, datasets) and viz (umap-learn, scikit-learn) extras.

## The lab asks for a key during retrieval — is that right
No. Retrieval is keyless (local MiniLM embeddings). If something asks for a key before generation, something's wrong — check you didn't accidentally route retrieval through an LLM.
