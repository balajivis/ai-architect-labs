"""
mai_rag — Modern AI Pro · AI Architect course lab kit.

A glass-box facade over the RAG ecosystem with a ready-to-go SQL + vector data
layer. Import what you need:

    from mai_rag import corpus, evals, viz, golden
    from mai_rag.baseline import naive_rag

    store = corpus.load_policy_corpus()          # pre-seeded, keyless retrieval
    gs = golden.GoldenSet.from_seed(store)        # candidate golden cases
    run = evals.run_suite(store, gs, naive_rag, label="naive baseline")
    viz.scorecard(run["summary"])                 # the number to beat
"""
from __future__ import annotations

from . import corpus, evals, golden, llm, store, viz
from .baseline import naive_rag
from .store import Store

__all__ = ["corpus", "evals", "golden", "llm", "store", "viz", "naive_rag", "Store"]
__version__ = "0.1.5"
