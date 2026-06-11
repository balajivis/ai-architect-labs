# AI Architect — The Four Pillars

The Architect Programme covers the four production layers that separate a demo from a deployment. 16 hours, 70% hands-on labs, one capstone. Each folder below holds that pillar's spine; labs land in [`../notebooks/`](../notebooks/) (Python) or each pillar folder (Node, for MCP).

| # | Pillar | Layer | Folder |
|---|---|---|---|
| I | **Advanced RAG** | Input | [`01-advanced-rag/`](./01-advanced-rag/) |
| II | **Evals & Benchmarks** | Quality | [`02-evals-and-benchmarks/`](./02-evals-and-benchmarks/) |
| III | **MCP Engineering** | Integration | [`03-mcp-engineering/`](./03-mcp-engineering/) |
| IV | **Trust & Production** | Operations | [`04-trust-and-production/`](./04-trust-and-production/) |

**Capstone:** a trust-hardened multi-tenant app integrating all four pillars (defined in Pillar IV).

## The through-line

Every pillar runs on **one shared fixture** — the enterprise-policy corpus + the golden set you build in Pillar I, Module 1. Each later module re-runs that set and must *prove its lift*. The spine of every module: **concept → popular library → production reference → lab.**

## Setup

See the repo [README](../README.md) and the course setup instructions. TL;DR:
```bash
pip install "git+https://github.com/balajivis/ai-architect-labs.git"
```
Retrieval runs keyless (local MiniLM); only generation + LLM-judge need one LLM key.
