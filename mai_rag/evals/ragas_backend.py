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
        import ragas       # noqa: F401
        import datasets    # noqa: F401  — also in the [evals] extra, imported in score()
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

    # RAGAS prints a tqdm "Evaluating:" bar PER call — 12+ of them fight the tutor's spinner into a
    # scrolling waterfall. Silence tqdm + its logger + telemetry so the lab's own spinner reads clean.
    import os, logging
    os.environ.setdefault("TQDM_DISABLE", "1")
    os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")
    for _n in ("ragas", "datasets"):
        logging.getLogger(_n).setLevel(logging.ERROR)

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
    try:
        result = evaluate(ds, metrics=[metric_obj], show_progress=False)
    except TypeError:                                     # older/newer ragas without the kwarg
        result = evaluate(ds, metrics=[metric_obj])
    val = clamp01(list(result.scores[0].values())[0])
    return Score(metric, val, val >= 0.6, "ragas")
