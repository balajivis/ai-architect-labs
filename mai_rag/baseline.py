"""
mai_rag.baseline — the naive RAG every later module has to beat.

Single-shot: embed the query, vector-search top-k, stuff the chunks into one
prompt, answer. No hybrid search, no rerank, no agentic loop. This is the
baseline you measure in Module 1; its scorecard is the number to beat.
"""
from __future__ import annotations

from . import llm
from .store import Store

_PROMPT = """You are answering a question using only the provided context from \
the company knowledge base. If the context does not contain the answer, say you \
don't have enough information — do not invent facts.

Question: {q}

Context:
{ctx}

Answer:"""


def naive_rag(store: Store, query: str, k: int = 5, tier: str = "small") -> dict:
    """Return {answer, contexts, hits, query} — the shape every evaluator and
    the golden-set runner expect."""
    hits = store.search(query, k=k)
    ctx = "\n\n".join(f"[{i + 1}] ({h.title}) {h.content}" for i, h in enumerate(hits))
    answer = llm.complete(_PROMPT.format(q=query, ctx=ctx), tier=tier)
    return {
        "answer": answer,
        "contexts": [h.content for h in hits],
        "hits": hits,
        "query": query,
    }
