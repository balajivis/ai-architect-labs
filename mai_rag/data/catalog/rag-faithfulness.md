---
title: Faithfulness
doc_id: rag-faithfulness
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Faithfulness

Faithfulness measures whether a generated answer actually reflects the retrieved sources, without adding unsupported claims. An answer can sound fluent and still be unfaithful if it drifts beyond the evidence.

## Key ideas
- Checks that every claim is supported by retrieved context.
- Distinct from relevance: an answer can be on-topic yet unfaithful.
- A key signal for detecting hallucination in RAG systems.
- Often assessed with LLM-as-judge or evaluation frameworks.
- Improving grounding and prompting tends to raise faithfulness.

## At Modern AI Pro
MAI covers faithfulness as a central RAG quality dimension in the AI Architect track, at an overview level tied to evaluation.
