# Pillar IV · Trust & Production

> **Layer:** Operations · **Time:** ~4 hrs · **70% hands-on** · feeds the **Capstone**.
> **Lab kit:** extends the Pillar-I `mai_rag.store` (it already anticipates `tenant_id` + a `feedback` table) + Langfuse + Azure Content Safety.

## Thesis

**Trust is enforced in the layers every wrapper skips: a response only ships if it passed the guardrail, respected the user's ACL, cleared the HITL bar, and left a trace.** Production = those four are non-optional and observable.

## The spine (every module)

**A "good enough" system (app-level filters, no real isolation) → the SOTA control → a production reference that enforces it → lab.** Module 2 makes this concrete: an app-level `company_id` filter (the gap) becomes an *enforced* row-level `tenant_id` filter.

## Modules

| # | Module | What you build | Lab |
|---|---|---|---|
| 1 | **Guardrails & Output Safety** | a 4-gate pipeline: PII scrub → jailbreak detect → policy match → output classify (**LLM/ML, NO regex**) | run a jailbreak + PII payload through it |
| 2 | **ACLs & Multi-Tenancy** | row-level security; document-level ACLs; retrieval-time vs prompt-time enforcement | add enforced `tenant_id` RLS to the store |
| 3 | **HITL** | autonomy spectrum (Sheridan); approval gates; confidence/eval triggers; eval→HITL bridge | wire a trigger → queue → approve/reject |
| 4 | **Observability & Compliance** | tracing, cost/latency budgets, audit logs; EU AI Act (Art 13/14/50), GDPR/RTBF | trace a turn in Langfuse; fill the governance canvas |

## Key ideas

- **Guardrails are model-based, never regex** — Azure Content Safety / Prompt Shield + LLM judges.
- **ACLs must be *enforced*, not advisory** — the data layer rejects a query with no tenant scope; isolation can't be a prompt instruction.
- **HITL is a spectrum, not a switch** — autonomy shifts by confidence and stakes; failed evals route to a human queue.
- **Observability is always-on** — every turn is traced (cost, latency, scores); audit logs are the compliance backbone.

## Capstone

A **trust-hardened multi-tenant app** integrating all four pillars: Adaptive RAG (I) + CI eval gates (II) + an OAuth-2.1 MCP server (III) + RLS ACLs · HITL queue · injection defense · Langfuse · EU AI Act checklist (IV). Deployed as a Docker container on your own Azure (Container Apps / B1S VM) + Azure Postgres pgvector + Content Safety. This pillar's lab *is* the start of the capstone — don't duplicate the work.

## Lab setup

```bash
docker compose up            # local stack: app + pgvector + Langfuse
pip install "mai_rag[evals]"  # safety evals reuse the Pillar-II engines
```
