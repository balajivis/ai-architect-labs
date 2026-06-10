# Pillar I · Advanced RAG

> **Layer:** Input · **Time:** ~4 hrs · **70% hands-on**
> **Lab kit:** the `mai_rag` package in this repo + the pre-seeded 131-doc enterprise-policy corpus.

## Thesis

You already call an API and run basic retrieval. This pillar is the jump from a demo to a deployment: **no single RAG paradigm wins across all query/corpus pairs** — so you measure first, then earn every upgrade. We teach **eval-first**: build the measuring instrument, baseline a naive RAG, then prove each technique's lift on the *same* golden set.

## The spine (every module)

**Concept → popular library → production reference → lab on the shared corpus.** The golden set + scorecard from Module 1 is the through-line; Modules 2–5 each re-run it and must move `viz.compare(baseline, candidate)`.

## Modules

| # | Module | What you build | Notebook |
|---|---|---|---|
| 1 | **Evaluation First** | golden cases + criteria → baseline naive RAG → scorecard | [`../../notebooks/01_evaluation_first.ipynb`](../../notebooks/01_evaluation_first.ipynb) ✅ |
| 2 | **Retrieval, Measured** | hybrid (dense+BM25) + RRF + cross-encoder rerank + **Contextual Retrieval** → re-score | `02_retrieval_measured.ipynb` *(planned)* |
| 3 | **Agentic RAG, Measured** | decompose · HyDE · sufficiency loop · CRAG · budget caps → re-score on multi-hop | `03_agentic_rag.ipynb` *(planned)* |
| 4 | **Adaptive Routing (+ GraphRAG)** | complexity router + cost/quality dashboard; graph as a *routed* strategy (LazyGraphRAG/KET-RAG) | `04_adaptive_routing.ipynb` *(planned)* |
| 5 | **Memory & Personalization** | working/short/long memory + user-scoped retrieval → multi-turn faithfulness | `05_memory.ipynb` *(planned)* |

## Key ideas

- **Contextual Retrieval** (prepend LLM-generated chunk context before embedding + BM25) — single highest-ROI upgrade (−67% retrieval failure with rerank).
- **GraphRAG is a niche tool, not a default** — lead with *when graph loses*; LazyGraphRAG is the cost-rational version. The real skill is defending a "no" with data.
- **Routing beats any fixed paradigm** on the efficiency frontier (~66% cost cut for ~3.6pt accuracy).

## Lab setup

```bash
pip install "git+https://github.com/balajivis/ai-architect-labs.git@v0.1.1"
# in a notebook:
from mai_rag import corpus, evals, viz, baseline, golden
```
Retrieval/embeddings run **keyless** (local MiniLM). Only generation + LLM-judge need one LLM key — see the repo [setup](../../README.md).
