"""
Module 03: Evaluation & Quality Assurance -- Solutions
========================================================

Complete solutions for all 15 exercises on building eval frameworks,
LLM-as-judge patterns, regression testing, hallucination detection,
and CI/CD integration for AI applications.

Run this file directly to verify all solutions:
    python solutions.py
"""

import json
import math
import re
import statistics
import time
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
    """Build a structured eval test case with timestamp and metadata."""
    return {
        "test_id": test_id,
        "input_prompt": input_prompt,
        "expected_output": expected_output,
        # Default to empty dict/list if not provided
        "metadata": metadata if metadata is not None else {},
        "tags": tags if tags is not None else [],
        # ISO 8601 timestamp records when the test case was created
        "created_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Exercise 2: Build a Scoring Function (Exact, Fuzzy, Semantic)
# ---------------------------------------------------------------------------
def score_response(
    predicted: str,
    expected: str,
    method: str = "exact",
) -> dict:
    """Score a model response using exact match, fuzzy F1, or substring containment."""

    if method == "exact":
        # Case-insensitive, whitespace-stripped comparison
        match = predicted.strip().lower() == expected.strip().lower()
        return {
            "score": 1.0 if match else 0.0,
            "method": "exact",
            "details": {"matched": match},
        }

    elif method == "fuzzy":
        # Word-overlap F1: treat each text as a bag of lowercase words
        pred_words = set(predicted.lower().split())
        exp_words = set(expected.lower().split())

        if not pred_words or not exp_words:
            return {
                "score": 0.0,
                "method": "fuzzy",
                "details": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
            }

        # Precision = fraction of predicted words that are in expected
        overlap = pred_words & exp_words
        precision = len(overlap) / len(pred_words) if pred_words else 0.0
        # Recall = fraction of expected words that are in predicted
        recall = len(overlap) / len(exp_words) if exp_words else 0.0
        # F1 = harmonic mean of precision and recall
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return {
            "score": f1,
            "method": "fuzzy",
            "details": {"precision": precision, "recall": recall, "f1": f1},
        }

    elif method == "contains":
        # Check if expected appears as a substring in predicted (case-insensitive)
        found = expected.strip().lower() in predicted.strip().lower()
        return {
            "score": 1.0 if found else 0.0,
            "method": "contains",
            "details": {"found": found},
        }

    else:
        raise ValueError(f"Unknown scoring method: {method}")


# ---------------------------------------------------------------------------
# Exercise 3: Implement an Eval Harness Runner
# ---------------------------------------------------------------------------
def run_eval_harness(
    test_cases: list[dict],
    model_fn: Callable[[str], str],
    scoring_fn: Callable[[str, str], dict],
) -> dict:
    """Run a batch of eval test cases, score each, and aggregate results."""

    results = []
    total_score = 0.0

    for tc in test_cases:
        # Time each model call to track latency
        start = time.perf_counter()
        predicted = model_fn(tc["input_prompt"])
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        # Score the prediction against the expected answer
        score_result = scoring_fn(predicted, tc["expected_output"])
        score = score_result["score"]
        total_score += score

        results.append({
            "test_id": tc["test_id"],
            "predicted": predicted,
            "expected": tc["expected_output"],
            "score": score,
            "elapsed_ms": elapsed_ms,
        })

    total = len(test_cases)
    # A test case "passes" if score >= 0.5
    passed = sum(1 for r in results if r["score"] >= 0.5)
    failed = total - passed
    avg_score = total_score / total if total > 0 else 0.0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "avg_score": avg_score,
        "results": results,
    }


# ---------------------------------------------------------------------------
# Exercise 4: Build an LLM-as-Judge Prompt Template
# ---------------------------------------------------------------------------
def build_judge_prompt(
    question: str,
    model_answer: str,
    reference_answer: str,
    criteria: list[str],
) -> str:
    """Construct a structured LLM-as-judge prompt with XML sections."""

    # Build the criteria instructions block
    criteria_lines = []
    for criterion in criteria:
        criteria_lines.append(
            f"- {criterion}: Score from 1 (very poor) to 5 (excellent)"
        )
    criteria_block = "\n".join(criteria_lines)

    # Build the list of criterion keys for the JSON schema hint
    criteria_keys = ", ".join(f'"{c}"' for c in criteria)

    prompt = f"""You are an expert evaluation judge. Your task is to evaluate the quality of a model's answer compared to a reference answer.

<question>
{question}
</question>

<model_answer>
{model_answer}
</model_answer>

<reference_answer>
{reference_answer}
</reference_answer>

Evaluate the model answer on the following criteria:
{criteria_block}

You MUST respond with valid JSON only, using exactly this structure:
{{
  "scores": {{{criteria_keys}: <int 1-5>}},
  "reasoning": "<your explanation>"
}}

Do not include any text outside the JSON object."""

    return prompt


# ---------------------------------------------------------------------------
# Exercise 5: Implement Judge Response Parser (Structured Output)
# ---------------------------------------------------------------------------
def parse_judge_response(
    raw_response: str,
    expected_criteria: list[str],
) -> dict:
    """Parse an LLM judge response, handling markdown fences and messy output."""

    scores = {}
    reasoning = ""
    parse_success = False

    # Try to extract JSON from the response
    # Strategy 1: Look for JSON inside markdown code fences
    json_str = None
    fenced = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw_response, re.DOTALL)
    if fenced:
        json_str = fenced.group(1).strip()
    else:
        # Strategy 2: Look for a JSON object directly (first { to last })
        brace_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if brace_match:
            json_str = brace_match.group(0)

    if json_str:
        try:
            parsed = json.loads(json_str)
            # Extract scores dict
            if "scores" in parsed and isinstance(parsed["scores"], dict):
                scores = {k: int(v) for k, v in parsed["scores"].items()}
            # Extract reasoning string
            reasoning = parsed.get("reasoning", "")
            parse_success = True
        except (json.JSONDecodeError, ValueError, TypeError):
            # JSON was found but couldn't be parsed
            pass

    # Determine which expected criteria are missing from the parsed scores
    missing_criteria = [c for c in expected_criteria if c not in scores]

    # If parsing failed entirely, fall back to raw response as reasoning
    if not parse_success:
        reasoning = raw_response
        missing_criteria = list(expected_criteria)

    return {
        "scores": scores,
        "reasoning": reasoning,
        "parse_success": parse_success,
        "missing_criteria": missing_criteria,
    }


# ---------------------------------------------------------------------------
# Exercise 6: Build a Golden Dataset Manager
# ---------------------------------------------------------------------------
def manage_golden_dataset(
    dataset: list[dict],
    operation: str,
    payload: Optional[dict] = None,
    filter_tags: Optional[list[str]] = None,
) -> dict:
    """Manage golden eval datasets with CRUD and statistics operations."""

    if operation == "add":
        # Append a new test case and return the updated dataset
        new_dataset = dataset + [payload]
        return {
            "dataset": new_dataset,
            "count": len(new_dataset),
            "operation": "add",
        }

    elif operation == "remove":
        # Remove test case by test_id
        target_id = payload["test_id"]
        new_dataset = [tc for tc in dataset if tc["test_id"] != target_id]
        return {
            "dataset": new_dataset,
            "count": len(new_dataset),
            "operation": "remove",
        }

    elif operation == "filter":
        # Return only cases that have ALL of the filter_tags
        filter_set = set(filter_tags or [])
        filtered = [
            tc for tc in dataset
            if filter_set.issubset(set(tc.get("tags", [])))
        ]
        return {
            "dataset": filtered,
            "count": len(filtered),
            "operation": "filter",
        }

    elif operation == "stats":
        # Compute tag distribution and date range
        tag_counts: dict[str, int] = {}
        timestamps = []

        for tc in dataset:
            for tag in tc.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            if "created_at" in tc:
                timestamps.append(tc["created_at"])

        # Sort timestamps to find oldest/newest
        timestamps.sort()
        oldest = timestamps[0] if timestamps else None
        newest = timestamps[-1] if timestamps else None

        return {
            "dataset": dataset,
            "count": len(dataset),
            "operation": "stats",
            "tag_distribution": tag_counts,
            "oldest": oldest,
            "newest": newest,
        }

    else:
        raise ValueError(f"Unknown operation: {operation}")


# ---------------------------------------------------------------------------
# Exercise 7: Implement Regression Test Comparison
# ---------------------------------------------------------------------------
def compare_eval_runs(
    baseline_results: list[dict],
    candidate_results: list[dict],
    regression_threshold: float = 0.05,
) -> dict:
    """Compare baseline vs. candidate eval runs to detect regressions."""

    # Build lookup from test_id to score for both runs
    baseline_map = {r["test_id"]: r["score"] for r in baseline_results}
    candidate_map = {r["test_id"]: r["score"] for r in candidate_results}

    regressions = []
    improvements = []
    unchanged = []

    # Compare each test case present in both runs
    all_ids = set(baseline_map.keys()) | set(candidate_map.keys())
    for test_id in sorted(all_ids):
        b_score = baseline_map.get(test_id, 0.0)
        c_score = candidate_map.get(test_id, 0.0)
        delta = c_score - b_score

        entry = {
            "test_id": test_id,
            "baseline_score": b_score,
            "candidate_score": c_score,
            "delta": delta,
        }

        if delta < -regression_threshold:
            # Score dropped beyond threshold -> regression
            regressions.append(entry)
        elif delta >= regression_threshold and delta > 0:
            # Score improved at or beyond threshold -> improvement
            improvements.append(entry)
        else:
            # Within threshold -> unchanged
            unchanged.append(test_id)

    # Compute average scores for each run
    baseline_scores = [r["score"] for r in baseline_results]
    candidate_scores = [r["score"] for r in candidate_results]
    baseline_avg = (
        sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
    )
    candidate_avg = (
        sum(candidate_scores) / len(candidate_scores) if candidate_scores else 0.0
    )

    return {
        "regressions": regressions,
        "improvements": improvements,
        "unchanged": unchanged,
        "baseline_avg": baseline_avg,
        "candidate_avg": candidate_avg,
        "regression_count": len(regressions),
        "improvement_count": len(improvements),
    }


# ---------------------------------------------------------------------------
# Exercise 8: Build an A/B Test Statistical Comparator
# ---------------------------------------------------------------------------
def ab_test_compare(
    scores_a: list[float],
    scores_b: list[float],
    confidence_level: float = 0.95,
) -> dict:
    """Perform a z-test comparison of two score distributions."""

    n_a = len(scores_a)
    n_b = len(scores_b)
    mean_a = statistics.mean(scores_a)
    mean_b = statistics.mean(scores_b)
    # Use population stdev (not sample) for simplicity in this exercise
    std_a = statistics.pstdev(scores_a) if n_a > 1 else 0.0
    std_b = statistics.pstdev(scores_b) if n_b > 1 else 0.0

    # Compute z-score for two-sample z-test
    var_a = std_a ** 2
    var_b = std_b ** 2
    se = math.sqrt(var_a / n_a + var_b / n_b) if (n_a > 0 and n_b > 0) else 1.0
    z_score = (mean_a - mean_b) / se if se > 0 else 0.0

    # Critical z-values for common confidence levels
    z_critical = 1.96 if confidence_level <= 0.95 else 2.576
    is_significant = abs(z_score) > z_critical

    # Determine winner
    if is_significant:
        winner = "A" if mean_a > mean_b else "B"
    else:
        winner = "no_significant_difference"

    # Cohen's d = (mean_a - mean_b) / pooled_std
    pooled_std = math.sqrt((var_a + var_b) / 2) if (var_a + var_b) > 0 else 1.0
    effect_size = (mean_a - mean_b) / pooled_std

    return {
        "mean_a": mean_a,
        "mean_b": mean_b,
        "std_a": std_a,
        "std_b": std_b,
        "z_score": z_score,
        "is_significant": is_significant,
        "winner": winner,
        "effect_size": effect_size,
    }


# ---------------------------------------------------------------------------
# Exercise 9: Implement Hallucination Detection (Fact Checking)
# ---------------------------------------------------------------------------
def detect_hallucinations(
    response: str,
    source_documents: list[str],
    claim_extractor: Optional[Callable[[str], list[str]]] = None,
) -> dict:
    """Extract claims from a response and check each against sources."""

    # Stopwords to ignore when computing word overlap
    STOPWORDS = {
        "the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
        "to", "for", "of", "and", "or", "but", "it", "this", "that", "with",
    }

    # Extract claims: use the provided extractor or fall back to sentence split
    if claim_extractor:
        claims = claim_extractor(response)
    else:
        # Simple heuristic: split on ". " and strip trailing periods
        raw_claims = response.split(". ")
        claims = [c.strip().rstrip(".") for c in raw_claims if c.strip()]

    supported = []
    unsupported = []

    for claim in claims:
        # Tokenize the claim, removing stopwords
        claim_tokens = {
            w.lower() for w in claim.split()
            if w.lower() not in STOPWORDS and len(w) > 0
        }

        if not claim_tokens:
            # If claim has no meaningful tokens, consider it supported
            supported.append(claim)
            continue

        # Check if any source document contains >= 50% of the claim tokens
        is_supported = False
        for source in source_documents:
            source_tokens = set(source.lower().split())
            overlap = claim_tokens & source_tokens
            overlap_ratio = len(overlap) / len(claim_tokens)
            if overlap_ratio >= 0.5:
                is_supported = True
                break

        if is_supported:
            supported.append(claim)
        else:
            unsupported.append(claim)

    total = len(claims)
    hallucination_rate = len(unsupported) / total if total > 0 else 0.0

    return {
        "claims": claims,
        "supported": supported,
        "unsupported": unsupported,
        "hallucination_rate": hallucination_rate,
    }


# ---------------------------------------------------------------------------
# Exercise 10: Build a Citation Verifier
# ---------------------------------------------------------------------------
def verify_citations(
    response: str,
    cited_sources: list[dict],
) -> dict:
    """Verify [N] style citations in a response against source documents."""

    # Build a lookup from source id to source dict
    source_map = {s["id"]: s for s in cited_sources}

    # Find all citations in the response: [1], [2], etc.
    citation_pattern = re.compile(r"\[(\d+)\]")
    citations_found = citation_pattern.findall(response)

    verified = []

    # Split response into sentences for context extraction
    # We split on '. ' and keep track of which sentence each citation is in
    sentences = re.split(r"(?<=\.)\s+", response)

    for cite_num_str in citations_found:
        cite_id = int(cite_num_str)

        # Find the sentence containing this citation
        cite_sentence = ""
        cite_marker = f"[{cite_num_str}]"
        for sentence in sentences:
            if cite_marker in sentence:
                cite_sentence = sentence
                break

        if cite_id not in source_map:
            # Source not found in the provided sources list
            verified.append({
                "citation_id": cite_id,
                "sentence": cite_sentence,
                "status": "source_not_found",
            })
            continue

        # Check if at least 3 non-trivial words from the sentence
        # appear in the source content (case-insensitive)
        source_content = source_map[cite_id]["content"].lower()
        # Remove the citation marker itself from the sentence before checking
        clean_sentence = cite_sentence.replace(cite_marker, "").strip()
        words = clean_sentence.lower().split()
        # Non-trivial words: length > 3
        nontrivial = [w.strip(".,;:!?\"'()") for w in words if len(w.strip(".,;:!?\"'()")) > 3]
        matching_words = [w for w in nontrivial if w in source_content]

        if len(matching_words) >= 3:
            status = "valid"
        else:
            status = "invalid"

        verified.append({
            "citation_id": cite_id,
            "sentence": cite_sentence,
            "status": status,
        })

    total_citations = len(citations_found)
    valid_count = sum(1 for v in verified if v["status"] == "valid")
    verification_rate = valid_count / total_citations if total_citations > 0 else 1.0

    return {
        "total_citations": total_citations,
        "verified": verified,
        "verification_rate": verification_rate,
    }


# ---------------------------------------------------------------------------
# Exercise 11: Implement a Custom Domain-Specific Metric
# ---------------------------------------------------------------------------
def create_domain_metric(
    metric_name: str,
    scoring_rules: list[dict],
    aggregation: str = "mean",
) -> Callable[[str, str], dict]:
    """Factory that builds a reusable domain-specific scoring function."""

    def metric_fn(predicted: str, expected: str) -> dict:
        rule_results = []
        weighted_scores = []

        # Total weight for normalization (used in mean aggregation)
        total_weight = sum(r["weight"] for r in scoring_rules)

        for rule in scoring_rules:
            # Determine which text to check the pattern against
            text = predicted if rule["source"] == "predicted" else expected
            pattern = rule["pattern"]
            rule_type = rule["type"]

            # Evaluate the rule
            if rule_type == "contains":
                passed = pattern.lower() in text.lower()
            elif rule_type == "not_contains":
                passed = pattern.lower() not in text.lower()
            elif rule_type == "regex":
                passed = bool(re.search(pattern, text, re.IGNORECASE))
            else:
                passed = False

            rule_results.append({
                "rule_name": rule["name"],
                "passed": passed,
                "weight": rule["weight"],
            })

            # For weighted aggregation: 1.0 if passed, 0.0 if not
            score_val = 1.0 if passed else 0.0
            weighted_scores.append((score_val, rule["weight"]))

        # Aggregate into a final score
        if aggregation == "mean":
            # Weighted average: sum(score * weight) / sum(weight)
            if total_weight > 0:
                score = sum(s * w for s, w in weighted_scores) / total_weight
            else:
                score = 0.0
        elif aggregation == "min":
            # Minimum score across all rules (ignoring weights for min)
            score = min(s for s, _ in weighted_scores) if weighted_scores else 0.0
        else:
            score = 0.0

        return {
            "metric_name": metric_name,
            "score": score,
            "rule_results": rule_results,
        }

    return metric_fn


# ---------------------------------------------------------------------------
# Exercise 12: Build an Eval Result Aggregator with Statistics
# ---------------------------------------------------------------------------
def aggregate_eval_results(
    results: list[dict],
    group_by: Optional[str] = None,
) -> dict:
    """Aggregate eval results with descriptive statistics and optional grouping."""

    def compute_stats(items: list[dict]) -> dict:
        """Compute summary statistics for a list of result dicts."""
        if not items:
            return {
                "total": 0,
                "mean_score": 0.0,
                "median_score": 0.0,
                "std_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
                "pass_rate": 0.0,
                "p95_latency_ms": 0.0,
            }

        scores = [r["score"] for r in items]
        latencies = sorted([r["elapsed_ms"] for r in items])

        total = len(items)
        mean_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        std_score = statistics.pstdev(scores) if len(scores) >= 2 else 0.0
        min_score = min(scores)
        max_score = max(scores)
        pass_rate = sum(1 for s in scores if s >= 0.5) / total

        # 95th percentile latency: index = ceil(0.95 * n) - 1
        p95_idx = max(0, math.ceil(0.95 * total) - 1)
        p95_latency = latencies[p95_idx] if latencies else 0.0

        return {
            "total": total,
            "mean_score": mean_score,
            "median_score": median_score,
            "std_score": std_score,
            "min_score": min_score,
            "max_score": max_score,
            "pass_rate": pass_rate,
            "p95_latency_ms": p95_latency,
        }

    # Compute overall stats
    overall = compute_stats(results)

    # Compute per-group stats if group_by is provided
    groups: dict[str, dict] = {}
    if group_by is not None:
        # Group results by the first tag value in each result's tags list
        grouped: dict[str, list[dict]] = {}
        for r in results:
            tags = r.get("tags", [])
            # Use the first tag as the group key
            group_key = tags[0] if tags else "untagged"
            grouped.setdefault(group_key, []).append(r)

        for group_name, group_items in grouped.items():
            groups[group_name] = compute_stats(group_items)

    overall["groups"] = groups
    return overall


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
    """In-memory eval result store with save, get, query, and list actions."""

    if action == "save":
        # Append run_data to the store's runs list
        store.setdefault("runs", []).append(run_data)
        return {"success": True, "store": store}

    elif action == "get":
        # Find a specific run by run_id
        for run in store.get("runs", []):
            if run["run_id"] == run_id:
                return {"success": True, "run": run}
        return {"success": True, "run": None}

    elif action == "query":
        # Filter runs based on query criteria
        matching = []
        query = query or {}
        for run in store.get("runs", []):
            # Filter by model name
            if "model" in query and run.get("model") != query["model"]:
                continue

            # Filter by minimum pass rate (computed from results)
            if "min_pass_rate" in query:
                run_results = run.get("results", [])
                if run_results:
                    pass_rate = (
                        sum(1 for r in run_results if r.get("score", 0) >= 0.5)
                        / len(run_results)
                    )
                    if pass_rate < query["min_pass_rate"]:
                        continue

            # Filter by timestamp (runs after a given date)
            if "after" in query:
                run_ts = run.get("timestamp", "")
                if run_ts < query["after"]:
                    continue

            matching.append(run)

        return {"success": True, "runs": matching}

    elif action == "list":
        # Return a summary of all runs
        run_summaries = [
            {"run_id": r["run_id"], "timestamp": r.get("timestamp", "")}
            for r in store.get("runs", [])
        ]
        return {"success": True, "runs": run_summaries}

    else:
        return {"success": False, "error": f"Unknown action: {action}"}


# ---------------------------------------------------------------------------
# Exercise 14: Build a Quality Trend Analyzer
# ---------------------------------------------------------------------------
def analyze_quality_trends(
    runs: list[dict],
    window_size: int = 3,
) -> dict:
    """Analyze quality trends with moving averages and regression alerts."""

    # Sort runs chronologically by timestamp
    sorted_runs = sorted(runs, key=lambda r: r["timestamp"])
    sorted_ids = [r["run_id"] for r in sorted_runs]
    scores = [r["avg_score"] for r in sorted_runs]

    # Compute moving averages over the given window
    moving_averages = []
    for i in range(len(scores) - window_size + 1):
        window = scores[i : i + window_size]
        moving_averages.append(statistics.mean(window))

    # Determine overall trend from first to last moving average
    if len(moving_averages) >= 2:
        if moving_averages[-1] > moving_averages[0]:
            trend = "improving"
        elif moving_averages[-1] < moving_averages[0]:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # Detect alerts: any run whose score drops > 0.1 from the previous run
    alerts = []
    for i in range(1, len(sorted_runs)):
        prev_score = sorted_runs[i - 1]["avg_score"]
        curr_score = sorted_runs[i]["avg_score"]
        drop = prev_score - curr_score
        if drop > 0.1:
            alerts.append({
                "run_id": sorted_runs[i]["run_id"],
                "score_drop": round(drop, 4),
                "message": (
                    f"Score dropped by {drop:.4f} from "
                    f"{sorted_runs[i-1]['run_id']} to {sorted_runs[i]['run_id']}"
                ),
            })

    return {
        "sorted_run_ids": sorted_ids,
        "moving_averages": moving_averages,
        "trend": trend,
        "alerts": alerts,
    }


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
    """Generate a CI/CD pipeline config for automated eval runs."""

    # Build trigger configuration based on schedule type
    if schedule == "on_pr":
        trigger = {
            "event": "pull_request",
            "branches": ["main", "develop"],
            "paths": ["prompts/**", "evals/**", "src/**"],
        }
    elif schedule == "daily":
        trigger = {
            "event": "schedule",
            "cron": "0 6 * * *",  # Every day at 6 AM UTC
        }
    elif schedule == "weekly":
        trigger = {
            "event": "schedule",
            "cron": "0 6 * * 1",  # Every Monday at 6 AM UTC
        }
    else:
        trigger = {"event": schedule}

    # Build pipeline steps
    steps = [
        {
            "name": "setup-environment",
            "command": "pip install -r requirements.txt",
            "timeout": 300,
        },
        {
            "name": "run-eval-suite",
            "command": f"python {eval_suite_path} --output results.json",
            "timeout": 1800,
        },
        {
            "name": "compare-baseline",
            "command": "python scripts/compare_baseline.py --results results.json",
            "timeout": 120,
        },
        {
            "name": "upload-results",
            "command": "python scripts/upload_results.py --results results.json",
            "timeout": 60,
        },
    ]

    # Build quality gates from thresholds
    quality_gates = []
    if "min_pass_rate" in thresholds:
        quality_gates.append({
            "metric": "pass_rate",
            "operator": ">=",
            "value": thresholds["min_pass_rate"],
        })
    if "max_regression" in thresholds:
        quality_gates.append({
            "metric": "regression_rate",
            "operator": "<=",
            "value": thresholds["max_regression"],
        })
    if "min_avg_score" in thresholds:
        quality_gates.append({
            "metric": "avg_score",
            "operator": ">=",
            "value": thresholds["min_avg_score"],
        })

    # Notifications config
    notifications = {
        "enabled": notification_channel is not None,
        "channel": notification_channel,
        "on_failure": True,
    }

    # Artifacts to persist
    artifacts = [
        "results.json",
        "reports/eval_summary.html",
        "reports/regression_diff.json",
    ]

    return {
        "name": f"{project_name}-eval-pipeline",
        "trigger": trigger,
        "steps": steps,
        "quality_gates": quality_gates,
        "notifications": notifications,
        "matrix": {"models": models},
        "artifacts": artifacts,
    }


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    print("Running Evaluation & Quality Assurance solutions...\n")

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
    # Verify ISO format timestamp
    datetime.fromisoformat(tc["created_at"])
    print("Exercise 1 PASSED: Eval test case data structure")

    # --- Test Exercise 2 ---
    exact = score_response("Hello World", "hello world", method="exact")
    assert exact["score"] == 1.0
    assert exact["method"] == "exact"

    exact_miss = score_response("Hello", "World", method="exact")
    assert exact_miss["score"] == 0.0

    fuzzy = score_response(
        "The quick brown fox", "The slow brown dog", method="fuzzy"
    )
    assert 0.0 < fuzzy["score"] < 1.0
    assert "f1" in fuzzy["details"]
    assert "precision" in fuzzy["details"]
    assert "recall" in fuzzy["details"]

    contains = score_response(
        "Python is a great programming language", "programming language", method="contains"
    )
    assert contains["score"] == 1.0

    contains_miss = score_response("Python is great", "programming language", method="contains")
    assert contains_miss["score"] == 0.0
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
    assert harness["failed"] == 0
    assert harness["avg_score"] == 1.0
    assert len(harness["results"]) == 2
    assert "elapsed_ms" in harness["results"][0]
    assert harness["results"][0]["elapsed_ms"] >= 0.0
    print("Exercise 3 PASSED: Eval harness runner")

    # --- Test Exercise 4 ---
    prompt = build_judge_prompt(
        "What is ML?",
        "ML is machine learning.",
        "Machine learning is a subset of AI.",
        ["accuracy", "completeness"],
    )
    assert "<question>" in prompt
    assert "<model_answer>" in prompt
    assert "<reference_answer>" in prompt
    assert "accuracy" in prompt
    assert "completeness" in prompt
    assert "JSON" in prompt or "json" in prompt
    print("Exercise 4 PASSED: LLM-as-judge prompt template")

    # --- Test Exercise 5 ---
    good_response = '{"scores": {"accuracy": 4, "completeness": 3}, "reasoning": "Good answer"}'
    parsed = parse_judge_response(good_response, ["accuracy", "completeness"])
    assert parsed["parse_success"] is True
    assert parsed["scores"]["accuracy"] == 4
    assert parsed["scores"]["completeness"] == 3
    assert parsed["reasoning"] == "Good answer"
    assert len(parsed["missing_criteria"]) == 0

    bad_response = "I think it's pretty good overall."
    parsed_bad = parse_judge_response(bad_response, ["accuracy"])
    assert parsed_bad["parse_success"] is False
    assert "accuracy" in parsed_bad["missing_criteria"]
    assert parsed_bad["reasoning"] == bad_response

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
    assert stats["tag_distribution"]["support"] == 1

    removed = manage_golden_dataset(ds, "remove", payload={"test_id": "d1"})
    assert removed["count"] == 2
    print("Exercise 6 PASSED: Golden dataset manager")

    # --- Test Exercise 7 ---
    baseline = [
        {"test_id": "t1", "score": 0.8},
        {"test_id": "t2", "score": 0.8},
        {"test_id": "t3", "score": 0.8},
    ]
    candidate = [
        {"test_id": "t1", "score": 0.9},
        {"test_id": "t2", "score": 0.6},
        {"test_id": "t3", "score": 0.82},
    ]
    comparison = compare_eval_runs(baseline, candidate)
    assert comparison["regression_count"] == 1  # t2 dropped 0.2
    assert comparison["improvement_count"] == 1  # t1 improved 0.1
    assert len(comparison["regressions"]) == 1
    assert comparison["regressions"][0]["test_id"] == "t2"
    assert abs(comparison["baseline_avg"] - 0.8) < 0.001
    print("Exercise 7 PASSED: Regression test comparison")

    # --- Test Exercise 8 ---
    scores_a = [0.8, 0.85, 0.78, 0.82, 0.79, 0.81, 0.83, 0.80, 0.84, 0.77]
    scores_b = [0.90, 0.92, 0.88, 0.91, 0.89, 0.93, 0.87, 0.90, 0.91, 0.88]
    ab = ab_test_compare(scores_a, scores_b)
    assert "z_score" in ab
    assert "is_significant" in ab
    assert ab["winner"] in ("A", "B", "no_significant_difference")
    assert "effect_size" in ab
    # With these scores, B should be significantly better
    assert ab["mean_b"] > ab["mean_a"]
    assert ab["winner"] == "B"
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
    assert len(hall["unsupported"]) >= 1  # The Java claim
    assert len(hall["supported"]) >= 1
    assert 0.0 < hall["hallucination_rate"] < 1.0
    print("Exercise 9 PASSED: Hallucination detection")

    # --- Test Exercise 10 ---
    cited = [
        {"id": 1, "title": "Python History",
         "content": "Python was created by Guido van Rossum and first released in 1991."},
        {"id": 2, "title": "Python Features",
         "content": "Python is dynamically typed and garbage collected."},
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
    # Citation [1] should be valid (Guido van Rossum matches source 1)
    cite_1 = [v for v in verified["verified"] if v["citation_id"] == 1][0]
    assert cite_1["status"] == "valid"
    # Citation [3] should be source_not_found
    cite_3 = [v for v in verified["verified"] if v["citation_id"] == 3][0]
    assert cite_3["status"] == "source_not_found"
    print("Exercise 10 PASSED: Citation verifier")

    # --- Test Exercise 11 ---
    rules = [
        {"name": "has_disclaimer", "type": "contains",
         "pattern": "consult your doctor", "weight": 2.0, "source": "predicted"},
        {"name": "no_banned_word", "type": "not_contains",
         "pattern": "cure", "weight": 1.0, "source": "predicted"},
    ]
    metric_fn = create_domain_metric("healthcare_safety", rules, aggregation="mean")
    result = metric_fn(
        "You should consult your doctor before taking this medication.",
        "Medical advice about medication.",
    )
    assert result["metric_name"] == "healthcare_safety"
    assert result["score"] == 1.0  # Both rules pass
    assert len(result["rule_results"]) == 2
    assert all(r["passed"] for r in result["rule_results"])

    result_bad = metric_fn(
        "This pill will cure your disease instantly!",
        "Medical advice.",
    )
    assert result_bad["score"] < result["score"]
    # Neither rule passes: no disclaimer, contains "cure"
    assert result_bad["score"] == 0.0

    # Test with min aggregation
    metric_min = create_domain_metric("strict_check", rules, aggregation="min")
    result_partial = metric_min(
        "You should consult your doctor about this cure.",
        "Advice.",
    )
    assert result_partial["score"] == 0.0  # min of (1.0, 0.0) = 0.0
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
    assert "std_score" in agg
    assert "p95_latency_ms" in agg
    assert agg["groups"] == {}  # No grouping requested

    agg_grouped = aggregate_eval_results(eval_results, group_by="category")
    assert "cat_a" in agg_grouped["groups"]
    assert "cat_b" in agg_grouped["groups"]
    assert agg_grouped["groups"]["cat_a"]["total"] == 10
    assert agg_grouped["groups"]["cat_b"]["total"] == 10
    print("Exercise 12 PASSED: Eval result aggregator")

    # --- Test Exercise 13 ---
    store = {"runs": []}
    run1 = {
        "run_id": "run-001",
        "timestamp": "2024-01-15T10:00:00",
        "model": "claude-3-opus",
        "results": [{"test_id": "t1", "score": 0.9}],
    }
    run2 = {
        "run_id": "run-002",
        "timestamp": "2024-02-15T10:00:00",
        "model": "gpt-4o",
        "results": [{"test_id": "t1", "score": 0.85}],
    }
    saved = eval_result_store(store, "save", run_data=run1)
    assert saved["success"] is True
    saved = eval_result_store(saved["store"], "save", run_data=run2)
    assert saved["success"] is True

    retrieved = eval_result_store(saved["store"], "get", run_id="run-001")
    assert retrieved["success"] is True
    assert retrieved["run"]["model"] == "claude-3-opus"

    queried = eval_result_store(
        saved["store"], "query",
        query={"model": "gpt-4o"},
    )
    assert len(queried["runs"]) == 1

    listed = eval_result_store(saved["store"], "list")
    assert len(listed["runs"]) == 2
    print("Exercise 13 PASSED: Eval result storage and retrieval")

    # --- Test Exercise 14 ---
    trend_runs = [
        {"run_id": f"r{i}", "timestamp": f"2024-01-{i+1:02d}T10:00:00",
         "avg_score": 0.7 + i * 0.02, "pass_rate": 0.8 + i * 0.01}
        for i in range(6)
    ]
    trends = analyze_quality_trends(trend_runs, window_size=3)
    assert trends["sorted_run_ids"] == ["r0", "r1", "r2", "r3", "r4", "r5"]
    assert len(trends["moving_averages"]) == 4  # 6 - 3 + 1
    assert trends["trend"] == "improving"
    assert isinstance(trends["alerts"], list)
    # No alerts expected since scores are monotonically increasing
    assert len(trends["alerts"]) == 0

    # Test with a drop to trigger an alert
    drop_runs = [
        {"run_id": "a", "timestamp": "2024-01-01T10:00:00", "avg_score": 0.9, "pass_rate": 0.9},
        {"run_id": "b", "timestamp": "2024-01-02T10:00:00", "avg_score": 0.7, "pass_rate": 0.7},
        {"run_id": "c", "timestamp": "2024-01-03T10:00:00", "avg_score": 0.8, "pass_rate": 0.8},
    ]
    drop_trends = analyze_quality_trends(drop_runs, window_size=2)
    assert len(drop_trends["alerts"]) == 1
    assert drop_trends["alerts"][0]["run_id"] == "b"
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
    assert ci_config["trigger"]["event"] == "pull_request"
    assert len(ci_config["steps"]) >= 3
    assert len(ci_config["quality_gates"]) == 3
    assert ci_config["notifications"]["enabled"] is True
    assert ci_config["notifications"]["channel"] == "#evals-alerts"
    assert ci_config["matrix"]["models"] == ["claude-3-opus", "gpt-4o"]
    assert len(ci_config["artifacts"]) > 0

    # Test daily schedule
    daily_config = generate_eval_ci_config(
        "test-proj", "evals.py", ["model-a"],
        {"min_pass_rate": 0.8}, schedule="daily",
    )
    assert daily_config["trigger"]["event"] == "schedule"
    assert "cron" in daily_config["trigger"]
    assert daily_config["notifications"]["enabled"] is False
    print("Exercise 15 PASSED: CI/CD integration config generator")

    print("\n=== All 15 exercises passed! ===")
