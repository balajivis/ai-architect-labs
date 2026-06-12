---
title: Context Engineering
doc_id: rag-context-engineering
topic_area: RAG & Retrieval
source: synthetic
type: topic
---
# Context Engineering

Context engineering is the practice of deciding what information goes into a model's context window, in what order, and in what form, to get reliable answers. In RAG it governs how retrieved passages, instructions, and history are assembled into a prompt.

## Key ideas
- Curates and orders the content placed in the context window.
- Balances completeness against limited context space.
- Manages instructions, retrieved evidence, and conversation history together.
- Poor context assembly causes many "model" failures that aren't the model's fault.
- A discipline distinct from but adjacent to prompt engineering.

## At Modern AI Pro
MAI treats context engineering as a core skill in the Practitioner and AI Architect tracks, with overview material on how to assemble effective context.
