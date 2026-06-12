---
title: RAG Security
doc_id: rag-rag-security
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# RAG Security

RAG security covers the risks that arise when a model reads from external documents — including prompt injection hidden in content, leakage of sensitive data, and access-control gaps. Because RAG pulls in untrusted text, the retrieval layer itself becomes an attack surface.

## Key ideas
- Retrieved content can carry injected instructions that hijack the model.
- Access controls must follow the data, so users only see what they're allowed to.
- Sensitive information can leak through answers or citations if unguarded.
- Source trust and content sanitization matter before indexing.
- Security spans ingestion, retrieval, generation, and logging.

## At Modern AI Pro
MAI addresses RAG security risks and mitigations at an overview level in the AI Architect track, alongside guardrails and evaluation.
