"""
Module 10 Exercises: Customer Scenario Simulation
==================================================

These exercises build the tooling an Applied AI / Solutions Engineer uses
daily: qualifying customers, scoping POCs, running workshops, handling
incidents, and orchestrating full scenario simulations.

For Swift developers: think of each exercise as a self-contained "service
object" -- like building a HealthKit data pipeline or a StoreKit receipt
validator -- but for the customer-facing side of AI engineering.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any


# ---------------------------------------------------------------------------
# Exercise 1: Customer Profile Model
# ---------------------------------------------------------------------------
# Build a structured customer profile that captures everything a solutions
# engineer needs to know before a first call: industry vertical, company
# size, current tech stack, AI maturity, and key requirements.
#
# This is the "source of truth" that every downstream tool (triage,
# POC scoping, workshop planning) reads from.
#
# Swift analogy: Like a Core Data entity with computed properties and
# validation -- the canonical model object in your domain layer.
# ---------------------------------------------------------------------------

class CompanySize(Enum):
    STARTUP = "startup"           # < 50 employees
    SMB = "smb"                   # 50-500
    MID_MARKET = "mid_market"     # 500-5000
    ENTERPRISE = "enterprise"     # 5000+


class AIMaturity(Enum):
    EXPLORING = "exploring"       # No AI in production
    EXPERIMENTING = "experimenting"  # POCs / prototypes
    SCALING = "scaling"           # Some AI in production
    OPTIMIZING = "optimizing"     # Mature AI operations


@dataclass
class CustomerProfile:
    """Complete customer profile for pre-call preparation.

    Attributes:
        company_name: Legal entity name.
        industry: Vertical (e.g. "healthcare", "fintech", "e-commerce").
        size: Company size tier.
        employee_count: Approximate headcount.
        ai_maturity: Current AI adoption level.
        tech_stack: List of key technologies (e.g. ["Python", "AWS", "PostgreSQL"]).
        requirements: List of stated needs / goals.
        annual_revenue_mm: Annual revenue in millions USD (optional).
        existing_ai_tools: AI tools already in use (e.g. ["OpenAI", "Hugging Face"]).
        pain_points: Specific challenges the customer faces.
    """
    company_name: str
    industry: str
    size: CompanySize
    employee_count: int
    ai_maturity: AIMaturity
    tech_stack: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    annual_revenue_mm: float | None = None
    existing_ai_tools: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)

    def is_enterprise(self) -> bool:
        """Return True if the customer qualifies as enterprise tier.

        Enterprise = CompanySize.ENTERPRISE OR employee_count >= 5000
        OR annual_revenue_mm >= 500.
        """
        # TODO: Implement
        pass

    def tech_stack_overlap(self, supported_stack: list[str]) -> float:
        """Return fraction of customer's stack that is in supported_stack.

        Case-insensitive comparison. Returns 0.0 if customer has no stack.
        """
        # TODO: Implement
        pass

    def readiness_score(self) -> float:
        """Score 0-100 indicating how ready the customer is for an AI engagement.

        Scoring rubric (sum the applicable points):
          - ai_maturity: EXPLORING=10, EXPERIMENTING=25, SCALING=40, OPTIMIZING=50
          - Has >= 3 requirements listed: +15
          - Has >= 2 items in existing_ai_tools: +15
          - Has identified pain_points (>= 1): +10
          - tech_stack has >= 3 items: +10
        Cap at 100.
        """
        # TODO: Implement
        pass

    def to_summary(self) -> str:
        """One-line human-readable summary.

        Format: "{company_name} | {industry} | {size.value} | AI:{ai_maturity.value} | Readiness:{readiness_score():.0f}"
        """
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 2: Technical Requirements Discovery Questionnaire
# ---------------------------------------------------------------------------
# Implement a structured questionnaire that guides discovery calls.
# Each question has a category, the question text, acceptable answer
# types, and follow-up logic.
#
# Swift analogy: Like building a dynamic UITableView form where cells
# appear/disappear based on previous answers (think insurance app flow).
# ---------------------------------------------------------------------------

class QuestionCategory(Enum):
    USE_CASE = "use_case"
    DATA = "data"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    TIMELINE = "timeline"
    BUDGET = "budget"


@dataclass
class Question:
    """A single discovery question."""
    id: str
    category: QuestionCategory
    text: str
    required: bool = True
    depends_on: str | None = None       # Question ID that must be answered first
    expected_type: str = "text"          # "text", "number", "choice", "multi_choice"
    choices: list[str] | None = None    # For choice / multi_choice types


@dataclass
class QuestionnaireResponse:
    """A completed (or partial) questionnaire."""
    answers: dict[str, Any] = field(default_factory=dict)  # question_id -> answer

    def is_complete(self, questions: list[Question]) -> bool:
        """Return True if all required questions have answers."""
        # TODO: Implement
        pass

    def completion_percentage(self, questions: list[Question]) -> float:
        """Return percentage of required questions answered (0-100)."""
        # TODO: Implement
        pass

    def unanswered_required(self, questions: list[Question]) -> list[str]:
        """Return list of IDs of required questions that are not yet answered."""
        # TODO: Implement
        pass


def build_discovery_questionnaire() -> list[Question]:
    """Build and return the standard discovery questionnaire.

    Must include at least 8 questions spanning at least 4 categories.
    At least one question should have depends_on set.
    At least one question should be of type "choice" with choices provided.

    Returns:
        Ordered list of Question objects.
    """
    # TODO: Implement - return a list of Question objects
    pass


# ---------------------------------------------------------------------------
# Exercise 3: POC Scope Document Generator
# ---------------------------------------------------------------------------
# Given a customer profile and questionnaire responses, generate a
# structured POC (Proof of Concept) scope document.
#
# Swift analogy: Like generating an App Store Connect submission
# package from your Xcode project metadata.
# ---------------------------------------------------------------------------

@dataclass
class POCScope:
    """Structured POC scope document."""
    title: str
    customer_name: str
    objective: str
    success_criteria: list[str]
    deliverables: list[str]
    timeline_weeks: int
    required_resources: list[str]
    risks: list[str]
    out_of_scope: list[str]

    def to_markdown(self) -> str:
        """Render the POC scope as a Markdown document.

        Include sections: Objective, Success Criteria (bulleted),
        Deliverables (bulleted), Timeline, Required Resources (bulleted),
        Risks (bulleted), Out of Scope (bulleted).
        """
        # TODO: Implement
        pass


def generate_poc_scope(
    profile: CustomerProfile,
    responses: QuestionnaireResponse,
    questions: list[Question],
) -> POCScope:
    """Generate a POC scope document from customer profile and discovery answers.

    Rules:
      - title: "AI POC: {profile.company_name} - {industry}"
      - objective: derived from the first answered USE_CASE question, or a default
      - timeline_weeks: 4 if startup/smb, 8 if mid_market, 12 if enterprise
      - success_criteria: must have at least 2 items
      - deliverables: must have at least 2 items
      - risks: add "Data quality unknown" if no DATA questions answered
      - out_of_scope: always include "Production deployment"

    Returns:
        A populated POCScope dataclass.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Success Criteria Framework
# ---------------------------------------------------------------------------
# Define measurable success criteria for customer engagements.
# Each criterion has a metric, a target, a measurement method, and a
# priority level.
# ---------------------------------------------------------------------------

class CriteriaPriority(Enum):
    MUST_HAVE = "must_have"
    SHOULD_HAVE = "should_have"
    NICE_TO_HAVE = "nice_to_have"


@dataclass
class SuccessCriterion:
    """A single measurable success criterion."""
    name: str
    metric: str
    target_value: float
    unit: str
    measurement_method: str
    priority: CriteriaPriority
    lower_is_better: bool = False   # True for latency, error rate, etc.

    def is_met(self, actual_value: float) -> bool:
        """Return True if the criterion is satisfied.

        If lower_is_better is True (e.g. latency), actual <= target means met.
        Otherwise (e.g. accuracy), actual >= target means met.
        """
        # TODO: Implement
        pass


@dataclass
class SuccessFramework:
    """Collection of success criteria for an engagement."""
    criteria: list[SuccessCriterion] = field(default_factory=list)

    def add_criterion(self, criterion: SuccessCriterion) -> None:
        """Add a criterion. Raise ValueError if name already exists."""
        # TODO: Implement
        pass

    def evaluate(self, actuals: dict[str, float]) -> dict[str, bool]:
        """Evaluate all criteria against actual values.

        Args:
            actuals: dict mapping criterion name -> actual measured value.

        Returns:
            dict mapping criterion name -> whether it was met.
            Missing actuals count as not met.
        """
        # TODO: Implement
        pass

    def pass_rate(self, actuals: dict[str, float]) -> float:
        """Return fraction of criteria that are met (0.0 - 1.0)."""
        # TODO: Implement
        pass

    def must_haves_met(self, actuals: dict[str, float]) -> bool:
        """Return True only if ALL must_have criteria are met."""
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 5: Customer Triage Classifier
# ---------------------------------------------------------------------------
# Classify inbound customer requests by priority and complexity so that
# the right SE is assigned. This is the "router" in a support org.
#
# Swift analogy: Like a notification routing engine that decides which
# UNNotificationCategory to assign based on payload content.
# ---------------------------------------------------------------------------

class TriagePriority(Enum):
    CRITICAL = "critical"     # Production down, revenue impact
    HIGH = "high"             # Significant blocker
    MEDIUM = "medium"         # Important but not blocking
    LOW = "low"               # Nice to have / general inquiry


class TriageComplexity(Enum):
    SIMPLE = "simple"         # < 1 day effort
    MODERATE = "moderate"     # 1-5 days effort
    COMPLEX = "complex"       # 1-4 weeks effort
    STRATEGIC = "strategic"   # Multi-month engagement


@dataclass
class TriageResult:
    """Result of triaging a customer request."""
    priority: TriagePriority
    complexity: TriageComplexity
    recommended_team: str
    estimated_effort_days: int
    reasoning: str


def triage_customer_request(
    request_text: str,
    profile: CustomerProfile,
    is_production_issue: bool = False,
    revenue_impact: bool = False,
) -> TriageResult:
    """Classify a customer request by priority and complexity.

    Priority rules (pick the highest that applies):
      - CRITICAL if is_production_issue AND revenue_impact
      - CRITICAL if is_production_issue AND profile.is_enterprise()
      - HIGH if is_production_issue OR revenue_impact
      - HIGH if profile.is_enterprise() and any keyword in request_text:
        ["urgent", "blocker", "deadline", "critical"]
      - MEDIUM if profile.size in (MID_MARKET, ENTERPRISE)
      - LOW otherwise

    Complexity rules:
      - STRATEGIC if len(request_text) > 500 and profile.is_enterprise()
      - COMPLEX if len(request_text) > 300 or "integration" in request_text.lower()
      - MODERATE if len(request_text) > 100
      - SIMPLE otherwise

    recommended_team:
      - "incident_response" if priority is CRITICAL
      - "solutions_engineering" if complexity is COMPLEX or STRATEGIC
      - "technical_support" otherwise

    estimated_effort_days:
      - SIMPLE=1, MODERATE=3, COMPLEX=10, STRATEGIC=30

    Returns:
        TriageResult with all fields populated.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Workshop Agenda Builder
# ---------------------------------------------------------------------------
# Build customized technical workshop agendas based on customer profile
# and goals. Workshops are how SEs demonstrate value and build trust.
#
# Swift analogy: Like building a WWDC lab schedule dynamically based on
# which frameworks the developer team uses.
# ---------------------------------------------------------------------------

@dataclass
class AgendaItem:
    """A single item on a workshop agenda."""
    title: str
    duration_minutes: int
    presenter: str
    item_type: str            # "presentation", "demo", "hands_on", "discussion", "break"
    description: str = ""


@dataclass
class WorkshopAgenda:
    """Complete workshop agenda."""
    title: str
    customer_name: str
    date: str
    total_duration_minutes: int
    items: list[AgendaItem] = field(default_factory=list)

    def add_item(self, item: AgendaItem) -> None:
        """Add an item. Raise ValueError if total would exceed total_duration_minutes."""
        # TODO: Implement
        pass

    def current_duration(self) -> int:
        """Return sum of all item durations in minutes."""
        # TODO: Implement
        pass

    def remaining_minutes(self) -> int:
        """Return minutes remaining in the agenda."""
        # TODO: Implement
        pass

    def to_schedule(self, start_time: str = "09:00") -> list[dict[str, str]]:
        """Generate a time-boxed schedule.

        Args:
            start_time: HH:MM format start time.

        Returns:
            List of dicts with keys: "time", "title", "duration", "type".
            Each "time" is the computed start time in HH:MM format.
        """
        # TODO: Implement
        pass


def build_workshop_agenda(
    profile: CustomerProfile,
    focus_areas: list[str],
    duration_hours: int = 4,
) -> WorkshopAgenda:
    """Build a customized workshop agenda for a customer.

    Rules:
      - Always start with a 15-min "Welcome & Introductions" (presentation)
      - Always end with a 15-min "Q&A and Next Steps" (discussion)
      - Include a 15-min break roughly in the middle
      - For each focus_area, add a 30-min hands_on session
      - Fill remaining time with a "Platform Overview" demo
      - title: "AI Workshop: {focus_areas joined by ', '}"

    Returns:
        A WorkshopAgenda with items that fit within duration_hours.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Enterprise Security Questionnaire Responder
# ---------------------------------------------------------------------------
# Enterprise customers send lengthy security questionnaires before buying.
# Build a knowledge base of pre-approved answers and a matcher that finds
# the best response for each incoming question.
#
# Swift analogy: Like building a FAQ search with string similarity --
# similar to implementing a UISearchController with fuzzy matching.
# ---------------------------------------------------------------------------

@dataclass
class SecurityAnswer:
    """A pre-approved answer in the security knowledge base."""
    question_pattern: str    # Canonical form of the question
    answer: str
    category: str            # "encryption", "access_control", "compliance", etc.
    keywords: list[str] = field(default_factory=list)
    last_reviewed: str = ""  # ISO date of last legal/security review


class SecurityQuestionnaireResponder:
    """Match incoming security questions to pre-approved answers."""

    def __init__(self) -> None:
        self.knowledge_base: list[SecurityAnswer] = []

    def add_answer(self, answer: SecurityAnswer) -> None:
        """Add a pre-approved answer to the knowledge base."""
        # TODO: Implement
        pass

    def _keyword_score(self, question: str, entry: SecurityAnswer) -> float:
        """Score how well a question matches an entry based on keyword overlap.

        Score = number of entry keywords found in question (case-insensitive)
                divided by total entry keywords. Returns 0.0 if no keywords.
        """
        # TODO: Implement
        pass

    def find_best_answer(self, question: str, min_score: float = 0.3) -> SecurityAnswer | None:
        """Find the best matching pre-approved answer for a question.

        Uses _keyword_score to rank entries. Returns the highest-scoring
        entry if its score >= min_score, else None.
        """
        # TODO: Implement
        pass

    def respond_to_questionnaire(
        self, questions: list[str], min_score: float = 0.3
    ) -> list[dict[str, Any]]:
        """Process a full questionnaire and return responses.

        Returns:
            List of dicts with keys:
              - "question": the original question
              - "answer": matched answer text or "NEEDS MANUAL REVIEW"
              - "confidence": the keyword score (0.0 if no match)
              - "category": matched category or "unknown"
        """
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 8: Compliance Checklist for Multiple Frameworks
# ---------------------------------------------------------------------------
# Build compliance checklists for SOC2, HIPAA, and GDPR. Each item has
# a control description, status, and evidence reference.
#
# Swift analogy: Like managing entitlements and privacy manifests for
# App Store review -- different "frameworks" with overlapping requirements.
# ---------------------------------------------------------------------------

class ComplianceStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"


@dataclass
class ComplianceItem:
    """A single compliance control item."""
    control_id: str
    framework: str                # "SOC2", "HIPAA", "GDPR"
    description: str
    status: ComplianceStatus = ComplianceStatus.NOT_STARTED
    evidence: str = ""
    owner: str = ""


@dataclass
class ComplianceChecklist:
    """Compliance checklist spanning multiple frameworks."""
    items: list[ComplianceItem] = field(default_factory=list)

    def add_item(self, item: ComplianceItem) -> None:
        """Add item. Raise ValueError if control_id already exists."""
        # TODO: Implement
        pass

    def get_by_framework(self, framework: str) -> list[ComplianceItem]:
        """Return all items for a given framework."""
        # TODO: Implement
        pass

    def completion_by_framework(self) -> dict[str, float]:
        """Return completion percentage per framework.

        An item counts as "complete" if status is IMPLEMENTED or VERIFIED.
        Returns dict mapping framework name -> percentage (0-100).
        """
        # TODO: Implement
        pass

    def gaps(self) -> list[ComplianceItem]:
        """Return all items that are NOT_STARTED or IN_PROGRESS."""
        # TODO: Implement
        pass

    def overall_completion(self) -> float:
        """Return overall completion percentage across all frameworks (0-100)."""
        # TODO: Implement
        pass


def build_compliance_checklist(frameworks: list[str]) -> ComplianceChecklist:
    """Build a compliance checklist for the given frameworks.

    Supported frameworks: "SOC2", "HIPAA", "GDPR".
    Each framework should have at least 3 control items.
    Raise ValueError for unsupported frameworks.

    Returns:
        A ComplianceChecklist populated with NOT_STARTED items.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Incident Severity Classifier
# ---------------------------------------------------------------------------
# Classify production incidents by severity based on impact metrics.
# This drives the incident response process (who gets paged, SLA timers).
#
# Swift analogy: Like crash report triage in Xcode Organizer -- deciding
# which crashes to fix first based on frequency and user impact.
# ---------------------------------------------------------------------------

class IncidentSeverity(Enum):
    SEV1 = "sev1"   # Total outage, all customers affected
    SEV2 = "sev2"   # Major degradation, many customers affected
    SEV3 = "sev3"   # Partial issue, some customers affected
    SEV4 = "sev4"   # Minor issue, minimal impact


@dataclass
class IncidentReport:
    """Raw incident report data."""
    title: str
    description: str
    affected_customers: int
    total_customers: int
    is_data_loss: bool = False
    is_security_breach: bool = False
    service_degradation_percent: float = 0.0   # 0-100
    revenue_impact_per_hour: float = 0.0


def classify_incident_severity(report: IncidentReport) -> IncidentSeverity:
    """Classify an incident report into a severity level.

    Rules (pick the highest / most severe that applies):
      - SEV1 if is_security_breach OR is_data_loss
      - SEV1 if affected_customers / total_customers > 0.5
      - SEV1 if service_degradation_percent >= 90
      - SEV2 if affected_customers / total_customers > 0.25
      - SEV2 if service_degradation_percent >= 50
      - SEV2 if revenue_impact_per_hour >= 10000
      - SEV3 if affected_customers / total_customers > 0.05
      - SEV3 if service_degradation_percent >= 20
      - SEV4 otherwise

    Returns:
        IncidentSeverity enum value.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Incident Communication Template Engine
# ---------------------------------------------------------------------------
# Generate formatted incident communications for different audiences
# (internal engineering, customer-facing, executive).
# ---------------------------------------------------------------------------

class CommunicationAudience(Enum):
    INTERNAL = "internal"       # Engineering team
    CUSTOMER = "customer"       # Affected customers
    EXECUTIVE = "executive"     # C-suite / VP


def generate_incident_communication(
    report: IncidentReport,
    severity: IncidentSeverity,
    audience: CommunicationAudience,
    status: str = "investigating",
    eta_minutes: int | None = None,
) -> str:
    """Generate an incident communication message.

    Format varies by audience:

    INTERNAL:
        "[{severity.value}] {report.title}
        Status: {status}
        Affected: {report.affected_customers}/{report.total_customers} customers
        Degradation: {report.service_degradation_percent}%
        Revenue impact: ${report.revenue_impact_per_hour}/hr
        Data loss: {Yes/No} | Security breach: {Yes/No}
        ETA: {eta_minutes} minutes (or 'TBD')"

    CUSTOMER:
        "Service Update: {report.title}
        We are aware of an issue affecting some of our services.
        Current status: {status}
        Estimated resolution: {eta_minutes} minutes (or 'We are working on a resolution')
        We apologize for any inconvenience."

    EXECUTIVE:
        "INCIDENT ALERT - {severity.value.upper()}
        Issue: {report.title}
        Business Impact: {affected_pct:.1f}% of customers affected
        Revenue Risk: ${report.revenue_impact_per_hour}/hr
        Status: {status}
        ETA: {eta_minutes} min (or 'Determining')"

    Returns:
        Formatted communication string.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Escalation Decision Tree
# ---------------------------------------------------------------------------
# Given incident severity, elapsed time, and context, determine whether
# to escalate and to whom.
# ---------------------------------------------------------------------------

@dataclass
class EscalationAction:
    """An escalation decision."""
    should_escalate: bool
    escalation_level: int          # 0 = no escalation, 1 = manager, 2 = director, 3 = VP
    notify: list[str]              # Roles/teams to notify
    reason: str


def evaluate_escalation(
    severity: IncidentSeverity,
    elapsed_minutes: int,
    is_customer_facing: bool = True,
    previous_escalation_level: int = 0,
) -> EscalationAction:
    """Determine if an incident should be escalated.

    Escalation rules:
      SEV1:
        - 0-15 min: level 1 (notify: ["on_call_manager", "incident_commander"])
        - 15-30 min: level 2 (notify: ["director_engineering", "director_support"])
        - 30+ min: level 3 (notify: ["vp_engineering", "cto"])
      SEV2:
        - 0-30 min: level 0 (no escalation, notify: ["on_call_engineer"])
        - 30-60 min: level 1 (notify: ["on_call_manager"])
        - 60+ min: level 2 (notify: ["director_engineering"])
      SEV3:
        - 0-60 min: level 0 (no escalation, notify: ["on_call_engineer"])
        - 60-120 min: level 1 (notify: ["on_call_manager"])
        - 120+ min: level 2 (notify: ["director_engineering"])
      SEV4:
        - Always level 0 (notify: ["on_call_engineer"])

    An escalation should happen (should_escalate=True) only if the
    computed level > previous_escalation_level.

    If is_customer_facing is True and severity is SEV1 or SEV2, also add
    "customer_success" to the notify list.

    Returns:
        EscalationAction with appropriate fields.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Customer Health Score Calculator
# ---------------------------------------------------------------------------
# Compute a composite health score for ongoing customer relationships.
# This is how Customer Success teams decide where to focus attention.
#
# Swift analogy: Like computing a "battery health" percentage from
# multiple sensor readings (cycle count, capacity, temperature).
# ---------------------------------------------------------------------------

@dataclass
class CustomerHealthMetrics:
    """Raw metrics for computing customer health."""
    api_calls_last_30d: int
    api_calls_previous_30d: int       # For trend comparison
    error_rate_percent: float         # 0-100
    support_tickets_open: int
    support_tickets_resolved_30d: int
    nps_score: int | None             # -100 to 100, or None if not collected
    days_since_last_login: int
    contract_months_remaining: int
    feature_adoption_percent: float   # 0-100, % of purchased features in use


def calculate_health_score(metrics: CustomerHealthMetrics) -> dict[str, Any]:
    """Calculate a composite customer health score.

    Component scores (each 0 - 100):
      usage_score:
        - If api_calls_previous_30d == 0: 50 if api_calls_last_30d > 0 else 0
        - Else: min(100, (api_calls_last_30d / api_calls_previous_30d) * 100)
      reliability_score:
        - 100 - (error_rate_percent * 2)   [clamp to 0-100]
      support_score:
        - Start at 100
        - Subtract 10 per open ticket (floor at 0)
        - Add 5 per resolved ticket in 30d (cap at 100)
      engagement_score:
        - Start at 100
        - Subtract 5 per day since last login (floor at 0)
      adoption_score:
        - Directly use feature_adoption_percent
      satisfaction_score:
        - If nps_score is None: 50 (neutral)
        - Else: (nps_score + 100) / 2  (maps -100..100 to 0..100)

    overall_score = weighted average:
        usage=0.20, reliability=0.15, support=0.15,
        engagement=0.20, adoption=0.15, satisfaction=0.15

    health_status:
        - "healthy" if overall >= 70
        - "at_risk" if 40 <= overall < 70
        - "critical" if overall < 40

    Returns:
        Dict with keys: "usage_score", "reliability_score", "support_score",
        "engagement_score", "adoption_score", "satisfaction_score",
        "overall_score", "health_status"
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 13: Migration Plan Generator
# ---------------------------------------------------------------------------
# Generate a phased migration plan for customers moving from one AI
# provider to another (e.g., OpenAI -> Anthropic, or on-prem -> cloud).
# ---------------------------------------------------------------------------

class MigrationPhase(Enum):
    ASSESSMENT = "assessment"
    PILOT = "pilot"
    PARALLEL_RUN = "parallel_run"
    CUTOVER = "cutover"
    DECOMMISSION = "decommission"


@dataclass
class MigrationTask:
    """A single task in a migration plan."""
    phase: MigrationPhase
    title: str
    description: str
    duration_days: int
    dependencies: list[str] = field(default_factory=list)   # Task titles
    owner: str = ""


@dataclass
class MigrationPlan:
    """Complete migration plan."""
    customer_name: str
    source_platform: str
    target_platform: str
    tasks: list[MigrationTask] = field(default_factory=list)

    def add_task(self, task: MigrationTask) -> None:
        """Add a task. Raise ValueError if title already exists."""
        # TODO: Implement
        pass

    def total_duration_days(self) -> int:
        """Estimate total duration (sum of task durations -- simplified, ignores parallelism)."""
        # TODO: Implement
        pass

    def tasks_by_phase(self) -> dict[str, list[MigrationTask]]:
        """Group tasks by phase. Keys are phase values."""
        # TODO: Implement
        pass

    def critical_path(self) -> list[str]:
        """Return task titles in dependency order (topological sort).

        Tasks with no dependencies come first.
        If a task depends on another, it appears after its dependency.
        Raise ValueError if there is a circular dependency.
        """
        # TODO: Implement
        pass


def generate_migration_plan(
    customer_name: str,
    source_platform: str,
    target_platform: str,
    num_endpoints: int,
) -> MigrationPlan:
    """Generate a migration plan for moving between AI platforms.

    Must create tasks for all 5 phases. Scale duration by num_endpoints:
      - ASSESSMENT: 1 task, 5 days base
      - PILOT: 1 task, 10 days base
      - PARALLEL_RUN: 1 task, max(14, num_endpoints * 2) days
      - CUTOVER: 1 task, max(5, num_endpoints) days
      - DECOMMISSION: 1 task, 5 days base

    Each task depends on the previous phase's task (linear chain).

    Returns:
        A populated MigrationPlan.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Exercise 14: Stakeholder Communication Matrix
# ---------------------------------------------------------------------------
# Map stakeholders to their communication preferences, frequency,
# and the types of updates they care about.
# ---------------------------------------------------------------------------

class StakeholderRole(Enum):
    EXECUTIVE_SPONSOR = "executive_sponsor"
    TECHNICAL_LEAD = "technical_lead"
    PROJECT_MANAGER = "project_manager"
    END_USER = "end_user"
    PROCUREMENT = "procurement"
    SECURITY_TEAM = "security_team"


class UpdateType(Enum):
    STATUS_REPORT = "status_report"
    TECHNICAL_DETAIL = "technical_detail"
    RISK_ALERT = "risk_alert"
    MILESTONE = "milestone"
    BUDGET = "budget"
    SECURITY = "security"


@dataclass
class Stakeholder:
    """A stakeholder in a customer engagement."""
    name: str
    role: StakeholderRole
    email: str
    update_types: list[UpdateType] = field(default_factory=list)
    frequency_days: int = 7       # How often they want updates


@dataclass
class CommunicationMatrix:
    """Maps stakeholders to their communication needs."""
    stakeholders: list[Stakeholder] = field(default_factory=list)

    def add_stakeholder(self, stakeholder: Stakeholder) -> None:
        """Add a stakeholder. Raise ValueError if email already exists."""
        # TODO: Implement
        pass

    def get_recipients_for_update(self, update_type: UpdateType) -> list[Stakeholder]:
        """Return all stakeholders who should receive a given update type."""
        # TODO: Implement
        pass

    def get_due_updates(self, days_since_last_update: int) -> list[Stakeholder]:
        """Return stakeholders who are due for an update.

        A stakeholder is due if days_since_last_update >= their frequency_days.
        """
        # TODO: Implement
        pass

    def generate_distribution_plan(self, update_type: UpdateType) -> list[dict[str, Any]]:
        """Generate a distribution plan for a given update type.

        Returns:
            List of dicts with keys: "name", "email", "role", "update_type".
        """
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 15: Full Scenario Simulation Runner
# ---------------------------------------------------------------------------
# Tie everything together: run a complete customer engagement scenario
# from initial contact through POC scoping, workshop delivery, incident
# handling, and health monitoring.
#
# Swift analogy: Like an integration test that exercises your full
# app stack -- AppDelegate through to network layer and persistence.
# ---------------------------------------------------------------------------

@dataclass
class ScenarioEvent:
    """A single event in a scenario simulation."""
    timestamp: str          # ISO format
    event_type: str         # "contact", "discovery", "poc", "workshop", "incident", "health_check"
    description: str
    data: dict[str, Any] = field(default_factory=dict)
    outcome: str = ""


@dataclass
class SimulationResult:
    """Result of running a full scenario simulation."""
    scenario_name: str
    customer: CustomerProfile
    events: list[ScenarioEvent] = field(default_factory=list)
    final_health_status: str = ""
    total_events: int = 0
    success: bool = False

    def add_event(self, event: ScenarioEvent) -> None:
        """Add an event and increment total_events."""
        # TODO: Implement
        pass

    def get_events_by_type(self, event_type: str) -> list[ScenarioEvent]:
        """Return all events of a given type."""
        # TODO: Implement
        pass

    def to_timeline(self) -> list[str]:
        """Return list of formatted timeline entries.

        Format: "[{timestamp}] {event_type}: {description} -> {outcome}"
        """
        # TODO: Implement
        pass


def run_scenario_simulation(scenario_name: str) -> SimulationResult:
    """Run a complete customer engagement scenario simulation.

    Steps:
      1. Create a CustomerProfile (use a realistic sample enterprise customer)
      2. Build and "complete" a discovery questionnaire
      3. Run triage on the customer request
      4. Generate a POC scope document
      5. Build a workshop agenda
      6. Simulate an incident (create report, classify severity, generate comms)
      7. Calculate customer health score
      8. Set final_health_status and success based on health score

    Each step should create a ScenarioEvent and add it to the result.
    success = True if final health_status is "healthy".

    Returns:
        SimulationResult with all events populated.
    """
    # TODO: Implement
    pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_customer_profile():
    """Test Exercise 1: Customer Profile Model."""
    profile = CustomerProfile(
        company_name="Acme Corp",
        industry="fintech",
        size=CompanySize.ENTERPRISE,
        employee_count=8000,
        ai_maturity=AIMaturity.SCALING,
        tech_stack=["Python", "AWS", "PostgreSQL", "Kubernetes"],
        requirements=["Reduce fraud detection latency", "Automate KYC", "Improve chatbot"],
        annual_revenue_mm=1200.0,
        existing_ai_tools=["OpenAI", "Hugging Face", "MLflow"],
        pain_points=["High false positive rate", "Slow model deployment"],
    )
    assert profile.is_enterprise() is True
    assert 0.0 <= profile.tech_stack_overlap(["Python", "AWS", "GCP", "Kubernetes"]) <= 1.0
    assert profile.tech_stack_overlap(["Python", "AWS", "GCP", "Kubernetes"]) == 0.75
    assert profile.readiness_score() > 0
    assert profile.readiness_score() <= 100
    summary = profile.to_summary()
    assert "Acme Corp" in summary
    assert "fintech" in summary
    print("  Exercise 1 (Customer Profile): PASSED")


def test_discovery_questionnaire():
    """Test Exercise 2: Discovery Questionnaire."""
    questions = build_discovery_questionnaire()
    assert len(questions) >= 8
    categories = {q.category for q in questions}
    assert len(categories) >= 4
    assert any(q.depends_on is not None for q in questions)
    assert any(q.expected_type == "choice" and q.choices for q in questions)

    response = QuestionnaireResponse()
    assert response.is_complete(questions) is False
    assert response.completion_percentage(questions) == 0.0

    for q in questions:
        if q.required:
            response.answers[q.id] = "sample answer"
    assert response.is_complete(questions) is True
    assert response.completion_percentage(questions) == 100.0
    print("  Exercise 2 (Discovery Questionnaire): PASSED")


def test_poc_scope():
    """Test Exercise 3: POC Scope Generator."""
    profile = CustomerProfile(
        company_name="TechStartup Inc",
        industry="e-commerce",
        size=CompanySize.STARTUP,
        employee_count=30,
        ai_maturity=AIMaturity.EXPERIMENTING,
        tech_stack=["Python", "React"],
        requirements=["Product recommendation engine"],
    )
    questions = build_discovery_questionnaire()
    responses = QuestionnaireResponse(
        answers={questions[0].id: "We need product recommendations"}
    )
    scope = generate_poc_scope(profile, responses, questions)
    assert scope.customer_name == "TechStartup Inc"
    assert scope.timeline_weeks == 4
    assert len(scope.success_criteria) >= 2
    assert len(scope.deliverables) >= 2
    assert "Production deployment" in scope.out_of_scope
    md = scope.to_markdown()
    assert "Objective" in md
    assert "Success Criteria" in md
    print("  Exercise 3 (POC Scope): PASSED")


def test_success_criteria():
    """Test Exercise 4: Success Criteria Framework."""
    framework = SuccessFramework()
    framework.add_criterion(SuccessCriterion(
        name="Latency", metric="p99_latency_ms", target_value=200.0,
        unit="ms", measurement_method="API monitoring", priority=CriteriaPriority.MUST_HAVE,
        lower_is_better=True,
    ))
    framework.add_criterion(SuccessCriterion(
        name="Accuracy", metric="f1_score", target_value=0.9,
        unit="score", measurement_method="Test set evaluation", priority=CriteriaPriority.MUST_HAVE,
    ))
    framework.add_criterion(SuccessCriterion(
        name="User Satisfaction", metric="csat", target_value=4.0,
        unit="rating", measurement_method="Survey", priority=CriteriaPriority.NICE_TO_HAVE,
    ))
    actuals = {"Latency": 150.0, "Accuracy": 0.92, "User Satisfaction": 3.5}
    results = framework.evaluate(actuals)
    assert results["Latency"] is True
    assert results["Accuracy"] is True
    assert results["User Satisfaction"] is False
    assert framework.must_haves_met(actuals) is True
    assert 0.0 <= framework.pass_rate(actuals) <= 1.0
    print("  Exercise 4 (Success Criteria): PASSED")


def test_triage_classifier():
    """Test Exercise 5: Customer Triage."""
    profile = CustomerProfile(
        company_name="BigBank", industry="fintech",
        size=CompanySize.ENTERPRISE, employee_count=10000,
        ai_maturity=AIMaturity.SCALING,
    )
    result = triage_customer_request(
        "Our production API is down and causing revenue loss",
        profile, is_production_issue=True, revenue_impact=True,
    )
    assert result.priority == TriagePriority.CRITICAL
    assert result.recommended_team == "incident_response"

    result2 = triage_customer_request(
        "Quick question about pricing",
        CustomerProfile(
            company_name="SmallCo", industry="retail",
            size=CompanySize.STARTUP, employee_count=10,
            ai_maturity=AIMaturity.EXPLORING,
        ),
    )
    assert result2.priority == TriagePriority.LOW
    assert result2.complexity == TriageComplexity.SIMPLE
    print("  Exercise 5 (Triage Classifier): PASSED")


def test_workshop_agenda():
    """Test Exercise 6: Workshop Agenda Builder."""
    profile = CustomerProfile(
        company_name="MedTech", industry="healthcare",
        size=CompanySize.MID_MARKET, employee_count=2000,
        ai_maturity=AIMaturity.EXPERIMENTING,
    )
    agenda = build_workshop_agenda(profile, ["RAG Pipeline", "Prompt Engineering"], duration_hours=4)
    assert agenda.customer_name == "MedTech"
    assert agenda.current_duration() <= agenda.total_duration_minutes
    schedule = agenda.to_schedule("09:00")
    assert len(schedule) > 0
    assert schedule[0]["time"] == "09:00"
    print("  Exercise 6 (Workshop Agenda): PASSED")


def test_security_responder():
    """Test Exercise 7: Security Questionnaire Responder."""
    responder = SecurityQuestionnaireResponder()
    responder.add_answer(SecurityAnswer(
        question_pattern="How is data encrypted at rest?",
        answer="All data is encrypted at rest using AES-256.",
        category="encryption",
        keywords=["encrypt", "data", "rest", "storage"],
    ))
    responder.add_answer(SecurityAnswer(
        question_pattern="How do you handle access control?",
        answer="We use RBAC with SSO integration.",
        category="access_control",
        keywords=["access", "control", "rbac", "sso", "authentication"],
    ))
    result = responder.find_best_answer("Is customer data encrypted at rest?")
    assert result is not None
    assert result.category == "encryption"

    responses = responder.respond_to_questionnaire([
        "How is data encrypted in storage?",
        "What is your favorite color?",
    ])
    assert len(responses) == 2
    assert responses[0]["answer"] != "NEEDS MANUAL REVIEW"
    assert responses[1]["answer"] == "NEEDS MANUAL REVIEW"
    print("  Exercise 7 (Security Responder): PASSED")


def test_compliance_checklist():
    """Test Exercise 8: Compliance Checklist."""
    checklist = build_compliance_checklist(["SOC2", "HIPAA"])
    soc2_items = checklist.get_by_framework("SOC2")
    hipaa_items = checklist.get_by_framework("HIPAA")
    assert len(soc2_items) >= 3
    assert len(hipaa_items) >= 3
    assert checklist.overall_completion() == 0.0
    assert len(checklist.gaps()) == len(checklist.items)

    for item in soc2_items:
        item.status = ComplianceStatus.VERIFIED
    completion = checklist.completion_by_framework()
    assert completion["SOC2"] == 100.0
    assert completion["HIPAA"] == 0.0
    print("  Exercise 8 (Compliance Checklist): PASSED")


def test_incident_classifier():
    """Test Exercise 9: Incident Severity Classifier."""
    report = IncidentReport(
        title="API Gateway Down",
        description="All API requests returning 503",
        affected_customers=950, total_customers=1000,
        service_degradation_percent=95.0,
        revenue_impact_per_hour=50000,
    )
    assert classify_incident_severity(report) == IncidentSeverity.SEV1

    minor = IncidentReport(
        title="Slow response on dashboard",
        description="Dashboard loads in 5s instead of 1s",
        affected_customers=10, total_customers=1000,
        service_degradation_percent=5.0,
    )
    assert classify_incident_severity(minor) == IncidentSeverity.SEV4
    print("  Exercise 9 (Incident Classifier): PASSED")


def test_incident_communication():
    """Test Exercise 10: Incident Communication."""
    report = IncidentReport(
        title="Database Failover",
        description="Primary DB failed over to replica",
        affected_customers=500, total_customers=1000,
        service_degradation_percent=60.0,
        revenue_impact_per_hour=25000,
    )
    internal = generate_incident_communication(
        report, IncidentSeverity.SEV2, CommunicationAudience.INTERNAL,
        status="mitigating", eta_minutes=30,
    )
    assert "SEV2" in internal or "sev2" in internal
    assert "mitigating" in internal

    customer = generate_incident_communication(
        report, IncidentSeverity.SEV2, CommunicationAudience.CUSTOMER,
        status="mitigating", eta_minutes=30,
    )
    assert "revenue" not in customer.lower()
    assert "30" in customer

    executive = generate_incident_communication(
        report, IncidentSeverity.SEV2, CommunicationAudience.EXECUTIVE,
    )
    assert "SEV2" in executive or "sev2" in executive.lower()
    print("  Exercise 10 (Incident Communication): PASSED")


def test_escalation():
    """Test Exercise 11: Escalation Decision Tree."""
    action = evaluate_escalation(IncidentSeverity.SEV1, elapsed_minutes=5)
    assert action.should_escalate is True
    assert action.escalation_level == 1
    assert "on_call_manager" in action.notify

    action2 = evaluate_escalation(IncidentSeverity.SEV1, elapsed_minutes=45)
    assert action2.escalation_level == 3
    assert "vp_engineering" in action2.notify or "cto" in action2.notify

    action3 = evaluate_escalation(IncidentSeverity.SEV4, elapsed_minutes=999)
    assert action3.escalation_level == 0
    assert action3.should_escalate is False
    print("  Exercise 11 (Escalation): PASSED")


def test_health_score():
    """Test Exercise 12: Customer Health Score."""
    metrics = CustomerHealthMetrics(
        api_calls_last_30d=10000,
        api_calls_previous_30d=8000,
        error_rate_percent=2.0,
        support_tickets_open=1,
        support_tickets_resolved_30d=5,
        nps_score=60,
        days_since_last_login=2,
        contract_months_remaining=18,
        feature_adoption_percent=75.0,
    )
    result = calculate_health_score(metrics)
    assert "overall_score" in result
    assert "health_status" in result
    assert result["health_status"] == "healthy"
    assert 0 <= result["overall_score"] <= 100

    bad_metrics = CustomerHealthMetrics(
        api_calls_last_30d=100,
        api_calls_previous_30d=10000,
        error_rate_percent=40.0,
        support_tickets_open=15,
        support_tickets_resolved_30d=0,
        nps_score=-50,
        days_since_last_login=60,
        contract_months_remaining=2,
        feature_adoption_percent=10.0,
    )
    bad_result = calculate_health_score(bad_metrics)
    assert bad_result["health_status"] == "critical"
    print("  Exercise 12 (Health Score): PASSED")


def test_migration_plan():
    """Test Exercise 13: Migration Plan Generator."""
    plan = generate_migration_plan("Acme Corp", "OpenAI", "Anthropic", num_endpoints=5)
    assert plan.customer_name == "Acme Corp"
    assert len(plan.tasks) == 5
    phases = plan.tasks_by_phase()
    assert "assessment" in phases
    assert "cutover" in phases
    assert plan.total_duration_days() > 0
    path = plan.critical_path()
    assert len(path) == 5
    print("  Exercise 13 (Migration Plan): PASSED")


def test_communication_matrix():
    """Test Exercise 14: Stakeholder Communication Matrix."""
    matrix = CommunicationMatrix()
    matrix.add_stakeholder(Stakeholder(
        name="Jane CTO", role=StakeholderRole.EXECUTIVE_SPONSOR,
        email="jane@acme.com",
        update_types=[UpdateType.STATUS_REPORT, UpdateType.RISK_ALERT, UpdateType.MILESTONE],
        frequency_days=7,
    ))
    matrix.add_stakeholder(Stakeholder(
        name="Bob Engineer", role=StakeholderRole.TECHNICAL_LEAD,
        email="bob@acme.com",
        update_types=[UpdateType.TECHNICAL_DETAIL, UpdateType.STATUS_REPORT],
        frequency_days=3,
    ))
    risk_recipients = matrix.get_recipients_for_update(UpdateType.RISK_ALERT)
    assert len(risk_recipients) == 1
    assert risk_recipients[0].name == "Jane CTO"

    due = matrix.get_due_updates(days_since_last_update=5)
    assert any(s.name == "Bob Engineer" for s in due)

    plan = matrix.generate_distribution_plan(UpdateType.STATUS_REPORT)
    assert len(plan) == 2
    print("  Exercise 14 (Communication Matrix): PASSED")


def test_scenario_simulation():
    """Test Exercise 15: Full Scenario Simulation."""
    result = run_scenario_simulation("Enterprise Onboarding")
    assert result.scenario_name == "Enterprise Onboarding"
    assert result.total_events >= 7
    assert result.final_health_status in ("healthy", "at_risk", "critical")
    assert isinstance(result.success, bool)
    timeline = result.to_timeline()
    assert len(timeline) == result.total_events
    print("  Exercise 15 (Scenario Simulation): PASSED")


if __name__ == "__main__":
    print("Testing Customer Scenario Simulation exercises...\n")
    test_customer_profile()
    test_discovery_questionnaire()
    test_poc_scope()
    test_success_criteria()
    test_triage_classifier()
    test_workshop_agenda()
    test_security_responder()
    test_compliance_checklist()
    test_incident_classifier()
    test_incident_communication()
    test_escalation()
    test_health_score()
    test_migration_plan()
    test_communication_matrix()
    test_scenario_simulation()
    print("\nAll 15 exercises passed!")
