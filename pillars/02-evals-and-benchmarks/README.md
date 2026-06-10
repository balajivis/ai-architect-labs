# Pillar II · Evals & Benchmarks

> **Layer:** Quality · **Time:** ~4 hrs · **70% hands-on**
> **Lab kit:** `mai_rag.evals` (native engines + RAGAS backend + safety) on the shared golden set.

## Thesis

**You can't improve what you don't measure. Define "good" as code, baseline it, then prove every change lifts the same set.** This is eval-driven development — the pillar nobody builds. Pillar I gave you the eval primer; here you go deep on the craft.

## The spine (every module)

**Concept (you build it) → popular library (RAGAS/DeepEval) → production reference → lab.** RAGAS specifically is pluggable: run the transparent implementation you build, *or* the real `ragas` library — same output schema, so the golden set composes across both.

## Modules

| # | Module | What you build | Notebook |
|---|---|---|---|
| 1 | **LLM-as-Judge** | a rubric; pairwise + single-score judging; bias/position calibration | `06_llm_as_judge.ipynb` *(planned)* |
| 2 | **RAGAS, Measured** | faithfulness · answer-relevancy · context-precision/recall (claim-decomposition, deterministic) | `07_ragas.ipynb` *(planned)* |
| 3 | **Golden Sets + Safety/Compliance** | 3-tier golden hierarchy; safety & EU AI Act as *evals* — **LLM/ML-based, NO regex** | `08_golden_safety.ipynb` *(planned)* |
| 4 | **Eval-Driven Dev + Benchmarks** | CI gating · regression · HITL bridge · public benchmarks (MMLU, SWE-bench, GAIA…) | `09_eval_driven_dev.ipynb` *(planned)* |

## Key ideas

- **The 9-engine toolkit:** llm-judge, semantic-similarity, exact-match, contains, human-review + **RAGAS ×4**.
- **Safety is an eval, not a regex** — PII, jailbreak, toxicity, prompt-injection are all model-judged.
- **The 3-tier golden hierarchy:** base capability → blueprint-specific → production thumbs-downs promoted back into the set.
- **Eval-driven loop:** every technique is judged by whether it moves the scorecard — `viz.compare("baseline", candidate)`.

## Lab setup

```bash
pip install "mai_rag[evals] @ git+https://github.com/balajivis/ai-architect-labs.git@v0.1.1"
from mai_rag.evals import suite          # the 9 engines
from mai_rag.evals import ragas_backend  # native | ragas — same schema
```
The golden set you saved in Pillar I Module 1 is the fixture here. Safety/PII evals use Azure Content Safety or an LLM judge — never regex.
