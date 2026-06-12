---
title: Re-Ranking
doc_id: rag-re-ranking
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Re-Ranking

Re-ranking takes an initial set of retrieved candidates and reorders them by relevance using a more precise (and more expensive) model. It improves the final context handed to the language model without scanning the whole corpus.

## Key ideas
- A second pass that sharpens the order of an initial candidate set.
- Trades a little extra latency/cost for noticeably better relevance.
- Often uses a cross-encoder style scorer that reads query and passage together.
- Lets you retrieve broadly first, then keep only the best few.
- A common, high-impact upgrade to a basic retrieval pipeline.

## At Modern AI Pro
MAI presents re-ranking as a practical retrieval-quality boost in the AI Architect track, at an overview level.
