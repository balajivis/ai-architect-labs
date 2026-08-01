"""
mai_rag.evals.deepeval_backend — thin wrapper over the real DeepEval library.

The third implementation of the same four metrics. Same EvalInput → same Score shape as
`native` and `ragas_backend`, so nothing downstream cares which one ran — that is the
whole point: a metric you have never diffed against a second (and third) implementation
is a number you are trusting on faith.

Where the three differ is instructive, and it is the lesson of Pillar II:
  · native            — our from-scratch prompts (open the box: `mai_rag.evals.native??`)
  · ragas             — reference-light RAG metrics, its own prompt lineage
  · deepeval          — pytest-shaped assertions; metrics carry a `reason` string, and
                        `context_precision`/`recall` are RETRIEVAL metrics keyed off the
                        expected output rather than a judged relevance list

By default DeepEval calls OpenAI. We do NOT want a second key requirement in class, so we
route it through the kit's own chokepoint (`mai_rag.llm`) via a tiny DeepEvalBaseLLM
adapter — whatever provider the student already configured (class proxy / Groq / Azure)
evaluates the metrics. One key, three libraries.

Requires the `deepeval` extra:  pip install "mai_rag[deepeval]"
"""
from __future__ import annotations

from .base import EvalInput, Score, clamp01

# DeepEval's names for the four metrics we teach.
_METRICS = {"faithfulness", "answer_relevancy", "context_precision", "context_recall"}

_adapter = None          # cached DeepEvalBaseLLM wrapper around mai_rag.llm


def available() -> bool:
    try:
        import deepeval  # noqa: F401
        return True
    except Exception:
        return False


def _require():
    if not available():
        raise ImportError(
            'DeepEval not installed. Run:  pip install "mai_rag[deepeval]"  '
            '(or use backend="native").'
        )


def _model():
    """A DeepEvalBaseLLM that calls mai_rag.llm — so DeepEval needs no key of its own."""
    global _adapter
    if _adapter is not None:
        return _adapter
    from deepeval.models.base_model import DeepEvalBaseLLM
    from .. import llm as _llm

    class MaiRagLLM(DeepEvalBaseLLM):
        def load_model(self):
            return None

        def generate(self, prompt: str, *args, **kwargs) -> str:
            return _llm.complete(prompt, tier="small")

        async def a_generate(self, prompt: str, *args, **kwargs) -> str:
            return self.generate(prompt)

        def get_model_name(self) -> str:
            try:
                return f"mai_rag:{_llm.model_for('small')}"
            except Exception:
                return "mai_rag"

    _adapter = MaiRagLLM()
    return _adapter


def score(metric: str, e: EvalInput) -> Score | None:
    """Run a single DeepEval metric and normalize to a Score. Returns None when the
    metric needs a reference (expected output) the case does not carry."""
    _require()
    if metric not in _METRICS:
        return None
    if metric in ("context_recall", "context_precision") and not e.expected:
        return None                       # DeepEval keys both off expected_output

    from deepeval.test_case import LLMTestCase
    from deepeval.metrics import (
        FaithfulnessMetric,
        AnswerRelevancyMetric,
        ContextualPrecisionMetric,
        ContextualRecallMetric,
    )

    model = _model()
    metric_obj = {
        "faithfulness":      lambda: FaithfulnessMetric(model=model),
        "answer_relevancy":  lambda: AnswerRelevancyMetric(model=model),
        "context_precision": lambda: ContextualPrecisionMetric(model=model),
        "context_recall":    lambda: ContextualRecallMetric(model=model),
    }[metric]()

    tc = LLMTestCase(
        input=e.question,
        actual_output=e.answer,
        expected_output=e.expected or None,
        retrieval_context=list(e.contexts or []),
    )
    metric_obj.measure(tc)
    val = clamp01(metric_obj.score)
    reason = getattr(metric_obj, "reason", None) or "deepeval"
    return Score(metric, val, val >= 0.6, f"deepeval · {str(reason)[:160]}")
