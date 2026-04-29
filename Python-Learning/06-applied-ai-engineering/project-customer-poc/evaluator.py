"""Evaluation harness for scoring LLM outputs.

Defines an EvalCase model, provides multiple scoring functions (exact match,
fuzzy match, mock semantic similarity), an eval runner that processes test
suites, and summary-statistics helpers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class EvalCase:
    """A single evaluation test case."""

    name: str
    input_text: str
    expected: str
    actual: str = ""
    score: float = 0.0
    scoring_method: str = ""
    passed: bool = False


@dataclass
class EvalSummary:
    """Aggregate statistics for a completed evaluation run."""

    total_cases: int
    passed: int
    failed: int
    pass_rate: float
    mean_score: float
    min_score: float
    max_score: float
    scores_by_method: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def exact_match(expected: str, actual: str) -> float:
    """Return 1.0 if expected and actual are identical (case-insensitive), else 0.0."""
    return 1.0 if expected.strip().lower() == actual.strip().lower() else 0.0


def fuzzy_match(expected: str, actual: str) -> float:
    """Score based on word overlap (Jaccard similarity).

    Returns a float between 0.0 and 1.0.
    """
    expected_words = set(expected.strip().lower().split())
    actual_words = set(actual.strip().lower().split())
    if not expected_words and not actual_words:
        return 1.0
    if not expected_words or not actual_words:
        return 0.0
    intersection = expected_words & actual_words
    union = expected_words | actual_words
    return len(intersection) / len(union)


def semantic_similarity_mock(expected: str, actual: str) -> float:
    """Mock semantic similarity that uses character-level n-gram overlap.

    In production this would call an embedding model; here we approximate
    with bigram overlap to demonstrate the interface.
    """
    def bigrams(text: str) -> set:
        t = text.strip().lower()
        return {t[i : i + 2] for i in range(len(t) - 1)} if len(t) >= 2 else {t}

    bg_expected = bigrams(expected)
    bg_actual = bigrams(actual)
    if not bg_expected or not bg_actual:
        return 0.0
    intersection = bg_expected & bg_actual
    union = bg_expected | bg_actual
    return len(intersection) / len(union)


# Registry of available scoring methods.
SCORING_METHODS: Dict[str, Callable[[str, str], float]] = {
    "exact_match": exact_match,
    "fuzzy_match": fuzzy_match,
    "semantic_similarity": semantic_similarity_mock,
}


# ---------------------------------------------------------------------------
# Eval runner
# ---------------------------------------------------------------------------

class EvalRunner:
    """Runs evaluation cases against a scoring function and collects results."""

    def __init__(self, scoring_method: str = "fuzzy_match", pass_threshold: float = 0.5) -> None:
        if scoring_method not in SCORING_METHODS:
            raise ValueError(f"Unknown scoring method: {scoring_method}. Choose from {list(SCORING_METHODS.keys())}")
        self.scoring_method = scoring_method
        self.pass_threshold = pass_threshold
        self._scorer = SCORING_METHODS[scoring_method]

    def evaluate_case(self, case: EvalCase) -> EvalCase:
        """Score a single eval case in place and return it."""
        case.score = round(self._scorer(case.expected, case.actual), 4)
        case.scoring_method = self.scoring_method
        case.passed = case.score >= self.pass_threshold
        return case

    def run(self, cases: List[EvalCase]) -> List[EvalCase]:
        """Score all cases and return the list."""
        for case in cases:
            self.evaluate_case(case)
        return cases

    @staticmethod
    def summarize(cases: List[EvalCase]) -> EvalSummary:
        """Compute summary statistics from scored eval cases."""
        if not cases:
            return EvalSummary(
                total_cases=0, passed=0, failed=0,
                pass_rate=0.0, mean_score=0.0,
                min_score=0.0, max_score=0.0,
            )

        scores = [c.score for c in cases]
        passed = sum(1 for c in cases if c.passed)
        failed = len(cases) - passed

        # Group scores by method.
        method_scores: Dict[str, List[float]] = {}
        for c in cases:
            method_scores.setdefault(c.scoring_method, []).append(c.score)
        avg_by_method = {m: round(sum(s) / len(s), 4) for m, s in method_scores.items()}

        return EvalSummary(
            total_cases=len(cases),
            passed=passed,
            failed=failed,
            pass_rate=round(passed / len(cases), 4),
            mean_score=round(sum(scores) / len(scores), 4),
            min_score=round(min(scores), 4),
            max_score=round(max(scores), 4),
            scores_by_method=avg_by_method,
        )
