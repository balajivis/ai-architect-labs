---
title: Chunking
doc_id: rag-chunking
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Chunking

Chunking is how you split long documents into smaller passages before indexing them for retrieval. Chunk size and boundaries strongly influence whether the right context can be found and whether it fits in the model's prompt.

## Key ideas
- Breaks documents into retrievable units sized for embedding and prompting.
- Too large dilutes relevance; too small loses context.
- Overlap between chunks helps preserve meaning across boundaries.
- Structure-aware splitting (headings, sentences) often beats naive splitting.
- Good chunking is one of the highest-leverage, lowest-glamour RAG decisions.

## At Modern AI Pro
MAI covers chunking strategy as a practical lever in the Practitioner and AI Architect tracks, at an overview level focused on the trade-offs.
