"""
Module 03: Evaluation & Quality Assurance -- Exercises
========================================================

15 exercises on building eval frameworks, LLM-as-judge patterns,
regression testing, hallucination detection, and CI/CD integration
for AI applications.

These skills are essential for solutions engineers and applied AI
engineers who must demonstrate that LLM-powered systems meet
quality bars before shipping to customers.

Run this file directly to check your solutions:
    python exercises.py
"""

import json
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# Exercise 1: Build an Eval Test Case Data Structure
# ---------------------------------------------------------------------------
def create_eval_test_case(
    test_id: str,
    input_prompt: str,
    expected_output: str,
    metadata: Optional[dict] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """
    Build a structured eval test case that can be serialized and stored.

    A test case is the atomic unit of any eval suite. It pairs an input
    prompt with one or more expected outputs and carries metadata for
    filtering and analysis (e.g., difficulty, category, customer).

    Scenario: You are building an eval suite for a customer's RAG chatbot.
    Each test case captures a user question, the ideal answer, and tags
    that let you slice results by topic or difficulty.

    Args:
        test_id: Unique identifier for the test case (e.g., "tc-001").
        input_prompt: The prompt that will be sent to the model.
        expected_output: The reference/golden answer.
        metadata: Optional dict of arbitrary metadata (difficulty, source, etc.).
        tags: Optional list of string tags for filtering (e.g., ["finance", "hard"]).

    Returns:
        A dict with keys: 'test_id', 'input_prompt', 'expected_output',
        'metadata', 'tags', 'created_at' (ISO 8601 timestamp string).
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Build a Scoring Function (Exact, Fuzzy, Semantic)
# ---------------------------------------------------------------------------
def score_response(
    predicted: str,
    expected: str,
    method: str = "exact",
) -> dict:
    """
    Score a model response against an expected answer using different methods.

    Scoring is the heart of any eval. Different tasks need different metrics:
    - "exact": binary 1.0 or 0.0, case-insensitive stripped match
    - "fuzzy": word-overlap F1 score (precision & recall on word sets)
    - "contains": 1.0 if expected is a substring of predicted (case-insensitive),
      else 0.0

    Scenario: A customer asks "Does your system support exact matching AND
    fuzzy matching?" You need to prove the eval framework handles both.

    Args:
        predicted: The model's actual output.
        expected: The golden/reference answer.
        method: One of "exact", "fuzzy", "contains".

    Returns:
        Dict with 'score' (float 0.0-1.0), 'method' (str), 'details' (dict).
        For "fuzzy", details should include 'precision', 'recall', 'f1'.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Implement an Eval Harness Runner
# ---------------------------------------------------------------------------
def run_eval_harness(
    test_cases: list[dict],
    model_fn: Callable[[str], str],
    scoring_fn: Callable[[str, str], dict],
) -> dict:
    """
    Execute a batch of eval test cases through a model and score results.

    The harness is the orchestrator: for each test case it calls the model,
    scores the output, records latency, and aggregates results.

    Scenario: Before a customer demo, you need to run 50 test cases against
    a fine-tuned model and produce a summary report in under a minute.

    Args:
        test_cases: List of test case dicts (from Exercise 1 format).
        model_fn: Callable that takes an input_prompt string and returns
                  the model's response string.
        scoring_fn: Callable that takes (predicted, expected) and returns
                    a score dict (from Exercise 2 format).

    Returns:
        Dict with:
        - 'total': int count of test cases
        - 'passed': int count where score >= 0.5
        - 'failed': int count where score < 0.5
        - 'avg_score': float average score across all cases
        - 'results': list of dicts, each with 'test_id', 'predicted',
           'expected', 'score', 'elapsed_ms' (float)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Build an LLM-as-Judge Prompt Template
# ---------------------------------------------------------------------------
def build_judge_prompt(
    question: str,
    model_answer: str,
    reference_answer: str,
    criteria: list[str],
) -> str:
    """
    Construct a structured prompt for an LLM judge to evaluate quality.

    LLM-as-judge is the industry pattern for evaluating open-ended responses
    where exact-match scoring fails. The prompt must force structured output
    so results can be parsed programmatically.

    Scenario: A customer's chatbot gives long-form answers about insurance
    policies. Human eval is too slow, so you build an automated judge.

    Args:
        question: The original user question.
        model_answer: The answer produced by the model under evaluation.
        reference_answer: The golden reference answer.
        criteria: List of evaluation criteria strings
                  (e.g., ["accuracy", "completeness", "conciseness"]).

    Returns:
        A prompt string that:
        - Presents the question, model answer, and reference answer in
          clearly labeled XML-style sections
        - Lists each criterion with instructions to score 1-5
        - Requests output as valid JSON with keys 'scores' (dict of
          criterion->int) and 'reasoning' (str)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Implement Judge Response Parser (Structured Output)
# ---------------------------------------------------------------------------
def parse_judge_response(
    raw_response: str,
    expected_criteria: list[str],
) -> dict:
    """
    Parse an LLM judge's response into structured scores.

    Judge responses are notoriously messy: they may include preamble text,
    markdown code fences, or slightly different key names. A robust parser
    must handle these variations.

    Scenario: Your automated eval pipeline calls the judge model 500 times.
    Even a 1% parse failure rate means 5 manual reviews. Build it robust.

    Args:
        raw_response: The raw text output from the judge LLM. May contain
                      JSON embedded in markdown fences or plain text.
        expected_criteria: The criteria names you expect scores for.

    Returns:
        Dict with:
        - 'scores': dict mapping each criterion to its int score (1-5)
        - 'reasoning': str explanation from the judge
        - 'parse_success': bool whether parsing succeeded cleanly
        - 'missing_criteria': list of criteria names not found in response

    If JSON parsing fails entirely, return scores as empty dict,
    reasoning as the raw response, parse_success as False, and
    missing_criteria as the full expected_criteria list.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Build a Golden Dataset Manager
# ---------------------------------------------------------------------------
def manage_golden_dataset(
    dataset: list[dict],
    operation: str,
    payload: Optional[dict] = None,
    filter_tags: Optional[list[str]] = None,
) -> dict:
    """
    Manage a golden evaluation dataset with CRUD + filter operations.

    Golden datasets are curated sets of (input, expected_output) pairs
    that serve as the ground truth for evals. They need versioning,
    filtering, and statistics.

    Scenario: Your customer has 200 eval cases across 5 product categories.
    They want to run evals on just "billing" cases, add new ones weekly,
    and track dataset growth.

    Args:
        dataset: Current list of test case dicts.
        operation: One of "add", "remove", "filter", "stats".
        payload: For "add", a test case dict to append.
                 For "remove", a dict with 'test_id' to remove.
                 For "filter" and "stats", ignored.
        filter_tags: For "filter", return only cases matching ALL these tags.
                     Ignored for other operations.

    Returns:
        Dict with:
        - 'dataset': the resulting dataset (list of test case dicts)
        - 'count': int number of items in result
        - 'operation': the operation performed
        For "stats", also include:
        - 'tag_distribution': dict mapping each tag to its count
        - 'oldest' and 'newest': ISO timestamp strings (or None if empty)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Implement Regression Test Comparison
# ---------------------------------------------------------------------------
def compare_eval_runs(
    baseline_results: list[dict],
    candidate_results: list[dict],
    regression_threshold: float = 0.05,
) -> dict:
    """
    Compare two eval runs to detect regressions and improvements.

    When you update a prompt, swap models, or change retrieval logic,
    you must ensure quality does not regress. This function compares
    score-by-score and flags significant changes.

    Scenario: A customer upgraded from GPT-4 to GPT-4o. Run the same
    eval suite on both and show the PM a clear regression report.

    Args:
        baseline_results: Results from the baseline run. Each dict has
                          'test_id' and 'score' (float).
        candidate_results: Results from the candidate run. Same format.
        regression_threshold: A score drop larger than this is a regression.

    Returns:
        Dict with:
        - 'regressions': list of dicts with 'test_id', 'baseline_score',
          'candidate_score', 'delta'
        - 'improvements': same format, for score increases > threshold
        - 'unchanged': list of test_id strings within threshold
        - 'baseline_avg': float
        - 'candidate_avg': float
        - 'regression_count': int
        - 'improvement_count': int
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Build an A/B Test Statistical Comparator
# ---------------------------------------------------------------------------
def ab_test_compare(
    scores_a: list[float],
    scores_b: list[float],
    confidence_level: float = 0.95,
) -> dict:
    """
    Perform a statistical comparison of two sets of eval scores.

    Real A/B testing for AI requires more than "which average is higher."
    You need effect size and confidence intervals to make go/no-go decisions.

    Scenario: A customer tested two prompt variants on 100 queries each.
    They ask: "Is variant B actually better, or is it just noise?"

    Implement WITHOUT scipy -- use manual z-test approximation:
    - z = (mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b)
    - For 95% confidence, |z| > 1.96 means statistically significant
    - For 99% confidence, |z| > 2.576

    Args:
        scores_a: Scores from variant A.
        scores_b: Scores from variant B.
        confidence_level: 0.95 or 0.99.

    Returns:
        Dict with:
        - 'mean_a', 'mean_b': float means
        - 'std_a', 'std_b': float standard deviations
        - 'z_score': float computed z statistic
        - 'is_significant': bool
        - 'winner': "A", "B", or "no_significant_difference"
        - 'effect_size': float (Cohen's d = (mean_a - mean_b) / pooled_std)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Implement Hallucination Detection (Fact Checking)
# ---------------------------------------------------------------------------
def detect_hallucinations(
    response: str,
    source_documents: list[str],
    claim_extractor: Optional[Callable[[str], list[str]]] = None,
) -> dict:
    """
    Check a model response for claims not supported by source documents.

    Hallucination is the top concern for enterprise AI. This function
    extracts factual claims from the response and checks each against
    the source material using word overlap as a proxy for support.

    Scenario: A legal-tech customer needs to verify that the AI's contract
    summaries don't fabricate clauses. Every unsupported claim is flagged.

    If no claim_extractor is provided, split the response into sentences
    (split on '. ') as a simple claim extraction heuristic.

    A claim is "supported" if at least 50% of its non-stopword tokens
    appear in any single source document. Use this stopword list:
    {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
     "to", "for", "of", "and", "or", "but", "it", "this", "that", "with"}

    Args:
        response: The model's generated text.
        source_documents: List of source text strings to check against.
        claim_extractor: Optional callable that takes text and returns
                         a list of claim strings.

    Returns:
        Dict with:
        - 'claims': list of extracted claim strings
        - 'supported': list of claims found in sources
        - 'unsupported': list of claims NOT found in sources
        - 'hallucination_rate': float (unsupported / total, or 0.0 if no claims)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Build a Citation Verifier
# ---------------------------------------------------------------------------
def verify_citations(
    response: str,
    cited_sources: list[dict],
) -> dict:
    """
    Verify that citations in a response actually match their sources.

    RAG systems often include citations like [1], [2]. This function
    checks that each citation references real content from the source.

    Scenario: A customer's research assistant cites papers by number.
    Verify that the text around each citation actually comes from that source.

    Citation format in response: [N] where N is a 1-based index into
    cited_sources. Each cited_source dict has 'id' (int), 'title' (str),
    and 'content' (str).

    For each citation found, extract the sentence containing it and check
    if at least 3 non-trivial words (length > 3) from that sentence appear
    in the cited source's content (case-insensitive).

    Args:
        response: The model response containing [N] citations.
        cited_sources: List of source dicts with 'id', 'title', 'content'.

    Returns:
        Dict with:
        - 'total_citations': int count of citations found
        - 'verified': list of dicts with 'citation_id', 'sentence', 'status'
          where status is "valid" or "invalid" or "source_not_found"
        - 'verification_rate': float (valid / total, or 1.0 if no citations)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Implement a Custom Domain-Specific Metric
# ---------------------------------------------------------------------------
def create_domain_metric(
    metric_name: str,
    scoring_rules: list[dict],
    aggregation: str = "mean",
) -> Callable[[str, str], dict]:
    """
    Create a reusable domain-specific scoring function from rules.

    Different industries need different metrics: legal cares about citation
    accuracy, healthcare about safety disclaimers, finance about numerical
    precision. This factory builds custom scorers.

    Scenario: A healthcare customer needs a metric that checks if the
    response includes a disclaimer, avoids banned terms, and mentions
    the drug name from the question.

    Each scoring_rule dict has:
    - 'name': str rule name
    - 'type': one of "contains", "not_contains", "regex"
    - 'pattern': str to check (plain text or regex pattern)
    - 'weight': float weight for this rule (weights are normalized)
    - 'source': "predicted" or "expected" -- which text to check the
      pattern against

    aggregation: "mean" (weighted average) or "min" (lowest rule score)

    Args:
        metric_name: Name for this custom metric.
        scoring_rules: List of rule dicts as described above.
        aggregation: "mean" or "min".

    Returns:
        A callable(predicted: str, expected: str) -> dict with:
        - 'metric_name': str
        - 'score': float 0.0-1.0
        - 'rule_results': list of dicts with 'rule_name', 'passed' (bool),
          'weight'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Build an Eval Result Aggregator with Statistics
# ---------------------------------------------------------------------------
def aggregate_eval_results(
    results: list[dict],
    group_by: Optional[str] = None,
) -> dict:
    """
    Aggregate evaluation results with descriptive statistics.

    After running hundreds of evals, stakeholders need summary stats:
    overall pass rate, score distribution, and breakdowns by category.

    Scenario: After running 500 evals, the VP of Engineering asks:
    "What's our overall quality? How does it break down by topic?"

    Each result dict has: 'test_id', 'score' (float), 'tags' (list[str]),
    'elapsed_ms' (float).

    Args:
        results: List of eval result dicts.
        group_by: Optional tag name to group results by. If provided,
                  compute stats per group using the first matching tag value.

    Returns:
        Dict with:
        - 'total': int
        - 'mean_score': float
        - 'median_score': float
        - 'std_score': float (0.0 if fewer than 2 results)
        - 'min_score': float
        - 'max_score': float
        - 'pass_rate': float (fraction with score >= 0.5)
        - 'p95_latency_ms': float (95th percentile of elapsed_ms)
        - 'groups': dict mapping group name to the same stats structure
          (without nested 'groups'), or empty dict if group_by is None
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 13: Implement Eval Result Storage and Retrieval
# ---------------------------------------------------------------------------
def eval_result_store(
    store: dict,
    action: str,
    run_id: Optional[str] = None,
    run_data: Optional[dict] = None,
    query: Optional[dict] = None,
) -> dict:
    """
    Store and retrieve eval run results with querying support.

    Eval results must be persisted so you can compare across time, models,
    and prompt versions. This simulates a simple in-memory store.

    Scenario: Over 3 months, you ran 50 eval sweeps. Now the customer
    asks "Show me all runs from last month where pass_rate > 0.8."

    The store is a dict with key 'runs' mapping to a list of run dicts.

    Actions:
    - "save": Add run_data (must include 'run_id', 'timestamp', 'model',
      'results') to the store. Return the updated store.
    - "get": Retrieve a specific run by run_id.
    - "query": Filter runs. query dict may have:
      - 'model': str to match
      - 'min_pass_rate': float minimum
      - 'after': ISO timestamp string -- only runs after this date
    - "list": Return all run_ids with their timestamps.

    Args:
        store: The current store dict.
        action: One of "save", "get", "query", "list".
        run_id: For "get", the run to retrieve.
        run_data: For "save", the run data dict.
        query: For "query", the filter criteria dict.

    Returns:
        Dict with 'success' (bool) and action-specific data:
        - "save": 'store' (updated store)
        - "get": 'run' (the run dict, or None)
        - "query": 'runs' (list of matching run dicts)
        - "list": 'runs' (list of dicts with 'run_id' and 'timestamp')
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: Build a Quality Trend Analyzer
# ---------------------------------------------------------------------------
def analyze_quality_trends(
    runs: list[dict],
    window_size: int = 3,
) -> dict:
    """
    Analyze quality trends across multiple eval runs over time.

    Trending helps answer: "Are we getting better or worse?" Compute
    moving averages and detect inflection points.

    Scenario: A customer runs weekly evals. After 12 weeks they want
    to see if their prompt engineering efforts are paying off.

    Each run dict has: 'run_id' (str), 'timestamp' (ISO string),
    'avg_score' (float), 'pass_rate' (float).

    Runs should be sorted by timestamp before analysis.

    A moving average is computed over window_size consecutive runs.
    A trend is "improving" if the last moving avg > first moving avg,
    "declining" if last < first, "stable" otherwise.

    An alert is generated when any run's avg_score drops more than
    0.1 below the previous run.

    Args:
        runs: List of run summary dicts.
        window_size: Number of runs for moving average.

    Returns:
        Dict with:
        - 'sorted_run_ids': list of run_id strings in chronological order
        - 'moving_averages': list of floats (one per valid window position,
          length = len(runs) - window_size + 1)
        - 'trend': "improving", "declining", or "stable"
        - 'alerts': list of dicts with 'run_id', 'score_drop' (positive float),
          'message'
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: Implement an Eval CI/CD Integration Config Generator
# ---------------------------------------------------------------------------
def generate_eval_ci_config(
    project_name: str,
    eval_suite_path: str,
    models: list[str],
    thresholds: dict,
    schedule: str = "on_pr",
    notification_channel: Optional[str] = None,
) -> dict:
    """
    Generate a CI/CD pipeline configuration for automated eval runs.

    Evals should run automatically on every PR or on a schedule. This
    generator produces a config structure that a CI system can consume.

    Scenario: You're helping a customer set up GitHub Actions to run
    evals on every pull request that touches the prompts/ directory.

    Args:
        project_name: Name of the project.
        eval_suite_path: Path to the eval test suite file.
        models: List of model identifiers to evaluate.
        thresholds: Dict with quality gates:
            - 'min_pass_rate': float (e.g., 0.85)
            - 'max_regression': float (e.g., 0.05)
            - 'min_avg_score': float (e.g., 0.7)
        schedule: "on_pr", "daily", or "weekly".
        notification_channel: Optional channel for alerts (e.g., "#evals-alerts").

    Returns:
        Dict representing the CI config with:
        - 'name': str pipeline name
        - 'trigger': dict with schedule/event details
        - 'steps': list of step dicts, each with 'name', 'command', 'timeout'
        - 'quality_gates': list of gate dicts with 'metric', 'operator', 'value'
        - 'notifications': dict with 'enabled' (bool), 'channel', 'on_failure' (bool)
        - 'matrix': dict with 'models' list
        - 'artifacts': list of artifact path strings to save
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import re
    import time

    print("Running Evaluation & Quality Assurance exercises...\n")

    # --- Test Exercise 1 ---
    tc = create_eval_test_case(
        "tc-001",
        "What is Python?",
        "Python is a programming language.",
        metadata={"difficulty": "easy"},
        tags=["general", "intro"],
    )
    assert tc["test_id"] == "tc-001"
    assert tc["input_prompt"] == "What is Python?"
    assert tc["expected_output"] == "Python is a programming language."
    assert tc["metadata"]["difficulty"] == "easy"
    assert "general" in tc["tags"]
    assert "created_at" in tc
    print("Exercise 1 PASSED: Eval test case data structure")

    # --- Test Exercise 2 ---
    exact = score_response("Hello World", "hello world", method="exact")
    assert exact["score"] == 1.0
    assert exact["method"] == "exact"

    fuzzy = score_response(
        "The quick brown fox", "The slow brown dog", method="fuzzy"
    )
    assert 0.0 < fuzzy["score"] < 1.0
    assert "f1" in fuzzy["details"]

    contains = score_response(
        "Python is a great programming language", "programming language", method="contains"
    )
    assert contains["score"] == 1.0
    print("Exercise 2 PASSED: Scoring functions")

    # --- Test Exercise 3 ---
    cases = [
        create_eval_test_case("t1", "Q1", "A1"),
        create_eval_test_case("t2", "Q2", "A2"),
    ]

    def mock_model(prompt: str) -> str:
        return prompt.replace("Q", "A")

    def mock_scorer(predicted: str, expected: str) -> dict:
        return {"score": 1.0 if predicted == expected else 0.0}

    harness = run_eval_harness(cases, mock_model, mock_scorer)
    assert harness["total"] == 2
    assert harness["passed"] == 2
    assert harness["avg_score"] == 1.0
    assert len(harness["results"]) == 2
    assert "elapsed_ms" in harness["results"][0]
    print("Exercise 3 PASSED: Eval harness runner")

    # --- Test Exercise 4 ---
    prompt = build_judge_prompt(
        "What is ML?",
        "ML is machine learning.",
        "Machine learning is a subset of AI.",
        ["accuracy", "completeness"],
    )
    assert "<question>" in prompt or "question" in prompt.lower()
    assert "accuracy" in prompt
    assert "completeness" in prompt
    assert "JSON" in prompt or "json" in prompt
    print("Exercise 4 PASSED: LLM-as-judge prompt template")

    # --- Test Exercise 5 ---
    good_response = '{"scores": {"accuracy": 4, "completeness": 3}, "reasoning": "Good answer"}'
    parsed = parse_judge_response(good_response, ["accuracy", "completeness"])
    assert parsed["parse_success"] is True
    assert parsed["scores"]["accuracy"] == 4
    assert len(parsed["missing_criteria"]) == 0

    bad_response = "I think it's pretty good overall."
    parsed_bad = parse_judge_response(bad_response, ["accuracy"])
    assert parsed_bad["parse_success"] is False
    assert "accuracy" in parsed_bad["missing_criteria"]

    fenced = '```json\n{"scores": {"accuracy": 5}, "reasoning": "Perfect"}\n```'
    parsed_fenced = parse_judge_response(fenced, ["accuracy"])
    assert parsed_fenced["parse_success"] is True
    assert parsed_fenced["scores"]["accuracy"] == 5
    print("Exercise 5 PASSED: Judge response parser")

    # --- Test Exercise 6 ---
    ds = [
        create_eval_test_case("d1", "Q1", "A1", tags=["billing"]),
        create_eval_test_case("d2", "Q2", "A2", tags=["support"]),
        create_eval_test_case("d3", "Q3", "A3", tags=["billing", "urgent"]),
    ]
    added = manage_golden_dataset(
        ds, "add",
        payload=create_eval_test_case("d4", "Q4", "A4", tags=["billing"]),
    )
    assert added["count"] == 4

    filtered = manage_golden_dataset(ds, "filter", filter_tags=["billing"])
    assert filtered["count"] == 2

    stats = manage_golden_dataset(ds, "stats")
    assert "tag_distribution" in stats
    assert stats["tag_distribution"]["billing"] == 2

    removed = manage_golden_dataset(ds, "remove", payload={"test_id": "d1"})
    assert removed["count"] == 2
    print("Exercise 6 PASSED: Golden dataset manager")

    # --- Test Exercise 7 ---
    baseline = [
        {"test_id": "t1", "score": 0.9},
        {"test_id": "t2", "score": 0.8},
        {"test_id": "t3", "score": 0.7},
    ]
    candidate = [
        {"test_id": "t1", "score": 0.95},
        {"test_id": "t2", "score": 0.6},
        {"test_id": "t3", "score": 0.72},
    ]
    comparison = compare_eval_runs(baseline, candidate)
    assert comparison["regression_count"] >= 1
    assert comparison["improvement_count"] >= 1
    assert len(comparison["regressions"]) > 0
    assert "baseline_avg" in comparison
    print("Exercise 7 PASSED: Regression test comparison")

    # --- Test Exercise 8 ---
    scores_a = [0.8, 0.85, 0.78, 0.82, 0.79, 0.81, 0.83, 0.80, 0.84, 0.77]
    scores_b = [0.90, 0.92, 0.88, 0.91, 0.89, 0.93, 0.87, 0.90, 0.91, 0.88]
    ab = ab_test_compare(scores_a, scores_b)
    assert "z_score" in ab
    assert "is_significant" in ab
    assert ab["winner"] in ("A", "B", "no_significant_difference")
    assert "effect_size" in ab
    print("Exercise 8 PASSED: A/B test statistical comparator")

    # --- Test Exercise 9 ---
    sources = [
        "Python was created by Guido van Rossum in 1991.",
        "Python supports multiple programming paradigms.",
    ]
    response_text = (
        "Python was created by Guido van Rossum. "
        "Python was originally written in Java. "
        "Python supports multiple programming paradigms."
    )
    hall = detect_hallucinations(response_text, sources)
    assert len(hall["claims"]) >= 2
    assert len(hall["unsupported"]) >= 1
    assert 0.0 <= hall["hallucination_rate"] <= 1.0
    print("Exercise 9 PASSED: Hallucination detection")

    # --- Test Exercise 10 ---
    cited = [
        {"id": 1, "title": "Python History", "content": "Python was created by Guido van Rossum and first released in 1991."},
        {"id": 2, "title": "Python Features", "content": "Python is dynamically typed and garbage collected."},
    ]
    resp_with_cites = (
        "Python was created by Guido van Rossum [1]. "
        "It uses static typing exclusively [2]. "
        "Python is the best language ever [3]."
    )
    verified = verify_citations(resp_with_cites, cited)
    assert verified["total_citations"] == 3
    assert any(v["status"] == "valid" for v in verified["verified"])
    assert any(v["status"] == "source_not_found" for v in verified["verified"])
    print("Exercise 10 PASSED: Citation verifier")

    # --- Test Exercise 11 ---
    rules = [
        {"name": "has_disclaimer", "type": "contains", "pattern": "consult your doctor",
         "weight": 2.0, "source": "predicted"},
        {"name": "no_banned_word", "type": "not_contains", "pattern": "cure",
         "weight": 1.0, "source": "predicted"},
    ]
    metric_fn = create_domain_metric("healthcare_safety", rules, aggregation="mean")
    result = metric_fn(
        "You should consult your doctor before taking this medication.",
        "Medical advice about medication.",
    )
    assert result["metric_name"] == "healthcare_safety"
    assert result["score"] > 0.0
    assert len(result["rule_results"]) == 2

    result_bad = metric_fn(
        "This pill will cure your disease instantly!",
        "Medical advice.",
    )
    assert result_bad["score"] < result["score"]
    print("Exercise 11 PASSED: Custom domain-specific metric")

    # --- Test Exercise 12 ---
    eval_results = [
        {"test_id": f"t{i}", "score": 0.5 + (i % 5) * 0.1,
         "tags": ["cat_a" if i % 2 == 0 else "cat_b"], "elapsed_ms": 100.0 + i * 10}
        for i in range(20)
    ]
    agg = aggregate_eval_results(eval_results)
    assert agg["total"] == 20
    assert "mean_score" in agg
    assert "median_score" in agg
    assert "p95_latency_ms" in agg

    agg_grouped = aggregate_eval_results(eval_results, group_by="category")
    # group_by uses tag values, so groups are based on tag values present
    print("Exercise 12 PASSED: Eval result aggregator")

    # --- Test Exercise 13 ---
    store = {"runs": []}
    run1 = {
        "run_id": "run-001",
        "timestamp": "2024-01-15T10:00:00",
        "model": "claude-3-opus",
        "results": [{"test_id": "t1", "score": 0.9}],
    }
    saved = eval_result_store(store, "save", run_data=run1)
    assert saved["success"] is True

    retrieved = eval_result_store(saved["store"], "get", run_id="run-001")
    assert retrieved["success"] is True
    assert retrieved["run"]["model"] == "claude-3-opus"

    listed = eval_result_store(saved["store"], "list")
    assert len(listed["runs"]) == 1
    print("Exercise 13 PASSED: Eval result storage and retrieval")

    # --- Test Exercise 14 ---
    trend_runs = [
        {"run_id": f"r{i}", "timestamp": f"2024-01-{i+1:02d}T10:00:00",
         "avg_score": 0.7 + i * 0.02, "pass_rate": 0.8 + i * 0.01}
        for i in range(6)
    ]
    trends = analyze_quality_trends(trend_runs, window_size=3)
    assert len(trends["sorted_run_ids"]) == 6
    assert len(trends["moving_averages"]) == 4  # 6 - 3 + 1
    assert trends["trend"] == "improving"
    assert isinstance(trends["alerts"], list)
    print("Exercise 14 PASSED: Quality trend analyzer")

    # --- Test Exercise 15 ---
    ci_config = generate_eval_ci_config(
        project_name="chatbot-v2",
        eval_suite_path="evals/test_suite.py",
        models=["claude-3-opus", "gpt-4o"],
        thresholds={"min_pass_rate": 0.85, "max_regression": 0.05, "min_avg_score": 0.7},
        schedule="on_pr",
        notification_channel="#evals-alerts",
    )
    assert ci_config["name"] == "chatbot-v2-eval-pipeline"
    assert "trigger" in ci_config
    assert len(ci_config["steps"]) >= 3
    assert len(ci_config["quality_gates"]) >= 2
    assert ci_config["notifications"]["enabled"] is True
    assert ci_config["matrix"]["models"] == ["claude-3-opus", "gpt-4o"]
    print("Exercise 15 PASSED: CI/CD integration config generator")

    print("\n=== All 15 exercises passed! ===")
