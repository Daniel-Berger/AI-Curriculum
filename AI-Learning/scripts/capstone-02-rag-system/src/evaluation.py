"""
RAGAS Evaluation Module
=======================

Evaluates RAG system quality using the RAGAS framework and custom metrics.
Measures both retrieval quality and generation quality.

Metrics:
- **Faithfulness**: Does the answer stick to the retrieved context?
- **Answer Relevancy**: Is the answer relevant to the question?
- **Context Precision**: Are the retrieved documents relevant?
- **Context Recall**: Are all necessary documents retrieved?
- **Answer Correctness**: Does the answer match the ground truth?

Also supports custom metrics for latency, cost, and retrieval depth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .retriever import RetrievalResult


@dataclass
class EvalSample:
    """A single evaluation sample.

    Attributes
    ----------
    question : str
        The input question.
    ground_truth : str
        The expected correct answer.
    retrieved_contexts : list of str
        The contexts that were retrieved by the system.
    generated_answer : str
        The answer produced by the RAG system.
    """

    question: str
    ground_truth: str
    retrieved_contexts: List[str] = field(default_factory=list)
    generated_answer: str = ""


@dataclass
class EvalResults:
    """Aggregated evaluation results.

    Attributes
    ----------
    metrics : dict
        Aggregate metric scores (mean across all samples).
    per_sample : list of dict
        Per-sample metric breakdowns.
    num_samples : int
        Total samples evaluated.
    """

    metrics: Dict[str, float] = field(default_factory=dict)
    per_sample: List[Dict[str, float]] = field(default_factory=list)
    num_samples: int = 0


class RAGEvaluator:
    """Evaluate RAG system quality using RAGAS and custom metrics.

    Parameters
    ----------
    metrics : list of str, optional
        Which metrics to compute. Defaults to all RAGAS metrics.
    llm_model : str
        LLM to use for metric computation (some RAGAS metrics require an LLM).

    Examples
    --------
    >>> evaluator = RAGEvaluator()
    >>> results = evaluator.evaluate(eval_dataset)
    >>> print(results.metrics)
    {'faithfulness': 0.85, 'answer_relevancy': 0.92, ...}
    """

    DEFAULT_METRICS = [
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "context_recall",
        "answer_correctness",
    ]

    def __init__(
        self,
        metrics: Optional[List[str]] = None,
        llm_model: str = "gpt-4o",
    ) -> None:
        self.metrics = metrics or self.DEFAULT_METRICS
        self.llm_model = llm_model

    def evaluate(self, dataset: List[EvalSample]) -> EvalResults:
        """Run RAGAS evaluation on a dataset.

        Parameters
        ----------
        dataset : list of EvalSample
            Evaluation samples with questions, ground truths, and system outputs.

        Returns
        -------
        EvalResults
            Aggregated and per-sample evaluation results.
        """
        raise NotImplementedError

    def compute_faithfulness(
        self, answer: str, contexts: List[str]
    ) -> float:
        """Compute the faithfulness score for a single sample.

        Measures whether claims in the answer are supported by the contexts.

        Parameters
        ----------
        answer : str
            Generated answer.
        contexts : list of str
            Retrieved contexts.

        Returns
        -------
        float
            Faithfulness score between 0.0 and 1.0.
        """
        raise NotImplementedError

    def compute_answer_relevancy(self, question: str, answer: str) -> float:
        """Compute answer relevancy for a single sample.

        Measures whether the answer addresses the question.

        Parameters
        ----------
        question : str
            Input question.
        answer : str
            Generated answer.

        Returns
        -------
        float
            Relevancy score between 0.0 and 1.0.
        """
        raise NotImplementedError

    def compute_context_precision(
        self, question: str, contexts: List[str], ground_truth: str
    ) -> float:
        """Compute context precision for a single sample.

        Measures the proportion of retrieved contexts that are relevant.

        Parameters
        ----------
        question : str
            Input question.
        contexts : list of str
            Retrieved contexts.
        ground_truth : str
            Expected answer.

        Returns
        -------
        float
            Precision score between 0.0 and 1.0.
        """
        raise NotImplementedError

    def load_dataset(self, path: str) -> List[EvalSample]:
        """Load an evaluation dataset from a JSON file.

        Parameters
        ----------
        path : str
            Path to the JSON evaluation dataset.

        Returns
        -------
        list of EvalSample
            Parsed evaluation samples.
        """
        raise NotImplementedError

    def save_results(self, results: EvalResults, path: str) -> None:
        """Save evaluation results to a JSON file.

        Parameters
        ----------
        results : EvalResults
            Evaluation results to save.
        path : str
            Output file path.
        """
        raise NotImplementedError
