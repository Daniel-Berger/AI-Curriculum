# Module 07: Technical Communication

Technical communication is not a soft skill -- it is a core engineering competency. At companies like Anthropic, OpenAI, and Google, solutions engineers spend as much time writing documentation, tutorials, and customer-facing guides as they do writing code. The ability to translate between business stakeholders and engineering teams, to produce documentation that developers actually want to read, and to present complex ideas clearly under pressure will differentiate you from candidates who can only code.

This module treats technical communication as an engineering discipline with repeatable patterns, testable outputs, and measurable quality.

---

## 1. Writing API Tutorials

An API tutorial is not a reference manual. A reference manual says "here is every parameter." A tutorial says "here is how to accomplish something meaningful, step by step." The distinction matters because developers reach for tutorials when they are trying to solve a problem, and they reach for reference docs when they already know what they are doing.

### The Anatomy of an Effective Tutorial

Every strong API tutorial follows a predictable arc:

1. **Context**: What will the reader build? Why does it matter?
2. **Prerequisites**: What must be installed, configured, or understood first?
3. **Minimal Working Example**: The simplest possible version that produces output.
4. **Progressive Enhancement**: Layer on complexity one concept at a time.
5. **Complete Example**: The full, production-aware version.
6. **Troubleshooting**: Common errors and how to resolve them.
7. **Next Steps**: Where to go from here.

### Tutorial Generator in Python

The following class demonstrates how to structure tutorial content programmatically. This pattern is useful when generating documentation from API schemas or when maintaining tutorials across multiple SDK versions.

```python
"""
tutorial_generator.py
Generates structured API tutorials from endpoint definitions.
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import textwrap


class Difficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class CodeSample:
    """A single code example within a tutorial step."""
    language: str
    code: str
    description: str
    expected_output: Optional[str] = None

    def render_markdown(self) -> str:
        lines = [f"**{self.description}**", ""]
        lines.append(f"```{self.language}")
        lines.append(textwrap.dedent(self.code).strip())
        lines.append("```")
        if self.expected_output:
            lines.append("")
            lines.append("**Expected output:**")
            lines.append("```")
            lines.append(self.expected_output.strip())
            lines.append("```")
        return "\n".join(lines)


@dataclass
class TutorialStep:
    """One step in a tutorial's progression."""
    title: str
    explanation: str
    code_sample: CodeSample
    difficulty: Difficulty = Difficulty.BEGINNER
    common_errors: list[str] = field(default_factory=list)

    def render_markdown(self) -> str:
        lines = [
            f"### {self.title}",
            "",
            self.explanation,
            "",
            self.code_sample.render_markdown(),
        ]
        if self.common_errors:
            lines.append("")
            lines.append("**Common errors at this step:**")
            for error in self.common_errors:
                lines.append(f"- {error}")
        return "\n".join(lines)


@dataclass
class Tutorial:
    """A complete API tutorial with progressive complexity."""
    title: str
    overview: str
    prerequisites: list[str]
    steps: list[TutorialStep]

    def render_markdown(self) -> str:
        lines = [f"# {self.title}", "", self.overview, ""]

        # Prerequisites section
        lines.append("## Prerequisites")
        lines.append("")
        for prereq in self.prerequisites:
            lines.append(f"- {prereq}")
        lines.append("")

        # Steps with progressive difficulty
        for i, step in enumerate(self.steps, 1):
            badge = f"[{step.difficulty.value}]"
            lines.append(f"## Step {i}: {step.title} {badge}")
            lines.append("")
            lines.append(step.explanation)
            lines.append("")
            lines.append(step.code_sample.render_markdown())
            if step.common_errors:
                lines.append("")
                lines.append("**Watch out for:**")
                for err in step.common_errors:
                    lines.append(f"- {err}")
            lines.append("")

        return "\n".join(lines)


# --- Build a tutorial for the Claude Messages API ---

tutorial = Tutorial(
    title="Getting Started with Claude Messages API",
    overview=(
        "In this tutorial you will send your first message to Claude, "
        "handle the response, and then add streaming, error handling, "
        "and conversation history."
    ),
    prerequisites=[
        "Python 3.10+",
        "An Anthropic API key (set as ANTHROPIC_API_KEY env var)",
        "`pip install anthropic`",
    ],
    steps=[
        TutorialStep(
            title="Send Your First Message",
            explanation="Start with the simplest possible call.",
            difficulty=Difficulty.BEGINNER,
            code_sample=CodeSample(
                language="python",
                code="""
                import anthropic

                client = anthropic.Anthropic()
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=256,
                    messages=[{"role": "user", "content": "Hello, Claude!"}],
                )
                print(response.content[0].text)
                """,
                description="Minimal Claude API call",
                expected_output="Hello! How can I help you today?",
            ),
            common_errors=[
                "AuthenticationError: Ensure ANTHROPIC_API_KEY is set",
                "NotFoundError: Check the model name string exactly",
            ],
        ),
        TutorialStep(
            title="Add Error Handling",
            explanation="Production code must handle API errors gracefully.",
            difficulty=Difficulty.INTERMEDIATE,
            code_sample=CodeSample(
                language="python",
                code="""
                import anthropic

                client = anthropic.Anthropic()
                try:
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=256,
                        messages=[{"role": "user", "content": "Summarize quantum computing."}],
                    )
                    print(response.content[0].text)
                except anthropic.AuthenticationError:
                    print("Invalid API key. Check ANTHROPIC_API_KEY.")
                except anthropic.RateLimitError:
                    print("Rate limited. Implement exponential backoff.")
                except anthropic.APIError as e:
                    print(f"API error: {e.status_code} - {e.message}")
                """,
                description="API call with structured error handling",
            ),
            common_errors=[
                "Catching base Exception hides real bugs -- catch specific errors",
                "Forgetting to handle RateLimitError in production",
            ],
        ),
        TutorialStep(
            title="Stream the Response",
            explanation="Streaming lets you display tokens as they arrive.",
            difficulty=Difficulty.ADVANCED,
            code_sample=CodeSample(
                language="python",
                code="""
                import anthropic

                client = anthropic.Anthropic()
                with client.messages.stream(
                    model="claude-sonnet-4-20250514",
                    max_tokens=512,
                    messages=[{"role": "user", "content": "Explain transformers."}],
                ) as stream:
                    for text in stream.text_stream:
                        print(text, end="", flush=True)
                print()  # final newline
                """,
                description="Streaming response with real-time output",
            ),
            common_errors=[
                "Using .create() instead of .stream() for streaming",
                "Forgetting flush=True causes buffered output",
            ],
        ),
    ],
)

# Generate the tutorial as Markdown
print(tutorial.render_markdown())
```

### Common Mistakes in API Tutorials

| Mistake | Why It Hurts | Fix |
|---------|-------------|-----|
| Skipping prerequisites | Reader fails at step 1 and leaves | List exact versions and install commands |
| Non-runnable code | Copy-paste fails, trust is lost | Test every sample in a clean environment |
| Giant first example | Overwhelms the reader | Start with 5-10 lines, then build up |
| No expected output | Reader cannot verify success | Show what they should see |
| Outdated model names | Code throws NotFoundError | Use a variable or constant for model IDs |
| Missing error handling | Works in demo, breaks in production | Show at least one error-handling pattern |

> **Swift Developer Note:** Apple's documentation follows a similar progressive pattern: WWDC sessions start with the simplest SwiftUI view, then layer on modifiers and state. The "Getting Started with SwiftUI" guide is an exemplar of this structure. The difference in AI API docs is that you must also cover authentication, rate limits, and cost -- concerns that do not exist in local Swift development.

---

## 2. Code Sample Best Practices

Code samples are the single most-read part of any developer documentation. Research from Google's developer relations team shows that developers look at code first, then read the surrounding text only when the code does not make sense on its own.

### The Five Rules of Code Samples

1. **Self-contained**: A developer should be able to copy the sample, paste it into a file, and run it with no modification other than inserting their API key.
2. **Error-aware**: Samples should show what happens when things go wrong.
3. **Idiomatic**: Follow the conventions of the target language. Python samples should be Pythonic. Do not write Java-in-Python.
4. **Versioned**: Pin dependency versions. An unversioned sample is a ticking time bomb.
5. **Annotated**: Use comments to explain the "why," not the "what."

### Self-Contained Sample Template

```python
"""
self_contained_sample.py
Demonstrates a fully self-contained code sample pattern.

Requirements:
    pip install anthropic==0.39.0 httpx==0.27.0

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python self_contained_sample.py
"""

import os
import sys

# --- Dependency check ---
try:
    import anthropic
except ImportError:
    print("Missing dependency. Install with: pip install anthropic==0.39.0")
    sys.exit(1)

# --- Configuration ---
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    print("Error: Set the ANTHROPIC_API_KEY environment variable.")
    print("  export ANTHROPIC_API_KEY='sk-ant-...'")
    sys.exit(1)

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 256


def summarize(text: str) -> str:
    """Send text to Claude and return a summary.

    Args:
        text: The content to summarize.

    Returns:
        A one-paragraph summary from Claude.

    Raises:
        anthropic.APIError: If the API call fails.
    """
    client = anthropic.Anthropic(api_key=API_KEY)
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": f"Summarize this in one paragraph:\n\n{text}",
            }
        ],
    )
    return response.content[0].text


# --- Main ---
if __name__ == "__main__":
    sample_text = (
        "Large language models are neural networks trained on vast amounts "
        "of text data. They learn statistical patterns in language and can "
        "generate coherent text, answer questions, write code, and perform "
        "many other language tasks. The transformer architecture, introduced "
        "in 2017, is the foundation for most modern LLMs."
    )

    try:
        result = summarize(sample_text)
        print("Summary:")
        print(result)
    except anthropic.RateLimitError:
        print("Rate limited. Wait a moment and try again.")
    except anthropic.APIError as e:
        print(f"API error ({e.status_code}): {e.message}")
```

### Code Sample Validation Script

In a documentation pipeline, you want to automatically verify that every code sample in your docs actually runs. Here is a lightweight validator.

```python
"""
sample_validator.py
Extracts and validates Python code blocks from Markdown files.
"""

import re
import subprocess
import tempfile
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationResult:
    file: str
    block_index: int
    passed: bool
    error: Optional[str] = None  # type: ignore[name-defined]

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        msg = f"[{status}] {self.file} block #{self.block_index}"
        if self.error:
            msg += f"\n  Error: {self.error}"
        return msg


# Fix the Optional import
from typing import Optional  # noqa: E402


@dataclass
class ValidationResult:
    file: str
    block_index: int
    passed: bool
    error: Optional[str] = None

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        msg = f"[{status}] {self.file} block #{self.block_index}"
        if self.error:
            msg += f"\n  Error: {self.error}"
        return msg


def extract_python_blocks(markdown_text: str) -> list[str]:
    """Extract all ```python ... ``` code blocks from Markdown."""
    pattern = r"```python\n(.*?)```"
    return re.findall(pattern, markdown_text, re.DOTALL)


def validate_syntax(code: str) -> Optional[str]:
    """Check if code has valid Python syntax. Returns error or None."""
    try:
        compile(code, "<sample>", "exec")
        return None
    except SyntaxError as e:
        return f"Line {e.lineno}: {e.msg}"


def validate_execution(code: str, timeout: int = 10) -> Optional[str]:
    """Attempt to run the code in a subprocess. Returns error or None."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                return result.stderr.strip().split("\n")[-1]
            return None
        except subprocess.TimeoutExpired:
            return "Execution timed out"
        finally:
            Path(f.name).unlink(missing_ok=True)


def validate_markdown_file(
    filepath: str,
    syntax_only: bool = True,
) -> list[ValidationResult]:
    """Validate all Python code blocks in a Markdown file.

    Args:
        filepath: Path to the Markdown file.
        syntax_only: If True, only check syntax. If False, also run code.

    Returns:
        List of validation results for each code block.
    """
    text = Path(filepath).read_text()
    blocks = extract_python_blocks(text)
    results = []

    for i, block in enumerate(blocks):
        # Always check syntax
        syntax_error = validate_syntax(block)
        if syntax_error:
            results.append(ValidationResult(
                file=filepath, block_index=i,
                passed=False, error=f"Syntax: {syntax_error}",
            ))
            continue

        # Optionally run the code
        if not syntax_only:
            exec_error = validate_execution(block)
            if exec_error:
                results.append(ValidationResult(
                    file=filepath, block_index=i,
                    passed=False, error=f"Runtime: {exec_error}",
                ))
                continue

        results.append(ValidationResult(
            file=filepath, block_index=i, passed=True,
        ))

    return results


# Usage
if __name__ == "__main__":
    import glob

    md_files = glob.glob("docs/**/*.md", recursive=True)
    total_pass = 0
    total_fail = 0

    for md_file in md_files:
        results = validate_markdown_file(md_file, syntax_only=True)
        for r in results:
            print(r)
            if r.passed:
                total_pass += 1
            else:
                total_fail += 1

    print(f"\nResults: {total_pass} passed, {total_fail} failed")
    sys.exit(1 if total_fail > 0 else 0)
```

### Versioning Your Samples

```python
"""
versioned_samples.py
Demonstrates how to maintain code samples across SDK versions.
"""

from dataclasses import dataclass


@dataclass
class VersionedSample:
    """A code sample that adapts to different SDK versions."""
    sdk_version: str
    code: str
    deprecation_note: str = ""


# Maintain a registry of samples per SDK version
CHAT_COMPLETION_SAMPLES: dict[str, VersionedSample] = {
    "v0.25": VersionedSample(
        sdk_version="0.25.x",
        code="""
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(message.content[0].text)
""",
        deprecation_note="claude-3-sonnet-20240229 is deprecated. Use claude-sonnet-4-20250514.",
    ),
    "v0.39": VersionedSample(
        sdk_version="0.39.x",
        code="""
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(message.content[0].text)
""",
    ),
}


def get_sample_for_version(version_prefix: str) -> VersionedSample:
    """Return the appropriate sample for a given SDK version."""
    if version_prefix in CHAT_COMPLETION_SAMPLES:
        sample = CHAT_COMPLETION_SAMPLES[version_prefix]
        if sample.deprecation_note:
            print(f"WARNING: {sample.deprecation_note}")
        return sample

    # Fall back to the latest version
    latest_key = max(CHAT_COMPLETION_SAMPLES.keys())
    return CHAT_COMPLETION_SAMPLES[latest_key]
```

> **Swift Developer Note:** Apple's sample code projects are the gold standard for self-contained examples -- you download an Xcode project that builds and runs immediately. In the Python/API world, the equivalent is a single file with a `requirements.txt` or inline dependency check. The key principle is the same: minimize time-to-working-code. Where Swift uses Xcode's managed dependencies, Python samples should pin exact versions with `pip install package==x.y.z`.

---

## 3. Business-to-Technical Translation

Solutions engineers sit at the boundary between customers who speak in business outcomes and engineering teams who speak in system specifications. The ability to translate between these two worlds is the most consistently tested skill in SE interviews.

### The Translation Framework

```
Business Language          Translation Layer         Technical Specification
-----------------         -----------------         ----------------------
"We need it faster"   ->  What latency target?  ->  P95 < 200ms
"It needs to scale"   ->  To what volume?       ->  10K requests/minute
"Make it smarter"     ->  What metric improves? ->  Accuracy > 95% on eval set
"It keeps breaking"   ->  What errors occur?    ->  Retry logic + circuit breaker
"Too expensive"       ->  What's the budget?    ->  < $0.02 per request
```

### Requirements Translator

```python
"""
requirements_translator.py
Converts business requirements into technical specifications.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Priority(Enum):
    CRITICAL = "P0"
    HIGH = "P1"
    MEDIUM = "P2"
    LOW = "P3"


@dataclass
class BusinessRequirement:
    """What the customer says they need."""
    statement: str
    stakeholder: str
    context: str = ""


@dataclass
class TechnicalSpec:
    """What the engineering team needs to build."""
    requirement: str
    acceptance_criteria: list[str]
    metrics: dict[str, str]  # metric_name -> target_value
    constraints: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    estimated_effort: str = ""


@dataclass
class TranslatedRequirement:
    """A business requirement paired with its technical translation."""
    business: BusinessRequirement
    technical: TechnicalSpec
    priority: Priority
    questions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


# --- Common translation patterns ---

TRANSLATION_PATTERNS: dict[str, dict] = {
    "faster": {
        "questions": [
            "What is the current latency (P50, P95, P99)?",
            "What is the target latency?",
            "Is this about throughput or individual request speed?",
            "Are there specific endpoints that are slow?",
        ],
        "typical_specs": {
            "metrics": {"p95_latency_ms": "<200", "p99_latency_ms": "<500"},
            "approaches": [
                "Response caching",
                "Model size reduction (Sonnet -> Haiku)",
                "Streaming responses",
                "Async processing for non-blocking tasks",
            ],
        },
    },
    "cheaper": {
        "questions": [
            "What is the current cost per request / per month?",
            "What is the target budget?",
            "Are there requests that could use a smaller model?",
            "Can any responses be cached?",
        ],
        "typical_specs": {
            "metrics": {"cost_per_request": "<$0.01", "monthly_budget": "<$5000"},
            "approaches": [
                "Tiered model routing (Haiku for simple, Sonnet for complex)",
                "Prompt optimization to reduce token count",
                "Response caching for repeated queries",
                "Batch processing for non-real-time tasks",
            ],
        },
    },
    "accurate": {
        "questions": [
            "How is accuracy currently measured?",
            "What is the current accuracy score?",
            "What types of errors are most costly?",
            "Is there a labeled evaluation dataset?",
        ],
        "typical_specs": {
            "metrics": {"accuracy": ">95%", "hallucination_rate": "<2%"},
            "approaches": [
                "RAG with curated knowledge base",
                "Evaluation pipeline with human review",
                "Prompt engineering with few-shot examples",
                "Fine-tuning on domain-specific data",
            ],
        },
    },
    "scale": {
        "questions": [
            "What is the current request volume?",
            "What is the target volume and by when?",
            "Are there traffic spikes (e.g., marketing campaigns)?",
            "What is the acceptable degradation under load?",
        ],
        "typical_specs": {
            "metrics": {
                "requests_per_minute": "10000",
                "concurrent_users": "5000",
            },
            "approaches": [
                "Horizontal scaling with load balancer",
                "Request queuing with priority lanes",
                "Rate limiting per customer tier",
                "Auto-scaling based on queue depth",
            ],
        },
    },
}


def translate_requirement(
    business_req: BusinessRequirement,
) -> TranslatedRequirement:
    """Translate a business requirement into a technical specification.

    This is a simplified pattern matcher. In practice, you would conduct
    a discovery conversation with the customer to fill in the gaps.
    """
    statement_lower = business_req.statement.lower()

    # Match against known patterns
    matched_pattern = None
    for keyword, pattern in TRANSLATION_PATTERNS.items():
        if keyword in statement_lower:
            matched_pattern = pattern
            break

    if matched_pattern is None:
        return TranslatedRequirement(
            business=business_req,
            technical=TechnicalSpec(
                requirement="Needs discovery conversation",
                acceptance_criteria=["TBD after discovery"],
                metrics={},
            ),
            priority=Priority.MEDIUM,
            questions=[
                "Can you describe the specific behavior you want?",
                "What does success look like for this feature?",
                "What is the timeline for delivery?",
            ],
        )

    return TranslatedRequirement(
        business=business_req,
        technical=TechnicalSpec(
            requirement=f"Address: {business_req.statement}",
            acceptance_criteria=[
                f"{k} {v}" for k, v in matched_pattern["typical_specs"]["metrics"].items()
            ],
            metrics=matched_pattern["typical_specs"]["metrics"],
            constraints=[],
            dependencies=[],
        ),
        priority=Priority.HIGH,
        questions=matched_pattern["questions"],
        assumptions=[
            "Metrics targets are initial estimates pending discovery",
            "Approaches listed are options, not commitments",
        ],
    )


# --- Example usage ---

req = BusinessRequirement(
    statement="Our chatbot is too slow, customers are complaining",
    stakeholder="VP of Customer Success",
    context="E-commerce support chatbot, 500 requests/min peak",
)

translated = translate_requirement(req)
print(f"Business: {translated.business.statement}")
print(f"Priority: {translated.priority.value}")
print(f"Technical: {translated.technical.requirement}")
print(f"Acceptance criteria: {translated.technical.acceptance_criteria}")
print(f"\nQuestions to ask the customer:")
for q in translated.questions:
    print(f"  - {q}")
```

### Speaking Both Languages

The key skill is knowing when to use which language:

| Audience | Language | Example |
|----------|----------|---------|
| C-suite executive | Business outcomes | "This reduces support costs by 40%" |
| Product manager | Features and timelines | "We can ship RAG search in 3 sprints" |
| Engineering lead | Architecture and tradeoffs | "We trade 50ms latency for 10x cache hit rate" |
| Individual developer | Code and APIs | "Use `client.messages.stream()` for real-time output" |

### Stakeholder Communication Template

```python
"""
stakeholder_update.py
Generate audience-appropriate status updates from a single source of truth.
"""

from dataclasses import dataclass
from enum import Enum


class Audience(Enum):
    EXECUTIVE = "executive"
    PRODUCT = "product"
    ENGINEERING = "engineering"
    CUSTOMER = "customer"


@dataclass
class ProjectStatus:
    """Single source of truth for project state."""
    project_name: str
    status: str  # on_track, at_risk, blocked
    completion_pct: int
    current_milestone: str
    blockers: list[str]
    technical_details: str
    business_impact: str
    next_steps: list[str]
    metrics: dict[str, str]


def generate_update(status: ProjectStatus, audience: Audience) -> str:
    """Generate an audience-appropriate status update."""

    if audience == Audience.EXECUTIVE:
        # Short, outcome-focused, no jargon
        lines = [
            f"**{status.project_name}** - {status.status.replace('_', ' ').title()}",
            "",
            f"**Impact:** {status.business_impact}",
            f"**Progress:** {status.completion_pct}% complete",
        ]
        if status.blockers:
            lines.append(f"**Needs attention:** {status.blockers[0]}")
        return "\n".join(lines)

    elif audience == Audience.PRODUCT:
        # Feature-focused, timeline-aware
        lines = [
            f"## {status.project_name}",
            f"**Status:** {status.status} | **Progress:** {status.completion_pct}%",
            f"**Current milestone:** {status.current_milestone}",
            "",
            "**Key metrics:**",
        ]
        for metric, value in status.metrics.items():
            lines.append(f"- {metric}: {value}")
        lines.append("")
        lines.append("**Next steps:**")
        for step in status.next_steps:
            lines.append(f"- {step}")
        return "\n".join(lines)

    elif audience == Audience.ENGINEERING:
        # Technical details, architecture decisions, blockers
        lines = [
            f"## {status.project_name}",
            f"Status: {status.status} ({status.completion_pct}%)",
            "",
            f"**Technical details:** {status.technical_details}",
            "",
            "**Blockers:**",
        ]
        for blocker in status.blockers:
            lines.append(f"- [ ] {blocker}")
        lines.append("")
        lines.append("**Metrics:**")
        for metric, value in status.metrics.items():
            lines.append(f"- `{metric}`: {value}")
        return "\n".join(lines)

    elif audience == Audience.CUSTOMER:
        # Reassuring, non-technical, focused on their experience
        lines = [
            f"**Update on {status.project_name}**",
            "",
            f"We are making strong progress ({status.completion_pct}% complete).",
            f"Current focus: {status.current_milestone}.",
            "",
            "**What this means for you:**",
            status.business_impact,
            "",
            "**Next steps:**",
        ]
        # Only share customer-relevant next steps
        for step in status.next_steps[:2]:
            lines.append(f"- {step}")
        return "\n".join(lines)

    return "Unknown audience type"


# --- Example ---

status = ProjectStatus(
    project_name="RAG Pipeline Integration",
    status="on_track",
    completion_pct=65,
    current_milestone="Vector store migration to Pinecone",
    blockers=["Waiting on customer to provide evaluation dataset"],
    technical_details=(
        "Migrated from FAISS to Pinecone serverless. Embedding model "
        "switched from all-MiniLM-L6 to text-embedding-3-large. Chunk "
        "size optimized from 512 to 384 tokens after eval showed 8% "
        "recall improvement."
    ),
    business_impact="Search accuracy improved from 78% to 91% on test queries",
    next_steps=[
        "Complete Pinecone migration by Friday",
        "Run evaluation on customer dataset",
        "Performance benchmark under production load",
        "Update API documentation for new endpoints",
    ],
    metrics={
        "retrieval_accuracy": "91%",
        "p95_latency": "180ms",
        "index_size": "2.1M vectors",
        "cost_per_query": "$0.003",
    },
)

for audience in Audience:
    print(f"\n{'='*60}")
    print(f"  {audience.value.upper()} UPDATE")
    print(f"{'='*60}")
    print(generate_update(status, audience))
```

> **Swift Developer Note:** In the iOS world, the equivalent of business-to-technical translation is converting a designer's Figma mockup into UIKit constraints or SwiftUI layouts. You learned to ask "what happens on smaller screens?" and "what if the text is very long?" The same instinct applies here: when a customer says "make it faster," you ask "faster for whom, measured how, and at what cost?"

---

## 4. Migration Guides

Migration guides are among the highest-stakes documents a solutions engineer writes. A bad migration guide means customers stay on the old version (creating support burden), switch to a competitor, or attempt the migration and break their production systems.

### Migration Guide Structure

Every migration guide needs these sections:

1. **Why Migrate**: What benefits does the new version offer?
2. **What Changed**: Exhaustive list of breaking changes.
3. **Migration Path**: Step-by-step upgrade instructions.
4. **Compatibility Matrix**: What works with what.
5. **Rollback Plan**: How to undo the migration if something breaks.
6. **Timeline**: Deprecation dates and support windows.

### Migration Diff Generator

```python
"""
migration_guide.py
Tools for generating migration guides between API versions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ChangeType(Enum):
    BREAKING = "breaking"
    DEPRECATION = "deprecation"
    NEW_FEATURE = "new_feature"
    BEHAVIOR_CHANGE = "behavior_change"


@dataclass
class APIChange:
    """A single change between API versions."""
    change_type: ChangeType
    area: str  # e.g., "authentication", "endpoints", "parameters"
    description: str
    old_code: str
    new_code: str
    migration_notes: str = ""

    def render_markdown(self) -> str:
        badge = {
            ChangeType.BREAKING: "BREAKING",
            ChangeType.DEPRECATION: "DEPRECATED",
            ChangeType.NEW_FEATURE: "NEW",
            ChangeType.BEHAVIOR_CHANGE: "CHANGED",
        }[self.change_type]

        lines = [
            f"#### [{badge}] {self.area}: {self.description}",
            "",
            "**Before:**",
            "```python",
            self.old_code.strip(),
            "```",
            "",
            "**After:**",
            "```python",
            self.new_code.strip(),
            "```",
        ]
        if self.migration_notes:
            lines.extend(["", f"> **Note:** {self.migration_notes}"])
        return "\n".join(lines)


@dataclass
class MigrationGuide:
    """A complete migration guide between two API versions."""
    from_version: str
    to_version: str
    changes: list[APIChange]
    deprecation_date: Optional[str] = None
    sunset_date: Optional[str] = None

    @property
    def breaking_changes(self) -> list[APIChange]:
        return [c for c in self.changes if c.change_type == ChangeType.BREAKING]

    @property
    def deprecations(self) -> list[APIChange]:
        return [c for c in self.changes if c.change_type == ChangeType.DEPRECATION]

    def render_markdown(self) -> str:
        lines = [
            f"# Migration Guide: v{self.from_version} to v{self.to_version}",
            "",
        ]

        # Timeline
        if self.deprecation_date or self.sunset_date:
            lines.append("## Timeline")
            lines.append("")
            if self.deprecation_date:
                lines.append(
                    f"- **Deprecation date:** {self.deprecation_date} "
                    f"(v{self.from_version} enters maintenance mode)"
                )
            if self.sunset_date:
                lines.append(
                    f"- **Sunset date:** {self.sunset_date} "
                    f"(v{self.from_version} will stop working)"
                )
            lines.append("")

        # Summary
        n_breaking = len(self.breaking_changes)
        n_deprecations = len(self.deprecations)
        lines.append("## Summary")
        lines.append("")
        lines.append(
            f"This migration involves **{n_breaking} breaking change(s)** "
            f"and **{n_deprecations} deprecation(s)**."
        )
        lines.append("")

        # Breaking changes first (most important)
        if self.breaking_changes:
            lines.append("## Breaking Changes")
            lines.append("")
            lines.append("These changes **will break your code** if not addressed.")
            lines.append("")
            for change in self.breaking_changes:
                lines.append(change.render_markdown())
                lines.append("")

        # Then deprecations
        if self.deprecations:
            lines.append("## Deprecations")
            lines.append("")
            lines.append("These still work but will be removed in a future version.")
            lines.append("")
            for change in self.deprecations:
                lines.append(change.render_markdown())
                lines.append("")

        # Other changes
        other = [
            c for c in self.changes
            if c.change_type not in (ChangeType.BREAKING, ChangeType.DEPRECATION)
        ]
        if other:
            lines.append("## Other Changes")
            lines.append("")
            for change in other:
                lines.append(change.render_markdown())
                lines.append("")

        return "\n".join(lines)


# --- Example: OpenAI to Anthropic migration ---

provider_migration = MigrationGuide(
    from_version="openai-1.x",
    to_version="anthropic-0.39.x",
    changes=[
        APIChange(
            change_type=ChangeType.BREAKING,
            area="Client Initialization",
            description="Different client class and environment variable",
            old_code="""
from openai import OpenAI

client = OpenAI()  # uses OPENAI_API_KEY
""",
            new_code="""
import anthropic

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY
""",
            migration_notes="Set ANTHROPIC_API_KEY in your environment.",
        ),
        APIChange(
            change_type=ChangeType.BREAKING,
            area="Chat Completions",
            description="Different method name and response structure",
            old_code="""
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
)
text = response.choices[0].message.content
""",
            new_code="""
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,  # required in Anthropic API
    messages=[{"role": "user", "content": "Hello"}],
)
text = response.content[0].text
""",
            migration_notes=(
                "Anthropic requires max_tokens. Response uses .content[0].text "
                "instead of .choices[0].message.content."
            ),
        ),
        APIChange(
            change_type=ChangeType.BREAKING,
            area="System Prompt",
            description="System prompt is a top-level parameter, not a message",
            old_code="""
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"},
    ],
)
""",
            new_code="""
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "Hello"},
    ],
)
""",
            migration_notes=(
                "In the Anthropic API, system is a top-level parameter, not "
                "a message in the messages array. Do not include a message "
                "with role='system'."
            ),
        ),
        APIChange(
            change_type=ChangeType.BREAKING,
            area="Streaming",
            description="Different streaming interface",
            old_code="""
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
""",
            new_code="""
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
""",
            migration_notes=(
                "Anthropic uses a context manager for streaming. The "
                "stream.text_stream iterator yields text strings directly "
                "instead of chunk objects."
            ),
        ),
        APIChange(
            change_type=ChangeType.BEHAVIOR_CHANGE,
            area="Token Counting",
            description="Usage field location differs",
            old_code="""
# OpenAI
input_tokens = response.usage.prompt_tokens
output_tokens = response.usage.completion_tokens
""",
            new_code="""
# Anthropic
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
""",
            migration_notes="Field names differ but the concept is identical.",
        ),
        APIChange(
            change_type=ChangeType.NEW_FEATURE,
            area="Extended Thinking",
            description="Claude supports extended thinking for complex reasoning",
            old_code="""
# No direct equivalent in OpenAI
""",
            new_code="""
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,
    },
    messages=[{"role": "user", "content": "Solve this step by step..."}],
)

# Access thinking and response separately
for block in response.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Answer: {block.text}")
""",
            migration_notes=(
                "Extended thinking is unique to Claude. Use it for math, "
                "logic, and complex analysis tasks."
            ),
        ),
    ],
    deprecation_date=None,
    sunset_date=None,
)

print(provider_migration.render_markdown())
```

### Backward Compatibility Layer

When helping customers migrate, it is often useful to provide a compatibility layer that lets them migrate incrementally rather than all at once.

```python
"""
compat_layer.py
Provides a unified interface across LLM providers to ease migration.
"""

from dataclasses import dataclass
from typing import Optional, Iterator
from abc import ABC, abstractmethod


@dataclass
class Message:
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class LLMResponse:
    """Provider-agnostic response format."""
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        model: str,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> LLMResponse:
        ...

    @abstractmethod
    def stream_chat(
        self,
        messages: list[Message],
        model: str,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        ...


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: Optional[str] = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)

    def chat(
        self,
        messages: list[Message],
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> LLMResponse:
        # Separate system message from conversation messages
        system_msg = None
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                chat_messages.append(
                    {"role": msg.role, "content": msg.content}
                )

        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": chat_messages,
            "temperature": temperature,
        }
        if system_msg:
            kwargs["system"] = system_msg

        response = self.client.messages.create(**kwargs)

        return LLMResponse(
            text=response.content[0].text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=model,
            provider="anthropic",
        )

    def stream_chat(
        self,
        messages: list[Message],
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        system_msg = None
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                chat_messages.append(
                    {"role": msg.role, "content": msg.content}
                )

        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": chat_messages,
        }
        if system_msg:
            kwargs["system"] = system_msg

        with self.client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text


class OpenAIProvider(LLMProvider):
    """OpenAI provider."""

    def __init__(self, api_key: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    def chat(
        self,
        messages: list[Message],
        model: str = "gpt-4",
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> LLMResponse:
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=openai_messages,
            temperature=temperature,
        )

        return LLMResponse(
            text=response.choices[0].message.content or "",
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            model=model,
            provider="openai",
        )

    def stream_chat(
        self,
        messages: list[Message],
        model: str = "gpt-4",
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        stream = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=openai_messages,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# --- Usage: provider-agnostic code ---

def run_with_provider(provider: LLMProvider) -> None:
    """This function works identically regardless of provider."""
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="What is machine learning?"),
    ]

    response = provider.chat(messages)
    print(f"[{response.provider}] {response.text[:100]}...")
    print(f"Tokens: {response.input_tokens} in, {response.output_tokens} out")


# Switch providers with a single line change:
# provider = OpenAIProvider()
# provider = AnthropicProvider()
```

> **Swift Developer Note:** This compatibility layer pattern is analogous to writing a protocol in Swift and having multiple conforming types -- like how `URLSession` and Alamofire can both conform to a `NetworkClient` protocol. The Swift evolution proposal process (SE-NNNN) is itself an excellent example of migration communication: each proposal documents the motivation, detailed design, source compatibility impact, and migration path. Study SE-0005 (better translation of Objective-C APIs) for a masterclass in migration documentation.

---

## 5. Technical Blog Posts and Whitepapers

Technical blog posts and whitepapers serve different purposes but share a common goal: establishing credibility while communicating complex ideas clearly.

### Blog Post vs. Whitepaper

| Dimension | Blog Post | Whitepaper |
|-----------|-----------|------------|
| Length | 800-2000 words | 3000-10000 words |
| Tone | Conversational, first-person | Formal, third-person |
| Audience | Developers browsing | Decision-makers evaluating |
| Goal | Teach, inspire, drive adoption | Persuade, provide evidence |
| Lifespan | 3-6 months (then update) | 1-2 years |
| Code | Lots of runnable examples | Architecture diagrams, benchmarks |

### Blog Post Structure Generator

```python
"""
blog_post_structure.py
Generates outlines for technical blog posts targeting developer audiences.
"""

from dataclasses import dataclass, field
from enum import Enum


class PostType(Enum):
    TUTORIAL = "tutorial"           # "How to build X with Y"
    DEEP_DIVE = "deep_dive"         # "How X works under the hood"
    COMPARISON = "comparison"       # "X vs Y: Which should you use?"
    ANNOUNCEMENT = "announcement"   # "Introducing feature X"
    CASE_STUDY = "case_study"       # "How Company X achieved Y"
    OPINION = "opinion"             # "Why X matters for Y"


@dataclass
class BlogSection:
    heading: str
    key_points: list[str]
    includes_code: bool = False
    estimated_words: int = 200


@dataclass
class BlogOutline:
    title: str
    post_type: PostType
    target_audience: str
    hook: str  # Opening sentence/paragraph
    sections: list[BlogSection]
    seo_keywords: list[str] = field(default_factory=list)

    @property
    def estimated_reading_time(self) -> int:
        total_words = sum(s.estimated_words for s in self.sections)
        return max(1, total_words // 200)  # ~200 words per minute

    def render_outline(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            f"**Type:** {self.post_type.value}",
            f"**Audience:** {self.target_audience}",
            f"**Reading time:** ~{self.estimated_reading_time} min",
            f"**SEO keywords:** {', '.join(self.seo_keywords)}",
            "",
            "## Hook",
            "",
            self.hook,
            "",
        ]

        for i, section in enumerate(self.sections, 1):
            code_badge = " [includes code]" if section.includes_code else ""
            lines.append(f"## {i}. {section.heading}{code_badge}")
            lines.append(f"*~{section.estimated_words} words*")
            lines.append("")
            for point in section.key_points:
                lines.append(f"- {point}")
            lines.append("")

        return "\n".join(lines)


# --- Templates for common post types ---

def tutorial_outline(
    topic: str,
    technology: str,
    difficulty: str = "intermediate",
) -> BlogOutline:
    """Generate a tutorial blog post outline."""
    return BlogOutline(
        title=f"How to Build {topic} with {technology}",
        post_type=PostType.TUTORIAL,
        target_audience=f"{difficulty}-level developers using {technology}",
        hook=(
            f"You want to build {topic.lower()} but the documentation is "
            f"scattered across five repos and three blog posts from 2022. "
            f"Here is the complete guide, tested and working as of today."
        ),
        sections=[
            BlogSection(
                heading="What We Are Building",
                key_points=[
                    "Screenshot or diagram of the final result",
                    "Why this approach over alternatives",
                    "Time estimate: 30 minutes",
                ],
                estimated_words=150,
            ),
            BlogSection(
                heading="Prerequisites",
                key_points=[
                    "Required tools and versions",
                    "Environment setup commands",
                    "API keys or accounts needed",
                ],
                includes_code=True,
                estimated_words=100,
            ),
            BlogSection(
                heading="Step 1: The Minimal Version",
                key_points=[
                    "Simplest possible working example",
                    "Explain every line",
                    "Show expected output",
                ],
                includes_code=True,
                estimated_words=300,
            ),
            BlogSection(
                heading="Step 2: Adding Real-World Features",
                key_points=[
                    "Error handling",
                    "Configuration",
                    "Edge cases",
                ],
                includes_code=True,
                estimated_words=400,
            ),
            BlogSection(
                heading="Step 3: Production Considerations",
                key_points=[
                    "Performance optimization",
                    "Monitoring and logging",
                    "Cost management",
                ],
                includes_code=True,
                estimated_words=300,
            ),
            BlogSection(
                heading="Common Pitfalls",
                key_points=[
                    "Top 3-5 mistakes and how to avoid them",
                    "Links to relevant documentation",
                ],
                estimated_words=200,
            ),
            BlogSection(
                heading="Next Steps",
                key_points=[
                    "Links to advanced tutorials",
                    "Community resources",
                    "Call to action (try the API, star the repo)",
                ],
                estimated_words=100,
            ),
        ],
        seo_keywords=[
            topic.lower(),
            technology.lower(),
            f"{technology.lower()} tutorial",
            f"how to {topic.lower()}",
            f"{technology.lower()} example",
        ],
    )


# --- Example ---

outline = tutorial_outline(
    topic="a RAG Pipeline",
    technology="Claude API and ChromaDB",
)
print(outline.render_outline())
```

### Writing for Developer Audiences

Rules that distinguish developer-targeted writing from general technical writing:

1. **Lead with code, not prose.** Developers scroll past paragraphs to find code blocks. Put a working example in the first 200 words.

2. **Show, then explain.** Present the code, then explain what it does -- not the other way around. Developers want to see the shape of the solution before reading the theory.

3. **Be honest about limitations.** Developers respect honesty. "This approach does not work well for documents longer than 100K tokens" builds more trust than omitting the limitation.

4. **Use real data, not foo/bar.** Replace `user_123` with a realistic example. Replace `do_thing()` with `classify_support_ticket()`.

5. **Version everything.** Include the date, the SDK version, and the model version. Developer content rots fast in the AI space.

```python
"""
Example: Good vs. bad developer writing patterns.
"""

# BAD: Abstract, generic, hard to connect to reality
BAD_EXAMPLE = """
To use the API, create a client and call the method with your data.
The response will contain the result. Handle errors as needed.
"""

# GOOD: Concrete, specific, immediately useful
GOOD_EXAMPLE = """
Send a support ticket to Claude for classification:

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=50,
    messages=[{
        "role": "user",
        "content": (
            "Classify this support ticket as billing, technical, or general.\\n\\n"
            "Ticket: I was charged twice for my Pro subscription last month."
        ),
    }],
)
# Returns: "billing"
print(response.content[0].text)
```

This costs ~$0.001 per classification. For 10,000 tickets/day, budget
roughly $10/day. If cost is a concern, switch to Claude Haiku for ~10x
savings with minimal accuracy loss on simple classification tasks.
"""
```

> **Swift Developer Note:** Apple's developer blog (swift.org/blog) is excellent at leading with code. Posts like "Introducing Swift Testing" show the new API immediately, then explain the design rationale. WWDC sessions follow the same pattern: demo first, slides second. The AI industry has adopted this approach enthusiastically -- Anthropic's cookbook repository on GitHub is essentially a blog in Jupyter notebook form.

---

## 6. Internal Documentation

Internal documentation -- the docs your own team reads -- is chronically undervalued and underwritten. It is also the documentation that saves your team during a 3 AM incident or when onboarding a new engineer.

### Architecture Decision Records (ADRs)

An ADR captures the context, decision, and consequences of a significant architectural choice. The format was popularized by Michael Nygard.

```python
"""
adr_generator.py
Generate Architecture Decision Records in a consistent format.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class ADR:
    """Architecture Decision Record following the Nygard format."""
    number: int
    title: str
    status: str  # "proposed", "accepted", "deprecated", "superseded"
    context: str
    decision: str
    consequences: list[str]
    date_created: date = field(default_factory=date.today)
    deciders: list[str] = field(default_factory=list)
    supersedes: Optional[int] = None
    superseded_by: Optional[int] = None

    def render_markdown(self) -> str:
        lines = [
            f"# ADR-{self.number:04d}: {self.title}",
            "",
            f"**Date:** {self.date_created.isoformat()}",
            f"**Status:** {self.status}",
        ]

        if self.deciders:
            lines.append(f"**Deciders:** {', '.join(self.deciders)}")
        if self.supersedes:
            lines.append(f"**Supersedes:** ADR-{self.supersedes:04d}")
        if self.superseded_by:
            lines.append(f"**Superseded by:** ADR-{self.superseded_by:04d}")

        lines.extend([
            "",
            "## Context",
            "",
            self.context,
            "",
            "## Decision",
            "",
            self.decision,
            "",
            "## Consequences",
            "",
        ])

        for consequence in self.consequences:
            lines.append(f"- {consequence}")

        return "\n".join(lines)


# Example ADR
adr = ADR(
    number=7,
    title="Use Claude Haiku for Intent Classification, Sonnet for Generation",
    status="accepted",
    context=(
        "Our customer-facing chatbot handles two tasks: classifying the user's "
        "intent (billing, technical, general) and generating a response. "
        "Currently we use Claude Sonnet for both, costing $0.015 per "
        "interaction. At 50K interactions/day, this is $750/day. The "
        "classification step is simple and does not need Sonnet's full "
        "capability."
    ),
    decision=(
        "We will use a tiered model approach: Claude Haiku for intent "
        "classification ($0.001/call) and Claude Sonnet for response "
        "generation ($0.012/call). The classification prompt is fixed and "
        "simple. Only the generation step benefits from Sonnet's reasoning."
    ),
    consequences=[
        "Cost reduction from $0.015 to $0.013 per interaction (~13% savings)",
        "At 50K interactions/day, saves ~$100/day or ~$36K/year",
        "Adds ~50ms latency for the additional API call",
        "Requires maintaining two model configurations",
        "Classification accuracy must be monitored; if it drops below 95%, "
        "revisit this decision",
        "Creates a pattern we can reuse for other multi-step workflows",
    ],
    deciders=["Alice (Tech Lead)", "Bob (Solutions Engineer)"],
)

print(adr.render_markdown())
```

### Runbook Template

A runbook is a step-by-step guide for handling operational procedures, especially incidents.

```python
"""
runbook_template.py
Structured runbook generation for operational procedures.
"""

from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    SEV1 = "SEV1 - Service Down"
    SEV2 = "SEV2 - Major Degradation"
    SEV3 = "SEV3 - Minor Impact"
    SEV4 = "SEV4 - No User Impact"


@dataclass
class RunbookStep:
    action: str
    command: str = ""       # Shell command or API call
    expected_result: str = ""
    if_fails: str = ""      # What to do if this step fails


@dataclass
class Runbook:
    title: str
    description: str
    severity: Severity
    symptoms: list[str]
    prerequisites: list[str]
    steps: list[RunbookStep]
    escalation: str = ""
    rollback_steps: list[RunbookStep] = field(default_factory=list)

    def render_markdown(self) -> str:
        lines = [
            f"# Runbook: {self.title}",
            "",
            f"**Severity:** {self.severity.value}",
            "",
            f"**Description:** {self.description}",
            "",
            "## Symptoms",
            "",
        ]
        for symptom in self.symptoms:
            lines.append(f"- {symptom}")

        lines.extend(["", "## Prerequisites", ""])
        for prereq in self.prerequisites:
            lines.append(f"- {prereq}")

        lines.extend(["", "## Steps", ""])
        for i, step in enumerate(self.steps, 1):
            lines.append(f"### Step {i}: {step.action}")
            lines.append("")
            if step.command:
                lines.append("```bash")
                lines.append(step.command)
                lines.append("```")
                lines.append("")
            if step.expected_result:
                lines.append(f"**Expected:** {step.expected_result}")
                lines.append("")
            if step.if_fails:
                lines.append(f"**If this fails:** {step.if_fails}")
                lines.append("")

        if self.rollback_steps:
            lines.extend(["## Rollback", ""])
            for i, step in enumerate(self.rollback_steps, 1):
                lines.append(f"{i}. {step.action}")
                if step.command:
                    lines.append(f"   ```bash\n   {step.command}\n   ```")

        if self.escalation:
            lines.extend(["", "## Escalation", "", self.escalation])

        return "\n".join(lines)


# Example runbook
runbook = Runbook(
    title="LLM API Rate Limiting Incident",
    description="Handle situations where our application is being rate-limited by the LLM provider.",
    severity=Severity.SEV2,
    symptoms=[
        "HTTP 429 responses increasing in monitoring dashboard",
        "Customer-facing latency P95 exceeds 5 seconds",
        "Error rate exceeds 5% on /api/chat endpoint",
    ],
    prerequisites=[
        "Access to Grafana dashboard (LLM Monitoring)",
        "kubectl access to production cluster",
        "Anthropic console access for rate limit status",
    ],
    steps=[
        RunbookStep(
            action="Confirm rate limiting is the issue",
            command='kubectl logs -l app=llm-proxy --tail=100 | grep "429"',
            expected_result="Multiple 429 responses from api.anthropic.com",
            if_fails="Check if the issue is network-related instead (see Network Runbook)",
        ),
        RunbookStep(
            action="Check current rate limit usage",
            command="curl -s https://api.anthropic.com/v1/rate_limits -H 'x-api-key: $KEY'",
            expected_result="Usage near or at limit threshold",
        ),
        RunbookStep(
            action="Enable request queuing with backpressure",
            command="kubectl set env deployment/llm-proxy QUEUE_ENABLED=true QUEUE_MAX_SIZE=1000",
            expected_result="Requests queue instead of failing immediately",
        ),
        RunbookStep(
            action="Reduce non-critical traffic",
            command="kubectl scale deployment/batch-processor --replicas=0",
            expected_result="Batch processing paused, freeing rate limit capacity",
            if_fails="Manually disable batch jobs in the admin panel",
        ),
        RunbookStep(
            action="Contact provider if limits need temporary increase",
            command="# Open support ticket at https://support.anthropic.com",
            expected_result="Acknowledgment within 1 hour for SEV2",
        ),
    ],
    rollback_steps=[
        RunbookStep(
            action="Re-enable batch processing",
            command="kubectl scale deployment/batch-processor --replicas=3",
        ),
        RunbookStep(
            action="Disable request queuing",
            command="kubectl set env deployment/llm-proxy QUEUE_ENABLED=false",
        ),
    ],
    escalation=(
        "If rate limiting persists after 30 minutes, escalate to the "
        "on-call platform engineer and notify the account manager at "
        "the LLM provider."
    ),
)

print(runbook.render_markdown())
```

### Incident Postmortem Template

```python
"""
postmortem.py
Blameless incident postmortem structure.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TimelineEntry:
    timestamp: str
    event: str
    actor: str = ""  # who did/noticed this


@dataclass
class Postmortem:
    title: str
    date: str
    severity: str
    duration_minutes: int
    summary: str
    impact: str
    root_cause: str
    timeline: list[TimelineEntry]
    what_went_well: list[str]
    what_went_wrong: list[str]
    action_items: list[dict[str, str]]  # {"action": ..., "owner": ..., "due": ...}
    lessons_learned: list[str] = field(default_factory=list)

    def render_markdown(self) -> str:
        lines = [
            f"# Postmortem: {self.title}",
            "",
            f"**Date:** {self.date}",
            f"**Severity:** {self.severity}",
            f"**Duration:** {self.duration_minutes} minutes",
            "",
            "## Summary",
            "",
            self.summary,
            "",
            "## Impact",
            "",
            self.impact,
            "",
            "## Root Cause",
            "",
            self.root_cause,
            "",
            "## Timeline",
            "",
            "| Time | Event | Actor |",
            "|------|-------|-------|",
        ]
        for entry in self.timeline:
            lines.append(f"| {entry.timestamp} | {entry.event} | {entry.actor} |")

        lines.extend(["", "## What Went Well", ""])
        for item in self.what_went_well:
            lines.append(f"- {item}")

        lines.extend(["", "## What Went Wrong", ""])
        for item in self.what_went_wrong:
            lines.append(f"- {item}")

        if self.lessons_learned:
            lines.extend(["", "## Lessons Learned", ""])
            for lesson in self.lessons_learned:
                lines.append(f"- {lesson}")

        lines.extend(["", "## Action Items", ""])
        lines.append("| Action | Owner | Due Date |")
        lines.append("|--------|-------|----------|")
        for item in self.action_items:
            lines.append(
                f"| {item['action']} | {item['owner']} | {item['due']} |"
            )

        return "\n".join(lines)
```

> **Swift Developer Note:** Apple has an internal culture of detailed postmortems, though they rarely share them publicly. The closest public equivalent is the Swift evolution process, where rejected proposals include detailed rationale. The iOS community's practice of writing "what went wrong" blog posts after App Store rejections follows a similar pattern. ADRs serve the same purpose as the "Motivation" and "Alternatives Considered" sections in Swift Evolution proposals.

---

## 7. Presentation Skills for Engineers

Technical presentations are a core part of the solutions engineer role. You will present to customers during proof-of-concept reviews, to internal teams during architecture discussions, and at conferences or meetups to build your company's developer community.

### Presentation Structure

The most effective technical presentations follow one of three structures:

**1. The Problem-Solution Arc** (best for customer presentations)
- Here is the problem you face
- Here is why it is hard
- Here is how our approach solves it
- Here is the evidence it works
- Here is what you do next

**2. The Deep-Dive** (best for engineering audiences)
- Here is the system at a high level
- Let us zoom into this specific component
- Here is how it works under the hood
- Here are the tradeoffs we made and why
- Here are the open questions

**3. The Live Build** (best for developer audiences)
- Here is what we will build in the next 20 minutes
- Start coding from scratch
- Narrate decisions as you make them
- Show it working at the end
- Share the code

### Slide Design Principles

```python
"""
presentation_checklist.py
Checklist for technical presentations.
"""

from dataclasses import dataclass


@dataclass
class SlideReview:
    """Review checklist for a single slide."""
    slide_number: int
    title: str
    has_too_much_text: bool
    has_code: bool
    code_font_readable: bool = True  # >= 18pt
    has_diagram: bool = False
    single_idea: bool = True  # one idea per slide

    @property
    def issues(self) -> list[str]:
        problems = []
        if self.has_too_much_text:
            problems.append("Too much text. Aim for <6 bullet points, <8 words each.")
        if self.has_code and not self.code_font_readable:
            problems.append("Code font too small. Use >=18pt for live presentations.")
        if not self.single_idea:
            problems.append("Multiple ideas on one slide. Split into separate slides.")
        if self.has_code and len(self.title) > 0:
            # Heuristic: code slides should have minimal surrounding text
            pass
        return problems


PRESENTATION_CHECKLIST = """
## Technical Presentation Checklist

### Before the Presentation
- [ ] Test all demos on the actual presentation machine
- [ ] Have a backup plan if live demo fails (screenshots, video recording)
- [ ] Check internet connectivity (for API demos)
- [ ] Pre-authenticate all services (no typing passwords on screen)
- [ ] Increase terminal font size to >= 18pt
- [ ] Close all notifications (Slack, email, OS notifications)
- [ ] Have water nearby

### Slide Design
- [ ] Maximum 6 bullet points per slide
- [ ] Maximum 8 words per bullet point
- [ ] Code examples use syntax highlighting
- [ ] Code font is >= 18pt
- [ ] One idea per slide
- [ ] Diagrams over text for architecture
- [ ] Consistent color scheme throughout

### Live Coding
- [ ] Pre-type any boilerplate (imports, config)
- [ ] Use a large, clean terminal with dark background
- [ ] Have a "checkpoint" version ready if you get stuck
- [ ] Practice the typing 3x at presentation speed
- [ ] Prepare for "what if it fails" at each step

### Delivery
- [ ] Open with a hook: problem, question, or surprising fact
- [ ] Narrate what you are doing during live coding
- [ ] Pause after key points (count to 3 silently)
- [ ] Make eye contact with the audience, not the screen
- [ ] End with a clear call to action

### Virtual Presentations
- [ ] Share only the relevant window (not full screen)
- [ ] Use a second monitor for speaker notes
- [ ] Have a co-presenter monitor chat for questions
- [ ] Record the session for async viewers
- [ ] Test screen sharing before the meeting starts
"""

print(PRESENTATION_CHECKLIST)
```

### Handling Questions

The most important skill during Q&A is not having every answer -- it is being honest about what you do and do not know.

**Framework for answering questions:**

1. **Repeat the question** (ensures everyone heard it, gives you time to think).
2. **Acknowledge it** ("Great question" is fine, but do not say it for every question).
3. **Answer directly** if you know the answer.
4. **Admit uncertainty** if you do not: "I do not know the exact number, but I can find out and follow up."
5. **Redirect if off-topic**: "That is an important question that deserves its own discussion. Can I follow up with you after?"

**Dangerous patterns to avoid:**
- Making up an answer. Developers will verify, and you will lose credibility permanently.
- Getting defensive. If someone points out a flaw, acknowledge it.
- Going down a rabbit hole. Keep answers to 60 seconds unless the questioner asks for more detail.
- Ignoring the question and answering a different one.

> **Swift Developer Note:** WWDC presentations are the benchmark for technical talks. Notice how Apple engineers structure their sessions: they open with a real-world scenario, show working code immediately, build complexity gradually, and always end with a "next steps" slide. The Q&A labs are separate from presentations, which is a format worth considering -- it separates the "teaching" mode from the "answering" mode. Also notice that WWDC slides use very large font sizes and minimal text. If your slide looks like a wall of text, it belongs in a blog post, not a presentation.

---

## 8. Customer Communication Patterns

Customer communication as a solutions engineer follows predictable patterns. Knowing these patterns lets you respond quickly and consistently, even under pressure.

### Status Update Template

```python
"""
customer_comms.py
Templates for common customer communication patterns.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class UpdateType(Enum):
    PROGRESS = "progress"
    BLOCKER = "blocker"
    MILESTONE = "milestone"
    INCIDENT = "incident"
    FEATURE_RESPONSE = "feature_response"


@dataclass
class CustomerUpdate:
    """A structured customer communication."""
    update_type: UpdateType
    customer_name: str
    subject: str
    body: str
    action_items: list[str] = field(default_factory=list)
    internal_notes: str = ""  # not shared with customer

    def render_email(self) -> str:
        lines = [
            f"Subject: {self.subject}",
            "",
            f"Hi {self.customer_name} team,",
            "",
            self.body,
        ]

        if self.action_items:
            lines.append("")
            lines.append("**Next steps:**")
            for item in self.action_items:
                lines.append(f"- {item}")

        lines.extend([
            "",
            "Please let me know if you have any questions.",
            "",
            "Best,",
            "[Your Name]",
        ])

        return "\n".join(lines)


def incident_communication(
    customer_name: str,
    service_affected: str,
    current_status: str,
    eta_minutes: int | None = None,
    root_cause: str = "",
) -> CustomerUpdate:
    """Generate an incident communication for a customer.

    Follows the pattern: Acknowledge -> Impact -> Action -> Timeline.
    """
    body_lines = [
        f"We are aware of an issue affecting {service_affected} and "
        f"are actively working to resolve it.",
        "",
        f"**Current status:** {current_status}",
    ]

    if root_cause:
        body_lines.extend(["", f"**Root cause:** {root_cause}"])

    if eta_minutes:
        body_lines.extend([
            "",
            f"**Estimated resolution:** Within {eta_minutes} minutes",
        ])

    body_lines.extend([
        "",
        "We will provide updates every 30 minutes until this is resolved.",
    ])

    return CustomerUpdate(
        update_type=UpdateType.INCIDENT,
        customer_name=customer_name,
        subject=f"[Incident] {service_affected} - {current_status}",
        body="\n".join(body_lines),
        action_items=[
            "No action required from your side",
            "We will send the next update by "
            f"{datetime.now().strftime('%H:%M')} UTC",
        ],
    )


def feature_request_response(
    customer_name: str,
    feature_requested: str,
    decision: str,  # "planned", "considering", "declined"
    rationale: str,
    alternative: str = "",
    timeline: str = "",
) -> CustomerUpdate:
    """Respond to a customer feature request.

    The key principle: never say 'no' without saying 'but here is
    what you can do instead.'
    """
    decision_language = {
        "planned": (
            f"We are excited to share that **{feature_requested}** is on our "
            f"roadmap."
        ),
        "considering": (
            f"Thank you for suggesting **{feature_requested}**. We are "
            f"actively evaluating this and your input is valuable in "
            f"prioritizing our roadmap."
        ),
        "declined": (
            f"We have carefully considered **{feature_requested}**. After "
            f"evaluating the technical implications and our current "
            f"priorities, we have decided not to pursue this at this time."
        ),
    }

    body_lines = [decision_language.get(decision, "")]
    body_lines.extend(["", f"**Rationale:** {rationale}"])

    if alternative:
        body_lines.extend([
            "",
            f"**Alternative approach:** {alternative}",
        ])

    if timeline:
        body_lines.extend(["", f"**Timeline:** {timeline}"])

    action_items = []
    if decision == "planned":
        action_items.append("We will notify you when this enters development")
    elif decision == "considering":
        action_items.append(
            "We may reach out for additional input on your use case"
        )
    elif decision == "declined" and alternative:
        action_items.append(
            "We can schedule a call to walk through the alternative approach"
        )

    return CustomerUpdate(
        update_type=UpdateType.FEATURE_RESPONSE,
        customer_name=customer_name,
        subject=f"Re: Feature Request - {feature_requested}",
        body="\n".join(body_lines),
        action_items=action_items,
    )


# --- The Art of Saying No ---

def constructive_no(
    what_they_want: str,
    why_not: str,
    what_instead: str,
) -> str:
    """Frame a 'no' as a 'yes, but differently.'

    Never:  'We can't do that.'
    Always: 'Here's what we can do that addresses your underlying need.'
    """
    return (
        f"I understand you need {what_they_want}. "
        f"{why_not} "
        f"What I can offer instead is {what_instead}. "
        f"Would that address your core need?"
    )


# Examples of constructive no
examples = [
    constructive_no(
        what_they_want="a dedicated model fine-tuned on your data",
        why_not=(
            "Fine-tuning requires significant data preparation and ongoing "
            "maintenance costs that may not be justified given your current volume."
        ),
        what_instead=(
            "a RAG pipeline with your documentation that achieves similar "
            "accuracy with much faster iteration time and lower cost"
        ),
    ),
    constructive_no(
        what_they_want="guaranteed 99.99% uptime in the SLA",
        why_not=(
            "Our current infrastructure supports 99.9% uptime, and the "
            "additional nine requires redundancy that would significantly "
            "increase costs."
        ),
        what_instead=(
            "99.9% uptime with an automatic failover to a secondary provider, "
            "giving you effective 99.95%+ availability at a fraction of the cost "
            "of true 99.99%"
        ),
    ),
]

for i, example in enumerate(examples, 1):
    print(f"\nExample {i}:")
    print(example)
```

### Setting Expectations

The most common source of customer frustration is not failure -- it is surprise. If you set expectations clearly upfront, customers can plan around limitations.

**The Expectation-Setting Framework:**

1. **Be specific about what you will deliver** ("A working prototype with 3 endpoints, not a production system").
2. **Be specific about when** ("End of next week" not "soon").
3. **Be specific about what you will not deliver** ("This will not include authentication or rate limiting").
4. **Identify risks early** ("This depends on getting access to your data by Wednesday. If that slips, the timeline moves with it.").
5. **Update immediately when things change** (do not wait for the next scheduled check-in).

> **Swift Developer Note:** Apple's developer communication style is famously opaque -- "we'll look into it" on Radar tickets with no follow-up for months. This is explicitly what you should NOT do as a solutions engineer. The AI/ML industry expects much more transparent communication. Study how Anthropic, OpenAI, and other providers communicate API changes, model updates, and incidents through their status pages and changelogs. The contrast with Apple's style is instructive: be more like the API changelog, less like Radar.

---

## 9. Swift Comparison

As a developer transitioning from the Apple ecosystem, you bring a deep familiarity with Apple's distinctive approach to technical communication. Understanding both the strengths and weaknesses of that approach will help you calibrate your own communication style for the AI engineering world.

### Apple Documentation Style vs. AI API Documentation

| Aspect | Apple Style | AI API Style |
|--------|------------|--------------|
| Tone | Formal, authoritative | Conversational, practical |
| Code samples | Xcode-integrated, buildable projects | Copy-paste single files |
| Versioning | Tied to OS versions | Tied to SDK + model versions |
| Deprecation | Gentle ("deprecated" compiler warnings) | Hard deadlines ("sunsets on DATE") |
| Community input | Minimal (Swift Evolution is the exception) | Extensive (GitHub issues, Discord) |
| Error docs | Sparse | Detailed (HTTP status codes, retry guidance) |
| Pricing | Not applicable (free frameworks) | Central concern (cost-per-token) |

### WWDC Presentation Patterns

WWDC sessions follow a remarkably consistent structure that you can adapt:

```python
"""
wwdc_to_tech_talk.py
Map WWDC presentation patterns to AI engineering talks.
"""

WWDC_STRUCTURE = {
    "opening": {
        "wwdc": "Hi, I'm [Name] from the [Framework] team.",
        "ai_eng": (
            "I'm [Name], a solutions engineer at [Company]. Today I'll "
            "show you how to [solve specific problem]."
        ),
        "principle": "Establish credibility immediately.",
    },
    "motivation": {
        "wwdc": "Developers have been asking for [feature]. Today we're excited to announce...",
        "ai_eng": (
            "Your customers are asking for [capability]. Here's how to "
            "build it in 30 minutes."
        ),
        "principle": "Frame around the audience's needs, not your features.",
    },
    "demo_first": {
        "wwdc": "Let me show you what's possible. [switches to Xcode]",
        "ai_eng": (
            "Let me show you the end result first. [shows working app] "
            "Now let's build it step by step."
        ),
        "principle": "Show the destination before the journey.",
    },
    "progressive_detail": {
        "wwdc": "Start with basic usage -> add modifiers -> show advanced patterns",
        "ai_eng": (
            "Start with basic API call -> add error handling -> add "
            "streaming -> add tool use"
        ),
        "principle": "Layer complexity. Never dump everything at once.",
    },
    "gotchas": {
        "wwdc": "'One thing to note...' or 'Keep in mind...'",
        "ai_eng": (
            "'A common mistake here is...' or 'In production, you'll "
            "also want to...'"
        ),
        "principle": "Preemptively address issues the audience will hit.",
    },
    "closing": {
        "wwdc": "To learn more, check out these related sessions...",
        "ai_eng": (
            "The full code is on GitHub at [link]. For questions, "
            "reach out on our Discord or open an issue."
        ),
        "principle": "Clear next steps. Never end with 'any questions?'",
    },
}

for phase, details in WWDC_STRUCTURE.items():
    print(f"\n## {phase.replace('_', ' ').title()}")
    print(f"  WWDC:   {details['wwdc']}")
    print(f"  AI Eng: {details['ai_eng']}")
    print(f"  Why:    {details['principle']}")
```

### Swift Evolution Proposals as Communication Models

Swift Evolution proposals (SE-NNNN) are among the best examples of technical communication in the software industry. Each proposal contains:

- **Introduction**: One-paragraph summary
- **Motivation**: Why this change is needed (the "business case")
- **Proposed Solution**: What specifically changes
- **Detailed Design**: How it works technically
- **Source Compatibility**: Impact on existing code (migration concerns)
- **Alternatives Considered**: What else was evaluated and why it was rejected

This structure maps directly to the kind of technical proposals you will write as a solutions engineer:

```python
"""
technical_proposal.py
Adapt the Swift Evolution proposal format for AI engineering proposals.
"""

from dataclasses import dataclass, field


@dataclass
class TechnicalProposal:
    """A technical proposal in the style of Swift Evolution."""
    proposal_id: str
    title: str
    author: str
    status: str

    # The SE-style sections
    introduction: str
    motivation: str
    proposed_solution: str
    detailed_design: str
    impact_on_existing_systems: str
    alternatives_considered: list[dict[str, str]]  # {"approach": ..., "rejected_because": ...}

    # Additional sections for business context
    cost_estimate: str = ""
    timeline: str = ""
    risks: list[str] = field(default_factory=list)

    def render_markdown(self) -> str:
        lines = [
            f"# {self.proposal_id}: {self.title}",
            "",
            f"**Author:** {self.author}",
            f"**Status:** {self.status}",
            "",
            "## Introduction",
            "",
            self.introduction,
            "",
            "## Motivation",
            "",
            self.motivation,
            "",
            "## Proposed Solution",
            "",
            self.proposed_solution,
            "",
            "## Detailed Design",
            "",
            self.detailed_design,
            "",
            "## Impact on Existing Systems",
            "",
            self.impact_on_existing_systems,
            "",
            "## Alternatives Considered",
            "",
        ]

        for alt in self.alternatives_considered:
            lines.append(f"### {alt['approach']}")
            lines.append("")
            lines.append(f"Rejected because: {alt['rejected_because']}")
            lines.append("")

        if self.cost_estimate:
            lines.extend(["## Cost Estimate", "", self.cost_estimate, ""])

        if self.timeline:
            lines.extend(["## Timeline", "", self.timeline, ""])

        if self.risks:
            lines.extend(["## Risks", ""])
            for risk in self.risks:
                lines.append(f"- {risk}")

        return "\n".join(lines)


# Example: proposing a model routing layer
proposal = TechnicalProposal(
    proposal_id="PROP-012",
    title="Intelligent Model Routing Layer",
    author="Solutions Engineering Team",
    status="Under Review",
    introduction=(
        "We propose adding an intelligent routing layer that automatically "
        "selects the optimal LLM model (Haiku, Sonnet, or Opus) based on "
        "query complexity, reducing costs by 30-40% without measurable "
        "quality degradation."
    ),
    motivation=(
        "Customers currently use a single model for all queries. Analysis "
        "of 100K production queries shows that 60% are simple lookups or "
        "classifications that do not require Sonnet-level reasoning. These "
        "queries could be handled by Haiku at 1/10th the cost."
    ),
    proposed_solution=(
        "A lightweight classifier (itself running on Haiku) analyzes each "
        "incoming query and routes it to the appropriate model tier. The "
        "classifier adds ~50ms latency but saves an average of $0.008 per "
        "query."
    ),
    detailed_design=(
        "The routing layer sits between the customer's application and the "
        "LLM API. It uses a prompt-based classifier with three categories: "
        "simple (Haiku), standard (Sonnet), complex (Opus). Classification "
        "confidence below 80% defaults to Sonnet. The system logs all "
        "routing decisions for ongoing evaluation."
    ),
    impact_on_existing_systems=(
        "The routing layer is deployed as a proxy. Existing applications "
        "change only the base URL. No SDK changes required. Response "
        "format is unchanged."
    ),
    alternatives_considered=[
        {
            "approach": "Client-side routing with rules engine",
            "rejected_because": (
                "Requires SDK changes for every customer and does not "
                "adapt to new query patterns without redeployment."
            ),
        },
        {
            "approach": "Always use the cheapest model with fallback",
            "rejected_because": (
                "Haiku-first with Sonnet fallback adds latency for 40% "
                "of queries (those that need Sonnet) and creates a poor "
                "user experience with visible delays."
            ),
        },
    ],
    cost_estimate=(
        "Routing classifier cost: ~$0.0002 per query. Net savings at "
        "50K queries/day: ~$400/day or $146K/year."
    ),
    timeline="2 weeks for prototype, 2 weeks for evaluation, 1 week for production rollout.",
    risks=[
        "Classifier may misroute complex queries to Haiku, degrading quality",
        "Additional latency may be unacceptable for real-time applications",
        "Classifier prompt needs ongoing maintenance as model capabilities change",
    ],
)

print(proposal.render_markdown())
```

> **Swift Developer Note:** If you have followed Swift Evolution, you already understand how to write a technical proposal. The format is nearly identical: motivation, design, alternatives, compatibility. The main addition in the AI/ML context is cost analysis -- something that never appears in Swift proposals because Swift frameworks are free. Practice translating your instinct for "source compatibility" into "backward compatibility for API consumers."

---

## 10. Interview Focus

Technical communication is evaluated in solutions engineer interviews more explicitly than in most other engineering roles. You will be asked to write, present, and explain -- sometimes all in the same interview loop.

### Common Interview Formats

**1. Writing Exercise (30-60 minutes)**
- Write a tutorial for a given API feature
- Write a migration guide for a version upgrade
- Write a customer email responding to a technical issue

**2. Live Presentation (30 minutes)**
- Present a technical topic to a mock customer
- Explain a complex concept to a non-technical audience
- Do a live coding demo

**3. Role-Play Scenarios (45 minutes)**
- Customer is frustrated with latency; diagnose and communicate
- Customer wants a feature that does not exist; respond constructively
- Customer's production system is down; lead the incident call

**4. Code Review / Documentation Review**
- Review a code sample and identify issues
- Improve existing documentation
- Write API reference from a code snippet

### Practice: Write a Tutorial From Scratch

Here is the kind of exercise you might encounter in an interview. Given an API endpoint, write a complete tutorial in 30 minutes.

```python
"""
interview_exercise.py
Practice exercise: Generate a tutorial for a fictional API endpoint.

INTERVIEW PROMPT:
"Write a tutorial showing developers how to use our new
Batch Processing API to classify 1,000 support tickets.
Include error handling and cost estimation."

TIME LIMIT: 30 minutes
"""

SAMPLE_TUTORIAL = """
# Batch Processing: Classify 1,000 Support Tickets with Claude

Processing support tickets one at a time is slow and expensive at scale.
The Batch API lets you submit up to 10,000 requests in a single call,
with results delivered within 24 hours at 50% cost savings.

## Prerequisites

- Python 3.10+
- `pip install anthropic==0.39.0`
- Anthropic API key with batch access enabled

## Step 1: Prepare Your Tickets

Your tickets need to be formatted as a JSONL file where each line is
a valid JSON object:

```python
import json
from pathlib import Path

tickets = [
    {"id": "T-001", "text": "I was charged twice for my subscription"},
    {"id": "T-002", "text": "The app crashes when I upload large files"},
    {"id": "T-003", "text": "How do I change my password?"},
    # ... imagine 997 more
]

# Write to JSONL format
with open("tickets.jsonl", "w") as f:
    for ticket in tickets:
        json.dump(ticket, f)
        f.write("\\n")

print(f"Prepared {len(tickets)} tickets")
```

## Step 2: Create Batch Requests

Convert each ticket into a batch request with a classification prompt:

```python
import anthropic
import json

def create_batch_request(ticket: dict) -> dict:
    return {
        "custom_id": ticket["id"],
        "params": {
            "model": "claude-haiku-3-5-20241022",
            "max_tokens": 20,
            "messages": [{
                "role": "user",
                "content": (
                    "Classify this support ticket into exactly one category: "
                    "billing, technical, account, or general.\\n\\n"
                    f"Ticket: {ticket['text']}\\n\\n"
                    "Category:"
                ),
            }],
        },
    }

# Build the batch
with open("tickets.jsonl") as f:
    tickets = [json.loads(line) for line in f]

requests = [create_batch_request(t) for t in tickets]
print(f"Created {len(requests)} batch requests")
```

## Step 3: Submit the Batch

```python
client = anthropic.Anthropic()

batch = client.batches.create(requests=requests)
print(f"Batch submitted: {batch.id}")
print(f"Status: {batch.processing_status}")
```

## Step 4: Poll for Results

```python
import time

while True:
    batch = client.batches.retrieve(batch.id)
    print(f"Status: {batch.processing_status}")

    if batch.processing_status == "ended":
        break

    time.sleep(60)  # check every minute

print(f"Completed: {batch.request_counts.succeeded} succeeded")
print(f"Failed: {batch.request_counts.errored} errored")
```

## Cost Estimate

| Item | Cost |
|------|------|
| 1,000 tickets x ~50 input tokens | $0.0125 |
| 1,000 tickets x ~5 output tokens | $0.00125 |
| **Total** | **~$0.014** |
| Compared to non-batch | ~$0.028 (50% more) |

## Common Issues

- **Batch rejected**: Check that all requests have valid `custom_id` values
- **High error rate**: Verify your prompt works on a single request first
- **Slow processing**: Batches are processed within 24 hours; plan accordingly
"""

print(SAMPLE_TUTORIAL)
```

### Communication-Focused Interview Questions

Prepare answers for these common questions:

```python
"""
interview_questions.py
Common SE interview questions focused on technical communication.
"""

INTERVIEW_QUESTIONS = [
    {
        "question": "How would you explain RAG to a non-technical executive?",
        "what_they_evaluate": [
            "Can you simplify without being inaccurate?",
            "Do you use analogies effectively?",
            "Do you connect to business value?",
        ],
        "sample_answer": (
            "Imagine your company's knowledge is in a library. Today, "
            "when a customer asks a question, the AI has to guess the "
            "answer from its general training. With RAG, we give the AI "
            "a librarian -- it searches your specific documents first, "
            "then answers based on what it finds. This means answers are "
            "grounded in your actual data, not guesses. Customers get "
            "accurate, source-cited responses, and you can update the "
            "knowledge base without retraining the model."
        ),
    },
    {
        "question": (
            "A customer says your API is 'too slow.' Walk me through "
            "how you would handle this."
        ),
        "what_they_evaluate": [
            "Do you ask clarifying questions before jumping to solutions?",
            "Do you show empathy?",
            "Is your diagnostic approach systematic?",
        ],
        "sample_answer": (
            "First, I would acknowledge their frustration and ask specific "
            "questions: What latency are they seeing? What is their target? "
            "Which endpoints are affected? Then I would look at the data: "
            "check their request patterns, model choice, prompt length, and "
            "whether they are using streaming. Common quick wins include "
            "switching to a smaller model for simple tasks, enabling "
            "streaming for perceived speed, and caching repeated queries. "
            "I would present options with tradeoffs rather than prescribing "
            "a single solution."
        ),
    },
    {
        "question": "Write a brief email to a customer whose feature request we are declining.",
        "what_they_evaluate": [
            "Tone: empathetic but clear",
            "Structure: decision, rationale, alternative",
            "Professionalism under awkward circumstances",
        ],
        "sample_answer": (
            "Subject: Re: Custom Model Hosting Request\\n\\n"
            "Hi Sarah,\\n\\n"
            "Thank you for sharing your requirements for dedicated model "
            "hosting. We have discussed this with our infrastructure team "
            "and, given our current architecture, dedicated hosting is not "
            "something we can offer at this time.\\n\\n"
            "I want to make sure your underlying need -- data isolation and "
            "guaranteed capacity -- is addressed. Two alternatives:\\n\\n"
            "1. Our Enterprise tier includes a dedicated throughput "
            "allocation that guarantees your requests are never queued.\\n"
            "2. We can set up VPC peering so your data never traverses "
            "the public internet.\\n\\n"
            "Would either of these address your core concern? I am happy "
            "to set up a call to discuss.\\n\\n"
            "Best,\\n[Your name]"
        ),
    },
    {
        "question": (
            "You are presenting a proof-of-concept to a customer. The live "
            "demo fails. What do you do?"
        ),
        "what_they_evaluate": [
            "Grace under pressure",
            "Preparation (do you have a backup?)",
            "Honesty vs. deflection",
        ],
        "sample_answer": (
            "First, do not panic or apologize excessively. Say something like: "
            "'It looks like we are hitting a connectivity issue. Let me switch "
            "to the recorded version of this demo while we debug.' Show the "
            "pre-recorded demo or screenshots. If the customer is technical, "
            "acknowledge the failure honestly: 'This is a good reminder of why "
            "we build retry logic and fallbacks -- exactly the patterns I was "
            "about to show you.' After the meeting, diagnose the issue and "
            "send a follow-up with the working demo."
        ),
    },
    {
        "question": (
            "How do you decide what level of detail to include in documentation?"
        ),
        "what_they_evaluate": [
            "Audience awareness",
            "Practical judgment",
            "Understanding of documentation types",
        ],
        "sample_answer": (
            "It depends on the document type and audience. For a quickstart "
            "guide, I include the absolute minimum to get a working result -- "
            "5-10 lines of code with one paragraph of context. For a "
            "migration guide, I include every breaking change with before/after "
            "code. For API reference, I document every parameter with type, "
            "default value, and a one-line description. The rule I follow: if "
            "the reader has to leave this document to accomplish their goal, "
            "I have not included enough detail. If they are skipping large "
            "sections, I have included too much."
        ),
    },
]

for i, q in enumerate(INTERVIEW_QUESTIONS, 1):
    print(f"\n{'='*70}")
    print(f"Question {i}: {q['question']}")
    print(f"\nEvaluation criteria:")
    for criterion in q["what_they_evaluate"]:
        print(f"  - {criterion}")
    print(f"\nSample answer:\n{q['sample_answer']}")
```

### Writing Sample Preparation

Many SE interviews ask for a writing sample. Here is how to prepare one.

```python
"""
writing_sample_checklist.py
Prepare a strong writing sample for SE interviews.
"""

WRITING_SAMPLE_GUIDE = """
## Preparing Your Writing Sample

### What to Write
Choose ONE of these formats:
1. A tutorial for an API you have used (Claude, OpenAI, Stripe, Twilio)
2. A migration guide you wish had existed
3. A technical blog post about a problem you solved

### Checklist

Content Quality:
- [ ] Solves a real problem a developer would face
- [ ] Code samples are tested and runnable
- [ ] Progressive complexity (simple -> advanced)
- [ ] Includes troubleshooting section
- [ ] Under 2,000 words (conciseness matters)

Technical Accuracy:
- [ ] All code compiles/runs without errors
- [ ] API calls use current SDK versions
- [ ] Model names are current (not deprecated)
- [ ] Error handling is present and correct

Writing Quality:
- [ ] Clear, direct sentences (no filler)
- [ ] Active voice ("Send a request" not "A request should be sent")
- [ ] Consistent formatting and terminology
- [ ] No spelling or grammar errors
- [ ] Proper code formatting with syntax highlighting

Structure:
- [ ] Title tells the reader what they will learn
- [ ] Opening paragraph sets context in 2-3 sentences
- [ ] Logical flow from beginning to end
- [ ] Conclusion with next steps
- [ ] Headers enable skimming

### Length Guidelines
- Tutorial: 1,000-1,500 words + code
- Migration guide: 800-1,200 words + code
- Blog post: 1,000-2,000 words

### Red Flags Interviewers Look For
- Code that does not run
- Outdated API references
- Passive voice throughout
- No error handling in samples
- Wall-of-text paragraphs without code breaks
- Explaining "what" without explaining "why"
"""

print(WRITING_SAMPLE_GUIDE)
```

> **Swift Developer Note:** If you have written Swift package documentation using DocC, you already understand the concept of structured documentation with embedded code samples. The transition is straightforward: DocC's "tutorial" format with step-by-step instructions maps directly to API tutorials. The difference is that DocC compiles your samples as part of the build, guaranteeing they work. In the Python/API world, you need to build that validation step yourself (see the sample_validator.py earlier in this lesson). Your experience with Xcode documentation comments (`///` and `/** */`) translates to Python docstrings -- same concept, different syntax.

---

## Summary

Technical communication is a multiplier on all your other engineering skills. A brilliant solution that no one can understand, adopt, or maintain is worth less than a good solution that is well-documented, clearly presented, and easy to migrate to.

### Key Takeaways

1. **Tutorials are not reference docs.** Tutorials guide, references enumerate. Know which you are writing.
2. **Code samples are read first.** Make them self-contained, runnable, and copy-paste ready.
3. **Translation is the SE superpower.** Converting between business language and technical specs is the most valuable skill in the role.
4. **Migration guides save customers.** Structure them around breaking changes, provide before/after code, and always include a rollback plan.
5. **Internal docs save your team.** ADRs, runbooks, and postmortems are not overhead -- they are engineering infrastructure.
6. **Presentations follow patterns.** Use problem-solution arcs, lead with demos, and practice handling failure gracefully.
7. **Saying no is an art.** Never decline without offering an alternative that addresses the underlying need.
8. **Interview prep is writing prep.** The best way to prepare for communication-focused interviews is to write tutorials, blog posts, and migration guides -- then get feedback on them.

### Practice Exercises

1. **Write a tutorial** for an API you have used (Claude, OpenAI, or another). Follow the structure from Section 1. Test every code sample.

2. **Translate three business requirements** into technical specifications using the framework from Section 3. Write the clarifying questions you would ask.

3. **Write a migration guide** for a real version upgrade you have experienced (or create one for the OpenAI-to-Anthropic migration from Section 4).

4. **Prepare a 5-minute presentation** explaining RAG to a non-technical audience. Record yourself and review.

5. **Write a feature request decline email** for a realistic scenario. Have someone else review it for tone.

6. **Create an ADR** for a technical decision in a project you are working on. Follow the template from Section 6.

7. **Practice the interview questions** from Section 10. Write out your answers, then practice speaking them aloud under a 90-second time limit.

---

*Next module: [08-multi-provider-and-multi-modal](../08-multi-provider-and-multi-modal/lesson.md) -- Building systems that work across LLM providers and modalities.*
