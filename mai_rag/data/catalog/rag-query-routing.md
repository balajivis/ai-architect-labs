---
title: Query Routing
doc_id: rag-query-routing
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Query Routing

Query routing decides where a question should go — which index, data source, tool, or pipeline is best suited to answer it. In systems with many knowledge sources, routing keeps retrieval focused and efficient.

## Key ideas
- Directs each query to the most appropriate source or pipeline.
- Avoids searching everything when only one source is relevant.
- Can route by topic, data type, or required tool.
- Improves both accuracy and cost in multi-source systems.
- Often implemented with a classifier or an LLM-based decision step.

## At Modern AI Pro
MAI covers query routing as part of designing multi-source retrieval systems in the AI Architect track, at an overview level.
