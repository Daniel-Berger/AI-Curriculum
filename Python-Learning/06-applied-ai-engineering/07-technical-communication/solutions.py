"""
Module 07 Solutions: Technical Communication
=============================================

Complete implementations for all 15 exercises with detailed comments.
Each solution includes design rationale relevant to Solutions Engineering
and Applied AI Engineering roles.
"""

import re
import ast
import json
import io
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass, field, asdict
from typing import Any
from datetime import datetime, date
import time


# ---------------------------------------------------------------------------
# Data classes (shared with exercises.py)
# ---------------------------------------------------------------------------

@dataclass
class APIEndpoint:
    """Describes a single API endpoint for tutorial generation."""
    method: str
    path: str
    description: str
    parameters: list[dict]
    request_body: dict | None = None
    response_body: dict | None = None


@dataclass
class ValidationResult:
    """Result of validating a code sample."""
    is_valid: bool
    syntax_ok: bool
    imports_found: list[str]
    imports_missing: list[str]
    has_main_guard: bool
    has_error_handling: bool
    has_type_hints: bool
    has_docstrings: bool
    completeness_score: float
    issues: list[str]


@dataclass
class TechnicalRequirement:
    """A single extracted technical requirement."""
    id: str
    category: str
    title: str
    description: str
    priority: str
    estimated_complexity: str
    dependencies: list[str]


@dataclass
class APIChange:
    """Represents a single change between API versions."""
    change_type: str
    component: str
    path: str
    old_value: Any
    new_value: Any
    breaking: bool
    migration_action: str


@dataclass
class ChangeEntry:
    """A single change to include in the changelog."""
    category: str
    description: str
    issue_ref: str = ""
    author: str = ""


@dataclass
class RunbookStep:
    """A single step in a runbook."""
    step_number: int
    action: str
    command: str = ""
    expected_output: str = ""
    rollback: str = ""
    warning: str = ""


@dataclass
class TimelineEvent:
    """A single event in the incident timeline."""
    timestamp: str
    description: str
    actor: str = ""


@dataclass
class ComplexityFactor:
    """A single factor contributing to project complexity."""
    name: str
    score: int
    weight: float
    rationale: str


@dataclass
class CoverageReport:
    """Documentation coverage report for a module."""
    total_public_items: int
    documented_items: int
    undocumented_items: list[str]
    coverage_percentage: float
    items: list[dict[str, Any]]


@dataclass
class SupportTicket:
    """A customer support ticket."""
    id: str
    subject: str
    body: str
    category: str = ""
    resolution: str = ""


@dataclass
class FAQEntry:
    """A generated FAQ entry."""
    question: str
    answer: str
    category: str
    source_ticket_ids: list[str]
    frequency: int


@dataclass
class ReleaseFeature:
    """A feature included in a release."""
    title: str
    technical_description: str
    user_benefit: str
    business_impact: str
    category: str
    breaking: bool = False


@dataclass
class Slide:
    """A single slide in the presentation."""
    slide_number: int
    title: str
    bullet_points: list[str]
    speaker_notes: str
    slide_type: str
    estimated_minutes: float


@dataclass
class CodeExample:
    """A code example extracted from documentation."""
    id: str
    language: str
    code: str
    expected_output: str | None = None
    line_number: int = 0
    description: str = ""


@dataclass
class TestResult:
    """Result of running a code example."""
    example_id: str
    passed: bool
    actual_output: str = ""
    error: str = ""
    execution_time_ms: float = 0.0


# ---------------------------------------------------------------------------
# Solution 1: API Tutorial Template Generator
# ---------------------------------------------------------------------------
# Design notes:
# - Structure mirrors real API tutorials (Anthropic, Stripe, Twilio)
# - Generates both curl and Python examples for each endpoint
# - Includes authentication setup specific to the auth_type
# - Quickstart uses the simplest endpoint (fewest required params)
# ---------------------------------------------------------------------------

def solution_1_api_tutorial_generator(
    api_name: str,
    base_url: str,
    endpoints: list[APIEndpoint],
    auth_type: str = "bearer_token",
) -> dict[str, Any]:
    """Solution 1: Generate a structured API tutorial template."""

    # Build auth setup instructions based on type
    auth_instructions = {
        "bearer_token": {
            "setup": "Set your API key as an environment variable: export API_KEY=your_key_here",
            "header": "Authorization: Bearer $API_KEY",
            "python": 'headers = {"Authorization": f"Bearer {api_key}"}',
        },
        "api_key_header": {
            "setup": "Set your API key as an environment variable: export API_KEY=your_key_here",
            "header": "X-API-Key: $API_KEY",
            "python": 'headers = {"X-API-Key": api_key}',
        },
        "basic_auth": {
            "setup": "Set your credentials: export API_USER=user API_PASS=pass",
            "header": "Authorization: Basic <base64(user:pass)>",
            "python": 'auth = (username, password)',
        },
    }

    auth_info = auth_instructions.get(auth_type, auth_instructions["bearer_token"])

    # Introduction section
    sections = [
        {
            "title": "Introduction",
            "content": (
                f"This tutorial walks you through using the {api_name}. "
                f"You will learn how to authenticate, make your first request, "
                f"and use each endpoint effectively."
            ),
            "code_blocks": [],
        },
        {
            "title": "Prerequisites",
            "content": (
                f"Before you begin, ensure you have:\n"
                f"- An API key (sign up at the developer portal)\n"
                f"- Python 3.8+ installed (for Python examples)\n"
                f"- curl installed (for command-line examples)\n\n"
                f"Authentication setup:\n{auth_info['setup']}"
            ),
            "code_blocks": [
                {"language": "bash", "code": f"pip install requests"},
                {"language": "python", "code": (
                    f"import requests\n\n"
                    f"api_key = os.environ['API_KEY']\n"
                    f"base_url = '{base_url}'\n"
                    f"{auth_info['python']}"
                )},
            ],
        },
    ]

    # Quick Start: pick the simplest endpoint (fewest required params)
    simplest = min(
        endpoints,
        key=lambda ep: sum(1 for p in ep.parameters if p.get("required", False)),
    )
    curl_example = _build_curl_example(simplest, base_url, auth_info["header"])
    python_example = _build_python_example(simplest, base_url, auth_type)

    sections.append({
        "title": "Quick Start",
        "content": (
            f"Let's make your first API call using the {simplest.path} endpoint. "
            f"{simplest.description}."
        ),
        "code_blocks": [
            {"language": "bash", "code": curl_example},
            {"language": "python", "code": python_example},
        ],
    })

    # Per-endpoint sections
    for ep in endpoints:
        # Build parameter table as a list of dicts for structured output
        param_table = []
        for param in ep.parameters:
            param_table.append({
                "name": param["name"],
                "type": param.get("type", "string"),
                "required": param.get("required", False),
                "description": param.get("description", ""),
            })

        ep_curl = _build_curl_example(ep, base_url, auth_info["header"])
        ep_python = _build_python_example(ep, base_url, auth_type)

        code_blocks = [
            {"language": "bash", "code": ep_curl},
            {"language": "python", "code": ep_python},
        ]
        if ep.response_body:
            code_blocks.append({
                "language": "json",
                "code": json.dumps(ep.response_body, indent=2),
            })

        sections.append({
            "title": f"{ep.method} {ep.path}",
            "content": ep.description,
            "parameters": param_table,
            "code_blocks": code_blocks,
        })

    # Troubleshooting section
    sections.append({
        "title": "Troubleshooting",
        "content": (
            "Common errors and solutions:\n\n"
            "- **401 Unauthorized**: Check your API key is valid and properly formatted.\n"
            "- **400 Bad Request**: Verify required parameters are included.\n"
            "- **429 Too Many Requests**: Implement exponential backoff.\n"
            "- **500 Internal Server Error**: Retry after a brief delay. Contact support if persistent."
        ),
        "code_blocks": [],
    })

    # Next steps section
    sections.append({
        "title": "Next Steps",
        "content": (
            f"Now that you know the basics of the {api_name}, explore:\n"
            f"- Advanced parameters and options\n"
            f"- Streaming responses for real-time output\n"
            f"- Error handling best practices\n"
            f"- Rate limiting and usage optimization"
        ),
        "code_blocks": [],
    })

    return {
        "title": f"{api_name} Tutorial",
        "sections": sections,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "endpoint_count": len(endpoints),
            "auth_type": auth_type,
        },
    }


def _build_curl_example(ep: APIEndpoint, base_url: str, auth_header: str) -> str:
    """Helper: build a curl command for an endpoint."""
    url = f"{base_url}{ep.path}"
    parts = [f'curl -X {ep.method} "{url}"']
    parts.append(f'  -H "{auth_header}"')
    parts.append('  -H "Content-Type: application/json"')
    if ep.request_body:
        body = json.dumps(ep.request_body, indent=2)
        parts.append(f"  -d '{body}'")
    return " \\\n".join(parts)


def _build_python_example(ep: APIEndpoint, base_url: str, auth_type: str) -> str:
    """Helper: build a Python requests example for an endpoint."""
    lines = ["import requests", "", f'url = "{base_url}{ep.path}"']
    if auth_type == "bearer_token":
        lines.append('headers = {"Authorization": f"Bearer {api_key}"}')
    elif auth_type == "api_key_header":
        lines.append('headers = {"X-API-Key": api_key}')
    else:
        lines.append('auth = (username, password)')

    if ep.method == "GET":
        if auth_type == "basic_auth":
            lines.append("response = requests.get(url, auth=auth)")
        else:
            lines.append("response = requests.get(url, headers=headers)")
    else:
        if ep.request_body:
            lines.append(f"data = {json.dumps(ep.request_body, indent=4)}")
            if auth_type == "basic_auth":
                lines.append("response = requests.post(url, json=data, auth=auth)")
            else:
                lines.append("response = requests.post(url, json=data, headers=headers)")
        else:
            if auth_type == "basic_auth":
                lines.append("response = requests.post(url, auth=auth)")
            else:
                lines.append("response = requests.post(url, headers=headers)")

    lines.append("print(response.json())")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Solution 2: Code Sample Validator
# ---------------------------------------------------------------------------
# Design notes:
# - Uses Python's ast module for reliable parsing (no regex hacks)
# - Walks the AST to find imports, docstrings, type hints, and try/except
# - Completeness score is a weighted average of quality checks
# - Catches SyntaxError gracefully for broken code
# ---------------------------------------------------------------------------

def solution_2_code_sample_validator(
    code: str,
    expected_imports: list[str] | None = None,
    require_error_handling: bool = False,
    require_type_hints: bool = False,
) -> ValidationResult:
    """Solution 2: Validate a Python code sample for documentation quality."""

    issues: list[str] = []

    # 1. Check syntax
    try:
        tree = ast.parse(code)
        syntax_ok = True
    except SyntaxError as e:
        return ValidationResult(
            is_valid=False,
            syntax_ok=False,
            imports_found=[],
            imports_missing=expected_imports or [],
            has_main_guard=False,
            has_error_handling=False,
            has_type_hints=False,
            has_docstrings=False,
            completeness_score=0.0,
            issues=[f"Syntax error: {e}"],
        )

    # 2. Find all imports
    imports_found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports_found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports_found.append(node.module)

    # Check expected imports
    imports_missing = []
    if expected_imports:
        for imp in expected_imports:
            if not any(imp in found for found in imports_found):
                imports_missing.append(imp)
                issues.append(f"Missing expected import: {imp}")

    # 3. Check for docstrings
    has_docstrings = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                has_docstrings = True
                break

    if not has_docstrings:
        issues.append("No docstrings found on functions or classes")

    # 4. Check for type hints
    has_type_hints = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check return annotation
            if node.returns is not None:
                has_type_hints = True
                break
            # Check argument annotations
            for arg in node.args.args:
                if arg.annotation is not None:
                    has_type_hints = True
                    break
            if has_type_hints:
                break

    if require_type_hints and not has_type_hints:
        issues.append("Type hints required but not found")

    # 5. Check for error handling (try/except)
    has_error_handling = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            has_error_handling = True
            break

    if require_error_handling and not has_error_handling:
        issues.append("Error handling (try/except) required but not found")

    # 6. Check for main guard
    has_main_guard = False
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Check if it's: if __name__ == "__main__"
            test = node.test
            if isinstance(test, ast.Compare):
                left = test.left
                if isinstance(left, ast.Name) and left.id == "__name__":
                    has_main_guard = True
                    break

    # 7. Compute completeness score
    checks = {
        "syntax": (True, 0.30),       # Syntax is critical
        "docstrings": (has_docstrings, 0.15),
        "type_hints": (has_type_hints, 0.15),
        "error_handling": (has_error_handling, 0.15),
        "main_guard": (has_main_guard, 0.10),
        "imports": (len(imports_missing) == 0, 0.15),
    }

    completeness_score = sum(
        weight for passed, weight in checks.values() if passed
    )

    is_valid = syntax_ok and len(imports_missing) == 0
    if require_error_handling:
        is_valid = is_valid and has_error_handling
    if require_type_hints:
        is_valid = is_valid and has_type_hints

    return ValidationResult(
        is_valid=is_valid,
        syntax_ok=syntax_ok,
        imports_found=imports_found,
        imports_missing=imports_missing,
        has_main_guard=has_main_guard,
        has_error_handling=has_error_handling,
        has_type_hints=has_type_hints,
        has_docstrings=has_docstrings,
        completeness_score=round(completeness_score, 2),
        issues=issues,
    )


# ---------------------------------------------------------------------------
# Solution 3: Technical Requirements Extractor
# ---------------------------------------------------------------------------
# Design notes:
# - Uses sentence-level analysis to extract requirements
# - Maps keyword strength to priority (must > should > could/nice)
# - Categorizes by domain: functional, non-functional, integration
# - Assigns complexity based on requirement breadth
# ---------------------------------------------------------------------------

def solution_3_requirements_extractor(
    business_description: str,
    keywords_to_categories: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Solution 3: Extract structured technical requirements from business text."""

    # Default keyword-to-category mapping
    default_mappings = {
        # Functional keywords
        "handle": "functional", "process": "functional", "generate": "functional",
        "display": "functional", "create": "functional", "support": "functional",
        "allow": "functional", "enable": "functional", "provide": "functional",
        "send": "functional", "receive": "functional", "store": "functional",
        "chatbot": "functional", "respond": "functional",
        # Non-functional keywords
        "fast": "non-functional", "secure": "non-functional",
        "scale": "non-functional", "scalable": "non-functional",
        "available": "non-functional", "reliable": "non-functional",
        "performance": "non-functional", "concurrent": "non-functional",
        "latency": "non-functional", "uptime": "non-functional",
        "compliant": "non-functional", "soc2": "non-functional",
        # Integration keywords
        "integrate": "integration", "connect": "integration",
        "api": "integration", "database": "integration",
        "import": "integration", "export": "integration",
        "salesforce": "integration", "zendesk": "integration",
        "postgresql": "integration", "redis": "integration",
        "webhook": "integration", "sync": "integration",
    }
    mappings = keywords_to_categories or default_mappings

    # Priority keywords
    must_keywords = {"must", "shall", "required", "need to", "needs to", "critical"}
    should_keywords = {"should", "expected", "important", "recommended"}
    nice_keywords = {"could", "nice to have", "would be nice", "optional", "ideally"}

    # Split into sentences
    sentences = re.split(r'[.!?]+', business_description)
    sentences = [s.strip() for s in sentences if s.strip()]

    requirements: list[dict[str, Any]] = []
    req_counter = 0

    for sentence in sentences:
        lower = sentence.lower()

        # Determine priority
        priority = "should-have"  # default
        for kw in must_keywords:
            if kw in lower:
                priority = "must-have"
                break
        if priority != "must-have":
            for kw in nice_keywords:
                if kw in lower:
                    priority = "nice-to-have"
                    break

        # Determine category by scanning for keywords
        category = "functional"  # default
        for keyword, cat in mappings.items():
            if keyword in lower:
                category = cat
                break

        # Only extract if the sentence describes a requirement (has action/need)
        action_indicators = (
            must_keywords | should_keywords | nice_keywords |
            {"need", "want", "require", "will", "have to"}
        )
        has_indicator = any(ind in lower for ind in action_indicators)

        # Also treat sentences with category keywords as requirements
        has_category_keyword = any(kw in lower for kw in mappings)

        if has_indicator or has_category_keyword:
            req_counter += 1
            req_id = f"REQ-{req_counter:03d}"

            # Estimate complexity based on sentence length and keyword count
            word_count = len(sentence.split())
            matching_keywords = sum(1 for kw in mappings if kw in lower)
            if word_count > 20 or matching_keywords > 3:
                complexity = "high"
            elif word_count > 10 or matching_keywords > 1:
                complexity = "medium"
            else:
                complexity = "low"

            # Create a concise title from the sentence
            title = sentence.strip()
            if len(title) > 80:
                title = title[:77] + "..."

            requirements.append(
                asdict(TechnicalRequirement(
                    id=req_id,
                    category=category,
                    title=title,
                    description=sentence.strip(),
                    priority=priority,
                    estimated_complexity=complexity,
                    dependencies=[],
                ))
            )

    # Build summary
    category_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    for req in requirements:
        category_counts[req["category"]] = category_counts.get(req["category"], 0) + 1
        priority_counts[req["priority"]] = priority_counts.get(req["priority"], 0) + 1

    return {
        "requirements": requirements,
        "summary": {
            "total": len(requirements),
            "by_category": category_counts,
            "by_priority": priority_counts,
        },
        "raw_input_length": len(business_description),
    }


# ---------------------------------------------------------------------------
# Solution 4: Migration Guide Generator
# ---------------------------------------------------------------------------
# Design notes:
# - Performs structural diff between old and new endpoint specs
# - Classifies each change as breaking or non-breaking
# - Generates migration actions (what the developer must do)
# - Produces a human-readable summary at the end
# ---------------------------------------------------------------------------

def solution_4_migration_guide_generator(
    old_version: str,
    new_version: str,
    old_endpoints: dict[str, dict],
    new_endpoints: dict[str, dict],
) -> dict[str, Any]:
    """Solution 4: Generate a migration guide by diffing two API versions."""

    changes: list[dict[str, Any]] = []

    old_paths = set(old_endpoints.keys())
    new_paths = set(new_endpoints.keys())

    # 1. Removed endpoints (BREAKING)
    for path in sorted(old_paths - new_paths):
        changes.append(asdict(APIChange(
            change_type="removed",
            component="endpoint",
            path=path,
            old_value=old_endpoints[path],
            new_value=None,
            breaking=True,
            migration_action=f"Remove all calls to {path}. Find the replacement endpoint in the new API.",
        )))

    # 2. Added endpoints (non-breaking)
    for path in sorted(new_paths - old_paths):
        changes.append(asdict(APIChange(
            change_type="added",
            component="endpoint",
            path=path,
            old_value=None,
            new_value=new_endpoints[path],
            breaking=False,
            migration_action=f"New endpoint {path} is available. See documentation for usage.",
        )))

    # 3. Modified endpoints (check for specific diffs)
    for path in sorted(old_paths & new_paths):
        old_spec = old_endpoints[path]
        new_spec = new_endpoints[path]

        # Check method change
        if old_spec.get("method") != new_spec.get("method"):
            changes.append(asdict(APIChange(
                change_type="modified",
                component="endpoint",
                path=path,
                old_value=old_spec["method"],
                new_value=new_spec["method"],
                breaking=True,
                migration_action=f"Update HTTP method from {old_spec['method']} to {new_spec['method']} for {path}.",
            )))

        # Check parameters
        old_params = old_spec.get("parameters", {})
        new_params = new_spec.get("parameters", {})
        old_param_names = set(old_params.keys())
        new_param_names = set(new_params.keys())

        # Removed parameters
        for param in sorted(old_param_names - new_param_names):
            is_required = old_params[param].get("required", False)
            changes.append(asdict(APIChange(
                change_type="removed",
                component="parameter",
                path=f"{path}.{param}",
                old_value=old_params[param],
                new_value=None,
                breaking=is_required,
                migration_action=f"Remove parameter '{param}' from {path} requests.",
            )))

        # Added parameters
        for param in sorted(new_param_names - old_param_names):
            is_required = new_params[param].get("required", False)
            changes.append(asdict(APIChange(
                change_type="added",
                component="parameter",
                path=f"{path}.{param}",
                old_value=None,
                new_value=new_params[param],
                breaking=is_required,
                migration_action=(
                    f"Add required parameter '{param}' to {path} requests."
                    if is_required
                    else f"Optional parameter '{param}' is now available for {path}."
                ),
            )))

        # Modified parameters (type or required changed)
        for param in sorted(old_param_names & new_param_names):
            if old_params[param] != new_params[param]:
                old_type = old_params[param].get("type")
                new_type = new_params[param].get("type")
                breaking = old_type != new_type  # Type change is breaking
                changes.append(asdict(APIChange(
                    change_type="modified",
                    component="parameter",
                    path=f"{path}.{param}",
                    old_value=old_params[param],
                    new_value=new_params[param],
                    breaking=breaking,
                    migration_action=f"Update parameter '{param}' in {path}: type changed from {old_type} to {new_type}.",
                )))

        # Check response field changes
        old_fields = set(old_spec.get("response_fields", []))
        new_fields = set(new_spec.get("response_fields", []))

        for resp_field in sorted(old_fields - new_fields):
            changes.append(asdict(APIChange(
                change_type="removed",
                component="response_field",
                path=f"{path}.response.{resp_field}",
                old_value=resp_field,
                new_value=None,
                breaking=True,
                migration_action=f"Response field '{resp_field}' has been removed from {path}. Update your parsing code.",
            )))

        for resp_field in sorted(new_fields - old_fields):
            changes.append(asdict(APIChange(
                change_type="added",
                component="response_field",
                path=f"{path}.response.{resp_field}",
                old_value=None,
                new_value=resp_field,
                breaking=False,
                migration_action=f"New response field '{resp_field}' is available in {path}.",
            )))

    breaking_count = sum(1 for c in changes if c["breaking"])
    non_breaking_count = len(changes) - breaking_count

    summary = (
        f"Migration from {old_version} to {new_version}: "
        f"{len(changes)} total changes ({breaking_count} breaking, "
        f"{non_breaking_count} non-breaking)."
    )

    return {
        "from_version": old_version,
        "to_version": new_version,
        "changes": changes,
        "breaking_changes_count": breaking_count,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Solution 5: Changelog Formatter
# ---------------------------------------------------------------------------
# Design notes:
# - Follows Keep a Changelog (https://keepachangelog.com) conventions
# - Categories appear in standardized order, empty ones omitted
# - Issue references become clickable links if repo_url is provided
# - Includes a comparison link between versions for diff navigation
# ---------------------------------------------------------------------------

def solution_5_changelog_formatter(
    version: str,
    release_date: str,
    changes: list[ChangeEntry],
    previous_version: str = "",
    repo_url: str = "",
) -> str:
    """Solution 5: Format changes into a Keep a Changelog style document."""

    # Standard category ordering per Keep a Changelog
    category_order = ["added", "changed", "deprecated", "removed", "fixed", "security"]
    category_titles = {
        "added": "Added",
        "changed": "Changed",
        "deprecated": "Deprecated",
        "removed": "Removed",
        "fixed": "Fixed",
        "security": "Security",
    }

    # Group changes by category
    grouped: dict[str, list[ChangeEntry]] = {}
    for change in changes:
        cat = change.category.lower()
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(change)

    # Build header with optional comparison link
    if previous_version and repo_url:
        header = f"## [{version}]({repo_url}/compare/{previous_version}...{version}) - {release_date}"
    else:
        header = f"## [{version}] - {release_date}"

    lines = [header, ""]

    # Build each category section in standard order
    for cat in category_order:
        if cat not in grouped:
            continue

        lines.append(f"### {category_titles[cat]}")
        for entry in grouped[cat]:
            description = entry.description
            # Add issue reference as link if available
            if entry.issue_ref and repo_url:
                ref_num = entry.issue_ref.lstrip("#")
                description += f" ([{entry.issue_ref}]({repo_url}/issues/{ref_num}))"
            elif entry.issue_ref:
                description += f" ({entry.issue_ref})"
            lines.append(f"- {description}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Solution 6: Architecture Decision Record (ADR) Template
# ---------------------------------------------------------------------------
# Design notes:
# - Follows the Nygard ADR format (the most widely used)
# - Structured for both human readability and machine parsing
# - Includes pros/cons matrix for objective comparison
# - Timestamps enable chronological ADR tracking
# ---------------------------------------------------------------------------

def solution_6_adr_generator(
    title: str,
    context: str,
    options: list[dict[str, Any]],
    decision: str,
    consequences: list[str],
    decision_makers: list[str] | None = None,
    status: str = "proposed",
) -> dict[str, Any]:
    """Solution 6: Generate an Architecture Decision Record (ADR)."""

    valid_statuses = {"proposed", "accepted", "deprecated", "superseded"}
    if status not in valid_statuses:
        status = "proposed"

    # Generate ADR number from timestamp (sortable)
    adr_number = datetime.now().strftime("%Y%m%d")
    current_date = datetime.now().strftime("%Y-%m-%d")

    sections = []

    # Context section
    sections.append({
        "heading": "Context",
        "content": context,
    })

    # Options Considered section
    options_content = []
    for i, opt in enumerate(options, 1):
        opt_text = f"**Option {i}: {opt['name']}**\n"
        opt_text += f"  Effort: {opt.get('effort', 'unknown')}\n"
        opt_text += "  Pros:\n"
        for pro in opt.get("pros", []):
            opt_text += f"    - {pro}\n"
        opt_text += "  Cons:\n"
        for con in opt.get("cons", []):
            opt_text += f"    - {con}\n"
        options_content.append(opt_text)

    sections.append({
        "heading": "Options Considered",
        "content": "\n".join(options_content),
    })

    # Decision section
    sections.append({
        "heading": "Decision",
        "content": decision,
    })

    # Consequences section
    consequences_text = "\n".join(f"- {c}" for c in consequences)
    sections.append({
        "heading": "Consequences",
        "content": consequences_text,
    })

    # Participants section
    if decision_makers:
        participants_text = "\n".join(f"- {p}" for p in decision_makers)
    else:
        participants_text = "- (not specified)"
    sections.append({
        "heading": "Participants",
        "content": participants_text,
    })

    return {
        "adr_number": adr_number,
        "title": title,
        "date": current_date,
        "status": status,
        "sections": sections,
    }


# ---------------------------------------------------------------------------
# Solution 7: Runbook Template Generator
# ---------------------------------------------------------------------------
# Design notes:
# - Structured for 3 AM on-call readability (clear steps, no ambiguity)
# - Each step has command, expected output, and rollback
# - Severity drives escalation urgency and SLA expectations
# - Estimated time = 2 minutes per step (industry heuristic)
# ---------------------------------------------------------------------------

def solution_7_runbook_generator(
    title: str,
    service_name: str,
    scenario: str,
    steps: list[dict[str, str]],
    escalation_contacts: list[dict[str, str]] | None = None,
    severity: str = "medium",
) -> dict[str, Any]:
    """Solution 7: Generate a structured runbook template."""

    valid_severities = {"critical", "high", "medium", "low"}
    if severity not in valid_severities:
        severity = "medium"

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Build RunbookStep objects
    runbook_steps = []
    for i, step_dict in enumerate(steps, 1):
        runbook_steps.append(asdict(RunbookStep(
            step_number=i,
            action=step_dict.get("action", ""),
            command=step_dict.get("command", ""),
            expected_output=step_dict.get("expected_output", ""),
            rollback=step_dict.get("rollback", ""),
            warning=step_dict.get("warning", ""),
        )))

    estimated_time = len(steps) * 2  # 2 minutes per step

    # Build sections
    sections = [
        {
            "heading": "Overview",
            "content": f"This runbook covers: {scenario}",
        },
        {
            "heading": "Prerequisites",
            "content": (
                f"- SSH access to {service_name} servers\n"
                f"- Admin credentials for monitoring dashboard\n"
                f"- Access to deployment pipeline\n"
                f"- Familiarity with service architecture"
            ),
        },
        {
            "heading": "Diagnostic Steps",
            "content": (
                f"Before starting resolution, confirm the issue:\n"
                f"1. Check monitoring dashboard for {service_name}\n"
                f"2. Review recent deployments and changes\n"
                f"3. Check dependent service health"
            ),
        },
        {
            "heading": "Resolution Steps",
            "content": "Follow the steps below in order.",
        },
        {
            "heading": "Verification",
            "content": (
                f"After completing resolution:\n"
                f"1. Confirm {service_name} health check returns 200\n"
                f"2. Monitor error rate for 10 minutes\n"
                f"3. Verify customer-facing functionality"
            ),
        },
    ]

    # Escalation section
    if escalation_contacts:
        contact_lines = []
        for contact in escalation_contacts:
            contact_lines.append(
                f"- {contact.get('name', 'N/A')} ({contact.get('role', 'N/A')}): "
                f"{contact.get('contact', 'N/A')}"
            )
        escalation_content = "\n".join(contact_lines)
    else:
        escalation_content = (
            "- Escalate to on-call engineering lead if issue is not resolved "
            "within estimated time."
        )

    sections.append({
        "heading": "Escalation",
        "content": escalation_content,
    })

    return {
        "title": title,
        "service": service_name,
        "severity": severity,
        "last_updated": current_date,
        "sections": sections,
        "steps": runbook_steps,
        "estimated_time_minutes": estimated_time,
    }


# ---------------------------------------------------------------------------
# Solution 8: Incident Postmortem Formatter
# ---------------------------------------------------------------------------
# Design notes:
# - Follows Google SRE blameless postmortem format
# - Auto-computes detection/response/resolution times from timeline
# - Action items are concrete, assigned, and dated
# - Structured for both human review and automated tracking
# ---------------------------------------------------------------------------

def solution_8_postmortem_formatter(
    title: str,
    incident_date: str,
    severity: str,
    duration_minutes: int,
    summary: str,
    impact: str,
    timeline: list[TimelineEvent],
    root_cause: str,
    action_items: list[dict[str, str]],
    lessons_learned: list[str],
) -> dict[str, Any]:
    """Solution 8: Format an incident postmortem document."""

    valid_severities = {"SEV1", "SEV2", "SEV3", "SEV4"}
    if severity not in valid_severities:
        severity = "SEV3"

    # Build timeline as list of dicts
    timeline_dicts = [asdict(event) for event in timeline]

    # Compute metrics from timeline
    # Detection time = time between first and second event
    # Response time = time between first alert and first human action
    # Resolution time = full duration
    detection_time_minutes = 0
    response_time_minutes = 0
    if len(timeline) >= 2:
        try:
            t0 = datetime.fromisoformat(timeline[0].timestamp.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(timeline[1].timestamp.replace("Z", "+00:00"))
            detection_time_minutes = int((t1 - t0).total_seconds() / 60)
        except (ValueError, IndexError):
            pass
    if len(timeline) >= 3:
        try:
            t0 = datetime.fromisoformat(timeline[0].timestamp.replace("Z", "+00:00"))
            # Find first human action (non-system actor)
            for event in timeline[1:]:
                if event.actor and event.actor not in ("PagerDuty", "Datadog", "system", "auto"):
                    t_human = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
                    response_time_minutes = int((t_human - t0).total_seconds() / 60)
                    break
        except (ValueError, IndexError):
            pass

    return {
        "title": title,
        "incident_date": incident_date,
        "severity": severity,
        "duration_minutes": duration_minutes,
        "summary": summary,
        "impact": impact,
        "timeline": timeline_dicts,
        "root_cause": root_cause,
        "action_items": action_items,
        "lessons_learned": lessons_learned,
        "metrics": {
            "detection_time_minutes": detection_time_minutes,
            "response_time_minutes": response_time_minutes,
            "resolution_time_minutes": duration_minutes,
        },
    }


# ---------------------------------------------------------------------------
# Solution 9: Technical Complexity Estimator
# ---------------------------------------------------------------------------
# Design notes:
# - Scoring rubric based on common project estimation frameworks
# - Weights reflect typical impact on timeline in AI/ML projects
# - ML and real-time requirements are weighted heavily (common underestimates)
# - Team size inversely affects risk (small team + large scope = danger)
# ---------------------------------------------------------------------------

def solution_9_complexity_estimator(
    project_name: str,
    integrations: list[str],
    data_sources: int,
    user_types: int,
    compliance_requirements: list[str],
    has_ml_component: bool = False,
    has_realtime_requirement: bool = False,
    team_size: int = 1,
) -> dict[str, Any]:
    """Solution 9: Estimate technical complexity of a project."""

    factors: list[dict[str, Any]] = []

    # 1. Integration complexity (weight: 0.20)
    n_integrations = len(integrations)
    if n_integrations == 0:
        int_score = 1
    elif n_integrations <= 2:
        int_score = 2
    elif n_integrations <= 4:
        int_score = 3
    elif n_integrations <= 7:
        int_score = 4
    else:
        int_score = 5
    factors.append(asdict(ComplexityFactor(
        name="Integration complexity",
        score=int_score,
        weight=0.20,
        rationale=f"{n_integrations} integrations: {', '.join(integrations) if integrations else 'none'}",
    )))

    # 2. Data complexity (weight: 0.15)
    if data_sources <= 1:
        data_score = 1
    elif data_sources <= 3:
        data_score = 2
    elif data_sources <= 5:
        data_score = 3
    elif data_sources <= 8:
        data_score = 4
    else:
        data_score = 5
    factors.append(asdict(ComplexityFactor(
        name="Data complexity",
        score=data_score,
        weight=0.15,
        rationale=f"{data_sources} data sources",
    )))

    # 3. User complexity (weight: 0.10)
    if user_types <= 1:
        user_score = 1
    elif user_types == 2:
        user_score = 2
    elif user_types <= 4:
        user_score = 3
    else:
        user_score = 4
    factors.append(asdict(ComplexityFactor(
        name="User complexity",
        score=user_score,
        weight=0.10,
        rationale=f"{user_types} distinct user types",
    )))

    # 4. Compliance complexity (weight: 0.15)
    n_compliance = len(compliance_requirements)
    compliance_lower = [c.lower() for c in compliance_requirements]
    has_strict = any(c in compliance_lower for c in ["hipaa", "pci", "pci-dss"])
    if n_compliance == 0:
        comp_score = 1
    elif n_compliance == 1:
        comp_score = 2
    elif n_compliance == 2:
        comp_score = 3
    elif has_strict:
        comp_score = 5
    else:
        comp_score = 4
    factors.append(asdict(ComplexityFactor(
        name="Compliance complexity",
        score=comp_score,
        weight=0.15,
        rationale=f"{n_compliance} compliance requirements: {', '.join(compliance_requirements) if compliance_requirements else 'none'}",
    )))

    # 5. ML complexity (weight: 0.20)
    if not has_ml_component:
        ml_score = 1
    elif has_realtime_requirement:
        ml_score = 5
    else:
        ml_score = 4
    factors.append(asdict(ComplexityFactor(
        name="ML complexity",
        score=ml_score,
        weight=0.20,
        rationale=f"ML: {'yes' if has_ml_component else 'no'}, Real-time: {'yes' if has_realtime_requirement else 'no'}",
    )))

    # 6. Real-time requirements (weight: 0.10)
    if not has_realtime_requirement:
        rt_score = 1
    elif has_ml_component:
        rt_score = 5
    else:
        rt_score = 3
    factors.append(asdict(ComplexityFactor(
        name="Real-time requirements",
        score=rt_score,
        weight=0.10,
        rationale=f"Real-time: {'yes' if has_realtime_requirement else 'no'}",
    )))

    # 7. Team capacity (weight: 0.10)
    if team_size >= 5:
        team_score = 1
    elif team_size >= 3:
        team_score = 2
    elif team_size == 2:
        team_score = 3
    else:
        team_score = 4
    factors.append(asdict(ComplexityFactor(
        name="Team capacity",
        score=team_score,
        weight=0.10,
        rationale=f"{team_size} engineers",
    )))

    # Compute weighted score
    weighted_score = sum(f["score"] * f["weight"] for f in factors)
    weighted_score = round(weighted_score, 2)

    # Determine complexity level
    if weighted_score < 2.0:
        complexity_level = "low"
    elif weighted_score <= 3.5:
        complexity_level = "medium"
    else:
        complexity_level = "high"

    # Estimate weeks based on complexity and team size
    base_weeks = {"low": 4, "medium": 8, "high": 16}
    estimated_weeks = max(2, base_weeks[complexity_level] // max(1, team_size))

    # Identify risk factors (score >= 4)
    risk_factors = [f["name"] for f in factors if f["score"] >= 4]

    # Generate recommendations
    recommendations = []
    if risk_factors:
        recommendations.append(f"High-risk areas: {', '.join(risk_factors)}. Consider additional resources or phased approach.")
    if has_ml_component and team_size < 3:
        recommendations.append("ML projects benefit from dedicated ML engineers. Consider expanding the team.")
    if has_realtime_requirement:
        recommendations.append("Real-time requirements need load testing early. Plan for performance validation sprints.")
    if has_strict:
        recommendations.append("Strict compliance requirements (HIPAA/PCI) need security review before development begins.")
    if not recommendations:
        recommendations.append("Project is well-scoped. Standard development process should suffice.")

    return {
        "project_name": project_name,
        "factors": factors,
        "weighted_score": weighted_score,
        "complexity_level": complexity_level,
        "estimated_weeks": estimated_weeks,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
    }


# ---------------------------------------------------------------------------
# Solution 10: Documentation Coverage Checker
# ---------------------------------------------------------------------------
# Design notes:
# - Walks the AST to find all public classes, functions, and methods
# - Skips private items (prefixed with _) as they are internal
# - Checks for both docstrings and type hints as quality indicators
# - Reports per-item details for targeted documentation improvements
# ---------------------------------------------------------------------------

def solution_10_doc_coverage_checker(
    source_code: str,
    module_name: str = "module",
) -> CoverageReport:
    """Solution 10: Check documentation coverage of Python source code."""

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return CoverageReport(
            total_public_items=0,
            documented_items=0,
            undocumented_items=[],
            coverage_percentage=0.0,
            items=[],
        )

    items: list[dict[str, Any]] = []

    def _has_docstring(node: ast.AST) -> bool:
        """Check if an AST node has a docstring."""
        if hasattr(node, "body") and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                val = first.value
                if isinstance(val.value, str):
                    return True
        return False

    def _has_type_hints(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if a function has any type annotations."""
        if node.returns is not None:
            return True
        for arg in node.args.args:
            if arg.annotation is not None:
                return True
        return False

    # Process top-level definitions
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            has_doc = _has_docstring(node)
            items.append({
                "name": node.name,
                "type": "class",
                "has_docstring": has_doc,
                "line_number": node.lineno,
                "has_type_hints": False,  # Classes don't have type hints in the same way
            })

            # Check methods within the class
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not child.name.startswith("_"):
                        method_has_doc = _has_docstring(child)
                        items.append({
                            "name": f"{node.name}.{child.name}",
                            "type": "method",
                            "has_docstring": method_has_doc,
                            "line_number": child.lineno,
                            "has_type_hints": _has_type_hints(child),
                        })

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            has_doc = _has_docstring(node)
            items.append({
                "name": node.name,
                "type": "function",
                "has_docstring": has_doc,
                "line_number": node.lineno,
                "has_type_hints": _has_type_hints(node),
            })

    total_public = len(items)
    documented = sum(1 for item in items if item["has_docstring"])
    undocumented = [item["name"] for item in items if not item["has_docstring"]]
    coverage_pct = (documented / total_public * 100) if total_public > 0 else 0.0

    return CoverageReport(
        total_public_items=total_public,
        documented_items=documented,
        undocumented_items=undocumented,
        coverage_percentage=round(coverage_pct, 1),
        items=items,
    )


# ---------------------------------------------------------------------------
# Solution 11: FAQ Generator from Support Tickets
# ---------------------------------------------------------------------------
# Design notes:
# - Uses Jaccard similarity on significant words for clustering
# - Greedy single-linkage clustering: if a ticket is similar to any ticket
#   already in a cluster, it joins that cluster
# - FAQ question is generated from the most common subject words
# - FAQ answer is the longest resolution (assumed to be most complete)
# ---------------------------------------------------------------------------

def solution_11_faq_generator(
    tickets: list[SupportTicket],
    similarity_threshold: float = 0.3,
    min_cluster_size: int = 2,
) -> dict[str, Any]:
    """Solution 11: Generate FAQ entries from support tickets."""

    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "how", "what", "why",
        "can", "do", "does", "not", "with", "for", "from", "this", "that",
        "have", "has", "will", "been", "being",
    }

    def _extract_words(text: str) -> set[str]:
        """Extract significant words from text."""
        # Lowercase, strip punctuation, filter short words and stopwords
        words = re.findall(r'[a-z]+', text.lower())
        return {w for w in words if len(w) > 3 and w not in stopwords}

    def _jaccard(set_a: set[str], set_b: set[str]) -> float:
        """Compute Jaccard similarity between two sets."""
        if not set_a or not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union)

    # Extract word sets for each ticket
    ticket_words: list[tuple[SupportTicket, set[str]]] = []
    for ticket in tickets:
        combined_text = f"{ticket.subject} {ticket.body}"
        words = _extract_words(combined_text)
        ticket_words.append((ticket, words))

    # Greedy clustering by similarity
    clusters: list[list[int]] = []  # list of ticket index groups
    assigned: set[int] = set()

    for i in range(len(ticket_words)):
        if i in assigned:
            continue
        cluster = [i]
        assigned.add(i)

        for j in range(i + 1, len(ticket_words)):
            if j in assigned:
                continue
            # Check similarity against any ticket already in this cluster
            for k in cluster:
                sim = _jaccard(ticket_words[k][1], ticket_words[j][1])
                if sim >= similarity_threshold:
                    cluster.append(j)
                    assigned.add(j)
                    break

        clusters.append(cluster)

    # Build FAQs from clusters meeting minimum size
    faqs: list[dict[str, Any]] = []
    covered_ticket_ids: set[str] = set()

    for cluster_indices in clusters:
        if len(cluster_indices) < min_cluster_size:
            continue

        cluster_tickets = [ticket_words[i][0] for i in cluster_indices]

        # Generate question from the most common subject
        # Use the subject of the ticket with the most representative words
        best_subject = max(cluster_tickets, key=lambda t: len(t.subject))
        question = f"How do I resolve: {best_subject.subject}?"

        # Generate answer from the longest/most detailed resolution
        resolutions = [t.resolution for t in cluster_tickets if t.resolution]
        if resolutions:
            answer = max(resolutions, key=len)
        else:
            answer = "Please contact support for assistance with this issue."

        # Determine category from tickets
        categories = [t.category for t in cluster_tickets if t.category]
        category = max(set(categories), key=categories.count) if categories else "general"

        source_ids = [t.id for t in cluster_tickets]
        covered_ticket_ids.update(source_ids)

        faqs.append(asdict(FAQEntry(
            question=question,
            answer=answer,
            category=category,
            source_ticket_ids=source_ids,
            frequency=len(cluster_tickets),
        )))

    # Sort by frequency descending
    faqs.sort(key=lambda f: f["frequency"], reverse=True)

    # Find uncategorized tickets
    all_ids = {t.id for t in tickets}
    uncategorized = sorted(all_ids - covered_ticket_ids)

    total_tickets = len(tickets)
    tickets_covered = len(covered_ticket_ids)
    coverage_pct = (tickets_covered / total_tickets * 100) if total_tickets > 0 else 0.0

    return {
        "faqs": faqs,
        "total_tickets": total_tickets,
        "tickets_covered": tickets_covered,
        "coverage_percentage": round(coverage_pct, 1),
        "uncategorized_ticket_ids": uncategorized,
    }


# ---------------------------------------------------------------------------
# Solution 12: Release Notes Formatter
# ---------------------------------------------------------------------------
# Design notes:
# - Three audience modes reflect real stakeholder communication patterns
# - Developers need migration details; PMs need user impact; execs need ROI
# - Breaking changes are always surfaced prominently for developers
# - Infrastructure items are hidden from non-technical audiences
# ---------------------------------------------------------------------------

def solution_12_release_notes_formatter(
    version: str,
    release_date: str,
    features: list[ReleaseFeature],
    audience: str = "developer",
) -> dict[str, Any]:
    """Solution 12: Format release notes tailored to a specific audience."""

    has_breaking = any(f.breaking for f in features)

    if audience == "developer":
        title = f"Release Notes v{version}"
        sections = []

        # Lead with breaking changes
        breaking_features = [f for f in features if f.breaking]
        if breaking_features:
            sections.append({
                "heading": "Breaking Changes",
                "items": [
                    {
                        "title": f.title,
                        "description": f.technical_description,
                        "migration_note": f"Action required: {f.technical_description}",
                    }
                    for f in breaking_features
                ],
            })

        # Group remaining by category
        category_order = ["feature", "improvement", "bugfix", "infrastructure"]
        category_titles = {
            "feature": "New Features",
            "improvement": "Improvements",
            "bugfix": "Bug Fixes",
            "infrastructure": "Infrastructure",
        }
        for cat in category_order:
            cat_features = [f for f in features if f.category == cat and not f.breaking]
            if cat_features:
                sections.append({
                    "heading": category_titles.get(cat, cat.title()),
                    "items": [
                        {"title": f.title, "description": f.technical_description}
                        for f in cat_features
                    ],
                })

    elif audience == "product":
        title = f"What's New in v{version}"
        sections = []

        # Features first, then improvements; skip infrastructure
        for cat, heading in [("feature", "New Features"), ("improvement", "Improvements"),
                             ("bugfix", "Bug Fixes")]:
            cat_features = [f for f in features if f.category == cat]
            if cat_features:
                sections.append({
                    "heading": heading,
                    "items": [
                        {"title": f.title, "description": f.user_benefit}
                        for f in cat_features
                    ],
                })

    elif audience == "executive":
        title = f"Release Summary: v{version}"
        # Only features and improvements
        relevant = [f for f in features if f.category in ("feature", "improvement")]
        feature_count = sum(1 for f in relevant if f.category == "feature")
        improvement_count = sum(1 for f in relevant if f.category == "improvement")

        sections = [{
            "heading": f"Summary ({feature_count} new features, {improvement_count} improvements)",
            "items": [
                {"title": f.title, "description": f.business_impact}
                for f in relevant
            ],
        }]

    else:
        title = f"Release Notes v{version}"
        sections = []

    return {
        "title": title,
        "audience": audience,
        "version": version,
        "date": release_date,
        "sections": sections,
        "has_breaking_changes": has_breaking,
    }


# ---------------------------------------------------------------------------
# Solution 13: Customer Status Update Template Engine
# ---------------------------------------------------------------------------
# Design notes:
# - Templates mirror real status page conventions (Statuspage.io patterns)
# - External updates are reassuring and action-oriented
# - Internal updates include technical details and ownership
# - Status indicators help scanning (similar to commit conventional types)
# ---------------------------------------------------------------------------

def solution_13_status_update_engine(
    update_type: str,
    title: str,
    status: str,
    details: dict[str, Any],
    audience: str = "external",
) -> dict[str, Any]:
    """Solution 13: Generate a customer status update."""

    timestamp = datetime.now().isoformat()

    # Status indicator mapping
    status_indicators = {
        # Incident
        "investigating": "[INVESTIGATING]",
        "identified": "[IDENTIFIED]",
        "monitoring": "[MONITORING]",
        "resolved": "[RESOLVED]",
        # Maintenance
        "scheduled": "[SCHEDULED]",
        "in_progress": "[IN PROGRESS]",
        "completed": "[COMPLETED]",
        # Project
        "on_track": "[ON TRACK]",
        "at_risk": "[AT RISK]",
        "delayed": "[DELAYED]",
    }
    status_emoji = status_indicators.get(status, f"[{status.upper()}]")

    sections: list[dict[str, str]] = []
    body_parts: list[str] = []

    if update_type == "incident":
        if audience == "external":
            body_parts.append(f"{status_emoji} {title}")
            body_parts.append("")

            if status == "investigating":
                body_parts.append("We are currently investigating reports of issues.")
            elif status == "identified":
                body_parts.append("We have identified the cause of the issue and are working on a resolution.")
            elif status == "monitoring":
                body_parts.append("A fix has been implemented. We are monitoring the situation.")
            elif status == "resolved":
                body_parts.append("This incident has been resolved. All services are operating normally.")

            affected = details.get("affected_services", [])
            if affected:
                sections.append({"heading": "Affected Services", "content": ", ".join(affected)})
                body_parts.append(f"\nAffected services: {', '.join(affected)}")

            impact = details.get("impact", "")
            if impact:
                sections.append({"heading": "Impact", "content": impact})
                body_parts.append(f"Impact: {impact}")

            workaround = details.get("workaround", "")
            if workaround:
                sections.append({"heading": "Workaround", "content": workaround})
                body_parts.append(f"\nWorkaround: {workaround}")

            eta = details.get("eta", "")
            if eta and status not in ("resolved",):
                sections.append({"heading": "Estimated Resolution", "content": eta})
                body_parts.append(f"Estimated time to resolution: {eta}")
        else:
            # Internal: include technical details
            body_parts.append(f"{status_emoji} INTERNAL: {title}")
            body_parts.append("")

            for key in ("affected_services", "impact", "current_action", "eta", "workaround"):
                val = details.get(key, "")
                if val:
                    if isinstance(val, list):
                        val = ", ".join(val)
                    heading = key.replace("_", " ").title()
                    sections.append({"heading": heading, "content": str(val)})
                    body_parts.append(f"{heading}: {val}")

    elif update_type == "maintenance":
        if audience == "external":
            body_parts.append(f"{status_emoji} Scheduled Maintenance: {title}")
            body_parts.append("")

            services = details.get("services", [])
            if services:
                sections.append({"heading": "Affected Services", "content": ", ".join(services)})
                body_parts.append(f"Affected services: {', '.join(services)}")

            start = details.get("start_time", "")
            end = details.get("end_time", "")
            if start and end:
                sections.append({"heading": "Window", "content": f"{start} to {end}"})
                body_parts.append(f"Maintenance window: {start} to {end}")

            desc = details.get("description", "")
            if desc:
                sections.append({"heading": "Description", "content": desc})
                body_parts.append(f"\n{desc}")
        else:
            body_parts.append(f"{status_emoji} INTERNAL Maintenance: {title}")
            body_parts.append("")
            for key, val in details.items():
                if val:
                    heading = key.replace("_", " ").title()
                    sections.append({"heading": heading, "content": str(val)})
                    body_parts.append(f"{heading}: {val}")

    elif update_type == "project":
        if audience == "external":
            body_parts.append(f"{status_emoji} Project Update: {title}")
            body_parts.append("")

            milestone = details.get("milestone", "")
            if milestone:
                sections.append({"heading": "Current Milestone", "content": milestone})
                body_parts.append(f"Current milestone: {milestone}")

            progress = details.get("progress_pct", "")
            if progress:
                sections.append({"heading": "Progress", "content": f"{progress}%"})
                body_parts.append(f"Progress: {progress}%")

            next_steps = details.get("next_steps", [])
            if next_steps:
                steps_str = ", ".join(next_steps) if isinstance(next_steps, list) else str(next_steps)
                sections.append({"heading": "Next Steps", "content": steps_str})
                body_parts.append(f"Next steps: {steps_str}")
        else:
            body_parts.append(f"{status_emoji} INTERNAL Project: {title}")
            body_parts.append("")
            for key, val in details.items():
                if val:
                    if isinstance(val, list):
                        val = ", ".join(str(v) for v in val)
                    heading = key.replace("_", " ").title()
                    sections.append({"heading": heading, "content": str(val)})
                    body_parts.append(f"{heading}: {val}")

    body = "\n".join(body_parts)

    return {
        "title": title,
        "type": update_type,
        "status": status,
        "audience": audience,
        "timestamp": timestamp,
        "body": body,
        "status_emoji": status_emoji,
        "sections": sections,
    }


# ---------------------------------------------------------------------------
# Solution 14: Technical Presentation Outline Generator
# ---------------------------------------------------------------------------
# Design notes:
# - Time allocation follows presentation best practices (10-20-70 rule adapted)
# - Audience type adjusts language and content focus
# - Demo gets 20% of available time (significant but not dominant)
# - Each slide has speaker notes to support the presenter
# ---------------------------------------------------------------------------

def solution_14_presentation_outline_generator(
    topic: str,
    audience: str,
    duration_minutes: int,
    key_points: list[str],
    include_demo: bool = False,
    include_code_samples: bool = False,
) -> dict[str, Any]:
    """Solution 14: Generate a technical presentation outline."""

    slides: list[dict[str, Any]] = []
    time_allocation: dict[str, float] = {}
    slide_num = 0

    # Fixed overhead: title(1) + agenda(1) + context(2) + summary(1) + Q&A(2) = 7 min
    fixed_overhead = 7.0
    remaining = max(1.0, duration_minutes - fixed_overhead)

    # Allocate demo time if requested (20% of remaining)
    demo_time = 0.0
    if include_demo:
        demo_time = round(remaining * 0.20, 1)
        remaining -= demo_time

    # Allocate code sample time (1 min per key point)
    code_time = 0.0
    if include_code_samples:
        code_time = min(len(key_points) * 1.0, remaining * 0.3)
        remaining -= code_time

    # Distribute remaining time across key points
    time_per_point = round(remaining / max(1, len(key_points)), 1)

    # Audience-specific language
    audience_context = {
        "technical": {
            "intro_notes": "Assume audience knows fundamentals. Dive into architecture and implementation details.",
            "point_prefix": "Technical deep-dive: ",
        },
        "business": {
            "intro_notes": "Focus on business outcomes and ROI. Use analogies instead of technical jargon.",
            "point_prefix": "Business value: ",
        },
        "mixed": {
            "intro_notes": "Balance technical accuracy with accessibility. Define terms when first used.",
            "point_prefix": "",
        },
    }
    ctx = audience_context.get(audience, audience_context["mixed"])

    # 1. Title slide
    slide_num += 1
    slides.append(asdict(Slide(
        slide_number=slide_num,
        title=topic,
        bullet_points=["Presenter Name", "Date", "Company"],
        speaker_notes=f"Welcome the audience. {ctx['intro_notes']}",
        slide_type="title",
        estimated_minutes=1.0,
    )))
    time_allocation["title"] = 1.0

    # 2. Agenda slide
    slide_num += 1
    slides.append(asdict(Slide(
        slide_number=slide_num,
        title="Agenda",
        bullet_points=key_points + (["Live Demo"] if include_demo else []) + ["Q&A"],
        speaker_notes="Walk through what we will cover today.",
        slide_type="content",
        estimated_minutes=1.0,
    )))
    time_allocation["agenda"] = 1.0

    # 3. Context/Problem slide
    slide_num += 1
    slides.append(asdict(Slide(
        slide_number=slide_num,
        title="The Challenge" if audience == "business" else "Problem Context",
        bullet_points=[
            "What problem are we solving?",
            "Why does this matter now?",
            "What are the current limitations?",
        ],
        speaker_notes="Set the stage for why this topic is important. Connect to audience pain points.",
        slide_type="content",
        estimated_minutes=2.0,
    )))
    time_allocation["context"] = 2.0

    # 4. Key point slides
    time_allocation["key_points"] = 0.0
    for i, point in enumerate(key_points):
        slide_num += 1
        slides.append(asdict(Slide(
            slide_number=slide_num,
            title=f"{ctx['point_prefix']}{point}" if ctx['point_prefix'] else point,
            bullet_points=[
                f"Key insight about {point}",
                "Supporting evidence or data",
                "Practical implications",
            ],
            speaker_notes=f"Cover {point} in depth. Use concrete examples relevant to the audience.",
            slide_type="content",
            estimated_minutes=time_per_point,
        )))
        time_allocation["key_points"] += time_per_point

        # Add code sample slide if requested
        if include_code_samples:
            slide_num += 1
            code_slide_time = code_time / max(1, len(key_points))
            slides.append(asdict(Slide(
                slide_number=slide_num,
                title=f"Code: {point}",
                bullet_points=["Code example demonstrating this concept"],
                speaker_notes=f"Walk through the code example for {point}. Highlight key lines.",
                slide_type="code",
                estimated_minutes=round(code_slide_time, 1),
            )))

    if include_code_samples:
        time_allocation["code_samples"] = code_time

    # 5. Demo slide
    if include_demo:
        slide_num += 1
        slides.append(asdict(Slide(
            slide_number=slide_num,
            title="Live Demo",
            bullet_points=[
                "Demo scenario overview",
                "Step-by-step walkthrough",
                "Key takeaways from the demo",
            ],
            speaker_notes="Run the prepared demo. Have a backup recording in case of technical issues.",
            slide_type="demo",
            estimated_minutes=demo_time,
        )))
        time_allocation["demo"] = demo_time

    # 6. Summary slide
    slide_num += 1
    slides.append(asdict(Slide(
        slide_number=slide_num,
        title="Key Takeaways",
        bullet_points=key_points[:4],  # Top 4 points as recap
        speaker_notes="Recap the main points. End with a clear call to action.",
        slide_type="summary",
        estimated_minutes=1.0,
    )))
    time_allocation["summary"] = 1.0

    # 7. Q&A slide
    slide_num += 1
    slides.append(asdict(Slide(
        slide_number=slide_num,
        title="Questions & Discussion",
        bullet_points=["Contact information", "Additional resources", "Follow-up channels"],
        speaker_notes="Open the floor for questions. Have 2-3 anticipated questions prepared.",
        slide_type="content",
        estimated_minutes=2.0,
    )))
    time_allocation["qa"] = 2.0

    return {
        "topic": topic,
        "audience": audience,
        "total_duration": duration_minutes,
        "slide_count": len(slides),
        "slides": slides,
        "time_allocation": time_allocation,
    }


# ---------------------------------------------------------------------------
# Solution 15: Code Example Test Runner Framework
# ---------------------------------------------------------------------------
# Design notes:
# - Parses markdown fenced code blocks with language info strings
# - Supports expected output blocks for verification
# - Uses exec() in isolated namespaces for safety
# - Captures stdout via redirect_stdout for output comparison
# - Falls back to syntax checking when execute=False
# ---------------------------------------------------------------------------

def solution_15_code_example_test_runner(
    document_text: str,
    execute: bool = False,
) -> dict[str, Any]:
    """Solution 15: Extract and optionally test code examples from documentation."""

    # Parse fenced code blocks
    # Pattern: ```language\ncode\n``` optionally followed by ```output\nexpected\n```
    block_pattern = re.compile(
        r'```(\w+)\n(.*?)```',
        re.DOTALL,
    )

    lines = document_text.split('\n')
    matches = list(block_pattern.finditer(document_text))

    examples: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    i = 0
    example_num = 0
    while i < len(matches):
        match = matches[i]
        language = match.group(1)
        code = match.group(2).strip()

        # Find line number (count newlines before match start)
        line_number = document_text[:match.start()].count('\n') + 1

        # Get description (line immediately before the code block)
        pre_text = document_text[:match.start()].rstrip()
        pre_lines = pre_text.split('\n')
        description = pre_lines[-1].strip() if pre_lines else ""

        # Check if next block is an output block
        expected_output = None
        if i + 1 < len(matches):
            next_match = matches[i + 1]
            next_lang = next_match.group(1)
            # Check if output block follows immediately (no significant text between)
            between = document_text[match.end():next_match.start()].strip()
            if next_lang == "output" and len(between) == 0:
                expected_output = next_match.group(2).strip()
                i += 1  # Skip the output block

        # Only track code blocks (not output blocks processed above)
        if language != "output":
            example_num += 1
            example_id = f"example_{example_num}"

            examples.append(asdict(CodeExample(
                id=example_id,
                language=language,
                code=code,
                expected_output=expected_output,
                line_number=line_number,
                description=description,
            )))

            # Test the example
            if language == "python":
                if execute:
                    # Execute the code and capture output
                    start_time = time.time()
                    try:
                        namespace: dict[str, Any] = {}
                        captured = io.StringIO()
                        with redirect_stdout(captured):
                            exec(code, namespace)
                        actual_output = captured.getvalue().strip()
                        elapsed = (time.time() - start_time) * 1000

                        if expected_output is not None:
                            passed = actual_output == expected_output
                            error = "" if passed else (
                                f"Expected: {expected_output!r}, Got: {actual_output!r}"
                            )
                        else:
                            passed = True  # No expected output, just check it runs
                            error = ""

                        results.append(asdict(TestResult(
                            example_id=example_id,
                            passed=passed,
                            actual_output=actual_output,
                            error=error,
                            execution_time_ms=round(elapsed, 2),
                        )))
                    except Exception as e:
                        elapsed = (time.time() - start_time) * 1000
                        results.append(asdict(TestResult(
                            example_id=example_id,
                            passed=False,
                            actual_output="",
                            error=str(e),
                            execution_time_ms=round(elapsed, 2),
                        )))
                else:
                    # Just validate syntax
                    try:
                        ast.parse(code)
                        results.append(asdict(TestResult(
                            example_id=example_id,
                            passed=True,
                            actual_output="",
                            error="",
                            execution_time_ms=0.0,
                        )))
                    except SyntaxError as e:
                        results.append(asdict(TestResult(
                            example_id=example_id,
                            passed=False,
                            actual_output="",
                            error=f"Syntax error: {e}",
                            execution_time_ms=0.0,
                        )))
            # Non-Python examples are skipped for testing

        i += 1

    # Only count Python examples in pass/fail stats (non-Python are not tested)
    python_results = [r for r in results]
    total = len(python_results)
    passed = sum(1 for r in python_results if r["passed"])
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0.0

    return {
        "examples": examples,
        "results": results,
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(pass_rate, 1),
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_solution_1():
    """Test API tutorial generator."""
    endpoints = [
        APIEndpoint(
            method="POST",
            path="/v1/messages",
            description="Send a message to Claude",
            parameters=[
                {"name": "model", "type": "string", "required": True},
                {"name": "max_tokens", "type": "integer", "required": True},
            ],
            request_body={"model": "claude-3", "max_tokens": 1024,
                          "messages": [{"role": "user", "content": "Hello"}]},
            response_body={"id": "msg_123", "content": [{"type": "text", "text": "Hi"}]},
        ),
        APIEndpoint(
            method="GET",
            path="/v1/models",
            description="List available models",
            parameters=[],
        ),
    ]
    result = solution_1_api_tutorial_generator(
        api_name="Messages API",
        base_url="https://api.anthropic.com",
        endpoints=endpoints,
        auth_type="bearer_token",
    )
    assert isinstance(result, dict)
    assert result["title"] == "Messages API Tutorial"
    assert "sections" in result
    assert len(result["sections"]) >= 4
    assert result["metadata"]["endpoint_count"] == 2
    assert result["metadata"]["auth_type"] == "bearer_token"
    # Verify section titles
    section_titles = [s["title"] for s in result["sections"]]
    assert "Introduction" in section_titles
    assert "Prerequisites" in section_titles
    assert "Quick Start" in section_titles
    assert "Troubleshooting" in section_titles
    print("  Solution 1 (API Tutorial Generator): PASSED")


def test_solution_2():
    """Test code sample validator."""
    good_code = '''
import json
from typing import Dict

def process_data(data: Dict[str, str]) -> str:
    """Process the input data."""
    try:
        return json.dumps(data)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    result = process_data({"key": "value"})
    print(result)
'''
    result = solution_2_code_sample_validator(good_code)
    assert result.syntax_ok is True
    assert result.has_docstrings is True
    assert result.has_error_handling is True
    assert result.has_main_guard is True
    assert result.has_type_hints is True
    assert result.completeness_score > 0.7

    bad_code = "def foo(\n    x = "
    result2 = solution_2_code_sample_validator(bad_code)
    assert result2.syntax_ok is False
    assert result2.is_valid is False
    assert result2.completeness_score == 0.0

    # Test with expected imports
    result3 = solution_2_code_sample_validator(
        "import os\nprint('hello')",
        expected_imports=["json"],
    )
    assert "json" in result3.imports_missing
    print("  Solution 2 (Code Sample Validator): PASSED")


def test_solution_3():
    """Test requirements extractor."""
    description = """
    We need a customer support chatbot that must handle 1000 concurrent users.
    It should integrate with our Salesforce CRM and Zendesk ticketing system.
    The system must be SOC2 compliant and should respond within 2 seconds.
    It would be nice to have multilingual support. The bot will need to
    connect to our PostgreSQL database for customer data.
    """
    result = solution_3_requirements_extractor(description)
    assert "requirements" in result
    assert len(result["requirements"]) >= 3
    assert "summary" in result
    priorities = [r["priority"] for r in result["requirements"]]
    assert "must-have" in priorities
    print("  Solution 3 (Requirements Extractor): PASSED")


def test_solution_4():
    """Test migration guide generator."""
    old_endpoints = {
        "/v1/complete": {
            "method": "POST",
            "parameters": {"prompt": {"type": "str", "required": True},
                           "max_tokens": {"type": "int", "required": True}},
            "response_fields": ["completion", "model"],
        },
        "/v1/models": {
            "method": "GET",
            "parameters": {},
            "response_fields": ["models"],
        },
    }
    new_endpoints = {
        "/v1/messages": {
            "method": "POST",
            "parameters": {"messages": {"type": "list", "required": True},
                           "model": {"type": "str", "required": True},
                           "max_tokens": {"type": "int", "required": True}},
            "response_fields": ["content", "model", "usage"],
        },
        "/v1/models": {
            "method": "GET",
            "parameters": {},
            "response_fields": ["models", "default_model"],
        },
    }
    result = solution_4_migration_guide_generator("v1", "v2", old_endpoints, new_endpoints)
    assert result["from_version"] == "v1"
    assert result["to_version"] == "v2"
    assert len(result["changes"]) > 0
    assert result["breaking_changes_count"] >= 1
    # Verify specific changes
    change_types = [c["change_type"] for c in result["changes"]]
    assert "removed" in change_types  # /v1/complete removed
    assert "added" in change_types    # /v1/messages added
    print("  Solution 4 (Migration Guide Generator): PASSED")


def test_solution_5():
    """Test changelog formatter."""
    changes = [
        ChangeEntry("added", "Streaming support for messages API", "#101"),
        ChangeEntry("added", "Vision input for Claude 3 models", "#102"),
        ChangeEntry("fixed", "Rate limiting header format", "#95"),
        ChangeEntry("changed", "Default max_tokens increased to 4096", "#100"),
        ChangeEntry("deprecated", "Legacy completions endpoint", "#98"),
    ]
    result = solution_5_changelog_formatter(
        version="2.1.0",
        release_date="2026-04-29",
        changes=changes,
        previous_version="2.0.0",
        repo_url="https://github.com/anthropic/sdk",
    )
    assert "## [2.1.0]" in result
    assert "### Added" in result
    assert "### Fixed" in result
    assert "### Deprecated" in result
    assert "Streaming support" in result
    # Verify category ordering: Added comes before Fixed
    assert result.index("### Added") < result.index("### Fixed")
    # Verify issue links
    assert "[#101]" in result
    print("  Solution 5 (Changelog Formatter): PASSED")


def test_solution_6():
    """Test ADR generator."""
    result = solution_6_adr_generator(
        title="Use pgvector for embedding storage",
        context="We need to store and query vector embeddings for our RAG system.",
        options=[
            {"name": "pgvector", "pros": ["SQL familiar", "ACID"],
             "cons": ["Newer technology"], "effort": "medium"},
            {"name": "Pinecone", "pros": ["Managed service", "Fast"],
             "cons": ["Vendor lock-in", "Cost"], "effort": "low"},
        ],
        decision="Use pgvector because it integrates with existing PostgreSQL infrastructure.",
        consequences=["Need to manage index maintenance", "Lower operational cost"],
        status="accepted",
    )
    assert result["title"] == "Use pgvector for embedding storage"
    assert result["status"] == "accepted"
    assert len(result["sections"]) >= 4
    section_headings = [s["heading"] for s in result["sections"]]
    assert "Context" in section_headings
    assert "Decision" in section_headings
    assert "Consequences" in section_headings
    print("  Solution 6 (ADR Generator): PASSED")


def test_solution_7():
    """Test runbook generator."""
    steps = [
        {"action": "Check service health", "command": "curl localhost:8080/health",
         "expected_output": '{"status": "ok"}', "rollback": "", "warning": ""},
        {"action": "Restart service", "command": "systemctl restart ml-api",
         "expected_output": "Active: active (running)",
         "rollback": "systemctl stop ml-api", "warning": "Will cause brief downtime"},
    ]
    result = solution_7_runbook_generator(
        title="ML API Service Recovery",
        service_name="ml-api",
        scenario="Service returning 503 errors",
        steps=steps,
        severity="high",
    )
    assert result["title"] == "ML API Service Recovery"
    assert result["severity"] == "high"
    assert len(result["steps"]) == 2
    assert result["estimated_time_minutes"] == 4
    assert result["steps"][0]["step_number"] == 1
    assert result["steps"][1]["warning"] == "Will cause brief downtime"
    print("  Solution 7 (Runbook Generator): PASSED")


def test_solution_8():
    """Test postmortem formatter."""
    timeline = [
        TimelineEvent("2026-04-28T14:00:00Z", "Alerts fired for high error rate", "PagerDuty"),
        TimelineEvent("2026-04-28T14:05:00Z", "On-call engineer acknowledged", "Alice"),
        TimelineEvent("2026-04-28T14:30:00Z", "Root cause identified: bad deployment", "Alice"),
        TimelineEvent("2026-04-28T14:45:00Z", "Rollback completed, service restored", "Alice"),
    ]
    action_items = [
        {"action": "Add deployment canary checks", "owner": "Bob",
         "due_date": "2026-05-15", "priority": "high"},
        {"action": "Improve alert runbooks", "owner": "Carol",
         "due_date": "2026-05-30", "priority": "medium"},
    ]
    result = solution_8_postmortem_formatter(
        title="Messages API Outage",
        incident_date="2026-04-28",
        severity="SEV2",
        duration_minutes=45,
        summary="Messages API returned 500 errors for 45 minutes.",
        impact="All API consumers experienced failures.",
        timeline=timeline,
        root_cause="Bad deployment passed CI but had runtime error.",
        action_items=action_items,
        lessons_learned=["Need canary deployments", "Runbooks were outdated"],
    )
    assert result["title"] == "Messages API Outage"
    assert result["severity"] == "SEV2"
    assert result["duration_minutes"] == 45
    assert len(result["action_items"]) == 2
    assert len(result["timeline"]) == 4
    # Check computed metrics
    assert result["metrics"]["detection_time_minutes"] == 5  # 14:00 -> 14:05
    assert result["metrics"]["response_time_minutes"] == 5   # First human action (Alice)
    assert result["metrics"]["resolution_time_minutes"] == 45
    print("  Solution 8 (Postmortem Formatter): PASSED")


def test_solution_9():
    """Test complexity estimator."""
    result = solution_9_complexity_estimator(
        project_name="Customer Support AI",
        integrations=["Salesforce", "Zendesk", "Slack", "PostgreSQL"],
        data_sources=6,
        user_types=3,
        compliance_requirements=["SOC2", "GDPR"],
        has_ml_component=True,
        has_realtime_requirement=True,
        team_size=2,
    )
    assert result["project_name"] == "Customer Support AI"
    assert result["complexity_level"] in ("low", "medium", "high")
    assert 0 < result["weighted_score"] <= 5.0
    assert len(result["factors"]) == 7
    assert isinstance(result["estimated_weeks"], (int, float))
    assert result["complexity_level"] == "high"
    # Check that ML is a risk factor
    assert "ML complexity" in result["risk_factors"]
    print("  Solution 9 (Complexity Estimator): PASSED")


def test_solution_10():
    """Test documentation coverage checker."""
    sample_code = '''
"""Module docstring."""

class MyClass:
    """Documented class."""

    def public_method(self, x: int) -> str:
        """Documented method."""
        return str(x)

    def _private_method(self):
        pass

    def undocumented_method(self):
        pass

def documented_function(name: str) -> str:
    """Has a docstring."""
    return name

def undocumented_function(x):
    return x
'''
    result = solution_10_doc_coverage_checker(sample_code, "test_module")
    assert result.total_public_items >= 4
    assert result.documented_items >= 3
    assert len(result.undocumented_items) >= 1
    assert "undocumented_function" in result.undocumented_items
    assert "undocumented_method" in [
        item.split(".")[-1] for item in result.undocumented_items
    ] or "MyClass.undocumented_method" in result.undocumented_items
    assert 0 < result.coverage_percentage <= 100
    print("  Solution 10 (Doc Coverage Checker): PASSED")


def test_solution_11():
    """Test FAQ generator."""
    tickets = [
        SupportTicket("T1", "Authentication error with API keys",
                      "Getting authentication error when calling API", "auth", "Use bearer token in header"),
        SupportTicket("T2", "Authentication error returns 401",
                      "API authentication error with invalid keys", "auth", "Check API key is valid"),
        SupportTicket("T3", "Authentication error expired keys",
                      "Authentication error after keys expired", "auth", "Regenerate API key from dashboard"),
        SupportTicket("T4", "Rate limit exceeded getting 429",
                      "Rate limit errors when sending requests", "limits", "Implement exponential backoff"),
        SupportTicket("T5", "Rate limit errors and threshold",
                      "Rate limit errors when hitting threshold", "limits", "See rate limits docs page"),
        SupportTicket("T6", "Unique billing question",
                      "Invoice format", "billing", "Contact billing team"),
    ]
    result = solution_11_faq_generator(tickets, similarity_threshold=0.3, min_cluster_size=2)
    assert len(result["faqs"]) >= 2
    assert result["total_tickets"] == 6
    assert result["tickets_covered"] >= 4
    assert "T6" in result["uncategorized_ticket_ids"]
    # Check FAQs are sorted by frequency (descending)
    freqs = [f["frequency"] for f in result["faqs"]]
    assert freqs == sorted(freqs, reverse=True)
    print("  Solution 11 (FAQ Generator): PASSED")


def test_solution_12():
    """Test release notes formatter."""
    features = [
        ReleaseFeature(
            title="Streaming Responses",
            technical_description="Server-sent events for real-time token streaming via /v1/messages with stream=true",
            user_benefit="See AI responses in real-time as they are generated",
            business_impact="Improved user experience reduces churn by estimated 15%",
            category="feature",
        ),
        ReleaseFeature(
            title="JSON Mode",
            technical_description="Guaranteed valid JSON output via response_format parameter",
            user_benefit="Reliable structured data extraction without parsing errors",
            business_impact="Reduces integration development time by 40%",
            category="improvement",
        ),
        ReleaseFeature(
            title="Legacy Auth Removal",
            technical_description="Removed X-API-Key header support; use Authorization: Bearer",
            user_benefit="Simplified authentication with industry-standard Bearer tokens",
            business_impact="Stronger security posture for enterprise customers",
            category="feature",
            breaking=True,
        ),
    ]
    dev_result = solution_12_release_notes_formatter("3.0.0", "2026-04-29", features, "developer")
    assert dev_result["has_breaking_changes"] is True
    assert dev_result["audience"] == "developer"
    assert any("Breaking" in s["heading"] for s in dev_result["sections"])

    exec_result = solution_12_release_notes_formatter("3.0.0", "2026-04-29", features, "executive")
    assert exec_result["audience"] == "executive"
    assert len(exec_result["sections"]) >= 1

    prod_result = solution_12_release_notes_formatter("3.0.0", "2026-04-29", features, "product")
    assert prod_result["audience"] == "product"
    print("  Solution 12 (Release Notes Formatter): PASSED")


def test_solution_13():
    """Test status update engine."""
    result = solution_13_status_update_engine(
        update_type="incident",
        title="Messages API Degraded Performance",
        status="identified",
        details={
            "affected_services": ["Messages API", "Embeddings API"],
            "impact": "Increased latency for 30% of requests",
            "current_action": "Scaling up backend infrastructure",
            "eta": "30 minutes",
            "workaround": "Retry requests with exponential backoff",
        },
        audience="external",
    )
    assert result["type"] == "incident"
    assert result["status"] == "identified"
    assert result["audience"] == "external"
    assert len(result["body"]) > 0
    assert len(result["sections"]) >= 2
    assert result["status_emoji"] == "[IDENTIFIED]"

    # Test internal version includes more detail
    internal = solution_13_status_update_engine(
        update_type="incident",
        title="Messages API Degraded Performance",
        status="identified",
        details={
            "affected_services": ["Messages API"],
            "impact": "High latency",
            "current_action": "Scaling up",
            "eta": "30 minutes",
            "workaround": "Retry",
        },
        audience="internal",
    )
    assert "INTERNAL" in internal["body"]
    print("  Solution 13 (Status Update Engine): PASSED")


def test_solution_14():
    """Test presentation outline generator."""
    result = solution_14_presentation_outline_generator(
        topic="Building RAG Applications with Claude",
        audience="technical",
        duration_minutes=30,
        key_points=[
            "RAG architecture overview",
            "Embedding and retrieval strategies",
            "Prompt engineering for RAG",
            "Evaluation and testing",
        ],
        include_demo=True,
    )
    assert result["topic"] == "Building RAG Applications with Claude"
    assert result["total_duration"] == 30
    assert len(result["slides"]) >= 6
    total_time = sum(s["estimated_minutes"] for s in result["slides"])
    assert abs(total_time - 30) < 1
    # Verify slide types
    slide_types = [s["slide_type"] for s in result["slides"]]
    assert "title" in slide_types
    assert "demo" in slide_types
    assert "summary" in slide_types
    print("  Solution 14 (Presentation Outline Generator): PASSED")


def test_solution_15():
    """Test code example test runner."""
    doc_text = """
# API Tutorial

Here is how to create a list:

```python
numbers = [1, 2, 3]
print(sum(numbers))
```

```output
6
```

And here is a dictionary example:

```python
data = {"key": "value"}
print(data["key"])
```

```output
value
```

Here is a non-Python example:

```bash
curl https://api.example.com
```
"""
    result = solution_15_code_example_test_runner(doc_text, execute=True)
    assert result["total"] >= 2
    assert result["passed"] >= 2
    assert result["pass_rate"] == 100.0

    # Verify examples were extracted correctly
    python_examples = [e for e in result["examples"] if e["language"] == "python"]
    assert len(python_examples) == 2
    assert python_examples[0]["expected_output"] == "6"

    # Test with syntax error
    bad_doc = """
```python
def broken(
```
"""
    result2 = solution_15_code_example_test_runner(bad_doc, execute=False)
    assert result2["failed"] >= 1
    assert "Syntax error" in result2["results"][0]["error"]
    print("  Solution 15 (Code Example Test Runner): PASSED")


if __name__ == "__main__":
    print("Testing Technical Communication solutions...\n")
    test_solution_1()
    test_solution_2()
    test_solution_3()
    test_solution_4()
    test_solution_5()
    test_solution_6()
    test_solution_7()
    test_solution_8()
    test_solution_9()
    test_solution_10()
    test_solution_11()
    test_solution_12()
    test_solution_13()
    test_solution_14()
    test_solution_15()
    print("\nAll Technical Communication solutions passed!")
