"""
Module 07 Exercises: Technical Communication
=============================================

15 exercises covering technical communication skills essential for
Solutions Engineers and Applied AI Engineers:

- API tutorial and documentation generation
- Code sample validation and testing
- Requirements extraction and translation
- Migration guides, changelogs, and release notes
- Architecture Decision Records (ADRs) and runbooks
- Incident postmortems and status updates
- Complexity estimation and documentation coverage
- FAQ generation and presentation outlines

For Swift developers: think of these like building the documentation
infrastructure behind developer.apple.com -- structured templates,
validated code samples, and automated formatting that keeps large-scale
developer documentation consistent and accurate.
"""

import re
import ast
import json
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime, date


# ============================================================================
# Exercise 1: API Tutorial Template Generator
# ============================================================================
# Build a generator that produces structured API tutorial documents from
# a specification dict. Tutorials are the bread and butter of developer
# relations -- a good tutorial can make or break API adoption.
#
# Real-world context: At companies like Anthropic or OpenAI, every new
# API capability ships with a tutorial. This automates the skeleton.
#
# Swift analogy: Like generating a DocC tutorial structure from a
# module's public API surface.
# ============================================================================

@dataclass
class APIEndpoint:
    """Describes a single API endpoint for tutorial generation."""
    method: str              # "GET", "POST", etc.
    path: str                # "/v1/messages"
    description: str         # Human-readable description
    parameters: list[dict]   # [{"name": "model", "type": "string", "required": True}]
    request_body: dict | None = None   # Example request body
    response_body: dict | None = None  # Example response body


def exercise_1_api_tutorial_generator(
    api_name: str,
    base_url: str,
    endpoints: list[APIEndpoint],
    auth_type: str = "bearer_token",
) -> dict[str, Any]:
    """
    Exercise 1: Generate a structured API tutorial template.

    Given an API specification, produce a tutorial document with:
    - Title and introduction section
    - Prerequisites section (auth setup, SDK install)
    - A "Quick Start" section with the simplest endpoint
    - Per-endpoint sections with: description, code example (curl + python),
      parameter table, and expected response
    - Troubleshooting section with common errors
    - Next steps section

    The output is a dict representing the tutorial structure, not raw text.
    Each section should have a "title", "content", and optional "code_blocks" list.

    Args:
        api_name: Name of the API (e.g., "Messages API")
        base_url: Base URL (e.g., "https://api.anthropic.com")
        endpoints: List of APIEndpoint objects
        auth_type: One of "bearer_token", "api_key_header", "basic_auth"

    Returns:
        Dict with keys: "title", "sections" (list of section dicts),
        "metadata" (generated_at, endpoint_count, auth_type)
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 2: Code Sample Validator
# ============================================================================
# Validate that code samples in documentation actually work -- check
# syntax, verify imports exist, and assess completeness. Broken code
# samples are the #1 source of developer frustration with docs.
#
# Real-world context: Solutions engineers constantly write code samples
# for customers. Automated validation catches errors before they ship.
# ============================================================================

@dataclass
class ValidationResult:
    """Result of validating a code sample."""
    is_valid: bool
    syntax_ok: bool
    imports_found: list[str]       # Imports that were found
    imports_missing: list[str]     # Imports referenced but not imported
    has_main_guard: bool           # Has if __name__ == "__main__"
    has_error_handling: bool       # Has try/except
    has_type_hints: bool           # Uses type annotations
    has_docstrings: bool           # Has at least one docstring
    completeness_score: float      # 0.0 to 1.0
    issues: list[str]              # List of specific issues found


def exercise_2_code_sample_validator(
    code: str,
    expected_imports: list[str] | None = None,
    require_error_handling: bool = False,
    require_type_hints: bool = False,
) -> ValidationResult:
    """
    Exercise 2: Validate a Python code sample for documentation quality.

    Check the following:
    1. Syntax validity (can it be parsed by ast.parse?)
    2. Import completeness (are all used names imported?)
    3. Presence of docstrings on functions/classes
    4. Type hint usage on function signatures
    5. Error handling (try/except blocks)
    6. Main guard presence
    7. Overall completeness score (0-1 based on checks above)

    For import checking: parse the AST, find all import statements, then
    find all Name nodes that reference modules. Compare against imports.
    If expected_imports is provided, verify those specific imports exist.

    Args:
        code: Python source code string
        expected_imports: Specific imports that must be present
        require_error_handling: Whether try/except is required
        require_type_hints: Whether type hints are required

    Returns:
        ValidationResult with detailed findings
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 3: Technical Requirements Extractor
# ============================================================================
# Translate a business description into structured technical requirements.
# This is what solutions engineers do daily: take "we want AI to help our
# customer service" and turn it into concrete technical specs.
#
# Swift analogy: Like parsing a product brief into a set of User Stories
# with acceptance criteria for your Jira board.
# ============================================================================

@dataclass
class TechnicalRequirement:
    """A single extracted technical requirement."""
    id: str                      # e.g., "REQ-001"
    category: str                # "functional", "non-functional", "integration"
    title: str                   # Short descriptive title
    description: str             # Detailed description
    priority: str                # "must-have", "should-have", "nice-to-have"
    estimated_complexity: str    # "low", "medium", "high"
    dependencies: list[str]      # IDs of requirements this depends on


def exercise_3_requirements_extractor(
    business_description: str,
    keywords_to_categories: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Exercise 3: Extract structured technical requirements from a business
    description.

    Parse the text to identify:
    1. Functional requirements (what the system should DO)
       - Look for action verbs: "must", "should", "will", "need to"
    2. Non-functional requirements (performance, security, scalability)
       - Look for: "fast", "secure", "scale", "available", "reliable"
    3. Integration requirements (external systems, APIs, data sources)
       - Look for: "integrate", "connect", "API", "database", "import/export"

    Assign IDs (REQ-001, REQ-002, ...), priorities based on keyword strength
    ("must" = must-have, "should" = should-have, "could"/"nice" = nice-to-have),
    and complexity estimates based on requirement scope.

    Args:
        business_description: Free-form text describing business needs
        keywords_to_categories: Optional override mapping keywords -> categories

    Returns:
        Dict with keys:
        - "requirements": list of TechnicalRequirement objects (as dicts)
        - "summary": dict with counts per category and priority
        - "raw_input_length": int (character count of input)
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 4: Migration Guide Generator
# ============================================================================
# Generate migration guides between API versions by diffing old vs new
# specs. When Anthropic ships a new API version, every customer needs a
# clear migration path.
#
# Swift analogy: Like generating migration notes for Core Data model
# versions or documenting breaking changes between major SDK releases.
# ============================================================================

@dataclass
class APIChange:
    """Represents a single change between API versions."""
    change_type: str        # "added", "removed", "modified", "deprecated"
    component: str          # "endpoint", "parameter", "response_field", "auth"
    path: str               # The API path or field affected
    old_value: Any          # Previous value/spec (None if added)
    new_value: Any          # New value/spec (None if removed)
    breaking: bool          # Whether this is a breaking change
    migration_action: str   # What the developer needs to do


def exercise_4_migration_guide_generator(
    old_version: str,
    new_version: str,
    old_endpoints: dict[str, dict],
    new_endpoints: dict[str, dict],
) -> dict[str, Any]:
    """
    Exercise 4: Generate a migration guide by diffing two API versions.

    Compare old_endpoints and new_endpoints to identify:
    1. Added endpoints (in new but not old)
    2. Removed endpoints (in old but not new)
    3. Modified endpoints (in both but with differences)
       - Changed parameters (added, removed, type changed)
       - Changed response fields
       - Changed methods

    For each change, determine if it is breaking:
    - Removed endpoints: BREAKING
    - Removed required parameters: BREAKING (usually)
    - Added required parameters: BREAKING
    - Added optional parameters: non-breaking
    - Added endpoints: non-breaking

    Endpoint dicts have structure:
    {"method": "POST", "parameters": {"model": {"type": "str", "required": True}},
     "response_fields": ["id", "content", "model"]}

    Args:
        old_version: e.g., "v1"
        new_version: e.g., "v2"
        old_endpoints: path -> endpoint spec dict
        new_endpoints: path -> endpoint spec dict

    Returns:
        Dict with keys:
        - "from_version", "to_version"
        - "changes": list of APIChange dicts
        - "breaking_changes_count": int
        - "summary": human-readable summary string
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 5: Changelog Formatter
# ============================================================================
# Format raw commit/change data into a professional changelog following
# Keep a Changelog conventions. Changelogs communicate what changed and
# why -- critical for enterprise customers evaluating upgrades.
#
# Swift analogy: Like auto-generating App Store release notes from your
# git history and PR descriptions.
# ============================================================================

@dataclass
class ChangeEntry:
    """A single change to include in the changelog."""
    category: str        # "added", "changed", "deprecated", "removed", "fixed", "security"
    description: str     # Human-readable description
    issue_ref: str = ""  # Optional issue/PR reference like "#123"
    author: str = ""     # Optional author


def exercise_5_changelog_formatter(
    version: str,
    release_date: str,
    changes: list[ChangeEntry],
    previous_version: str = "",
    repo_url: str = "",
) -> str:
    """
    Exercise 5: Format changes into a Keep a Changelog style document.

    Produce a markdown-formatted changelog section with:
    - Version header with date and comparison link
    - Changes grouped by category (Added, Changed, Deprecated, Removed,
      Fixed, Security) in that specific order
    - Each entry with optional issue reference as a link
    - Empty categories are omitted
    - If previous_version and repo_url are provided, include a diff link

    Format:
    ## [version] - release_date

    ### Added
    - Description of addition ([#123](repo_url/issues/123))

    ### Fixed
    - Description of fix

    Args:
        version: Release version string (e.g., "2.1.0")
        release_date: ISO format date string (e.g., "2026-04-29")
        changes: List of ChangeEntry objects
        previous_version: Previous version for diff link
        repo_url: Repository URL for issue/diff links

    Returns:
        Formatted markdown changelog string
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 6: Architecture Decision Record (ADR) Template
# ============================================================================
# ADRs document the WHY behind technical decisions. Solutions engineers
# write these to justify architectural choices to customers and
# internal teams alike.
#
# Swift analogy: Like writing a technical proposal for adopting SwiftUI
# over UIKit in a specific project context.
# ============================================================================

def exercise_6_adr_generator(
    title: str,
    context: str,
    options: list[dict[str, Any]],
    decision: str,
    consequences: list[str],
    decision_makers: list[str] | None = None,
    status: str = "proposed",
) -> dict[str, Any]:
    """
    Exercise 6: Generate an Architecture Decision Record (ADR).

    Create a structured ADR with these sections:
    1. Header: ADR number, title, date, status
    2. Context: Why is this decision needed?
    3. Options Considered: List each option with pros/cons
       Each option dict: {"name": str, "pros": [str], "cons": [str], "effort": str}
    4. Decision: Which option was chosen and why
    5. Consequences: What follows from this decision (positive and negative)
    6. Participants: Who was involved in the decision

    Status must be one of: "proposed", "accepted", "deprecated", "superseded"

    Args:
        title: Decision title (e.g., "Use PostgreSQL for vector storage")
        context: Background and motivation text
        options: List of option dicts with name, pros, cons, effort
        decision: The chosen option and rationale
        consequences: List of consequence strings
        decision_makers: List of people involved
        status: ADR status

    Returns:
        Dict with keys: "adr_number" (auto-generated based on timestamp),
        "title", "date", "status", "sections" (list of section dicts
        each with "heading" and "content")
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 7: Runbook Template Generator
# ============================================================================
# Runbooks are step-by-step operational procedures. When your LLM service
# goes down at 3 AM, the on-call engineer needs clear, executable steps
# -- not prose.
#
# Swift analogy: Like writing a detailed App Store submission checklist
# with verification steps and rollback procedures.
# ============================================================================

@dataclass
class RunbookStep:
    """A single step in a runbook."""
    step_number: int
    action: str             # What to do
    command: str = ""       # CLI command if applicable
    expected_output: str = ""  # What you should see
    rollback: str = ""      # How to undo this step
    warning: str = ""       # Any caution/danger notes


def exercise_7_runbook_generator(
    title: str,
    service_name: str,
    scenario: str,
    steps: list[dict[str, str]],
    escalation_contacts: list[dict[str, str]] | None = None,
    severity: str = "medium",
) -> dict[str, Any]:
    """
    Exercise 7: Generate a structured runbook template.

    Create a runbook with:
    1. Header: Title, service, severity, last updated
    2. Overview: What scenario this runbook covers
    3. Prerequisites: Required access, tools, permissions
    4. Diagnostic Steps: How to confirm the issue
    5. Resolution Steps: Numbered steps with commands, expected output,
       and rollback instructions
    6. Verification: How to confirm the fix worked
    7. Escalation: When and who to escalate to

    Each step dict: {"action": str, "command": str, "expected_output": str,
                     "rollback": str, "warning": str}

    Severity must be one of: "critical", "high", "medium", "low"

    Args:
        title: Runbook title
        service_name: Name of the service
        scenario: Description of the scenario/incident type
        steps: List of step dicts
        escalation_contacts: List of {"name": str, "role": str, "contact": str}
        severity: Severity level

    Returns:
        Dict with keys: "title", "service", "severity", "last_updated",
        "sections" (list of section dicts), "steps" (list of RunbookStep),
        "estimated_time_minutes" (2 min per step as default)
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 8: Incident Postmortem Formatter
# ============================================================================
# After an incident, a blameless postmortem documents what happened, why,
# and how to prevent recurrence. This is a critical communication artifact
# for enterprise customers and internal teams.
#
# Swift analogy: Like writing a detailed crash report analysis with
# stack traces, reproduction steps, and fix verification.
# ============================================================================

@dataclass
class TimelineEvent:
    """A single event in the incident timeline."""
    timestamp: str    # ISO format
    description: str
    actor: str = ""   # Person or system that took action


def exercise_8_postmortem_formatter(
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
    """
    Exercise 8: Format an incident postmortem document.

    Create a structured postmortem with:
    1. Header: Title, date, severity (SEV1-SEV4), duration, authors
    2. Executive Summary: 2-3 sentence overview
    3. Impact: Who/what was affected, metrics
    4. Timeline: Chronological events with timestamps
    5. Root Cause Analysis: What actually caused the incident
    6. Action Items: Concrete follow-ups with owners and due dates
       Each: {"action": str, "owner": str, "due_date": str, "priority": str}
    7. Lessons Learned: What we learned
    8. Metrics: detection_time, response_time, resolution_time (computed
       from timeline)

    Args:
        title: Incident title
        incident_date: ISO date of incident
        severity: "SEV1", "SEV2", "SEV3", or "SEV4"
        duration_minutes: Total incident duration
        summary: Brief summary
        impact: Impact description
        timeline: List of TimelineEvent objects
        root_cause: Root cause explanation
        action_items: List of action item dicts
        lessons_learned: List of lesson strings

    Returns:
        Dict with all postmortem sections plus computed metrics
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 9: Technical Complexity Estimator
# ============================================================================
# Estimate the complexity of a technical project based on structured
# inputs. Solutions engineers use this to set customer expectations
# and plan proof-of-concept timelines.
#
# Swift analogy: Like estimating story points for a sprint, but with
# a systematic scoring rubric instead of gut feel.
# ============================================================================

@dataclass
class ComplexityFactor:
    """A single factor contributing to project complexity."""
    name: str
    score: int            # 1-5 complexity score
    weight: float         # How much this factor matters (0.0-1.0)
    rationale: str        # Why this score


def exercise_9_complexity_estimator(
    project_name: str,
    integrations: list[str],
    data_sources: int,
    user_types: int,
    compliance_requirements: list[str],
    has_ml_component: bool = False,
    has_realtime_requirement: bool = False,
    team_size: int = 1,
) -> dict[str, Any]:
    """
    Exercise 9: Estimate technical complexity of a project.

    Score the following factors (1-5 each) with weights:
    1. Integration complexity (0.20): based on number and type of integrations
    2. Data complexity (0.15): based on data_sources count
    3. User complexity (0.10): based on user_types count
    4. Compliance complexity (0.15): based on compliance requirements
    5. ML complexity (0.20): whether ML is involved and what kind
    6. Real-time requirements (0.10): latency-sensitive or not
    7. Team capacity (0.10): team_size relative to scope

    Compute:
    - weighted_score: sum of (score * weight) for all factors
    - complexity_level: "low" (< 2.0), "medium" (2.0-3.5), "high" (> 3.5)
    - estimated_weeks: based on complexity_level and team_size
    - risk_factors: list of factors scoring >= 4

    Scoring rules:
    - integrations: 0 -> 1, 1-2 -> 2, 3-4 -> 3, 5-7 -> 4, 8+ -> 5
    - data_sources: 1 -> 1, 2-3 -> 2, 4-5 -> 3, 6-8 -> 4, 9+ -> 5
    - user_types: 1 -> 1, 2 -> 2, 3-4 -> 3, 5+ -> 4
    - compliance: 0 -> 1, 1 -> 2, 2 -> 3, 3+ -> 4, includes "hipaa"/"pci" -> 5
    - ML: False -> 1, True -> 4, True + realtime -> 5
    - Realtime: False -> 1, True -> 3, True + ML -> 5
    - Team: 5+ -> 1, 3-4 -> 2, 2 -> 3, 1 -> 4

    Args:
        project_name: Name of the project
        integrations: List of integration names
        data_sources: Number of data sources
        user_types: Number of distinct user types
        compliance_requirements: List (e.g., ["SOC2", "HIPAA"])
        has_ml_component: Whether ML/AI is involved
        has_realtime_requirement: Whether real-time processing is needed
        team_size: Number of engineers

    Returns:
        Dict with "project_name", "factors" (list of ComplexityFactor dicts),
        "weighted_score", "complexity_level", "estimated_weeks",
        "risk_factors", "recommendations"
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 10: Documentation Coverage Checker
# ============================================================================
# Check how well a Python module is documented by analyzing its source.
# Undocumented public APIs are a liability -- this tool quantifies the gap.
#
# Swift analogy: Like running DocC and checking for missing documentation
# warnings on public symbols.
# ============================================================================

@dataclass
class CoverageReport:
    """Documentation coverage report for a module."""
    total_public_items: int
    documented_items: int
    undocumented_items: list[str]   # Names of undocumented public items
    coverage_percentage: float       # 0-100
    items: list[dict[str, Any]]     # Per-item details


def exercise_10_doc_coverage_checker(
    source_code: str,
    module_name: str = "module",
) -> CoverageReport:
    """
    Exercise 10: Check documentation coverage of Python source code.

    Parse the source code AST and check for docstrings on:
    - Module level
    - All public classes (not starting with _)
    - All public functions/methods (not starting with _)

    For each public item, record:
    - name: qualified name (e.g., "MyClass.my_method")
    - type: "class", "function", "method"
    - has_docstring: bool
    - line_number: int
    - has_type_hints: bool (for functions/methods)

    Compute coverage_percentage = (documented / total) * 100

    Args:
        source_code: Python source code to analyze
        module_name: Name for the module in the report

    Returns:
        CoverageReport with per-item details
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 11: FAQ Generator from Support Tickets
# ============================================================================
# Cluster similar support tickets and generate FAQ entries. Solutions
# engineers use this to identify common customer pain points and create
# self-service documentation.
#
# Swift analogy: Like analyzing App Store reviews to identify common
# issues and building a knowledge base from them.
# ============================================================================

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


def exercise_11_faq_generator(
    tickets: list[SupportTicket],
    similarity_threshold: float = 0.3,
    min_cluster_size: int = 2,
) -> dict[str, Any]:
    """
    Exercise 11: Generate FAQ entries from support tickets.

    Process:
    1. Normalize ticket subjects (lowercase, strip punctuation)
    2. Group tickets by keyword similarity:
       - Extract significant words (> 3 chars, not stopwords)
       - Two tickets are similar if they share >= similarity_threshold
         fraction of their significant words (Jaccard similarity)
    3. For each group with >= min_cluster_size tickets:
       - Generate a question from the most common subject pattern
       - Generate an answer from the most detailed resolution
       - Record source ticket IDs and frequency count
    4. Sort FAQs by frequency (most common first)

    Stopwords to exclude: {"the", "a", "an", "is", "are", "was", "were",
    "how", "what", "why", "can", "do", "does", "not", "with", "for",
    "from", "this", "that", "have", "has", "will", "been", "being"}

    Args:
        tickets: List of support tickets
        similarity_threshold: Minimum Jaccard similarity to cluster (0-1)
        min_cluster_size: Minimum tickets to form a FAQ entry

    Returns:
        Dict with:
        - "faqs": list of FAQEntry dicts sorted by frequency desc
        - "total_tickets": int
        - "tickets_covered": int (tickets that matched a FAQ)
        - "coverage_percentage": float
        - "uncategorized_ticket_ids": list of ticket IDs not in any FAQ
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 12: Release Notes Formatter
# ============================================================================
# Format release notes for different audiences: developers (technical),
# product managers (feature-focused), and executives (business impact).
# The same release, three different stories.
#
# Swift analogy: Like writing different App Store descriptions for
# developers vs. end users vs. marketing.
# ============================================================================

@dataclass
class ReleaseFeature:
    """A feature included in a release."""
    title: str
    technical_description: str
    user_benefit: str
    business_impact: str
    category: str            # "feature", "improvement", "bugfix", "infrastructure"
    breaking: bool = False


def exercise_12_release_notes_formatter(
    version: str,
    release_date: str,
    features: list[ReleaseFeature],
    audience: str = "developer",
) -> dict[str, Any]:
    """
    Exercise 12: Format release notes tailored to a specific audience.

    Three audience modes:

    "developer":
    - Title: "Release Notes v{version}"
    - Lead with breaking changes (if any)
    - Group by category
    - Use technical_description for each item
    - Include migration notes for breaking changes

    "product":
    - Title: "What's New in v{version}"
    - Lead with features, then improvements
    - Use user_benefit for each item
    - Skip infrastructure items
    - No code or technical details

    "executive":
    - Title: "Release Summary: v{version}"
    - Only features and improvements
    - Use business_impact for each item
    - Include counts (X new features, Y improvements)
    - Keep it brief (one line per item max)

    Args:
        version: Release version
        release_date: ISO date
        features: List of ReleaseFeature objects
        audience: "developer", "product", or "executive"

    Returns:
        Dict with "title", "audience", "version", "date", "sections"
        (list of dicts with "heading" and "items"), "has_breaking_changes"
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 13: Customer Status Update Template Engine
# ============================================================================
# Generate customer-facing status updates for ongoing incidents or
# projects. Tone, detail level, and urgency markers vary by context.
#
# Swift analogy: Like generating push notification copy that varies
# by severity and user preferences.
# ============================================================================

def exercise_13_status_update_engine(
    update_type: str,
    title: str,
    status: str,
    details: dict[str, Any],
    audience: str = "external",
) -> dict[str, Any]:
    """
    Exercise 13: Generate a customer status update.

    update_type determines the template:

    "incident":
    - status must be one of: "investigating", "identified", "monitoring", "resolved"
    - details keys: "affected_services", "impact", "current_action", "eta",
      "workaround"
    - External: professional, reassuring tone; omit internal details
    - Internal: include technical details and action owners

    "maintenance":
    - status must be one of: "scheduled", "in_progress", "completed"
    - details keys: "services", "start_time", "end_time", "description"
    - External: focus on user impact and timing
    - Internal: include technical scope and rollback plan

    "project":
    - status must be one of: "on_track", "at_risk", "delayed", "completed"
    - details keys: "milestone", "progress_pct", "blockers", "next_steps"
    - External: focus on deliverables and timeline
    - Internal: include resource needs and risk details

    Args:
        update_type: "incident", "maintenance", or "project"
        title: Update title
        status: Status value appropriate for the update_type
        details: Context-specific details dict
        audience: "external" (customer-facing) or "internal"

    Returns:
        Dict with "title", "type", "status", "audience", "timestamp",
        "body" (formatted text), "status_emoji" (text indicator like
        "[RESOLVED]"), "sections" (list of section dicts)
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 14: Technical Presentation Outline Generator
# ============================================================================
# Generate a structured presentation outline from a topic and audience.
# Solutions engineers present constantly -- to customers, at conferences,
# and in internal reviews.
#
# Swift analogy: Like generating a Keynote slide structure with speaker
# notes and timing estimates.
# ============================================================================

@dataclass
class Slide:
    """A single slide in the presentation."""
    slide_number: int
    title: str
    bullet_points: list[str]
    speaker_notes: str
    slide_type: str          # "title", "content", "demo", "code", "summary"
    estimated_minutes: float


def exercise_14_presentation_outline_generator(
    topic: str,
    audience: str,
    duration_minutes: int,
    key_points: list[str],
    include_demo: bool = False,
    include_code_samples: bool = False,
) -> dict[str, Any]:
    """
    Exercise 14: Generate a technical presentation outline.

    Create a presentation structure:
    1. Title slide (1 min)
    2. Agenda/Overview slide (1 min)
    3. Context/Problem slide (2 min)
    4. Key point slides (remaining time distributed evenly across points,
       minus time for intro/close/demo)
    5. Demo slide if include_demo (allocate 20% of remaining time)
    6. Code sample slides if include_code_samples (1 per key point, 1 min each)
    7. Summary/Recap slide (1 min)
    8. Q&A slide (2 min)

    Audience affects language:
    - "technical": use precise terminology, include architecture details
    - "business": focus on outcomes, use plain language
    - "mixed": balance both, define terms when first used

    Args:
        topic: Presentation topic
        audience: "technical", "business", or "mixed"
        duration_minutes: Total presentation time
        key_points: Main points to cover
        include_demo: Whether to include a demo slot
        include_code_samples: Whether to include code example slides

    Returns:
        Dict with "topic", "audience", "total_duration", "slide_count",
        "slides" (list of Slide dicts), "time_allocation" (dict of
        section -> minutes)
    """
    # TODO: Implement
    pass


# ============================================================================
# Exercise 15: Code Example Test Runner Framework
# ============================================================================
# Build a framework that extracts code examples from documentation text,
# runs them, and reports results. This ensures docs stay in sync with
# the actual API behavior.
#
# Swift analogy: Like DocC's executable code snippets that verify
# examples compile and produce expected output.
# ============================================================================

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


def exercise_15_code_example_test_runner(
    document_text: str,
    execute: bool = False,
) -> dict[str, Any]:
    """
    Exercise 15: Extract and optionally test code examples from documentation.

    Process:
    1. Parse document_text for fenced code blocks:
       ```python
       <code here>
       ```
       Optionally followed by an expected output block:
       ```output
       <expected output>
       ```

    2. Extract each code block into a CodeExample with:
       - id: "example_1", "example_2", etc.
       - language: from the fence info string (e.g., "python")
       - code: the code content
       - expected_output: from the output block if present
       - line_number: line where the code block starts
       - description: text on the line immediately before the code block

    3. If execute is True and language is "python":
       - Run each example using exec() in a sandboxed namespace
       - Capture stdout as actual_output
       - Compare against expected_output if provided
       - Record pass/fail and any errors

    4. If execute is False, just validate syntax with ast.parse()

    Args:
        document_text: Markdown text containing code examples
        execute: Whether to actually run the code

    Returns:
        Dict with:
        - "examples": list of CodeExample dicts
        - "results": list of TestResult dicts
        - "total": int
        - "passed": int
        - "failed": int
        - "pass_rate": float (0-100)
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_exercise_1():
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
    result = exercise_1_api_tutorial_generator(
        api_name="Messages API",
        base_url="https://api.anthropic.com",
        endpoints=endpoints,
        auth_type="bearer_token",
    )
    assert isinstance(result, dict)
    assert result["title"] == "Messages API Tutorial"
    assert "sections" in result
    assert len(result["sections"]) >= 4  # intro, prerequisites, quickstart, endpoints...
    assert result["metadata"]["endpoint_count"] == 2
    assert result["metadata"]["auth_type"] == "bearer_token"
    print("  Exercise 1 (API Tutorial Generator): PASSED")


def test_exercise_2():
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
    result = exercise_2_code_sample_validator(good_code)
    assert result.syntax_ok is True
    assert result.has_docstrings is True
    assert result.has_error_handling is True
    assert result.has_main_guard is True
    assert result.has_type_hints is True
    assert result.completeness_score > 0.7

    bad_code = "def foo(\n    x = "  # syntax error
    result2 = exercise_2_code_sample_validator(bad_code)
    assert result2.syntax_ok is False
    assert result2.is_valid is False
    print("  Exercise 2 (Code Sample Validator): PASSED")


def test_exercise_3():
    """Test requirements extractor."""
    description = """
    We need a customer support chatbot that must handle 1000 concurrent users.
    It should integrate with our Salesforce CRM and Zendesk ticketing system.
    The system must be SOC2 compliant and should respond within 2 seconds.
    It would be nice to have multilingual support. The bot will need to
    connect to our PostgreSQL database for customer data.
    """
    result = exercise_3_requirements_extractor(description)
    assert "requirements" in result
    assert len(result["requirements"]) >= 3
    assert "summary" in result
    # Check that we found must-have requirements
    priorities = [r["priority"] for r in result["requirements"]]
    assert "must-have" in priorities
    print("  Exercise 3 (Requirements Extractor): PASSED")


def test_exercise_4():
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
    result = exercise_4_migration_guide_generator("v1", "v2", old_endpoints, new_endpoints)
    assert result["from_version"] == "v1"
    assert result["to_version"] == "v2"
    assert len(result["changes"]) > 0
    assert result["breaking_changes_count"] >= 1  # /v1/complete was removed
    print("  Exercise 4 (Migration Guide Generator): PASSED")


def test_exercise_5():
    """Test changelog formatter."""
    changes = [
        ChangeEntry("added", "Streaming support for messages API", "#101"),
        ChangeEntry("added", "Vision input for Claude 3 models", "#102"),
        ChangeEntry("fixed", "Rate limiting header format", "#95"),
        ChangeEntry("changed", "Default max_tokens increased to 4096", "#100"),
        ChangeEntry("deprecated", "Legacy completions endpoint", "#98"),
    ]
    result = exercise_5_changelog_formatter(
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
    print("  Exercise 5 (Changelog Formatter): PASSED")


def test_exercise_6():
    """Test ADR generator."""
    result = exercise_6_adr_generator(
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
    print("  Exercise 6 (ADR Generator): PASSED")


def test_exercise_7():
    """Test runbook generator."""
    steps = [
        {"action": "Check service health", "command": "curl localhost:8080/health",
         "expected_output": '{"status": "ok"}', "rollback": "", "warning": ""},
        {"action": "Restart service", "command": "systemctl restart ml-api",
         "expected_output": "Active: active (running)",
         "rollback": "systemctl stop ml-api", "warning": "Will cause brief downtime"},
    ]
    result = exercise_7_runbook_generator(
        title="ML API Service Recovery",
        service_name="ml-api",
        scenario="Service returning 503 errors",
        steps=steps,
        severity="high",
    )
    assert result["title"] == "ML API Service Recovery"
    assert result["severity"] == "high"
    assert len(result["steps"]) == 2
    assert result["estimated_time_minutes"] == 4  # 2 steps * 2 min
    print("  Exercise 7 (Runbook Generator): PASSED")


def test_exercise_8():
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
    result = exercise_8_postmortem_formatter(
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
    print("  Exercise 8 (Postmortem Formatter): PASSED")


def test_exercise_9():
    """Test complexity estimator."""
    result = exercise_9_complexity_estimator(
        project_name="Customer Support AI",
        integrations=["Salesforce", "Zendesk", "Slack", "PostgreSQL"],
        data_sources=3,
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
    # With ML + realtime + 4 integrations, should be high complexity
    assert result["complexity_level"] == "high"
    print("  Exercise 9 (Complexity Estimator): PASSED")


def test_exercise_10():
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
    result = exercise_10_doc_coverage_checker(sample_code, "test_module")
    assert result.total_public_items >= 4  # class, public_method, undocumented_method, 2 functions
    assert result.documented_items >= 3    # class, public_method, documented_function
    assert len(result.undocumented_items) >= 1
    assert "undocumented_function" in result.undocumented_items
    assert 0 < result.coverage_percentage <= 100
    print("  Exercise 10 (Doc Coverage Checker): PASSED")


def test_exercise_11():
    """Test FAQ generator."""
    tickets = [
        SupportTicket("T1", "How to authenticate API calls",
                      "Need help with auth", "auth", "Use bearer token in header"),
        SupportTicket("T2", "Authentication error with API",
                      "Getting 401 errors", "auth", "Check API key is valid"),
        SupportTicket("T3", "API authentication not working",
                      "Token rejected", "auth", "Regenerate API key from dashboard"),
        SupportTicket("T4", "Rate limit exceeded error",
                      "Getting 429 errors", "limits", "Implement exponential backoff"),
        SupportTicket("T5", "Rate limiting questions",
                      "What are the rate limits?", "limits", "See rate limits docs page"),
        SupportTicket("T6", "Unique billing question",
                      "Invoice format", "billing", "Contact billing team"),
    ]
    result = exercise_11_faq_generator(tickets, similarity_threshold=0.3, min_cluster_size=2)
    assert len(result["faqs"]) >= 2  # auth cluster + rate limit cluster
    assert result["total_tickets"] == 6
    assert result["tickets_covered"] >= 4
    assert "T6" in result["uncategorized_ticket_ids"]  # unique ticket not clustered
    print("  Exercise 11 (FAQ Generator): PASSED")


def test_exercise_12():
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
    dev_result = exercise_12_release_notes_formatter("3.0.0", "2026-04-29", features, "developer")
    assert dev_result["has_breaking_changes"] is True
    assert dev_result["audience"] == "developer"

    exec_result = exercise_12_release_notes_formatter("3.0.0", "2026-04-29", features, "executive")
    assert exec_result["audience"] == "executive"
    print("  Exercise 12 (Release Notes Formatter): PASSED")


def test_exercise_13():
    """Test status update engine."""
    result = exercise_13_status_update_engine(
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
    print("  Exercise 13 (Status Update Engine): PASSED")


def test_exercise_14():
    """Test presentation outline generator."""
    result = exercise_14_presentation_outline_generator(
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
    assert len(result["slides"]) >= 6  # title + agenda + key points + summary + Q&A
    total_time = sum(s["estimated_minutes"] for s in result["slides"])
    assert abs(total_time - 30) < 1  # Should roughly sum to duration
    print("  Exercise 14 (Presentation Outline Generator): PASSED")


def test_exercise_15():
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
    result = exercise_15_code_example_test_runner(doc_text, execute=True)
    assert result["total"] >= 2  # 2 Python examples
    assert result["passed"] >= 2  # Both should pass
    assert result["pass_rate"] == 100.0

    # Test with syntax error
    bad_doc = """
```python
def broken(
```
"""
    result2 = exercise_15_code_example_test_runner(bad_doc, execute=False)
    assert result2["failed"] >= 1
    print("  Exercise 15 (Code Example Test Runner): PASSED")


if __name__ == "__main__":
    print("Testing Technical Communication exercises...\n")
    test_exercise_1()
    test_exercise_2()
    test_exercise_3()
    test_exercise_4()
    test_exercise_5()
    test_exercise_6()
    test_exercise_7()
    test_exercise_8()
    test_exercise_9()
    test_exercise_10()
    test_exercise_11()
    test_exercise_12()
    test_exercise_13()
    test_exercise_14()
    test_exercise_15()
    print("\nAll Technical Communication exercises passed!")
