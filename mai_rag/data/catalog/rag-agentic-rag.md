---
title: Agentic RAG
doc_id: rag-agentic-rag
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Agentic RAG

Agentic RAG wraps retrieval inside an agent loop that can decide *whether* to retrieve, *what* to search for, and *when* it has enough evidence to answer. Instead of a single fixed retrieve-then-generate step, the system can plan, call tools, and iterate.

## Key ideas
- An agent decides retrieval actions dynamically rather than following one fixed path.
- Supports multi-step reasoning: search, read, refine the query, search again.
- Can route across multiple sources or tools depending on the question.
- More capable than basic RAG, but adds latency, cost, and orchestration complexity.
- Benefits from clear stopping criteria so loops don't run forever.

## At Modern AI Pro
MAI introduces Agentic RAG in the AI Architect course as a step up from basic pipelines, at an overview level that frames when the added complexity is worth it.
