"""
mai_rag.evals.native — transparent, from-scratch implementations of the core
evaluators. This is the "open the box" code: read it to see exactly what
faithfulness or context-precision *compute* before you trust the packaged
RAGAS version. Same Score shape as every other backend.

The LLM-graded engines use mai_rag.llm. Classification is always LLM-based —
never a regex floor (a phone-number pattern is not PII detection).
"""
from __future__ import annotations

import numpy as np

from ..llm import complete_json
from ..store import embed
from .base import EvalInput, Score, clamp01


def llm_judge(e: EvalInput, rubric: str = "overall correctness, grounding, and helpfulness") -> Score:
    r = complete_json(
        f"Grade the ANSWER to the QUESTION on a 0.0–1.0 scale for: {rubric}.\n"
        f"QUESTION: {e.question}\nANSWER: {e.answer}\n"
        f"Keys: score (0.0-1.0), reasoning (one sentence)."
    )
    s = clamp01(r.get("score"))
    return Score("llm_judge", s, s >= 0.6, str(r.get("reasoning", "")))


def faithfulness(e: EvalInput) -> Score:
    """Fraction of the answer's atomic claims that are supported by the context.
    The grounding metric — catches hallucination."""
    ctx = "\n\n".join(e.contexts) or "(no context)"
    r = complete_json(
        "Break the ANSWER into atomic factual claims. For each, decide if it is "
        "directly supported by the CONTEXT.\n"
        f"CONTEXT:\n{ctx}\n\nANSWER:\n{e.answer}\n\n"
        'Keys: claims (list of {claim, supported: true/false}), reasoning.'
    )
    claims = r.get("claims") or []
    if not claims:
        return Score("faithfulness", 1.0, True, "no factual claims to verify")
    supported = sum(1 for c in claims if c.get("supported"))
    s = supported / len(claims)
    return Score("faithfulness", s, s >= 0.8, f"{supported}/{len(claims)} claims grounded")


def answer_relevancy(e: EvalInput) -> Score:
    r = complete_json(
        "How directly and completely does the ANSWER address the QUESTION? "
        "Ignore whether it is factually correct — only relevance.\n"
        f"QUESTION: {e.question}\nANSWER: {e.answer}\n"
        "Keys: score (0.0-1.0), reasoning."
    )
    s = clamp01(r.get("score"))
    return Score("answer_relevancy", s, s >= 0.6, str(r.get("reasoning", "")))


def context_precision(e: EvalInput) -> Score | None:
    """Of the retrieved chunks, what fraction are actually relevant? Scores the
    retriever's signal-to-noise."""
    if not e.contexts:
        return None
    numbered = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(e.contexts))
    r = complete_json(
        "For each numbered CONTEXT chunk, decide if it is relevant to answering "
        "the QUESTION.\n"
        f"QUESTION: {e.question}\n\nCONTEXT:\n{numbered}\n\n"
        'Keys: verdicts (list of true/false, one per chunk in order), reasoning.'
    )
    verdicts = r.get("verdicts") or []
    if not verdicts:
        return Score("context_precision", 0.0, False, "no verdicts returned")
    rel = sum(1 for v in verdicts if v)
    s = rel / len(verdicts)
    return Score("context_precision", s, s >= 0.5, f"{rel}/{len(verdicts)} chunks relevant")


def context_recall(e: EvalInput) -> Score | None:
    """Of the facts in the reference answer, what fraction are present in the
    retrieved context? Requires a reference answer."""
    if not e.expected or not e.contexts:
        return None
    ctx = "\n\n".join(e.contexts)
    r = complete_json(
        "Break the REFERENCE answer into key facts. For each, decide whether it "
        "can be found in the CONTEXT.\n"
        f"REFERENCE:\n{e.expected}\n\nCONTEXT:\n{ctx}\n\n"
        'Keys: facts (list of {fact, present: true/false}), reasoning.'
    )
    facts = r.get("facts") or []
    if not facts:
        return Score("context_recall", 1.0, True, "no facts to cover")
    present = sum(1 for f in facts if f.get("present"))
    s = present / len(facts)
    return Score("context_recall", s, s >= 0.7, f"{present}/{len(facts)} facts covered")


def semantic_similarity(e: EvalInput) -> Score | None:
    """Cosine similarity between answer and reference — catches 'same meaning,
    different words'. No LLM, no judge bias."""
    if not e.expected:
        return None
    a, b = embed([e.answer, e.expected])
    cos = float(np.dot(a, b))  # vectors are L2-normalized
    s = clamp01((cos + 1) / 2)
    return Score("semantic_similarity", s, s >= 0.7, f"cosine={cos:.2f}")


def contains(e: EvalInput) -> Score | None:
    """Deterministic must-include check: fraction of required criteria phrases
    present in the answer. Cheapest engine — no model call."""
    if not e.criteria:
        return None
    low = e.answer.lower()
    hit = sum(1 for c in e.criteria if c.lower() in low)
    s = hit / len(e.criteria)
    return Score("contains", s, s == 1.0, f"{hit}/{len(e.criteria)} required phrases present")


def exact_match(e: EvalInput) -> Score | None:
    if not e.expected:
        return None
    s = 1.0 if e.answer.strip().lower() == e.expected.strip().lower() else 0.0
    return Score("exact_match", s, s == 1.0, "")
