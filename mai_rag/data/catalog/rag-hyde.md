---
title: HyDE (Hypothetical Document Embeddings)
doc_id: rag-hyde
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# HyDE (Hypothetical Document Embeddings)

HyDE improves retrieval by first asking the model to draft a hypothetical answer to the query, then embedding *that* draft to search with. The idea is that a fuller, answer-shaped text often matches relevant documents better than a short question.

## Key ideas
- Generate a hypothetical answer, then retrieve using its embedding.
- Helps when the raw query is short, vague, or vocabulary-mismatched.
- Bridges the gap between question phrasing and document phrasing.
- Adds a generation step, so it costs extra latency.
- One of several query-transformation techniques for better recall.

## At Modern AI Pro
MAI introduces HyDE among advanced query-transformation methods in the AI Architect track, at an overview level.
