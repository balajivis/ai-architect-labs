---
title: RAG (Retrieval-Augmented Generation)
doc_id: rag-retrieval-augmented-generation
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# RAG (Retrieval-Augmented Generation)

Retrieval-Augmented Generation pairs a language model with an external knowledge source so answers are grounded in your own documents rather than only the model's training data. At query time, relevant passages are fetched and handed to the model as context, which reduces hallucination and lets the system cite sources.

> Note: This doc merges the introductory "RAG" and "RAG Deep Dive" topics into a single overview entry. The deeper mechanics live in the dedicated MAI course, not in this catalog.

## Key ideas
- Two phases: an offline ingestion/indexing phase and an online retrieve-then-generate phase.
- Keeps answers current and verifiable without retraining the model.
- Works best when retrieval quality is high — garbage in, garbage out.
- Common building blocks: embeddings, a vector store, a retriever, and a prompt template.
- Trade-offs to manage: latency, cost, context-window limits, and freshness.

## At Modern AI Pro
MAI covers RAG end-to-end in the Practitioner and AI Architect tracks, starting from a plain-English overview and an interactive explainer, then building toward production patterns.
