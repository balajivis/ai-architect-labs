---
title: Multi-Query Expansion
doc_id: rag-multi-query-expansion
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Multi-Query Expansion

Multi-query expansion rewrites a single user question into several related queries, retrieves for each, and merges the results. It widens coverage so the system is less likely to miss relevant passages because of one narrow phrasing.

## Key ideas
- Generate multiple phrasings or sub-questions from one query.
- Retrieve for each, then combine and de-duplicate results.
- Improves recall on ambiguous or multi-part questions.
- Trades extra retrieval calls for broader coverage.
- Often paired with re-ranking to keep the merged set focused.

## At Modern AI Pro
MAI covers multi-query expansion as a recall-boosting technique in the AI Architect track, at an overview level.
