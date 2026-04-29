# Module 03: Evaluation & Quality Assurance

## Introduction for Swift Developers

If you have ever written XCTest assertions to verify deterministic outputs from a
function, you already understand the core motivation behind evaluation: proving that
your system works. But LLM-based systems shatter the fundamental assumption underlying
traditional testing -- that the same input always produces the same output. Every call
to an LLM can yield a different response, even with temperature set to zero. This means
you cannot simply `XCTAssertEqual(output, expected)` and call it a day.

Evaluation for AI systems is a discipline unto itself. At companies like Anthropic,
OpenAI, and Google, solutions engineers are expected to build custom evaluation
harnesses, design scoring rubrics, set up automated regression pipelines, and advise
customers on quality assurance strategies. This module teaches you to build all of that
from scratch using Python, with real code you can deploy in production.

---

## 1. Why Evaluation Matters for AI Engineers

### The Non-Determinism Problem

Traditional software testing relies on deterministic behavior:

```swift
// Swift: Deterministic -- always passes
func testAddition() {
    XCTAssertEqual(add(2, 3), 5)  // Always 5, forever
}
```

LLM outputs are non-deterministic by nature:

```python
# Python: Two calls, potentially two different outputs
response_1 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Summarize quantum computing in one sentence."}]
)

response_2 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Summarize quantum computing in one sentence."}]
)

# response_1.content != response_2.content (usually)
```

This means you need a fundamentally different testing mindset -- one that evaluates
properties, ranges, and quality dimensions rather than exact equality.

### The Evaluation Mindset

Think in terms of these four pillars:

1. **Correctness** -- Does the output contain accurate information?
2. **Relevance** -- Does it actually answer the question asked?
3. **Safety** -- Does it avoid harmful, biased, or inappropriate content?
4. **Consistency** -- Does it behave similarly across equivalent inputs?

```python
from dataclasses import dataclass
from enum import Enum


class EvalDimension(Enum):
    CORRECTNESS = "correctness"
    RELEVANCE = "relevance"
    SAFETY = "safety"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    TONE = "tone"


@dataclass
class EvalResult:
    """Result of evaluating a single dimension."""
    dimension: EvalDimension
    score: float  # 0.0 to 1.0
    reasoning: str
    passed: bool

    @property
    def grade(self) -> str:
        if self.score >= 0.9:
            return "A"
        elif self.score >= 0.8:
            return "B"
        elif self.score >= 0.7:
            return "C"
        elif self.score >= 0.6:
            return "D"
        return "F"
```

### Why Customers Care

When you are a solutions engineer deploying AI for an enterprise customer, trust is
everything. A chatbot that hallucinates once in a customer-facing setting can destroy
months of relationship-building. Evaluation is how you prove reliability:

- **Pre-deployment**: "Here are the results of 500 test cases across your domain."
- **Ongoing monitoring**: "Quality has remained above 95% over the last 30 days."
- **Regression prevention**: "We caught a quality drop in the latest prompt update before it hit production."

> **Swift Developer Note:** Think of evaluation like Xcode's Test Navigator, but
> instead of green/red pass/fail, you get a spectrum of scores across multiple
> dimensions. The shift from binary assertions to probabilistic quality measurement
> is the biggest mental model change you will make.

---

## 2. Building Custom Eval Harnesses

### Architecture of an Eval Harness

An evaluation harness has four components:

1. **Test Cases** -- Input/expected-output pairs with metadata
2. **Runner** -- Executes the system under test against each case
3. **Scorers** -- Functions that evaluate outputs on specific dimensions
4. **Reporter** -- Aggregates scores and produces reports

```python
from __future__ import annotations

import json
import time
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


# ── Test Case Definition ──────────────────────────────────────────────

@dataclass
class EvalTestCase:
    """A single test case for evaluation."""
    id: str
    input_text: str
    expected_output: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvalTestCase:
        return cls(
            id=data["id"],
            input_text=data["input_text"],
            expected_output=data.get("expected_output"),
            context=data.get("context", {}),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def load_from_jsonl(cls, path: str | Path) -> list[EvalTestCase]:
        """Load test cases from a JSONL file."""
        cases: list[EvalTestCase] = []
        with open(path) as f:
            for line in f:
                if line.strip():
                    cases.append(cls.from_dict(json.loads(line)))
        return cases


# ── Scorer Interface ──────────────────────────────────────────────────

@dataclass
class ScoreResult:
    """Result from a single scorer."""
    name: str
    score: float  # 0.0 to 1.0
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)


class Scorer(ABC):
    """Abstract base class for all scorers."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def score(
        self,
        input_text: str,
        output_text: str,
        expected_output: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ScoreResult:
        ...


# ── Built-in Scorers ─────────────────────────────────────────────────

class ExactMatchScorer(Scorer):
    """Checks if output exactly matches expected."""

    @property
    def name(self) -> str:
        return "exact_match"

    def score(
        self,
        input_text: str,
        output_text: str,
        expected_output: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ScoreResult:
        if expected_output is None:
            return ScoreResult(name=self.name, score=0.0, passed=False,
                               details={"error": "No expected output"})
        match = output_text.strip() == expected_output.strip()
        return ScoreResult(
            name=self.name,
            score=1.0 if match else 0.0,
            passed=match,
            details={"expected": expected_output, "actual": output_text},
        )


class ContainsScorer(Scorer):
    """Checks if output contains required substrings."""

    def __init__(self, required_substrings: list[str], case_sensitive: bool = False):
        self._required = required_substrings
        self._case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        return "contains"

    def score(
        self,
        input_text: str,
        output_text: str,
        expected_output: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ScoreResult:
        check_text = output_text if self._case_sensitive else output_text.lower()
        found = []
        missing = []
        for substring in self._required:
            check_sub = substring if self._case_sensitive else substring.lower()
            if check_sub in check_text:
                found.append(substring)
            else:
                missing.append(substring)
        ratio = len(found) / len(self._required) if self._required else 1.0
        return ScoreResult(
            name=self.name,
            score=ratio,
            passed=ratio == 1.0,
            details={"found": found, "missing": missing},
        )


class LengthScorer(Scorer):
    """Checks if output length is within bounds."""

    def __init__(self, min_chars: int = 0, max_chars: int = 10000):
        self._min = min_chars
        self._max = max_chars

    @property
    def name(self) -> str:
        return "length"

    def score(
        self,
        input_text: str,
        output_text: str,
        expected_output: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ScoreResult:
        length = len(output_text)
        in_range = self._min <= length <= self._max
        return ScoreResult(
            name=self.name,
            score=1.0 if in_range else 0.0,
            passed=in_range,
            details={"length": length, "min": self._min, "max": self._max},
        )
```

### The Eval Runner

```python
@dataclass
class EvalRunResult:
    """Complete result for one test case across all scorers."""
    test_case_id: str
    input_text: str
    output_text: str
    expected_output: str | None
    scores: list[ScoreResult]
    latency_ms: float
    timestamp: str

    @property
    def passed(self) -> bool:
        return all(s.passed for s in self.scores)

    @property
    def average_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(s.score for s in self.scores) / len(self.scores)


@dataclass
class EvalSuiteResult:
    """Aggregated results across all test cases."""
    suite_name: str
    results: list[EvalRunResult]
    run_timestamp: str
    config: dict[str, Any] = field(default_factory=dict)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    @property
    def average_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.average_score for r in self.results) / len(self.results)

    @property
    def average_latency_ms(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.latency_ms for r in self.results) / len(self.results)

    def scores_by_scorer(self) -> dict[str, float]:
        """Average score per scorer across all test cases."""
        scorer_totals: dict[str, list[float]] = {}
        for result in self.results:
            for score in result.scores:
                scorer_totals.setdefault(score.name, []).append(score.score)
        return {
            name: sum(scores) / len(scores)
            for name, scores in scorer_totals.items()
        }

    def failed_cases(self) -> list[EvalRunResult]:
        return [r for r in self.results if not r.passed]

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "run_timestamp": self.run_timestamp,
            "total_cases": len(self.results),
            "pass_rate": self.pass_rate,
            "average_score": self.average_score,
            "average_latency_ms": self.average_latency_ms,
            "scores_by_scorer": self.scores_by_scorer(),
            "config": self.config,
        }


# Type alias for the system under test
SystemUnderTest = Callable[[str], str]


class EvalHarness:
    """Main evaluation harness that ties everything together."""

    def __init__(
        self,
        name: str,
        system: SystemUnderTest,
        scorers: list[Scorer],
        test_cases: list[EvalTestCase],
    ):
        self.name = name
        self.system = system
        self.scorers = scorers
        self.test_cases = test_cases

    def run(self, verbose: bool = False) -> EvalSuiteResult:
        """Execute all test cases and return aggregated results."""
        results: list[EvalRunResult] = []

        for i, case in enumerate(self.test_cases):
            if verbose:
                print(f"  Running case {i + 1}/{len(self.test_cases)}: {case.id}")

            # Time the system call
            start = time.perf_counter()
            output = self.system(case.input_text)
            latency_ms = (time.perf_counter() - start) * 1000

            # Run all scorers
            scores = [
                scorer.score(
                    input_text=case.input_text,
                    output_text=output,
                    expected_output=case.expected_output,
                    context=case.context,
                )
                for scorer in self.scorers
            ]

            result = EvalRunResult(
                test_case_id=case.id,
                input_text=case.input_text,
                output_text=output,
                expected_output=case.expected_output,
                scores=scores,
                latency_ms=latency_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            results.append(result)

        return EvalSuiteResult(
            suite_name=self.name,
            results=results,
            run_timestamp=datetime.now(timezone.utc).isoformat(),
            config={"scorers": [s.name for s in self.scorers]},
        )

    def print_report(self, suite_result: EvalSuiteResult) -> None:
        """Print a human-readable report."""
        print(f"\n{'=' * 60}")
        print(f"Eval Suite: {suite_result.suite_name}")
        print(f"{'=' * 60}")
        print(f"Total cases:     {len(suite_result.results)}")
        print(f"Pass rate:       {suite_result.pass_rate:.1%}")
        print(f"Average score:   {suite_result.average_score:.3f}")
        print(f"Avg latency:     {suite_result.average_latency_ms:.0f}ms")
        print(f"\nScores by scorer:")
        for name, avg in suite_result.scores_by_scorer().items():
            print(f"  {name}: {avg:.3f}")

        failed = suite_result.failed_cases()
        if failed:
            print(f"\nFailed cases ({len(failed)}):")
            for r in failed[:5]:  # Show first 5 failures
                print(f"  - {r.test_case_id}: score={r.average_score:.3f}")
                for s in r.scores:
                    if not s.passed:
                        print(f"      {s.name}: {s.score:.3f} -- {s.details}")
        print(f"{'=' * 60}\n")
```

### Using the Harness

```python
import anthropic


def create_claude_system(
    system_prompt: str,
    model: str = "claude-sonnet-4-20250514",
) -> SystemUnderTest:
    """Create a SystemUnderTest wrapper around Claude."""
    client = anthropic.Anthropic()

    def call(input_text: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": input_text}],
        )
        return response.content[0].text

    return call


# Define test cases
test_cases = [
    EvalTestCase(
        id="greeting-001",
        input_text="Hello, I need help with my order #12345",
        expected_output=None,
        tags=["greeting", "order"],
        context={"expected_topics": ["order", "help"]},
    ),
    EvalTestCase(
        id="refund-001",
        input_text="I want a refund for my purchase",
        expected_output=None,
        tags=["refund"],
        context={"expected_topics": ["refund", "policy"]},
    ),
]

# Create system and scorers
system = create_claude_system("You are a helpful customer service agent.")
scorers = [
    LengthScorer(min_chars=50, max_chars=2000),
    ContainsScorer(["help"], case_sensitive=False),
]

# Run evaluation
harness = EvalHarness(
    name="customer-service-v1",
    system=system,
    scorers=scorers,
    test_cases=test_cases,
)
result = harness.run(verbose=True)
harness.print_report(result)
```

> **Swift Developer Note:** The `EvalHarness` class plays a role similar to
> `XCTestSuite` in XCTest. But instead of `XCTAssert*` macros, you compose
> `Scorer` objects that return continuous scores. Think of scorers as protocol
> conformances -- each one implements a `score()` method, just like how Swift
> protocols require implementing specific methods.

---

## 3. LLM-as-Judge Evaluation

### The Core Idea

When outputs are too complex for rule-based scoring (creative writing, nuanced
reasoning, multi-step explanations), you can use a powerful LLM to judge the quality
of another LLM's output. This is called "LLM-as-Judge" and it is the single most
important evaluation technique in modern AI engineering.

### Basic LLM Judge

```python
import anthropic
from pydantic import BaseModel, Field


class JudgeVerdict(BaseModel):
    """Structured output from the judge LLM."""
    score: int = Field(
        ..., ge=1, le=5,
        description="Quality score from 1 (terrible) to 5 (excellent)"
    )
    reasoning: str = Field(
        ...,
        description="Step-by-step reasoning for the score"
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Specific strengths of the response"
    )
    weaknesses: list[str] = Field(
        default_factory=list,
        description="Specific weaknesses of the response"
    )


class LLMJudge:
    """Use a powerful LLM to evaluate another LLM's output."""

    DEFAULT_RUBRIC = """You are an expert evaluator. Score the AI response on a scale
of 1-5 based on these criteria:

5 - Excellent: Accurate, comprehensive, well-structured, directly addresses the query
4 - Good: Mostly accurate and helpful, minor gaps or formatting issues
3 - Acceptable: Partially addresses the query, some inaccuracies or missing info
2 - Poor: Significant inaccuracies, misses the main point, or is unhelpful
1 - Terrible: Completely wrong, harmful, or irrelevant

Consider these dimensions:
- Factual accuracy
- Relevance to the question
- Completeness of the answer
- Clarity and structure
- Appropriate tone"""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        rubric: str | None = None,
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.rubric = rubric or self.DEFAULT_RUBRIC

    def evaluate(
        self,
        question: str,
        response: str,
        reference_answer: str | None = None,
    ) -> JudgeVerdict:
        """Evaluate a response using the judge LLM."""
        judge_prompt = f"""{self.rubric}

## Question
{question}

## AI Response to Evaluate
{response}
"""
        if reference_answer:
            judge_prompt += f"""
## Reference Answer (ground truth)
{reference_answer}
"""

        judge_prompt += """
Provide your evaluation as JSON with these fields:
- score (int, 1-5)
- reasoning (str)
- strengths (list of str)
- weaknesses (list of str)"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": judge_prompt}],
        )

        # Parse the judge's response into structured output
        raw_text = message.content[0].text

        # Extract JSON from the response (handle markdown code blocks)
        json_str = raw_text
        if "```json" in raw_text:
            json_str = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            json_str = raw_text.split("```")[1].split("```")[0]

        return JudgeVerdict.model_validate_json(json_str)


# Usage
judge = LLMJudge()
verdict = judge.evaluate(
    question="What causes rain?",
    response="Rain is caused by water evaporating from the surface, rising "
             "as vapor, cooling in the atmosphere to form clouds, and then "
             "condensing into droplets that fall as precipitation.",
)
print(f"Score: {verdict.score}/5")
print(f"Reasoning: {verdict.reasoning}")
```

### Multi-Dimensional Judge with Structured Output

For production use, you want the judge to evaluate across multiple specific dimensions:

```python
from pydantic import BaseModel, Field
from enum import Enum


class DimensionScore(BaseModel):
    """Score for a single evaluation dimension."""
    dimension: str
    score: int = Field(..., ge=1, le=5)
    reasoning: str


class MultiDimensionVerdict(BaseModel):
    """Multi-dimensional evaluation result."""
    dimensions: list[DimensionScore]
    overall_score: float = Field(..., ge=1.0, le=5.0)
    summary: str
    recommendation: str = Field(
        ...,
        description="One of: 'ship', 'revise', 'reject'"
    )


class MultiDimensionJudge:
    """Judge that evaluates across multiple configurable dimensions."""

    def __init__(
        self,
        dimensions: list[str] | None = None,
        model: str = "claude-sonnet-4-20250514",
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.dimensions = dimensions or [
            "accuracy",
            "completeness",
            "clarity",
            "relevance",
            "safety",
        ]

    def evaluate(
        self,
        question: str,
        response: str,
        context: str | None = None,
    ) -> MultiDimensionVerdict:
        dimensions_text = "\n".join(
            f"- **{dim}**: Score 1-5 with reasoning"
            for dim in self.dimensions
        )

        prompt = f"""You are an expert evaluator. Evaluate the following AI response
across these dimensions:

{dimensions_text}

## Question
{question}

## Response to Evaluate
{response}
"""
        if context:
            prompt += f"""
## Additional Context
{context}
"""

        prompt += """
Return your evaluation as JSON with:
- dimensions: list of {dimension, score (1-5), reasoning}
- overall_score: weighted average (float, 1.0-5.0)
- summary: brief overall assessment
- recommendation: "ship", "revise", or "reject"
"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = message.content[0].text
        json_str = raw_text
        if "```json" in raw_text:
            json_str = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            json_str = raw_text.split("```")[1].split("```")[0]

        return MultiDimensionVerdict.model_validate_json(json_str)


# Usage
judge = MultiDimensionJudge(
    dimensions=["medical_accuracy", "patient_safety", "clarity", "empathy"]
)
verdict = judge.evaluate(
    question="What should I do about chest pain?",
    response="Chest pain can have many causes. If severe, call 911 immediately.",
    context="This is a health information chatbot, not a diagnostic tool.",
)
for dim in verdict.dimensions:
    print(f"  {dim.dimension}: {dim.score}/5 -- {dim.reasoning}")
print(f"Overall: {verdict.overall_score}/5")
print(f"Recommendation: {verdict.recommendation}")
```

### Integrating LLM Judge as a Scorer

To plug the LLM judge into our harness from Section 2:

```python
class LLMJudgeScorer(Scorer):
    """Scorer that uses an LLM judge for evaluation."""

    def __init__(
        self,
        judge: LLMJudge,
        pass_threshold: int = 4,
    ):
        self._judge = judge
        self._pass_threshold = pass_threshold

    @property
    def name(self) -> str:
        return "llm_judge"

    def score(
        self,
        input_text: str,
        output_text: str,
        expected_output: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ScoreResult:
        verdict = self._judge.evaluate(
            question=input_text,
            response=output_text,
            reference_answer=expected_output,
        )
        return ScoreResult(
            name=self.name,
            score=verdict.score / 5.0,  # Normalize to 0-1
            passed=verdict.score >= self._pass_threshold,
            details={
                "raw_score": verdict.score,
                "reasoning": verdict.reasoning,
                "strengths": verdict.strengths,
                "weaknesses": verdict.weaknesses,
            },
        )
```

### Avoiding Judge Bias

LLM judges can exhibit systematic biases. Here are the major ones and mitigations:

```python
class DebiasedJudge:
    """Judge with built-in bias mitigation techniques."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model

    def evaluate_with_position_debiasing(
        self,
        question: str,
        response_a: str,
        response_b: str,
    ) -> dict[str, Any]:
        """
        Mitigate position bias by evaluating in both orders
        and averaging the results.

        Position bias: LLMs tend to prefer the first (or last) response
        shown, regardless of actual quality.
        """
        # Order 1: A first, B second
        score_a1, score_b1 = self._pairwise_compare(
            question, response_a, response_b
        )
        # Order 2: B first, A second
        score_b2, score_a2 = self._pairwise_compare(
            question, response_b, response_a
        )
        # Average to cancel position bias
        final_a = (score_a1 + score_a2) / 2
        final_b = (score_b1 + score_b2) / 2

        return {
            "response_a_score": final_a,
            "response_b_score": final_b,
            "winner": "A" if final_a > final_b else "B" if final_b > final_a else "tie",
            "position_bias_detected": abs((score_a1 - score_a2)) > 1,
        }

    def _pairwise_compare(
        self,
        question: str,
        first: str,
        second: str,
    ) -> tuple[int, int]:
        """Compare two responses and return scores for each."""
        prompt = f"""Compare these two responses to the question.
Score each independently on a 1-5 scale.

Question: {question}

Response 1:
{first}

Response 2:
{second}

Return JSON: {{"score_1": int, "score_2": int, "reasoning": str}}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        data = json.loads(raw)
        return data["score_1"], data["score_2"]
```

**Common biases and mitigations:**

| Bias | Description | Mitigation |
|------|-------------|------------|
| Position bias | Prefers first/last response | Swap order, average scores |
| Verbosity bias | Prefers longer responses | Add "length should not affect scoring" to rubric |
| Self-enhancement | Prefers its own style | Use a different model as judge |
| Anchoring | First score influences subsequent | Score each dimension independently |
| Sycophancy | Agrees with provided reference | Evaluate without reference first |

> **Swift Developer Note:** Position debiasing is conceptually similar to how you
> might run UI tests in both portrait and landscape to catch orientation-specific
> bugs. The principle is the same: vary the conditions to separate real quality
> differences from artifacts of the test setup.

---

## 4. Automated Regression Testing

### Golden Dataset Creation

A golden dataset is a curated collection of input/output pairs that represent the
expected behavior of your system. These are your "source of truth."

```python
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json


@dataclass
class GoldenExample:
    """A single example in the golden dataset."""
    id: str
    input_text: str
    expected_output: str
    category: str
    difficulty: str  # "easy", "medium", "hard"
    created_by: str  # "human" or "synthetic"
    verified: bool = True
    notes: str = ""


class GoldenDataset:
    """Manages a golden dataset for regression testing."""

    def __init__(self, name: str, path: str | Path):
        self.name = name
        self.path = Path(path)
        self.examples: list[GoldenExample] = []
        if self.path.exists():
            self._load()

    def _load(self) -> None:
        with open(self.path) as f:
            data = json.load(f)
            self.examples = [
                GoldenExample(**ex) for ex in data["examples"]
            ]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(
                {
                    "name": self.name,
                    "version": "1.0",
                    "total_examples": len(self.examples),
                    "examples": [asdict(ex) for ex in self.examples],
                },
                f,
                indent=2,
            )

    def add(self, example: GoldenExample) -> None:
        """Add a new golden example."""
        if any(ex.id == example.id for ex in self.examples):
            raise ValueError(f"Duplicate ID: {example.id}")
        self.examples.append(example)

    def filter_by_category(self, category: str) -> list[GoldenExample]:
        return [ex for ex in self.examples if ex.category == category]

    def filter_by_difficulty(self, difficulty: str) -> list[GoldenExample]:
        return [ex for ex in self.examples if ex.difficulty == difficulty]

    def to_eval_cases(self) -> list[EvalTestCase]:
        """Convert golden examples to eval test cases."""
        return [
            EvalTestCase(
                id=ex.id,
                input_text=ex.input_text,
                expected_output=ex.expected_output,
                tags=[ex.category, ex.difficulty],
                metadata={"created_by": ex.created_by, "notes": ex.notes},
            )
            for ex in self.examples
            if ex.verified
        ]

    def summary(self) -> dict[str, Any]:
        categories: dict[str, int] = {}
        difficulties: dict[str, int] = {}
        for ex in self.examples:
            categories[ex.category] = categories.get(ex.category, 0) + 1
            difficulties[ex.difficulty] = difficulties.get(ex.difficulty, 0) + 1
        return {
            "total": len(self.examples),
            "verified": sum(1 for ex in self.examples if ex.verified),
            "categories": categories,
            "difficulties": difficulties,
        }


# Build a golden dataset
dataset = GoldenDataset("customer-service", Path("golden/customer_service.json"))
dataset.add(GoldenExample(
    id="cs-001",
    input_text="How do I reset my password?",
    expected_output="To reset your password, go to Settings > Security > Reset Password.",
    category="account",
    difficulty="easy",
    created_by="human",
))
dataset.add(GoldenExample(
    id="cs-002",
    input_text="I was charged twice for my subscription",
    expected_output="I apologize for the double charge. Let me look into your account "
                    "and process a refund for the duplicate payment.",
    category="billing",
    difficulty="medium",
    created_by="human",
))
dataset.save()
```

### Regression Test Runner

```python
import hashlib
from datetime import datetime, timezone


@dataclass
class RegressionResult:
    """Result comparing current run against a baseline."""
    current_scores: dict[str, float]
    baseline_scores: dict[str, float]
    regressions: list[dict[str, Any]]
    improvements: list[dict[str, Any]]
    unchanged: list[str]
    overall_regression: bool

    def summary(self) -> str:
        lines = [
            f"Regressions: {len(self.regressions)}",
            f"Improvements: {len(self.improvements)}",
            f"Unchanged: {len(self.unchanged)}",
            f"Overall regression: {self.overall_regression}",
        ]
        if self.regressions:
            lines.append("\nRegressed cases:")
            for r in self.regressions:
                lines.append(
                    f"  {r['case_id']}: {r['baseline_score']:.3f} -> "
                    f"{r['current_score']:.3f} (delta: {r['delta']:.3f})"
                )
        return "\n".join(lines)


class RegressionTester:
    """Compare current eval results against a stored baseline."""

    def __init__(self, baseline_path: str | Path):
        self.baseline_path = Path(baseline_path)
        self._baseline: dict[str, float] | None = None

    def load_baseline(self) -> dict[str, float]:
        """Load baseline scores from disk."""
        if not self.baseline_path.exists():
            return {}
        with open(self.baseline_path) as f:
            data = json.load(f)
        return {item["case_id"]: item["score"] for item in data["results"]}

    def save_baseline(self, suite_result: EvalSuiteResult) -> None:
        """Save current results as the new baseline."""
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "suite_name": suite_result.suite_name,
            "results": [
                {"case_id": r.test_case_id, "score": r.average_score}
                for r in suite_result.results
            ],
        }
        with open(self.baseline_path, "w") as f:
            json.dump(data, f, indent=2)

    def compare(
        self,
        suite_result: EvalSuiteResult,
        regression_threshold: float = 0.1,
    ) -> RegressionResult:
        """Compare current results against baseline."""
        baseline = self.load_baseline()
        current = {
            r.test_case_id: r.average_score for r in suite_result.results
        }

        regressions = []
        improvements = []
        unchanged = []

        for case_id, current_score in current.items():
            baseline_score = baseline.get(case_id)
            if baseline_score is None:
                continue  # New test case, no comparison

            delta = current_score - baseline_score
            if delta < -regression_threshold:
                regressions.append({
                    "case_id": case_id,
                    "baseline_score": baseline_score,
                    "current_score": current_score,
                    "delta": delta,
                })
            elif delta > regression_threshold:
                improvements.append({
                    "case_id": case_id,
                    "baseline_score": baseline_score,
                    "current_score": current_score,
                    "delta": delta,
                })
            else:
                unchanged.append(case_id)

        return RegressionResult(
            current_scores=current,
            baseline_scores=baseline,
            regressions=regressions,
            improvements=improvements,
            unchanged=unchanged,
            overall_regression=len(regressions) > 0,
        )
```

### CI/CD Integration

Here is a practical script that runs evaluations in a CI pipeline:

```python
#!/usr/bin/env python3
"""
CI/CD evaluation script.

Usage:
    python run_evals.py --suite customer-service --baseline baselines/cs.json
    python run_evals.py --suite customer-service --update-baseline

Exit codes:
    0 - All evaluations passed, no regressions
    1 - Regressions detected
    2 - Configuration error
"""
import argparse
import sys
import json
from pathlib import Path


def run_ci_eval(
    suite_name: str,
    baseline_path: str,
    update_baseline: bool = False,
    fail_on_regression: bool = True,
) -> int:
    """Run evaluation suite in CI and check for regressions."""
    # Load golden dataset and create test cases
    dataset = GoldenDataset(suite_name, Path(f"golden/{suite_name}.json"))
    test_cases = dataset.to_eval_cases()

    if not test_cases:
        print(f"ERROR: No test cases found for suite '{suite_name}'")
        return 2

    # Create the system under test
    system = create_claude_system(
        system_prompt="You are a helpful customer service agent.",
        model="claude-sonnet-4-20250514",
    )

    # Create scorers
    scorers: list[Scorer] = [
        LengthScorer(min_chars=20, max_chars=2000),
        ContainsScorer(["help"], case_sensitive=False),
        LLMJudgeScorer(LLMJudge(), pass_threshold=4),
    ]

    # Run evaluation
    harness = EvalHarness(suite_name, system, scorers, test_cases)
    result = harness.run(verbose=True)
    harness.print_report(result)

    # Save results for tracking
    results_dir = Path("eval_results")
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / f"{suite_name}_{result.run_timestamp}.json"
    with open(results_file, "w") as f:
        json.dump(result.to_dict(), f, indent=2)

    # Check for regressions
    tester = RegressionTester(Path(baseline_path))

    if update_baseline:
        tester.save_baseline(result)
        print(f"Baseline updated: {baseline_path}")
        return 0

    regression_result = tester.compare(result)
    print(regression_result.summary())

    if regression_result.overall_regression and fail_on_regression:
        print("\nCI FAILED: Regressions detected!")
        return 1

    print("\nCI PASSED: No regressions detected.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run eval suite in CI")
    parser.add_argument("--suite", required=True, help="Suite name")
    parser.add_argument("--baseline", default="baselines/default.json")
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args()

    exit_code = run_ci_eval(
        suite_name=args.suite,
        baseline_path=args.baseline,
        update_baseline=args.update_baseline,
        fail_on_regression=not args.no_fail,
    )
    sys.exit(exit_code)
```

**GitHub Actions integration:**

```yaml
# .github/workflows/eval.yml
name: LLM Evaluation

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'src/llm/**'
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run evaluation suite
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python run_evals.py \
            --suite customer-service \
            --baseline baselines/customer-service.json

      - name: Upload eval results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: eval_results/
```

> **Swift Developer Note:** This CI/CD setup is analogous to running `xcodebuild test`
> in a GitHub Action, but with a key difference: you are not just checking pass/fail,
> you are tracking score distributions over time. Think of it like performance testing
> in Xcode where you set baselines and detect deviations, but applied to output quality
> instead of execution time.

---

## 5. A/B Testing for AI Features

### When to A/B Test

A/B testing is essential when you need to make data-driven decisions about:
- Prompt changes (does the new system prompt produce better results?)
- Model upgrades (is Claude Sonnet 4 better than Sonnet 3.5 for your use case?)
- Architecture changes (does adding RAG improve accuracy?)
- Parameter tuning (is temperature 0.3 better than 0.7?)

### Statistical Framework

```python
import math
from dataclasses import dataclass
from scipy import stats
import numpy as np


@dataclass
class ABTestConfig:
    """Configuration for an A/B test."""
    name: str
    metric_name: str
    minimum_detectable_effect: float  # e.g., 0.05 for 5% improvement
    significance_level: float = 0.05  # alpha
    power: float = 0.80  # 1 - beta
    baseline_rate: float = 0.0  # current metric value

    @property
    def required_sample_size(self) -> int:
        """Calculate required sample size per variant using power analysis."""
        # For proportions (e.g., pass rate)
        if 0 < self.baseline_rate < 1:
            p1 = self.baseline_rate
            p2 = p1 + self.minimum_detectable_effect
            p_avg = (p1 + p2) / 2

            z_alpha = stats.norm.ppf(1 - self.significance_level / 2)
            z_beta = stats.norm.ppf(self.power)

            n = (
                (z_alpha * math.sqrt(2 * p_avg * (1 - p_avg))
                 + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))
                / (p2 - p1)
            ) ** 2
            return math.ceil(n)

        # For continuous metrics (e.g., score 1-5), use Cohen's d
        effect_size = self.minimum_detectable_effect
        z_alpha = stats.norm.ppf(1 - self.significance_level / 2)
        z_beta = stats.norm.ppf(self.power)
        n = ((z_alpha + z_beta) / effect_size) ** 2
        return math.ceil(n)


@dataclass
class ABTestResult:
    """Result of an A/B test comparison."""
    control_mean: float
    treatment_mean: float
    control_n: int
    treatment_n: int
    p_value: float
    confidence_interval: tuple[float, float]
    is_significant: bool
    effect_size: float
    winner: str  # "control", "treatment", or "no_difference"


class ABTester:
    """Framework for running A/B tests on LLM outputs."""

    def __init__(self, config: ABTestConfig):
        self.config = config

    def compare_scores(
        self,
        control_scores: list[float],
        treatment_scores: list[float],
    ) -> ABTestResult:
        """Compare two sets of scores using appropriate statistical test."""
        control = np.array(control_scores)
        treatment = np.array(treatment_scores)

        control_mean = float(np.mean(control))
        treatment_mean = float(np.mean(treatment))

        # Use Mann-Whitney U test (non-parametric, good for ordinal scores)
        statistic, p_value = stats.mannwhitneyu(
            control, treatment, alternative="two-sided"
        )

        # Also compute Welch's t-test for confidence interval
        t_stat, t_p_value = stats.ttest_ind(control, treatment, equal_var=False)

        # Confidence interval for the difference in means
        diff = treatment_mean - control_mean
        se = math.sqrt(
            np.var(control, ddof=1) / len(control)
            + np.var(treatment, ddof=1) / len(treatment)
        )
        z = stats.norm.ppf(1 - self.config.significance_level / 2)
        ci = (diff - z * se, diff + z * se)

        # Cohen's d effect size
        pooled_std = math.sqrt(
            (np.var(control, ddof=1) + np.var(treatment, ddof=1)) / 2
        )
        effect_size = diff / pooled_std if pooled_std > 0 else 0.0

        is_significant = p_value < self.config.significance_level

        if not is_significant:
            winner = "no_difference"
        elif treatment_mean > control_mean:
            winner = "treatment"
        else:
            winner = "control"

        return ABTestResult(
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_n=len(control),
            treatment_n=len(treatment),
            p_value=float(p_value),
            confidence_interval=ci,
            is_significant=is_significant,
            effect_size=float(effect_size),
            winner=winner,
        )

    def compare_pass_rates(
        self,
        control_passes: int,
        control_total: int,
        treatment_passes: int,
        treatment_total: int,
    ) -> ABTestResult:
        """Compare two pass rates using a chi-squared test."""
        table = np.array([
            [control_passes, control_total - control_passes],
            [treatment_passes, treatment_total - treatment_passes],
        ])
        chi2, p_value, dof, expected = stats.chi2_contingency(table)

        control_rate = control_passes / control_total
        treatment_rate = treatment_passes / treatment_total
        diff = treatment_rate - control_rate

        # Wilson score interval for the difference
        se = math.sqrt(
            control_rate * (1 - control_rate) / control_total
            + treatment_rate * (1 - treatment_rate) / treatment_total
        )
        z = stats.norm.ppf(1 - self.config.significance_level / 2)
        ci = (diff - z * se, diff + z * se)

        is_significant = p_value < self.config.significance_level

        return ABTestResult(
            control_mean=control_rate,
            treatment_mean=treatment_rate,
            control_n=control_total,
            treatment_n=treatment_total,
            p_value=float(p_value),
            confidence_interval=ci,
            is_significant=is_significant,
            effect_size=float(diff),
            winner=(
                "no_difference" if not is_significant
                else "treatment" if treatment_rate > control_rate
                else "control"
            ),
        )

    def print_report(self, result: ABTestResult) -> None:
        """Print a formatted A/B test report."""
        print(f"\n{'=' * 50}")
        print(f"A/B Test: {self.config.name}")
        print(f"Metric: {self.config.metric_name}")
        print(f"{'=' * 50}")
        print(f"Control:   {result.control_mean:.4f} (n={result.control_n})")
        print(f"Treatment: {result.treatment_mean:.4f} (n={result.treatment_n})")
        print(f"Effect:    {result.effect_size:+.4f}")
        print(f"p-value:   {result.p_value:.6f}")
        print(f"95% CI:    [{result.confidence_interval[0]:.4f}, "
              f"{result.confidence_interval[1]:.4f}]")
        print(f"Significant: {result.is_significant}")
        print(f"Winner:    {result.winner}")
        print(f"{'=' * 50}\n")
```

### Practical A/B Test Example

```python
# Compare two prompt versions
config = ABTestConfig(
    name="system-prompt-v2-vs-v1",
    metric_name="judge_score",
    minimum_detectable_effect=0.3,  # 0.3 points on 1-5 scale
    baseline_rate=0.0,  # continuous metric, not a rate
)

# Check required sample size
print(f"Required samples per variant: {config.required_sample_size}")

# Run both variants on the same test cases
system_v1 = create_claude_system("You are a helpful assistant.")
system_v2 = create_claude_system(
    "You are a helpful assistant. Always structure your response with "
    "clear sections. Be concise but thorough."
)

judge = LLMJudge()
test_inputs = [case.input_text for case in test_cases]

v1_scores = []
v2_scores = []
for input_text in test_inputs:
    output_v1 = system_v1(input_text)
    output_v2 = system_v2(input_text)
    verdict_v1 = judge.evaluate(input_text, output_v1)
    verdict_v2 = judge.evaluate(input_text, output_v2)
    v1_scores.append(verdict_v1.score)
    v2_scores.append(verdict_v2.score)

# Analyze results
tester = ABTester(config)
result = tester.compare_scores(v1_scores, v2_scores)
tester.print_report(result)
```

> **Swift Developer Note:** If you have used Xcode's performance testing with
> `measure { }` blocks, the concept is similar. Xcode compares your measurements
> against a baseline and flags deviations. A/B testing for LLMs extends this by
> adding formal statistical rigor -- you are not just eyeballing whether something
> is "faster," you are computing whether the difference is statistically significant.

---

## 6. Hallucination Detection

### Types of Hallucination

1. **Factual hallucination** -- States incorrect facts
2. **Fabrication** -- Invents entities, citations, or events that do not exist
3. **Contradiction** -- Contradicts the provided context or itself
4. **Extrapolation** -- Goes beyond what the source material supports

### Retrieval-Augmented Verification

The most reliable hallucination detection strategy grounds the LLM's claims against
retrieved source documents:

```python
from dataclasses import dataclass
from pydantic import BaseModel, Field


class ClaimVerification(BaseModel):
    """Verification result for a single claim."""
    claim: str
    supported: bool
    supporting_evidence: str | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_passage: str | None = None


class HallucinationReport(BaseModel):
    """Full hallucination analysis report."""
    total_claims: int
    verified_claims: int
    unsupported_claims: int
    hallucination_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="0.0 = no hallucination, 1.0 = completely hallucinated"
    )
    claims: list[ClaimVerification]
    summary: str


class HallucinationDetector:
    """Detect hallucinations by verifying claims against source documents."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model

    def extract_claims(self, text: str) -> list[str]:
        """Extract verifiable factual claims from text."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Extract all specific, verifiable factual claims from this text.
Return each claim on its own line, prefixed with "- ".
Only include factual statements, not opinions or subjective assessments.

Text:
{text}""",
            }],
        )
        raw = message.content[0].text
        claims = [
            line.lstrip("- ").strip()
            for line in raw.strip().split("\n")
            if line.strip().startswith("- ")
        ]
        return claims

    def verify_against_sources(
        self,
        response: str,
        source_documents: list[str],
    ) -> HallucinationReport:
        """Verify an LLM response against source documents."""
        claims = self.extract_claims(response)

        if not claims:
            return HallucinationReport(
                total_claims=0,
                verified_claims=0,
                unsupported_claims=0,
                hallucination_score=0.0,
                claims=[],
                summary="No verifiable claims found in the response.",
            )

        # Combine sources into a single context
        combined_sources = "\n\n---\n\n".join(
            f"Source {i + 1}:\n{doc}" for i, doc in enumerate(source_documents)
        )

        # Verify each claim against sources
        prompt = f"""You are a fact-checker. For each claim below, determine if it is
supported by the provided source documents.

## Source Documents
{combined_sources}

## Claims to Verify
{chr(10).join(f'{i + 1}. {claim}' for i, claim in enumerate(claims))}

For each claim, provide a JSON object with:
- claim: the claim text
- supported: true/false
- supporting_evidence: quote from sources if supported, null if not
- confidence: 0.0-1.0 confidence in your verification
- source_passage: the relevant source passage, or null

Return a JSON array of these objects."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = message.content[0].text
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0]

        verifications = [
            ClaimVerification.model_validate(v)
            for v in json.loads(raw_text)
        ]

        verified = sum(1 for v in verifications if v.supported)
        unsupported = len(verifications) - verified
        hallucination_score = unsupported / len(verifications) if verifications else 0.0

        return HallucinationReport(
            total_claims=len(verifications),
            verified_claims=verified,
            unsupported_claims=unsupported,
            hallucination_score=hallucination_score,
            claims=verifications,
            summary=(
                f"{verified}/{len(verifications)} claims verified. "
                f"Hallucination score: {hallucination_score:.1%}"
            ),
        )

    def check_self_consistency(
        self,
        question: str,
        num_samples: int = 5,
    ) -> dict[str, Any]:
        """
        Check for hallucination via self-consistency.

        Generate multiple responses and check agreement.
        Inconsistent answers suggest hallucination.
        """
        responses: list[str] = []
        for _ in range(num_samples):
            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                temperature=0.7,  # Some variation
                messages=[{"role": "user", "content": question}],
            )
            responses.append(message.content[0].text)

        # Use the LLM to assess consistency
        consistency_prompt = f"""Analyze these {num_samples} responses to the same
question for consistency. Identify claims that appear in all responses (consistent)
vs claims that vary (potentially hallucinated).

Question: {question}

{"".join(f"Response {i + 1}: {r}" + chr(10) + chr(10) for i, r in enumerate(responses))}

Return JSON:
{{
    "consistent_claims": ["claim1", "claim2"],
    "inconsistent_claims": ["claim3", "claim4"],
    "consistency_score": 0.0-1.0,
    "assessment": "brief summary"
}}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": consistency_prompt}],
        )

        raw = message.content[0].text
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]

        return json.loads(raw)
```

### Citation Verification

For RAG systems that produce citations, verify that citations actually support the claims:

```python
@dataclass
class CitationCheck:
    """Result of checking a single citation."""
    claim_text: str
    cited_source: str
    source_content: str
    supports_claim: bool
    explanation: str


class CitationVerifier:
    """Verify that citations in LLM output actually support the claims."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model

    def verify_citations(
        self,
        response_with_citations: str,
        source_map: dict[str, str],  # citation_id -> source_text
    ) -> list[CitationCheck]:
        """
        Verify each citation in the response.

        Args:
            response_with_citations: LLM response with [1], [2] style citations
            source_map: Mapping from citation ID to source text
        """
        prompt = f"""Analyze this response and identify each factual claim paired
with its citation. Then determine if the cited source actually supports the claim.

Response:
{response_with_citations}

Sources:
{json.dumps(source_map, indent=2)}

For each claim-citation pair, return JSON array:
[{{
    "claim_text": "the claim made",
    "cited_source": "citation ID",
    "supports_claim": true/false,
    "explanation": "why it does/doesn't support the claim"
}}]"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]

        results = json.loads(raw)
        return [
            CitationCheck(
                claim_text=r["claim_text"],
                cited_source=r["cited_source"],
                source_content=source_map.get(r["cited_source"], ""),
                supports_claim=r["supports_claim"],
                explanation=r["explanation"],
            )
            for r in results
        ]


# Integrate as a Scorer
class HallucinationScorer(Scorer):
    """Scorer that checks for hallucinations using source documents."""

    def __init__(self, detector: HallucinationDetector):
        self._detector = detector

    @property
    def name(self) -> str:
        return "hallucination"

    def score(
        self,
        input_text: str,
        output_text: str,
        expected_output: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ScoreResult:
        source_docs = (context or {}).get("source_documents", [])
        if not source_docs:
            return ScoreResult(
                name=self.name, score=0.5, passed=True,
                details={"warning": "No source documents for verification"},
            )

        report = self._detector.verify_against_sources(output_text, source_docs)
        grounded_score = 1.0 - report.hallucination_score

        return ScoreResult(
            name=self.name,
            score=grounded_score,
            passed=grounded_score >= 0.8,  # At least 80% grounded
            details={
                "total_claims": report.total_claims,
                "verified": report.verified_claims,
                "unsupported": report.unsupported_claims,
                "hallucination_score": report.hallucination_score,
            },
        )
```

> **Swift Developer Note:** Hallucination detection is somewhat like checking for
> memory corruption or data races in Swift -- you are looking for situations where
> the system produces outputs that are internally inconsistent or not grounded in
> reality. Just as Thread Sanitizer checks that your concurrent code does not access
> memory illegally, hallucination detectors check that your LLM does not access
> "facts" that do not exist.

---

## 7. Custom Metrics

### Domain-Specific Scoring

Different domains require specialized evaluation criteria. A legal AI needs to be
evaluated differently than a code generation tool or a medical chatbot.

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


# ── Domain-Specific Scorer Framework ─────────────────────────────────

class DomainMetric(ABC):
    """Base class for domain-specific metrics."""

    @property
    @abstractmethod
    def domain(self) -> str:
        ...

    @property
    @abstractmethod
    def metric_name(self) -> str:
        ...

    @property
    @abstractmethod
    def weight(self) -> float:
        """Relative weight for this metric (0.0-1.0)."""
        ...

    @abstractmethod
    def evaluate(self, output: str, context: dict[str, Any]) -> float:
        """Return a score from 0.0 to 1.0."""
        ...


# ── Legal Domain Metrics ─────────────────────────────────────────────

class LegalAccuracyMetric(DomainMetric):
    """Check if legal references and citations are accurate."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model

    @property
    def domain(self) -> str:
        return "legal"

    @property
    def metric_name(self) -> str:
        return "legal_accuracy"

    @property
    def weight(self) -> float:
        return 0.4

    def evaluate(self, output: str, context: dict[str, Any]) -> float:
        jurisdiction = context.get("jurisdiction", "US Federal")
        prompt = f"""As a legal expert, evaluate this legal response for accuracy.

Jurisdiction: {jurisdiction}

Response:
{output}

Score from 0.0 to 1.0 on:
- Correctness of legal citations
- Accuracy of legal principles stated
- Appropriate caveats and disclaimers
- Relevance to the jurisdiction

Return JSON: {{"score": float, "issues": [str]}}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        data = json.loads(raw)
        return float(data["score"])


class LegalDisclaimerMetric(DomainMetric):
    """Check that appropriate legal disclaimers are present."""

    REQUIRED_DISCLAIMERS = [
        "not legal advice",
        "consult a lawyer",
        "attorney",
        "qualified professional",
    ]

    @property
    def domain(self) -> str:
        return "legal"

    @property
    def metric_name(self) -> str:
        return "legal_disclaimer"

    @property
    def weight(self) -> float:
        return 0.2

    def evaluate(self, output: str, context: dict[str, Any]) -> float:
        output_lower = output.lower()
        found = sum(
            1 for d in self.REQUIRED_DISCLAIMERS if d in output_lower
        )
        return min(1.0, found / 2)  # Need at least 2 disclaimer phrases


# ── Code Correctness Metrics ────────────────────────────────────────

class CodeCorrectnessMetric(DomainMetric):
    """Evaluate generated code for correctness."""

    @property
    def domain(self) -> str:
        return "code"

    @property
    def metric_name(self) -> str:
        return "code_correctness"

    @property
    def weight(self) -> float:
        return 0.5

    def evaluate(self, output: str, context: dict[str, Any]) -> float:
        """
        Evaluate code by extracting it and running test cases.

        context should contain:
            - test_cases: list of {"input": ..., "expected_output": ...}
            - language: "python"
        """
        test_cases = context.get("test_cases", [])
        if not test_cases:
            return 0.5  # Cannot evaluate without test cases

        # Extract code blocks from the response
        code = self._extract_code(output)
        if not code:
            return 0.0

        # Run each test case in a sandboxed environment
        passed = 0
        for tc in test_cases:
            try:
                result = self._run_code_safely(
                    code, tc["input"], tc["expected_output"]
                )
                if result:
                    passed += 1
            except Exception:
                continue

        return passed / len(test_cases)

    def _extract_code(self, text: str) -> str:
        """Extract Python code from markdown code blocks."""
        if "```python" in text:
            return text.split("```python")[1].split("```")[0].strip()
        elif "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text.strip()

    def _run_code_safely(
        self,
        code: str,
        test_input: str,
        expected_output: str,
    ) -> bool:
        """Run code in a restricted environment and check output."""
        import subprocess
        import tempfile

        full_code = f"{code}\n\nprint({test_input})"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(full_code)
            f.flush()
            try:
                result = subprocess.run(
                    ["python3", f.name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.stdout.strip() == expected_output.strip()
            except (subprocess.TimeoutExpired, Exception):
                return False


# ── Medical Safety Metrics ───────────────────────────────────────────

class MedicalSafetyMetric(DomainMetric):
    """Ensure medical responses include appropriate safety measures."""

    DANGER_PHRASES = [
        "you should take",
        "I recommend taking",
        "the dosage is",
        "stop taking your medication",
        "you don't need to see a doctor",
    ]

    SAFETY_PHRASES = [
        "consult your doctor",
        "healthcare provider",
        "medical professional",
        "seek medical attention",
        "not a substitute for medical advice",
    ]

    @property
    def domain(self) -> str:
        return "medical"

    @property
    def metric_name(self) -> str:
        return "medical_safety"

    @property
    def weight(self) -> float:
        return 0.6  # Safety is heavily weighted

    def evaluate(self, output: str, context: dict[str, Any]) -> float:
        output_lower = output.lower()

        # Check for dangerous phrases (each one reduces score)
        danger_count = sum(
            1 for phrase in self.DANGER_PHRASES if phrase in output_lower
        )

        # Check for safety phrases (each one adds score)
        safety_count = sum(
            1 for phrase in self.SAFETY_PHRASES if phrase in output_lower
        )

        # Start at 1.0, subtract for dangers, require at least one safety phrase
        score = 1.0
        score -= danger_count * 0.3
        if safety_count == 0:
            score -= 0.4  # Penalty for no safety disclaimers
        score = max(0.0, min(1.0, score))

        return score


# ── Weighted Multi-Metric Evaluator ──────────────────────────────────

class WeightedEvaluator:
    """Combine multiple domain metrics with weights."""

    def __init__(self, metrics: list[DomainMetric]):
        self.metrics = metrics
        total_weight = sum(m.weight for m in metrics)
        # Normalize weights to sum to 1.0
        self._normalized_weights = {
            m.metric_name: m.weight / total_weight for m in metrics
        }

    def evaluate(self, output: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate output across all metrics and return weighted score."""
        results: dict[str, float] = {}
        weighted_sum = 0.0

        for metric in self.metrics:
            score = metric.evaluate(output, context)
            results[metric.metric_name] = score
            weighted_sum += score * self._normalized_weights[metric.metric_name]

        return {
            "individual_scores": results,
            "weights": self._normalized_weights,
            "weighted_score": weighted_sum,
            "passed": weighted_sum >= 0.7,
        }


# Usage for legal domain
legal_evaluator = WeightedEvaluator([
    LegalAccuracyMetric(),
    LegalDisclaimerMetric(),
])

result = legal_evaluator.evaluate(
    output="According to 42 USC 1983, you may have a civil rights claim. "
           "However, this is not legal advice and you should consult a "
           "qualified attorney in your jurisdiction.",
    context={"jurisdiction": "US Federal"},
)
print(f"Weighted score: {result['weighted_score']:.3f}")
print(f"Individual scores: {result['individual_scores']}")
```

### Turning Domain Metrics into Harness Scorers

```python
class DomainMetricScorer(Scorer):
    """Adapter that wraps a DomainMetric as a Scorer for the eval harness."""

    def __init__(self, metric: DomainMetric, pass_threshold: float = 0.7):
        self._metric = metric
        self._threshold = pass_threshold

    @property
    def name(self) -> str:
        return f"{self._metric.domain}_{self._metric.metric_name}"

    def score(
        self,
        input_text: str,
        output_text: str,
        expected_output: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ScoreResult:
        metric_score = self._metric.evaluate(output_text, context or {})
        return ScoreResult(
            name=self.name,
            score=metric_score,
            passed=metric_score >= self._threshold,
            details={
                "domain": self._metric.domain,
                "metric": self._metric.metric_name,
                "weight": self._metric.weight,
            },
        )
```

> **Swift Developer Note:** Domain-specific metrics are like custom
> `XCTAssert` helpers you might write in Swift -- `assertValidJSON()`,
> `assertAccessibilityCompliant()`, etc. The difference is that these
> produce continuous scores rather than binary pass/fail, and they can be
> weighted to reflect business priorities (safety > formatting, for instance).

---

## 8. Evaluation Infrastructure

### Storing and Tracking Results

Production evaluation systems need persistent storage, versioning, and trend analysis:

```python
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class EvalStore:
    """SQLite-backed storage for evaluation results."""

    def __init__(self, db_path: str | Path = "eval_results.db"):
        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS eval_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suite_name TEXT NOT NULL,
                    run_timestamp TEXT NOT NULL,
                    model_version TEXT,
                    prompt_version TEXT,
                    pass_rate REAL,
                    average_score REAL,
                    average_latency_ms REAL,
                    total_cases INTEGER,
                    config_json TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS eval_case_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    test_case_id TEXT NOT NULL,
                    input_text TEXT,
                    output_text TEXT,
                    expected_output TEXT,
                    average_score REAL,
                    passed BOOLEAN,
                    latency_ms REAL,
                    scores_json TEXT,
                    FOREIGN KEY (run_id) REFERENCES eval_runs(id)
                );

                CREATE INDEX IF NOT EXISTS idx_runs_suite
                    ON eval_runs(suite_name);
                CREATE INDEX IF NOT EXISTS idx_runs_timestamp
                    ON eval_runs(run_timestamp);
                CREATE INDEX IF NOT EXISTS idx_cases_run
                    ON eval_case_results(run_id);
            """)

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_run(
        self,
        suite_result: EvalSuiteResult,
        model_version: str = "",
        prompt_version: str = "",
    ) -> int:
        """Save an eval run and all case results. Returns the run ID."""
        with self._connection() as conn:
            cursor = conn.execute(
                """INSERT INTO eval_runs
                   (suite_name, run_timestamp, model_version, prompt_version,
                    pass_rate, average_score, average_latency_ms,
                    total_cases, config_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    suite_result.suite_name,
                    suite_result.run_timestamp,
                    model_version,
                    prompt_version,
                    suite_result.pass_rate,
                    suite_result.average_score,
                    suite_result.average_latency_ms,
                    len(suite_result.results),
                    json.dumps(suite_result.config),
                ),
            )
            run_id = cursor.lastrowid

            for r in suite_result.results:
                conn.execute(
                    """INSERT INTO eval_case_results
                       (run_id, test_case_id, input_text, output_text,
                        expected_output, average_score, passed,
                        latency_ms, scores_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        run_id,
                        r.test_case_id,
                        r.input_text,
                        r.output_text,
                        r.expected_output,
                        r.average_score,
                        r.passed,
                        r.latency_ms,
                        json.dumps([
                            {"name": s.name, "score": s.score,
                             "passed": s.passed, "details": s.details}
                            for s in r.scores
                        ]),
                    ),
                )

            return run_id

    def get_trend(
        self,
        suite_name: str,
        limit: int = 30,
    ) -> list[dict[str, Any]]:
        """Get score trend over time for a suite."""
        with self._connection() as conn:
            rows = conn.execute(
                """SELECT run_timestamp, pass_rate, average_score,
                          average_latency_ms, model_version, prompt_version
                   FROM eval_runs
                   WHERE suite_name = ?
                   ORDER BY run_timestamp DESC
                   LIMIT ?""",
                (suite_name, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_case_history(
        self,
        suite_name: str,
        test_case_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get score history for a specific test case."""
        with self._connection() as conn:
            rows = conn.execute(
                """SELECT r.run_timestamp, c.average_score, c.passed,
                          c.latency_ms, r.model_version
                   FROM eval_case_results c
                   JOIN eval_runs r ON c.run_id = r.id
                   WHERE r.suite_name = ? AND c.test_case_id = ?
                   ORDER BY r.run_timestamp DESC
                   LIMIT ?""",
                (suite_name, test_case_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def detect_quality_drops(
        self,
        suite_name: str,
        threshold: float = 0.1,
        window: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Detect significant quality drops by comparing
        the latest run against the moving average.
        """
        trend = self.get_trend(suite_name, limit=window + 1)
        if len(trend) < 2:
            return []

        latest = trend[0]
        previous = trend[1:]
        avg_score = sum(t["average_score"] for t in previous) / len(previous)

        alerts = []
        if latest["average_score"] < avg_score - threshold:
            alerts.append({
                "type": "quality_drop",
                "severity": "high" if latest["average_score"] < avg_score - 2 * threshold else "medium",
                "current_score": latest["average_score"],
                "moving_average": avg_score,
                "delta": latest["average_score"] - avg_score,
                "timestamp": latest["run_timestamp"],
            })

        avg_latency = sum(t["average_latency_ms"] for t in previous) / len(previous)
        if latest["average_latency_ms"] > avg_latency * 1.5:
            alerts.append({
                "type": "latency_spike",
                "severity": "medium",
                "current_latency_ms": latest["average_latency_ms"],
                "moving_average_ms": avg_latency,
                "timestamp": latest["run_timestamp"],
            })

        return alerts
```

### Building a Simple Dashboard

```python
class EvalDashboard:
    """Generate text-based evaluation dashboards."""

    def __init__(self, store: EvalStore):
        self.store = store

    def suite_overview(self, suite_name: str) -> str:
        """Generate a text dashboard for a suite."""
        trend = self.store.get_trend(suite_name, limit=10)
        if not trend:
            return f"No data for suite '{suite_name}'"

        lines = [
            f"\n{'=' * 70}",
            f"  EVALUATION DASHBOARD: {suite_name}",
            f"{'=' * 70}",
            "",
            "  Recent Runs (newest first):",
            f"  {'Timestamp':<22} {'Score':>7} {'Pass%':>7} {'Latency':>10} {'Model':<20}",
            f"  {'-' * 68}",
        ]

        for run in trend:
            lines.append(
                f"  {run['run_timestamp'][:19]:<22} "
                f"{run['average_score']:>6.3f} "
                f"{run['pass_rate'] * 100:>6.1f}% "
                f"{run['average_latency_ms']:>8.0f}ms "
                f"{(run['model_version'] or 'N/A'):<20}"
            )

        # Trend indicator
        if len(trend) >= 2:
            delta = trend[0]["average_score"] - trend[1]["average_score"]
            indicator = "IMPROVING" if delta > 0.01 else "DECLINING" if delta < -0.01 else "STABLE"
            lines.extend([
                "",
                f"  Trend: {indicator} (delta: {delta:+.3f})",
            ])

        # Alerts
        alerts = self.store.detect_quality_drops(suite_name)
        if alerts:
            lines.extend(["", "  ALERTS:"])
            for alert in alerts:
                lines.append(
                    f"    [{alert['severity'].upper()}] {alert['type']}: "
                    f"{alert.get('current_score', alert.get('current_latency_ms'))}"
                )

        lines.append(f"{'=' * 70}\n")
        return "\n".join(lines)


# Usage
store = EvalStore("my_evals.db")

# After running evals, save them
run_id = store.save_run(
    suite_result=result,  # from EvalHarness.run()
    model_version="claude-sonnet-4-20250514",
    prompt_version="v2.1",
)

# Check for quality issues
alerts = store.detect_quality_drops("customer-service")
if alerts:
    for alert in alerts:
        print(f"ALERT: {alert['type']} - {alert['severity']}")
        # In production: send to Slack, PagerDuty, etc.

# Generate dashboard
dashboard = EvalDashboard(store)
print(dashboard.suite_overview("customer-service"))
```

### Version Tracking

Track which combination of model + prompt + system configuration produced each result:

```python
from dataclasses import dataclass
import hashlib


@dataclass
class SystemVersion:
    """Track the full configuration of a system under test."""
    model: str
    system_prompt: str
    temperature: float
    max_tokens: int
    tools: list[str] = field(default_factory=list)
    rag_config: dict[str, Any] = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        """Generate a unique hash of this configuration."""
        content = json.dumps(
            {
                "model": self.model,
                "system_prompt": self.system_prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "tools": sorted(self.tools),
                "rag_config": self.rag_config,
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def diff(self, other: SystemVersion) -> dict[str, tuple[Any, Any]]:
        """Show what changed between two versions."""
        changes = {}
        if self.model != other.model:
            changes["model"] = (self.model, other.model)
        if self.system_prompt != other.system_prompt:
            changes["system_prompt"] = (
                self.system_prompt[:50] + "...",
                other.system_prompt[:50] + "...",
            )
        if self.temperature != other.temperature:
            changes["temperature"] = (self.temperature, other.temperature)
        if self.max_tokens != other.max_tokens:
            changes["max_tokens"] = (self.max_tokens, other.max_tokens)
        if set(self.tools) != set(other.tools):
            changes["tools"] = (self.tools, other.tools)
        return changes


# Track versions across eval runs
v1 = SystemVersion(
    model="claude-sonnet-4-20250514",
    system_prompt="You are a helpful assistant.",
    temperature=0.3,
    max_tokens=1024,
)

v2 = SystemVersion(
    model="claude-sonnet-4-20250514",
    system_prompt="You are a helpful assistant. Be concise and structured.",
    temperature=0.2,
    max_tokens=1024,
)

print(f"V1 fingerprint: {v1.fingerprint}")
print(f"V2 fingerprint: {v2.fingerprint}")
print(f"Changes: {v1.diff(v2)}")
```

> **Swift Developer Note:** This version tracking is conceptually similar to how Xcode
> tracks build settings and provisioning profiles. When a build breaks, you want to
> know exactly what changed. The `SystemVersion.fingerprint` serves the same purpose
> as a build configuration hash -- it lets you uniquely identify what was running
> when a particular eval result was produced.

---

## 9. Swift Comparison

### Testing Philosophy Differences

| Aspect | Swift (XCTest) | Python (AI Eval) |
|--------|---------------|------------------|
| **Determinism** | Expected: same input = same output | Expected: same input can yield different outputs |
| **Assertions** | Binary pass/fail (`XCTAssertEqual`) | Continuous scores (0.0 to 1.0) |
| **Test granularity** | Unit, integration, UI | Case-level, dimension-level, suite-level |
| **Baseline comparison** | Snapshot testing, performance baselines | Golden datasets, regression baselines |
| **CI integration** | `xcodebuild test` | Custom eval scripts with exit codes |
| **Flakiness handling** | Retry, quarantine | Score averaging, statistical significance |

### Mapping Concepts

```swift
// Swift XCTest
class CustomerServiceTests: XCTestCase {
    func testGreetingResponse() {
        let response = chatbot.respond(to: "Hello")
        XCTAssertTrue(response.contains("help"))
        XCTAssertTrue(response.count > 20)
        XCTAssertTrue(response.count < 500)
    }

    func testRefundPolicy() {
        let response = chatbot.respond(to: "I want a refund")
        XCTAssertTrue(response.contains("refund"))
        XCTAssertTrue(response.contains("policy"))
    }

    // Performance baseline
    func testResponseTime() {
        measure {
            _ = chatbot.respond(to: "Hello")
        }
    }
}
```

```python
# Python equivalent with eval harness
test_cases = [
    EvalTestCase(
        id="greeting",
        input_text="Hello",
        context={"expected_topics": ["help"]},
    ),
    EvalTestCase(
        id="refund",
        input_text="I want a refund",
        context={"expected_topics": ["refund", "policy"]},
    ),
]

scorers = [
    ContainsScorer(["help"]),
    LengthScorer(min_chars=20, max_chars=500),
    LLMJudgeScorer(LLMJudge(), pass_threshold=4),
]

harness = EvalHarness("customer-service", system, scorers, test_cases)
result = harness.run()
# Instead of binary pass/fail, we get:
# - Continuous scores per dimension
# - Aggregate statistics
# - Trend tracking over time
```

### Snapshot Testing Analogy

Swift developers are familiar with snapshot testing (comparing UI screenshots against
reference images). AI evaluation has a direct analogue:

```swift
// Swift: Snapshot test
func testLoginScreen() {
    let vc = LoginViewController()
    assertSnapshot(matching: vc, as: .image)
    // Compares rendered UI against stored reference image
    // Fails if pixel diff exceeds threshold
}
```

```python
# Python: "Semantic snapshot" test
# Instead of pixel comparison, we do semantic similarity comparison

class SemanticSnapshotScorer(Scorer):
    """Compare output semantics against a reference, like UI snapshot testing."""

    def __init__(self, similarity_threshold: float = 0.85):
        self._threshold = similarity_threshold
        self.client = anthropic.Anthropic()

    @property
    def name(self) -> str:
        return "semantic_snapshot"

    def score(
        self,
        input_text: str,
        output_text: str,
        expected_output: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ScoreResult:
        if expected_output is None:
            return ScoreResult(
                name=self.name, score=0.0, passed=False,
                details={"error": "No reference snapshot"},
            )

        # Use LLM to compute semantic similarity
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            messages=[{
                "role": "user",
                "content": f"""Rate the semantic similarity between these two texts
on a scale from 0.0 (completely different meaning) to 1.0 (same meaning).

Text A: {expected_output}
Text B: {output_text}

Return JSON: {{"similarity": float, "reasoning": str}}""",
            }],
        )
        raw = message.content[0].text
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        data = json.loads(raw)
        similarity = float(data["similarity"])

        return ScoreResult(
            name=self.name,
            score=similarity,
            passed=similarity >= self._threshold,
            details={
                "similarity": similarity,
                "threshold": self._threshold,
                "reasoning": data["reasoning"],
            },
        )
```

### Protocol-Oriented Design

Swift developers can bring their protocol-oriented instincts to Python eval code:

```swift
// Swift protocol approach
protocol Evaluator {
    associatedtype Input
    associatedtype Output
    func evaluate(input: Input, output: Output) -> EvalScore
}

protocol Scorer {
    var name: String { get }
    func score(input: String, output: String) -> Double
}
```

```python
# Python equivalent using ABC (Abstract Base Class)
# Already demonstrated throughout this lesson with the Scorer ABC

# The key mapping:
# Swift protocol    -> Python ABC
# associatedtype    -> Generic[T] or type parameters
# protocol extension -> ABC with default implementations
# protocol conformance -> class inheritance from ABC
```

> **Swift Developer Note:** The entire eval harness architecture maps well to
> Swift's protocol-oriented design. The `Scorer` ABC is a protocol. Each concrete
> scorer (`ExactMatchScorer`, `LLMJudgeScorer`, etc.) is a conformance. The
> `EvalHarness` composes scorers the way a SwiftUI view composes modifiers. If you
> are comfortable with `protocol Sequence` and its conformers, you will find this
> pattern immediately familiar.

---

## 10. Interview Focus

### How to Discuss Evaluation in SE Interviews

At companies like Anthropic, OpenAI, and Google, solutions engineer and applied AI
engineer interviews frequently test your understanding of evaluation. Here is how to
approach these discussions.

### Common Interview Questions

**Q: "A customer says the chatbot is giving bad answers. How do you investigate?"**

Strong answer structure:
1. Define "bad" -- collect specific examples (hallucination? wrong tone? incomplete?)
2. Build a targeted eval suite from the failure cases
3. Score against multiple dimensions (accuracy, relevance, safety)
4. Compare against a baseline to determine if this is a regression or a known gap
5. Propose specific fixes (prompt changes, guardrails, RAG improvements)
6. Set up ongoing monitoring to prevent recurrence

```python
# Demonstrate your investigation approach in code
def investigate_quality_issue(
    failure_examples: list[dict[str, str]],
    system: SystemUnderTest,
) -> dict[str, Any]:
    """Structured approach to investigating a quality complaint."""

    # Step 1: Convert customer examples to eval cases
    cases = [
        EvalTestCase(
            id=f"customer-issue-{i}",
            input_text=ex["input"],
            expected_output=ex.get("expected"),
            tags=["customer-reported"],
        )
        for i, ex in enumerate(failure_examples)
    ]

    # Step 2: Run multi-dimensional evaluation
    judge = LLMJudge()
    scorers = [
        LLMJudgeScorer(judge, pass_threshold=4),
        LengthScorer(min_chars=50, max_chars=2000),
    ]

    harness = EvalHarness("quality-investigation", system, scorers, cases)
    result = harness.run(verbose=True)

    # Step 3: Identify patterns in failures
    failures = result.failed_cases()
    failure_patterns = {}
    for f in failures:
        for s in f.scores:
            if not s.passed:
                failure_patterns.setdefault(s.name, []).append(f.test_case_id)

    # Step 4: Generate report
    return {
        "total_cases": len(cases),
        "failures": len(failures),
        "pass_rate": result.pass_rate,
        "failure_patterns": failure_patterns,
        "recommendation": _generate_recommendation(failure_patterns),
    }


def _generate_recommendation(patterns: dict[str, list[str]]) -> str:
    if "hallucination" in patterns:
        return "Add RAG grounding or fact-checking guardrails"
    if "llm_judge" in patterns:
        return "Review and iterate on system prompt"
    if "length" in patterns:
        return "Adjust length constraints in prompt or parameters"
    return "Collect more examples and run deeper analysis"
```

**Q: "How would you evaluate a RAG system?"**

Key dimensions to mention:
1. **Retrieval quality** -- Are the right documents being retrieved? (Precision/Recall)
2. **Faithfulness** -- Does the answer stick to retrieved content? (Hallucination score)
3. **Answer relevance** -- Does the answer address the question?
4. **Context relevance** -- Is the retrieved context relevant to the question?

```python
class RAGEvaluator:
    """Evaluate a RAG system across retrieval and generation dimensions."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model

    def evaluate(
        self,
        question: str,
        answer: str,
        retrieved_contexts: list[str],
        ground_truth: str | None = None,
    ) -> dict[str, float]:
        """Evaluate RAG output across standard dimensions."""
        scores = {}

        # 1. Faithfulness: Is the answer grounded in retrieved context?
        scores["faithfulness"] = self._score_faithfulness(
            answer, retrieved_contexts
        )

        # 2. Answer relevance: Does the answer address the question?
        scores["answer_relevance"] = self._score_relevance(question, answer)

        # 3. Context relevance: Is the retrieved context relevant?
        scores["context_relevance"] = self._score_context_relevance(
            question, retrieved_contexts
        )

        # 4. Correctness (if ground truth available)
        if ground_truth:
            scores["correctness"] = self._score_correctness(
                answer, ground_truth
            )

        return scores

    def _score_faithfulness(
        self, answer: str, contexts: list[str]
    ) -> float:
        combined = "\n---\n".join(contexts)
        prompt = f"""Score 0.0-1.0: Is this answer fully supported by the context?

Context: {combined}
Answer: {answer}

Return JSON: {{"score": float}}"""
        return self._get_score(prompt)

    def _score_relevance(self, question: str, answer: str) -> float:
        prompt = f"""Score 0.0-1.0: Does this answer directly address the question?

Question: {question}
Answer: {answer}

Return JSON: {{"score": float}}"""
        return self._get_score(prompt)

    def _score_context_relevance(
        self, question: str, contexts: list[str]
    ) -> float:
        combined = "\n---\n".join(contexts)
        prompt = f"""Score 0.0-1.0: Is this context relevant to the question?

Question: {question}
Context: {combined}

Return JSON: {{"score": float}}"""
        return self._get_score(prompt)

    def _score_correctness(
        self, answer: str, ground_truth: str
    ) -> float:
        prompt = f"""Score 0.0-1.0: How correct is this answer compared to ground truth?

Answer: {answer}
Ground Truth: {ground_truth}

Return JSON: {{"score": float}}"""
        return self._get_score(prompt)

    def _get_score(self, prompt: str) -> float:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=128,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        return float(json.loads(raw)["score"])
```

**Q: "How do you handle evaluation at scale?"**

Key points:
- Async execution for parallel test case evaluation
- Batch API calls to reduce latency and cost
- Sampling strategies (do not evaluate every production request)
- Cost management (use smaller models for routine evals, larger for critical ones)

```python
import asyncio
from typing import Sequence


class AsyncEvalHarness:
    """Evaluation harness that runs test cases concurrently."""

    def __init__(
        self,
        name: str,
        system: SystemUnderTest,
        scorers: list[Scorer],
        max_concurrency: int = 10,
    ):
        self.name = name
        self.system = system
        self.scorers = scorers
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def _run_single(self, case: EvalTestCase) -> EvalRunResult:
        async with self._semaphore:
            # Run in thread pool since system calls are blocking
            loop = asyncio.get_event_loop()
            start = time.perf_counter()
            output = await loop.run_in_executor(
                None, self.system, case.input_text
            )
            latency_ms = (time.perf_counter() - start) * 1000

            # Run scorers (also potentially blocking)
            scores = []
            for scorer in self.scorers:
                score = await loop.run_in_executor(
                    None,
                    scorer.score,
                    case.input_text,
                    output,
                    case.expected_output,
                    case.context,
                )
                scores.append(score)

            return EvalRunResult(
                test_case_id=case.id,
                input_text=case.input_text,
                output_text=output,
                expected_output=case.expected_output,
                scores=scores,
                latency_ms=latency_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

    async def run_async(
        self,
        test_cases: Sequence[EvalTestCase],
        verbose: bool = False,
    ) -> EvalSuiteResult:
        """Run all test cases concurrently with bounded parallelism."""
        if verbose:
            print(f"Running {len(test_cases)} cases with "
                  f"max concurrency {self._semaphore._value}...")

        tasks = [self._run_single(case) for case in test_cases]
        results = await asyncio.gather(*tasks)

        return EvalSuiteResult(
            suite_name=self.name,
            results=list(results),
            run_timestamp=datetime.now(timezone.utc).isoformat(),
        )


# Usage
async def main():
    harness = AsyncEvalHarness(
        name="customer-service-v1",
        system=create_claude_system("You are a helpful assistant."),
        scorers=[LengthScorer(min_chars=50, max_chars=2000)],
        max_concurrency=5,
    )
    result = await harness.run_async(test_cases, verbose=True)
    print(f"Pass rate: {result.pass_rate:.1%}")

asyncio.run(main())
```

### Interview Tips

1. **Always start with the business goal.** Before discussing metrics, ask what the
   customer cares about. A legal chatbot has different priorities than a creative
   writing assistant.

2. **Show you understand the cost-quality tradeoff.** Running LLM-as-judge on every
   test case is expensive. Mention strategies like sampling, tiered evaluation
   (cheap heuristics first, expensive LLM judge only when needed), and caching.

3. **Demonstrate systematic thinking.** Walk through the full evaluation lifecycle:
   define metrics, build test suite, run evals, analyze results, iterate, monitor.

4. **Know the limitations.** LLM-as-judge is not perfect. Be ready to discuss inter-
   annotator agreement, judge calibration, and when human evaluation is necessary.

5. **Reference real frameworks.** Mention tools like Braintrust, Langsmith, RAGAS,
   or custom harnesses. Show you know the ecosystem while being able to build from
   scratch.

6. **Talk about regression prevention.** CI/CD integration is a strong signal that
   you think about operationalizing AI systems, not just building demos.

### Sample Technical Exercise

A typical interview exercise might be: "Design an evaluation system for a customer
support chatbot that handles billing questions."

```python
# Complete solution demonstrating interview-level thinking

def design_billing_chatbot_eval() -> EvalHarness:
    """
    Interview exercise: Design eval system for billing support chatbot.

    Demonstrates:
    - Thoughtful test case design across difficulty levels
    - Multiple scoring dimensions reflecting business priorities
    - Domain-specific metrics
    - Practical scorer composition
    """

    # 1. Define test cases covering key scenarios
    test_cases = [
        # Easy: straightforward questions
        EvalTestCase(
            id="billing-easy-001",
            input_text="What is my current balance?",
            expected_output=None,
            tags=["billing", "easy", "balance"],
            context={
                "expected_behavior": "Ask for account identification",
                "source_documents": ["Agents must verify identity before "
                                     "sharing account details."],
            },
        ),
        # Medium: requires policy knowledge
        EvalTestCase(
            id="billing-medium-001",
            input_text="I was charged $50 but my plan is $30/month. Why?",
            expected_output=None,
            tags=["billing", "medium", "overcharge"],
            context={
                "expected_behavior": "Explain possible reasons "
                                     "(overage, plan change, proration)",
                "source_documents": ["Common causes of higher-than-expected "
                                     "charges include data overages, mid-cycle "
                                     "plan changes, and prorated charges."],
            },
        ),
        # Hard: emotional customer, complex scenario
        EvalTestCase(
            id="billing-hard-001",
            input_text="This is ridiculous! You've been overcharging me for "
                       "3 months and nobody will help. I want to cancel everything!",
            expected_output=None,
            tags=["billing", "hard", "escalation", "retention"],
            context={
                "expected_behavior": "De-escalate, empathize, offer to "
                                     "investigate, mention retention options",
            },
        ),
    ]

    # 2. Create system under test
    system = create_claude_system(
        system_prompt=(
            "You are a billing support agent for TechCo. Be empathetic, "
            "accurate, and solution-oriented. Always verify customer identity "
            "before sharing account details. Follow company policies."
        ),
    )

    # 3. Compose scorers reflecting business priorities
    scorers: list[Scorer] = [
        # Basic quality checks
        LengthScorer(min_chars=50, max_chars=1500),

        # Must-have content checks
        ContainsScorer(
            required_substrings=["account", "help"],
            case_sensitive=False,
        ),

        # LLM judge for nuanced quality
        LLMJudgeScorer(
            judge=LLMJudge(
                rubric="""Evaluate this billing support response on:
1. Empathy and tone (does it acknowledge the customer's frustration?)
2. Accuracy (does it follow billing policies?)
3. Actionability (does it offer concrete next steps?)
4. Safety (does it avoid sharing sensitive info without verification?)

Score 1-5 with detailed reasoning.""",
            ),
            pass_threshold=4,
        ),

        # Hallucination check against source documents
        HallucinationScorer(HallucinationDetector()),
    ]

    return EvalHarness(
        name="billing-chatbot-eval",
        system=system,
        scorers=scorers,
        test_cases=test_cases,
    )
```

---

## Summary

### Key Takeaways

1. **Evaluation is not optional** -- it is the foundation of trust in AI systems.
   Without it, you are shipping untested software.

2. **Build composable eval harnesses** -- the `Scorer` abstraction lets you mix
   rule-based checks, LLM judges, and domain-specific metrics freely.

3. **LLM-as-Judge is powerful but imperfect** -- use position debiasing, structured
   output, and calibration to improve reliability. Know when human evaluation is needed.

4. **Automate regression detection** -- golden datasets and CI/CD integration catch
   quality drops before they reach customers.

5. **Statistical rigor matters for A/B testing** -- do not eyeball results. Calculate
   sample sizes, use appropriate tests, and report confidence intervals.

6. **Hallucination detection requires grounding** -- verify claims against source
   documents, check self-consistency, and validate citations.

7. **Domain-specific metrics reflect business reality** -- legal accuracy, medical
   safety, and code correctness each require specialized evaluation criteria.

8. **Infrastructure enables iteration** -- store results, track versions, build
   dashboards, and alert on quality drops.

### What to Build Next

- Extend the eval harness with async batch processing
- Build a web dashboard using FastAPI + HTMX for real-time eval monitoring
- Implement embedding-based semantic similarity scoring
- Create a synthetic test case generator using LLMs
- Set up a complete CI/CD pipeline with GitHub Actions and eval gates

### Further Reading

- Anthropic's guide to evaluating AI systems
- OpenAI Evals framework (open source)
- RAGAS: Evaluation framework for RAG pipelines
- Braintrust: Production evaluation platform
- "Judging LLM-as-a-Judge" (research paper on judge reliability)
- Stanford HELM benchmark methodology
