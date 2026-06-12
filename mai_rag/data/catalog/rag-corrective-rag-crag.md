---
title: Corrective RAG (CRAG)
doc_id: rag-corrective-rag-crag
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Corrective RAG (CRAG)

Corrective RAG adds a self-checking step: the system evaluates whether retrieved passages are actually relevant and, if they fall short, takes corrective action such as searching again or falling back to another source. It makes RAG more robust to weak first-pass retrieval.

## Key ideas
- Assesses retrieval quality before generating an answer.
- Triggers a fallback (e.g., broader or web search) when context is weak.
- Reduces confidently wrong answers from poor retrieval.
- A self-correcting loop, related to agentic patterns.
- Adds latency in exchange for reliability.

## At Modern AI Pro
MAI introduces Corrective RAG as a reliability pattern in the AI Architect track, at an overview level alongside agentic and self-checking approaches.
