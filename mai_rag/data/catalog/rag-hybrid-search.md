---
title: Hybrid Search
doc_id: rag-hybrid-search
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Hybrid Search

Hybrid search blends semantic (vector) search with traditional keyword search so you capture both meaning and exact-term matches. It is a common way to fix cases where pure semantic search misses names, codes, or rare terms.

## Key ideas
- Combines vector similarity with keyword/lexical matching.
- Catches exact terms (IDs, names, acronyms) that semantics can miss.
- Results from both methods are merged into one ranked list.
- Especially helpful for technical, legal, or product catalogs.
- Often paired with re-ranking for a final relevance pass.

## At Modern AI Pro
MAI covers hybrid search as a robustness technique in the AI Architect track, framing when to reach for it over pure semantic search.
