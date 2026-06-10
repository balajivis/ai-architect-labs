"""
mai_rag.evals.ragas_backend — thin wrapper over the real RAGAS library.

This is the *facade* in action: same EvalInput → same Score shape as the native
engines, so `viz.compare()` and the golden set do not care which backend ran.
The wrapper exists so (a) you can diff your from-scratch `native` metric against
the popular library, and (b) when RAGAS ships a breaking release we pin/fix it
here once, not in five notebooks.

Requires the `evals` extra:  pip install "mai_rag[evals]"
"""
from __future__ import annotations

from .base import EvalInput, Score, clamp01

_RAGAS_METRICS = {"faithfulness", "answer_relevancy", "context_precision", "context_recall"}


def available() -> bool:
    try:
        import ragas  # noqa: F401
        return True
    except Exception:
        return False


def _require():
    if not available():
        raise ImportError(
            'RAGAS not installed. Run:  pip install "mai_rag[evals]"  '
            "(or use backend=\"native\")."
        )


def score(metric: str, e: EvalInput) -> Score | None:
    """Run a single RAGAS metric and normalize to a Score. Falls back to None
    when the metric needs a reference the case does not have."""
    _require()
    if metric in ("context_recall",) and not e.expected:
        return None

    from datasets import Dataset
    from ragas import evaluate
    from ragas import metrics as M

    metric_obj = {
        "faithfulness": M.faithfulness,
        "answer_relevancy": M.answer_relevancy,
        "context_precision": M.context_precision,
        "context_recall": M.context_recall,
    }[metric]

    ds = Dataset.from_dict({
        "question": [e.question],
        "answer": [e.answer],
        "contexts": [e.contexts],
        "ground_truth": [e.expected or ""],
    })
    result = evaluate(ds, metrics=[metric_obj])
    val = clamp01(list(result.scores[0].values())[0])
    return Score(metric, val, val >= 0.6, "ragas")
