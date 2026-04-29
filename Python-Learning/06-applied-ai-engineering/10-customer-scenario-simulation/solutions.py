"""
Module 10 Solutions: Customer Scenario Simulation
==================================================

Complete implementations for all 15 exercises. Each solution includes
detailed comments explaining the design rationale and how it maps to
real-world Applied AI / Solutions Engineering workflows.

For Swift developers: these are the "service layer" objects you would
build behind a SwiftUI interface -- the business logic that powers
customer-facing tooling at companies like Anthropic, OpenAI, or Cohere.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any


# ============================================================================
# Solution 1: Customer Profile Model
# ============================================================================
# Design notes:
# - Dataclass gives us __init__, __repr__, __eq__ for free (like Swift structs)
# - Computed properties mirror what you would put in a Swift extension
# - The readiness_score() rubric is a simplified version of real "lead scoring"
#   used by sales engineering teams at every AI company
# ============================================================================

class CompanySize(Enum):
    STARTUP = "startup"
    SMB = "smb"
    MID_MARKET = "mid_market"
    ENTERPRISE = "enterprise"


class AIMaturity(Enum):
    EXPLORING = "exploring"
    EXPERIMENTING = "experimenting"
    SCALING = "scaling"
    OPTIMIZING = "optimizing"


@dataclass
class CustomerProfile:
    """Complete customer profile for pre-call preparation."""
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

        Multiple signals: explicit size tier, headcount threshold, or
        revenue threshold. In practice, you want to cast a wide net
        because enterprise deals have 10-50x the contract value.
        """
        return (
            self.size == CompanySize.ENTERPRISE
            or self.employee_count >= 5000
            or (self.annual_revenue_mm is not None and self.annual_revenue_mm >= 500)
        )

    def tech_stack_overlap(self, supported_stack: list[str]) -> float:
        """Return fraction of customer's stack that we support.

        Case-insensitive comparison. This tells you how much integration
        work is needed -- high overlap = faster time-to-value.
        """
        if not self.tech_stack:
            return 0.0
        # Normalize to lowercase for case-insensitive matching
        supported_lower = {s.lower() for s in supported_stack}
        matches = sum(1 for t in self.tech_stack if t.lower() in supported_lower)
        return matches / len(self.tech_stack)

    def readiness_score(self) -> float:
        """Score 0-100 indicating how ready the customer is for an AI engagement.

        This is a simplified "lead score" -- in production, you would weight
        these differently per vertical and feed them into a proper ML model.
        """
        # Base score from AI maturity
        maturity_scores = {
            AIMaturity.EXPLORING: 10,
            AIMaturity.EXPERIMENTING: 25,
            AIMaturity.SCALING: 40,
            AIMaturity.OPTIMIZING: 50,
        }
        score = maturity_scores[self.ai_maturity]

        # Bonus for clearly articulated requirements
        if len(self.requirements) >= 3:
            score += 15

        # Bonus for existing AI tool usage (shows budget and commitment)
        if len(self.existing_ai_tools) >= 2:
            score += 15

        # Bonus for identified pain points (shows self-awareness)
        if len(self.pain_points) >= 1:
            score += 10

        # Bonus for a real tech stack (shows technical maturity)
        if len(self.tech_stack) >= 3:
            score += 10

        return min(100.0, float(score))

    def to_summary(self) -> str:
        """One-line human-readable summary for CRM dashboards and Slack alerts."""
        return (
            f"{self.company_name} | {self.industry} | {self.size.value} "
            f"| AI:{self.ai_maturity.value} | Readiness:{self.readiness_score():.0f}"
        )


# ============================================================================
# Solution 2: Technical Requirements Discovery Questionnaire
# ============================================================================
# Design notes:
# - The depends_on field creates a directed graph of question dependencies
# - In a real tool, you would render this as a dynamic form (like Typeform)
# - The questionnaire response tracks completeness for handoff readiness
# ============================================================================

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
    depends_on: str | None = None
    expected_type: str = "text"
    choices: list[str] | None = None


@dataclass
class QuestionnaireResponse:
    """A completed (or partial) questionnaire."""
    answers: dict[str, Any] = field(default_factory=dict)

    def is_complete(self, questions: list[Question]) -> bool:
        """All required questions must be answered for a complete questionnaire."""
        return all(
            q.id in self.answers
            for q in questions
            if q.required
        )

    def completion_percentage(self, questions: list[Question]) -> float:
        """Track progress -- useful for showing a progress bar in the UI."""
        required = [q for q in questions if q.required]
        if not required:
            return 100.0
        answered = sum(1 for q in required if q.id in self.answers)
        return (answered / len(required)) * 100.0

    def unanswered_required(self, questions: list[Question]) -> list[str]:
        """Identifies gaps to highlight before a call ends."""
        return [
            q.id for q in questions
            if q.required and q.id not in self.answers
        ]


def build_discovery_questionnaire() -> list[Question]:
    """Build the standard discovery questionnaire.

    These questions map to real discovery call frameworks used at
    AI companies. The goal is to qualify the opportunity and understand
    technical requirements in a single 45-minute call.
    """
    return [
        Question(
            id="uc_primary",
            category=QuestionCategory.USE_CASE,
            text="What is the primary use case you want to solve with AI?",
            required=True,
            expected_type="text",
        ),
        Question(
            id="uc_current",
            category=QuestionCategory.USE_CASE,
            text="How are you currently solving this problem (manual process, existing tool, etc.)?",
            required=True,
            expected_type="text",
        ),
        Question(
            id="data_volume",
            category=QuestionCategory.DATA,
            text="What is the approximate volume of data you process daily?",
            required=True,
            expected_type="choice",
            choices=["< 1 GB", "1-100 GB", "100 GB - 1 TB", "> 1 TB"],
        ),
        Question(
            id="data_pii",
            category=QuestionCategory.DATA,
            text="Does your data contain PII or sensitive information?",
            required=True,
            expected_type="choice",
            choices=["Yes", "No", "Unsure"],
        ),
        Question(
            id="data_pii_types",
            category=QuestionCategory.DATA,
            text="What types of PII are present (names, SSN, health records, etc.)?",
            required=False,
            depends_on="data_pii",  # Only relevant if data_pii == "Yes"
            expected_type="text",
        ),
        Question(
            id="infra_cloud",
            category=QuestionCategory.INFRASTRUCTURE,
            text="What cloud provider(s) do you use?",
            required=True,
            expected_type="multi_choice",
            choices=["AWS", "GCP", "Azure", "On-premise", "Other"],
        ),
        Question(
            id="sec_compliance",
            category=QuestionCategory.SECURITY,
            text="What compliance frameworks must the solution meet?",
            required=True,
            expected_type="multi_choice",
            choices=["SOC2", "HIPAA", "GDPR", "FedRAMP", "None / Unsure"],
        ),
        Question(
            id="timeline_go_live",
            category=QuestionCategory.TIMELINE,
            text="When do you need the solution in production?",
            required=True,
            expected_type="choice",
            choices=["< 1 month", "1-3 months", "3-6 months", "6+ months"],
        ),
        Question(
            id="budget_range",
            category=QuestionCategory.BUDGET,
            text="What is your approximate annual budget for this initiative?",
            required=False,
            expected_type="choice",
            choices=["< $50K", "$50K-$200K", "$200K-$1M", "> $1M"],
        ),
        Question(
            id="infra_gpu",
            category=QuestionCategory.INFRASTRUCTURE,
            text="Do you have GPU infrastructure available for model training/inference?",
            required=True,
            expected_type="choice",
            choices=["Yes, on-premise", "Yes, cloud", "No", "Unsure"],
        ),
    ]


# ============================================================================
# Solution 3: POC Scope Document Generator
# ============================================================================
# Design notes:
# - The POC scope doc is one of the most important SE deliverables. It sets
#   expectations, defines success, and prevents scope creep.
# - The Markdown output is what actually gets shared in Google Docs / Notion.
# ============================================================================

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
        """Render as Markdown -- the standard format for customer-facing docs."""
        sections = [
            f"# {self.title}",
            f"\n**Customer:** {self.customer_name}",
            f"\n## Objective\n\n{self.objective}",
        ]

        # Helper to render bulleted lists
        def bullet_list(header: str, items: list[str]) -> str:
            bullets = "\n".join(f"- {item}" for item in items)
            return f"\n## {header}\n\n{bullets}"

        sections.append(bullet_list("Success Criteria", self.success_criteria))
        sections.append(bullet_list("Deliverables", self.deliverables))
        sections.append(f"\n## Timeline\n\n{self.timeline_weeks} weeks")
        sections.append(bullet_list("Required Resources", self.required_resources))
        sections.append(bullet_list("Risks", self.risks))
        sections.append(bullet_list("Out of Scope", self.out_of_scope))

        return "\n".join(sections)


def generate_poc_scope(
    profile: CustomerProfile,
    responses: QuestionnaireResponse,
    questions: list[Question],
) -> POCScope:
    """Generate a POC scope from profile + discovery answers.

    This replicates the manual process an SE does after every discovery
    call. Automating it saves 1-2 hours per engagement.
    """
    # Derive objective from use-case answers
    use_case_questions = [q for q in questions if q.category == QuestionCategory.USE_CASE]
    objective = "Validate AI solution feasibility for the customer's primary use case."
    for q in use_case_questions:
        if q.id in responses.answers:
            objective = f"Validate AI-powered solution for: {responses.answers[q.id]}"
            break

    # Timeline scales with company size (larger = more stakeholders, more process)
    timeline_map = {
        CompanySize.STARTUP: 4,
        CompanySize.SMB: 4,
        CompanySize.MID_MARKET: 8,
        CompanySize.ENTERPRISE: 12,
    }
    timeline_weeks = timeline_map[profile.size]

    # Build risks list
    risks = ["Timeline dependencies on customer data access"]
    # Check if any DATA category questions were answered
    data_questions = [q for q in questions if q.category == QuestionCategory.DATA]
    data_answered = any(q.id in responses.answers for q in data_questions)
    if not data_answered:
        risks.append("Data quality unknown")

    return POCScope(
        title=f"AI POC: {profile.company_name} - {profile.industry}",
        customer_name=profile.company_name,
        objective=objective,
        success_criteria=[
            "Demonstrate measurable improvement over current solution",
            "Achieve target accuracy/performance metrics on customer data",
            "Complete technical validation within timeline",
        ],
        deliverables=[
            "Working prototype with customer data integration",
            "Performance benchmark report",
            "Architecture recommendation document",
        ],
        timeline_weeks=timeline_weeks,
        required_resources=[
            "Solutions Engineer (50% allocation)",
            "Customer technical point of contact",
            "Access to sample/test data",
        ],
        risks=risks,
        out_of_scope=[
            "Production deployment",
            "Custom model training",
            "Long-term support and maintenance",
        ],
    )


# ============================================================================
# Solution 4: Success Criteria Framework
# ============================================================================
# Design notes:
# - MUST_HAVE vs SHOULD_HAVE vs NICE_TO_HAVE maps directly to MoSCoW
#   prioritization used in agile project management.
# - must_haves_met() is the gate check: if any must-have fails, the POC fails
#   regardless of how well everything else went.
# ============================================================================

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
        """Check if the criterion is satisfied.

        For metrics where lower is better (latency, error rate), actual
        must be <= target. For all others (accuracy, throughput), actual
        must be >= target. This mirrors real SLO evaluation logic.
        """
        if self.lower_is_better:
            return actual_value <= self.target_value
        return actual_value >= self.target_value


@dataclass
class SuccessFramework:
    """Collection of success criteria for an engagement."""
    criteria: list[SuccessCriterion] = field(default_factory=list)

    def add_criterion(self, criterion: SuccessCriterion) -> None:
        """Add a criterion, enforcing unique names."""
        if any(c.name == criterion.name for c in self.criteria):
            raise ValueError(f"Criterion '{criterion.name}' already exists")
        self.criteria.append(criterion)

    def evaluate(self, actuals: dict[str, float]) -> dict[str, bool]:
        """Evaluate all criteria. Missing actuals = not met."""
        return {
            c.name: c.is_met(actuals[c.name]) if c.name in actuals else False
            for c in self.criteria
        }

    def pass_rate(self, actuals: dict[str, float]) -> float:
        """Fraction of criteria met -- the "batting average" of the POC."""
        results = self.evaluate(actuals)
        if not results:
            return 0.0
        return sum(1 for v in results.values() if v) / len(results)

    def must_haves_met(self, actuals: dict[str, float]) -> bool:
        """The go/no-go gate check. ALL must-haves must pass."""
        results = self.evaluate(actuals)
        return all(
            results.get(c.name, False)
            for c in self.criteria
            if c.priority == CriteriaPriority.MUST_HAVE
        )


# ============================================================================
# Solution 5: Customer Triage Classifier
# ============================================================================
# Design notes:
# - This is the "router" that every support/SE org needs. At scale, this
#   becomes an ML model trained on historical ticket data.
# - The priority rules encode institutional knowledge about what matters most.
# - estimated_effort_days drives capacity planning.
# ============================================================================

class TriagePriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TriageComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    STRATEGIC = "strategic"


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

    The nested if-else chain mirrors how experienced SEs mentally triage
    incoming requests. Each rule is a heuristic refined through experience.
    """
    # --- Determine priority ---
    request_lower = request_text.lower()
    urgent_keywords = {"urgent", "blocker", "deadline", "critical"}

    if is_production_issue and revenue_impact:
        priority = TriagePriority.CRITICAL
        reason = "Production issue with revenue impact"
    elif is_production_issue and profile.is_enterprise():
        priority = TriagePriority.CRITICAL
        reason = "Production issue at enterprise customer"
    elif is_production_issue or revenue_impact:
        priority = TriagePriority.HIGH
        reason = "Production issue or revenue impact"
    elif profile.is_enterprise() and any(kw in request_lower for kw in urgent_keywords):
        priority = TriagePriority.HIGH
        reason = "Enterprise customer with urgent keywords"
    elif profile.size in (CompanySize.MID_MARKET, CompanySize.ENTERPRISE):
        priority = TriagePriority.MEDIUM
        reason = "Mid-market or enterprise customer"
    else:
        priority = TriagePriority.LOW
        reason = "Standard request from smaller customer"

    # --- Determine complexity ---
    text_len = len(request_text)
    if text_len > 500 and profile.is_enterprise():
        complexity = TriageComplexity.STRATEGIC
    elif text_len > 300 or "integration" in request_lower:
        complexity = TriageComplexity.COMPLEX
    elif text_len > 100:
        complexity = TriageComplexity.MODERATE
    else:
        complexity = TriageComplexity.SIMPLE

    # --- Determine team and effort ---
    effort_map = {
        TriageComplexity.SIMPLE: 1,
        TriageComplexity.MODERATE: 3,
        TriageComplexity.COMPLEX: 10,
        TriageComplexity.STRATEGIC: 30,
    }

    if priority == TriagePriority.CRITICAL:
        team = "incident_response"
    elif complexity in (TriageComplexity.COMPLEX, TriageComplexity.STRATEGIC):
        team = "solutions_engineering"
    else:
        team = "technical_support"

    return TriageResult(
        priority=priority,
        complexity=complexity,
        recommended_team=team,
        estimated_effort_days=effort_map[complexity],
        reasoning=reason,
    )


# ============================================================================
# Solution 6: Workshop Agenda Builder
# ============================================================================
# Design notes:
# - Workshops are the SE's primary tool for building technical trust.
# - The time-boxing logic is important: going over time is unprofessional,
#   and going under wastes the customer's calendar commitment.
# - to_schedule() produces the format that goes into the calendar invite.
# ============================================================================

@dataclass
class AgendaItem:
    """A single item on a workshop agenda."""
    title: str
    duration_minutes: int
    presenter: str
    item_type: str
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
        """Enforce time budget -- no agenda should silently overrun."""
        if self.current_duration() + item.duration_minutes > self.total_duration_minutes:
            raise ValueError(
                f"Adding '{item.title}' ({item.duration_minutes} min) would exceed "
                f"total duration ({self.total_duration_minutes} min). "
                f"Remaining: {self.remaining_minutes()} min."
            )
        self.items.append(item)

    def current_duration(self) -> int:
        return sum(item.duration_minutes for item in self.items)

    def remaining_minutes(self) -> int:
        return self.total_duration_minutes - self.current_duration()

    def to_schedule(self, start_time: str = "09:00") -> list[dict[str, str]]:
        """Generate a time-boxed schedule with computed start times.

        Parses HH:MM and accumulates durations to produce each slot's
        start time. This is what goes into the calendar invite body.
        """
        schedule = []
        hours, minutes = map(int, start_time.split(":"))
        current_minutes = hours * 60 + minutes

        for item in self.items:
            h, m = divmod(current_minutes, 60)
            schedule.append({
                "time": f"{h:02d}:{m:02d}",
                "title": item.title,
                "duration": f"{item.duration_minutes} min",
                "type": item.item_type,
            })
            current_minutes += item.duration_minutes

        return schedule


def build_workshop_agenda(
    profile: CustomerProfile,
    focus_areas: list[str],
    duration_hours: int = 4,
) -> WorkshopAgenda:
    """Build a customized workshop agenda.

    The structure follows a standard SE workshop template:
    open -> context -> deep dives -> break -> more deep dives -> close.
    """
    total_minutes = duration_hours * 60
    agenda = WorkshopAgenda(
        title=f"AI Workshop: {', '.join(focus_areas)}",
        customer_name=profile.company_name,
        date=datetime.now().strftime("%Y-%m-%d"),
        total_duration_minutes=total_minutes,
    )

    # Fixed bookends: welcome + Q&A + break = 45 min
    welcome = AgendaItem("Welcome & Introductions", 15, "SE Lead", "presentation")
    closing = AgendaItem("Q&A and Next Steps", 15, "SE Lead", "discussion")
    mid_break = AgendaItem("Break", 15, "", "break")

    # Hands-on sessions for each focus area (30 min each)
    hands_on_items = [
        AgendaItem(
            f"Hands-on: {area}", 30, "SE Lead", "hands_on",
            description=f"Interactive session covering {area}",
        )
        for area in focus_areas
    ]

    # Calculate remaining time for the overview demo
    fixed_time = 15 + 15 + 15  # welcome + break + closing
    hands_on_time = 30 * len(focus_areas)
    overview_time = total_minutes - fixed_time - hands_on_time

    # Build the agenda in order
    agenda.add_item(welcome)

    # Add overview if there is time
    if overview_time > 0:
        agenda.add_item(AgendaItem(
            "Platform Overview", overview_time, "SE Lead", "demo",
            description="High-level platform capabilities and architecture",
        ))

    # Insert hands-on sessions with break roughly in the middle
    mid_point = len(hands_on_items) // 2
    for i, item in enumerate(hands_on_items):
        if i == mid_point and mid_point > 0:
            agenda.add_item(mid_break)
        agenda.add_item(item)

    # If no hands-on items, still add the break
    if not hands_on_items:
        agenda.add_item(mid_break)

    agenda.add_item(closing)
    return agenda


# ============================================================================
# Solution 7: Enterprise Security Questionnaire Responder
# ============================================================================
# Design notes:
# - Enterprise sales cycles are gated on security review. A 200-question
#   questionnaire can take weeks if done manually.
# - The keyword-based matching is a simplified version of what you would
#   build with embeddings + vector search in production.
# - "NEEDS MANUAL REVIEW" is critical -- never auto-respond to a security
#   question you are not confident about.
# ============================================================================

@dataclass
class SecurityAnswer:
    """A pre-approved answer in the security knowledge base."""
    question_pattern: str
    answer: str
    category: str
    keywords: list[str] = field(default_factory=list)
    last_reviewed: str = ""


class SecurityQuestionnaireResponder:
    """Match incoming security questions to pre-approved answers."""

    def __init__(self) -> None:
        self.knowledge_base: list[SecurityAnswer] = []

    def add_answer(self, answer: SecurityAnswer) -> None:
        self.knowledge_base.append(answer)

    def _keyword_score(self, question: str, entry: SecurityAnswer) -> float:
        """Score based on keyword overlap.

        This is a bag-of-words approach. In production, you would use
        sentence embeddings (e.g., from Anthropic's embedding API) for
        semantic matching that handles synonyms and paraphrasing.
        """
        if not entry.keywords:
            return 0.0
        question_lower = question.lower()
        matches = sum(1 for kw in entry.keywords if kw.lower() in question_lower)
        return matches / len(entry.keywords)

    def find_best_answer(self, question: str, min_score: float = 0.3) -> SecurityAnswer | None:
        """Find the best matching answer above the confidence threshold.

        The min_score threshold prevents low-confidence auto-responses,
        which could create legal liability.
        """
        if not self.knowledge_base:
            return None

        best_entry = None
        best_score = 0.0

        for entry in self.knowledge_base:
            score = self._keyword_score(question, entry)
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_score >= min_score and best_entry is not None:
            return best_entry
        return None

    def respond_to_questionnaire(
        self, questions: list[str], min_score: float = 0.3
    ) -> list[dict[str, Any]]:
        """Process a full questionnaire.

        Returns structured responses suitable for pasting into the
        customer's questionnaire spreadsheet.
        """
        responses = []
        for question in questions:
            best = self.find_best_answer(question, min_score)
            if best is not None:
                score = self._keyword_score(question, best)
                responses.append({
                    "question": question,
                    "answer": best.answer,
                    "confidence": score,
                    "category": best.category,
                })
            else:
                responses.append({
                    "question": question,
                    "answer": "NEEDS MANUAL REVIEW",
                    "confidence": 0.0,
                    "category": "unknown",
                })
        return responses


# ============================================================================
# Solution 8: Compliance Checklist for Multiple Frameworks
# ============================================================================
# Design notes:
# - SOC2, HIPAA, and GDPR have overlapping requirements (encryption, access
#   control, audit logging) but different terminology and scopes.
# - In production, you would map controls across frameworks (a "crosswalk")
#   so that implementing one control satisfies multiple frameworks.
# - The completion_by_framework view is what you show to the CISO.
# ============================================================================

class ComplianceStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"


@dataclass
class ComplianceItem:
    """A single compliance control item."""
    control_id: str
    framework: str
    description: str
    status: ComplianceStatus = ComplianceStatus.NOT_STARTED
    evidence: str = ""
    owner: str = ""


@dataclass
class ComplianceChecklist:
    """Compliance checklist spanning multiple frameworks."""
    items: list[ComplianceItem] = field(default_factory=list)

    def add_item(self, item: ComplianceItem) -> None:
        """Enforce unique control IDs to prevent duplicate tracking."""
        if any(i.control_id == item.control_id for i in self.items):
            raise ValueError(f"Control ID '{item.control_id}' already exists")
        self.items.append(item)

    def get_by_framework(self, framework: str) -> list[ComplianceItem]:
        return [i for i in self.items if i.framework == framework]

    def completion_by_framework(self) -> dict[str, float]:
        """Per-framework completion -- the CISO's dashboard view."""
        frameworks: dict[str, list[ComplianceItem]] = defaultdict(list)
        for item in self.items:
            frameworks[item.framework].append(item)

        result = {}
        for fw, items in frameworks.items():
            completed = sum(
                1 for i in items
                if i.status in (ComplianceStatus.IMPLEMENTED, ComplianceStatus.VERIFIED)
            )
            result[fw] = (completed / len(items)) * 100.0 if items else 0.0
        return result

    def gaps(self) -> list[ComplianceItem]:
        """Items that need attention -- this drives the weekly standup."""
        return [
            i for i in self.items
            if i.status in (ComplianceStatus.NOT_STARTED, ComplianceStatus.IN_PROGRESS)
        ]

    def overall_completion(self) -> float:
        """Single number for executive reporting."""
        if not self.items:
            return 0.0
        completed = sum(
            1 for i in self.items
            if i.status in (ComplianceStatus.IMPLEMENTED, ComplianceStatus.VERIFIED)
        )
        return (completed / len(self.items)) * 100.0


def build_compliance_checklist(frameworks: list[str]) -> ComplianceChecklist:
    """Build a compliance checklist for the given frameworks.

    Each framework has a canonical set of controls. In production, these
    would come from a compliance database maintained by the security team.
    """
    # Control definitions per framework
    controls: dict[str, list[tuple[str, str]]] = {
        "SOC2": [
            ("SOC2-CC6.1", "Logical and physical access controls"),
            ("SOC2-CC6.2", "System component inventory and management"),
            ("SOC2-CC6.3", "Security event monitoring and alerting"),
            ("SOC2-CC7.1", "Change management procedures"),
            ("SOC2-CC8.1", "Incident response plan"),
        ],
        "HIPAA": [
            ("HIPAA-164.312a", "Access control and unique user identification"),
            ("HIPAA-164.312b", "Audit controls and activity logging"),
            ("HIPAA-164.312c", "Data integrity verification"),
            ("HIPAA-164.312d", "Authentication mechanisms"),
            ("HIPAA-164.312e", "Transmission security and encryption"),
        ],
        "GDPR": [
            ("GDPR-Art25", "Data protection by design and default"),
            ("GDPR-Art30", "Records of processing activities"),
            ("GDPR-Art32", "Security of processing (encryption, pseudonymization)"),
            ("GDPR-Art33", "Breach notification within 72 hours"),
            ("GDPR-Art35", "Data protection impact assessment"),
        ],
    }

    checklist = ComplianceChecklist()
    for framework in frameworks:
        if framework not in controls:
            raise ValueError(
                f"Unsupported framework: '{framework}'. "
                f"Supported: {list(controls.keys())}"
            )
        for control_id, description in controls[framework]:
            checklist.add_item(ComplianceItem(
                control_id=control_id,
                framework=framework,
                description=description,
            ))

    return checklist


# ============================================================================
# Solution 9: Incident Severity Classifier
# ============================================================================
# Design notes:
# - Security breaches and data loss are always SEV1 regardless of scope.
#   This is non-negotiable in every incident framework.
# - The affected_customers ratio is more meaningful than absolute numbers:
#   50 out of 100 customers is worse than 500 out of 1,000,000.
# - In production, this feeds into PagerDuty/OpsGenie routing rules.
# ============================================================================

class IncidentSeverity(Enum):
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"


@dataclass
class IncidentReport:
    """Raw incident report data."""
    title: str
    description: str
    affected_customers: int
    total_customers: int
    is_data_loss: bool = False
    is_security_breach: bool = False
    service_degradation_percent: float = 0.0
    revenue_impact_per_hour: float = 0.0


def classify_incident_severity(report: IncidentReport) -> IncidentSeverity:
    """Classify incident severity.

    Rules are evaluated in order of severity. The first match wins.
    This mirrors how real incident commanders make snap decisions.
    """
    # Calculate impact ratio (protect against division by zero)
    impact_ratio = (
        report.affected_customers / report.total_customers
        if report.total_customers > 0
        else 0.0
    )

    # --- SEV1 checks ---
    if report.is_security_breach or report.is_data_loss:
        return IncidentSeverity.SEV1
    if impact_ratio > 0.5:
        return IncidentSeverity.SEV1
    if report.service_degradation_percent >= 90:
        return IncidentSeverity.SEV1

    # --- SEV2 checks ---
    if impact_ratio > 0.25:
        return IncidentSeverity.SEV2
    if report.service_degradation_percent >= 50:
        return IncidentSeverity.SEV2
    if report.revenue_impact_per_hour >= 10000:
        return IncidentSeverity.SEV2

    # --- SEV3 checks ---
    if impact_ratio > 0.05:
        return IncidentSeverity.SEV3
    if report.service_degradation_percent >= 20:
        return IncidentSeverity.SEV3

    # --- Default ---
    return IncidentSeverity.SEV4


# ============================================================================
# Solution 10: Incident Communication Template Engine
# ============================================================================
# Design notes:
# - The THREE audiences have fundamentally different needs:
#   * Internal: full technical detail, metrics, everything
#   * Customer: reassurance, no internal details, empathy, ETA
#   * Executive: business impact in dollars, headcount, risk
# - NEVER leak internal details (revenue impact, security flags) to customers.
#   This is a career-ending mistake in incident management.
# ============================================================================

class CommunicationAudience(Enum):
    INTERNAL = "internal"
    CUSTOMER = "customer"
    EXECUTIVE = "executive"


def generate_incident_communication(
    report: IncidentReport,
    severity: IncidentSeverity,
    audience: CommunicationAudience,
    status: str = "investigating",
    eta_minutes: int | None = None,
) -> str:
    """Generate audience-appropriate incident communication.

    The format differences between audiences are critical:
    - Internal gets raw numbers for debugging
    - Customer gets reassurance without internal details
    - Executive gets business impact for decision-making
    """
    if audience == CommunicationAudience.INTERNAL:
        eta_str = f"{eta_minutes} minutes" if eta_minutes is not None else "TBD"
        data_loss_str = "Yes" if report.is_data_loss else "No"
        security_str = "Yes" if report.is_security_breach else "No"
        return (
            f"[{severity.value}] {report.title}\n"
            f"Status: {status}\n"
            f"Affected: {report.affected_customers}/{report.total_customers} customers\n"
            f"Degradation: {report.service_degradation_percent}%\n"
            f"Revenue impact: ${report.revenue_impact_per_hour}/hr\n"
            f"Data loss: {data_loss_str} | Security breach: {security_str}\n"
            f"ETA: {eta_str}"
        )

    elif audience == CommunicationAudience.CUSTOMER:
        # Customer comms: empathetic, no internal details, actionable
        eta_str = (
            f"{eta_minutes} minutes"
            if eta_minutes is not None
            else "We are working on a resolution"
        )
        return (
            f"Service Update: {report.title}\n"
            f"We are aware of an issue affecting some of our services.\n"
            f"Current status: {status}\n"
            f"Estimated resolution: {eta_str}\n"
            f"We apologize for any inconvenience."
        )

    else:  # EXECUTIVE
        affected_pct = (
            (report.affected_customers / report.total_customers * 100)
            if report.total_customers > 0
            else 0.0
        )
        eta_str = f"{eta_minutes} min" if eta_minutes is not None else "Determining"
        return (
            f"INCIDENT ALERT - {severity.value.upper()}\n"
            f"Issue: {report.title}\n"
            f"Business Impact: {affected_pct:.1f}% of customers affected\n"
            f"Revenue Risk: ${report.revenue_impact_per_hour}/hr\n"
            f"Status: {status}\n"
            f"ETA: {eta_str}"
        )


# ============================================================================
# Solution 11: Escalation Decision Tree
# ============================================================================
# Design notes:
# - Time-based escalation is the backbone of incident management. The longer
#   an incident runs, the higher it escalates.
# - The previous_escalation_level check prevents duplicate notifications.
#   Nobody wants to be paged twice for the same incident at the same level.
# - Adding "customer_success" for customer-facing issues ensures the CS team
#   can proactively reach out before customers start complaining on Twitter.
# ============================================================================

@dataclass
class EscalationAction:
    """An escalation decision."""
    should_escalate: bool
    escalation_level: int
    notify: list[str]
    reason: str


def evaluate_escalation(
    severity: IncidentSeverity,
    elapsed_minutes: int,
    is_customer_facing: bool = True,
    previous_escalation_level: int = 0,
) -> EscalationAction:
    """Determine if an incident should be escalated.

    The time thresholds come from industry-standard incident management
    frameworks (PagerDuty, Atlassian Incident Management, Google SRE book).
    """
    # Define escalation rules: (min_minutes, max_minutes, level, notify_list)
    rules: dict[IncidentSeverity, list[tuple[int, int, int, list[str]]]] = {
        IncidentSeverity.SEV1: [
            (0, 15, 1, ["on_call_manager", "incident_commander"]),
            (15, 30, 2, ["director_engineering", "director_support"]),
            (30, 999999, 3, ["vp_engineering", "cto"]),
        ],
        IncidentSeverity.SEV2: [
            (0, 30, 0, ["on_call_engineer"]),
            (30, 60, 1, ["on_call_manager"]),
            (60, 999999, 2, ["director_engineering"]),
        ],
        IncidentSeverity.SEV3: [
            (0, 60, 0, ["on_call_engineer"]),
            (60, 120, 1, ["on_call_manager"]),
            (120, 999999, 2, ["director_engineering"]),
        ],
        IncidentSeverity.SEV4: [
            (0, 999999, 0, ["on_call_engineer"]),
        ],
    }

    # Find the matching rule based on elapsed time
    severity_rules = rules[severity]
    level = 0
    notify: list[str] = ["on_call_engineer"]
    reason = "Default routing"

    for min_min, max_min, rule_level, rule_notify in severity_rules:
        if min_min <= elapsed_minutes < max_min:
            level = rule_level
            notify = list(rule_notify)  # Copy to avoid mutation
            reason = (
                f"{severity.value} incident at {elapsed_minutes} min "
                f"triggers level {level} escalation"
            )
            break

    # Add customer_success for customer-facing SEV1/SEV2
    if is_customer_facing and severity in (IncidentSeverity.SEV1, IncidentSeverity.SEV2):
        if "customer_success" not in notify:
            notify.append("customer_success")

    # Only escalate if this is a higher level than previous
    should_escalate = level > previous_escalation_level

    return EscalationAction(
        should_escalate=should_escalate,
        escalation_level=level,
        notify=notify,
        reason=reason,
    )


# ============================================================================
# Solution 12: Customer Health Score Calculator
# ============================================================================
# Design notes:
# - This is a simplified version of what Gainsight/Totango/ChurnZero compute.
# - Each component score captures a different dimension of the relationship.
# - The weighted average reflects what matters most: usage and engagement
#   are leading indicators; support and satisfaction are lagging indicators.
# - health_status drives CSM playbooks: "healthy" = upsell, "at_risk" =
#   intervention, "critical" = executive escalation.
# ============================================================================

@dataclass
class CustomerHealthMetrics:
    """Raw metrics for computing customer health."""
    api_calls_last_30d: int
    api_calls_previous_30d: int
    error_rate_percent: float
    support_tickets_open: int
    support_tickets_resolved_30d: int
    nps_score: int | None
    days_since_last_login: int
    contract_months_remaining: int
    feature_adoption_percent: float


def calculate_health_score(metrics: CustomerHealthMetrics) -> dict[str, Any]:
    """Calculate composite customer health score.

    Each component is normalized to 0-100 so they can be weighted
    and compared. The clamping prevents impossible scores.
    """
    # --- Usage score: trend analysis ---
    if metrics.api_calls_previous_30d == 0:
        usage_score = 50.0 if metrics.api_calls_last_30d > 0 else 0.0
    else:
        usage_score = min(100.0, (metrics.api_calls_last_30d / metrics.api_calls_previous_30d) * 100)

    # --- Reliability score: error rate impact ---
    reliability_score = max(0.0, min(100.0, 100.0 - (metrics.error_rate_percent * 2)))

    # --- Support score: ticket burden ---
    support_score = max(0.0, 100.0 - (metrics.support_tickets_open * 10))
    support_score = min(100.0, support_score + (metrics.support_tickets_resolved_30d * 5))

    # --- Engagement score: recency ---
    engagement_score = max(0.0, 100.0 - (metrics.days_since_last_login * 5))

    # --- Adoption score: feature usage breadth ---
    adoption_score = metrics.feature_adoption_percent

    # --- Satisfaction score: NPS normalization ---
    if metrics.nps_score is None:
        satisfaction_score = 50.0
    else:
        satisfaction_score = (metrics.nps_score + 100) / 2.0

    # --- Weighted average ---
    overall_score = (
        usage_score * 0.20
        + reliability_score * 0.15
        + support_score * 0.15
        + engagement_score * 0.20
        + adoption_score * 0.15
        + satisfaction_score * 0.15
    )

    # --- Status classification ---
    if overall_score >= 70:
        health_status = "healthy"
    elif overall_score >= 40:
        health_status = "at_risk"
    else:
        health_status = "critical"

    return {
        "usage_score": round(usage_score, 2),
        "reliability_score": round(reliability_score, 2),
        "support_score": round(support_score, 2),
        "engagement_score": round(engagement_score, 2),
        "adoption_score": round(adoption_score, 2),
        "satisfaction_score": round(satisfaction_score, 2),
        "overall_score": round(overall_score, 2),
        "health_status": health_status,
    }


# ============================================================================
# Solution 13: Migration Plan Generator
# ============================================================================
# Design notes:
# - The 5-phase structure (assess -> pilot -> parallel -> cutover -> decommission)
#   is the industry standard for platform migrations.
# - Parallel run is the critical risk-reduction phase: run both systems and
#   compare outputs before cutting over.
# - The topological sort in critical_path() handles dependency ordering.
#   In production, you would also compute the actual critical path duration
#   considering parallel tasks (CPM algorithm).
# ============================================================================

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
    dependencies: list[str] = field(default_factory=list)
    owner: str = ""


@dataclass
class MigrationPlan:
    """Complete migration plan."""
    customer_name: str
    source_platform: str
    target_platform: str
    tasks: list[MigrationTask] = field(default_factory=list)

    def add_task(self, task: MigrationTask) -> None:
        """Enforce unique task titles."""
        if any(t.title == task.title for t in self.tasks):
            raise ValueError(f"Task '{task.title}' already exists")
        self.tasks.append(task)

    def total_duration_days(self) -> int:
        """Simple sum -- a rough upper bound ignoring parallelism."""
        return sum(t.duration_days for t in self.tasks)

    def tasks_by_phase(self) -> dict[str, list[MigrationTask]]:
        """Group tasks by phase for Gantt chart rendering."""
        result: dict[str, list[MigrationTask]] = defaultdict(list)
        for task in self.tasks:
            result[task.phase.value].append(task)
        return dict(result)

    def critical_path(self) -> list[str]:
        """Topological sort of tasks by dependencies.

        Uses Kahn's algorithm. This is the same algorithm used in build
        systems (Make, Bazel) and CI/CD pipeline schedulers.
        """
        # Build adjacency list and in-degree count
        task_map = {t.title: t for t in self.tasks}
        in_degree: dict[str, int] = {t.title: 0 for t in self.tasks}
        adjacency: dict[str, list[str]] = {t.title: [] for t in self.tasks}

        for task in self.tasks:
            for dep in task.dependencies:
                if dep in adjacency:
                    adjacency[dep].append(task.title)
                    in_degree[task.title] += 1

        # Start with tasks that have no dependencies
        queue = [title for title, degree in in_degree.items() if degree == 0]
        result: list[str] = []

        while queue:
            # Sort for deterministic ordering
            queue.sort()
            current = queue.pop(0)
            result.append(current)

            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.tasks):
            raise ValueError("Circular dependency detected in migration plan")

        return result


def generate_migration_plan(
    customer_name: str,
    source_platform: str,
    target_platform: str,
    num_endpoints: int,
) -> MigrationPlan:
    """Generate a migration plan with tasks scaled by complexity.

    num_endpoints is the primary scaling factor. More endpoints =
    more parallel run time and more cutover effort.
    """
    plan = MigrationPlan(
        customer_name=customer_name,
        source_platform=source_platform,
        target_platform=target_platform,
    )

    # Define tasks in phase order with dependencies forming a linear chain
    task_defs = [
        (MigrationPhase.ASSESSMENT, "Assessment & Discovery",
         f"Audit all {num_endpoints} endpoints on {source_platform}, "
         f"document API usage patterns, and identify migration risks.",
         5, []),
        (MigrationPhase.PILOT, "Pilot Migration",
         f"Migrate 1-2 non-critical endpoints to {target_platform} "
         f"and validate functional parity.",
         10, ["Assessment & Discovery"]),
        (MigrationPhase.PARALLEL_RUN, "Parallel Run",
         f"Run both {source_platform} and {target_platform} in parallel "
         f"for all {num_endpoints} endpoints. Compare outputs and latency.",
         max(14, num_endpoints * 2), ["Pilot Migration"]),
        (MigrationPhase.CUTOVER, "Production Cutover",
         f"Switch all {num_endpoints} endpoints to {target_platform}. "
         f"Maintain rollback capability for 48 hours.",
         max(5, num_endpoints), ["Parallel Run"]),
        (MigrationPhase.DECOMMISSION, "Decommission Legacy",
         f"Remove {source_platform} integration code, revoke API keys, "
         f"and archive migration documentation.",
         5, ["Production Cutover"]),
    ]

    for phase, title, description, duration, deps in task_defs:
        plan.add_task(MigrationTask(
            phase=phase,
            title=title,
            description=description,
            duration_days=duration,
            dependencies=deps,
        ))

    return plan


# ============================================================================
# Solution 14: Stakeholder Communication Matrix
# ============================================================================
# Design notes:
# - Different stakeholders need different information at different frequencies.
#   Sending the CTO daily technical details is spam; not sending the PM weekly
#   status is negligence.
# - The distribution plan is what you feed into your CRM automation or
#   email templating system.
# ============================================================================

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
    frequency_days: int = 7


@dataclass
class CommunicationMatrix:
    """Maps stakeholders to their communication needs."""
    stakeholders: list[Stakeholder] = field(default_factory=list)

    def add_stakeholder(self, stakeholder: Stakeholder) -> None:
        """Enforce unique emails to prevent duplicate notifications."""
        if any(s.email == stakeholder.email for s in self.stakeholders):
            raise ValueError(f"Stakeholder with email '{stakeholder.email}' already exists")
        self.stakeholders.append(stakeholder)

    def get_recipients_for_update(self, update_type: UpdateType) -> list[Stakeholder]:
        """Filter stakeholders by update type subscription."""
        return [s for s in self.stakeholders if update_type in s.update_types]

    def get_due_updates(self, days_since_last_update: int) -> list[Stakeholder]:
        """Identify stakeholders who are overdue for an update.

        This drives the "who do I owe an email to" workflow that every
        SE runs on Monday morning.
        """
        return [
            s for s in self.stakeholders
            if days_since_last_update >= s.frequency_days
        ]

    def generate_distribution_plan(self, update_type: UpdateType) -> list[dict[str, Any]]:
        """Generate a distribution plan for automation.

        Returns structured data suitable for feeding into SendGrid,
        Mailchimp, or a custom CRM integration.
        """
        recipients = self.get_recipients_for_update(update_type)
        return [
            {
                "name": s.name,
                "email": s.email,
                "role": s.role.value,
                "update_type": update_type.value,
            }
            for s in recipients
        ]


# ============================================================================
# Solution 15: Full Scenario Simulation Runner
# ============================================================================
# Design notes:
# - This ties ALL previous exercises together into an end-to-end simulation.
# - In a real SE org, you would run this as a "dry run" before engaging
#   a new enterprise customer, to sanity-check your tooling and playbooks.
# - Each step creates a ScenarioEvent for audit trail / retrospective review.
# - The simulation uses the SAME functions from exercises 1-14, proving
#   they compose correctly (integration test mindset).
# ============================================================================

@dataclass
class ScenarioEvent:
    """A single event in a scenario simulation."""
    timestamp: str
    event_type: str
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
        """Add an event and keep the counter in sync."""
        self.events.append(event)
        self.total_events = len(self.events)

    def get_events_by_type(self, event_type: str) -> list[ScenarioEvent]:
        return [e for e in self.events if e.event_type == event_type]

    def to_timeline(self) -> list[str]:
        """Render a human-readable timeline for retrospective review."""
        return [
            f"[{e.timestamp}] {e.event_type}: {e.description} -> {e.outcome}"
            for e in self.events
        ]


def run_scenario_simulation(scenario_name: str) -> SimulationResult:
    """Run a complete customer engagement scenario.

    This is the integration test for the entire module. It exercises
    every tool we built and validates they compose correctly.
    """
    # Step 1: Create a realistic enterprise customer profile
    profile = CustomerProfile(
        company_name="GlobalBank Financial Services",
        industry="fintech",
        size=CompanySize.ENTERPRISE,
        employee_count=15000,
        ai_maturity=AIMaturity.SCALING,
        tech_stack=["Python", "AWS", "PostgreSQL", "Kubernetes", "Kafka"],
        requirements=[
            "Automate document processing for loan applications",
            "Build fraud detection copilot for analysts",
            "Implement customer service chatbot with RAG",
        ],
        annual_revenue_mm=2500.0,
        existing_ai_tools=["OpenAI", "Hugging Face", "Databricks"],
        pain_points=[
            "High false positive rate in fraud detection",
            "Manual document review taking 3 days per application",
        ],
    )

    result = SimulationResult(scenario_name=scenario_name, customer=profile)
    base_time = datetime(2024, 6, 1, 9, 0, 0)

    # Step 1 event: Initial contact
    result.add_event(ScenarioEvent(
        timestamp=base_time.isoformat(),
        event_type="contact",
        description=f"Initial contact from {profile.company_name}",
        data={"readiness_score": profile.readiness_score()},
        outcome=f"Readiness score: {profile.readiness_score():.0f}/100",
    ))

    # Step 2: Discovery questionnaire
    questions = build_discovery_questionnaire()
    responses = QuestionnaireResponse(answers={
        "uc_primary": "Automate loan document processing with AI",
        "uc_current": "Manual review by team of 50 analysts",
        "data_volume": "100 GB - 1 TB",
        "data_pii": "Yes",
        "data_pii_types": "Names, SSN, financial records",
        "infra_cloud": "AWS",
        "sec_compliance": "SOC2, GDPR",
        "timeline_go_live": "3-6 months",
        "budget_range": "> $1M",
        "infra_gpu": "Yes, cloud",
    })
    result.add_event(ScenarioEvent(
        timestamp=(base_time + timedelta(days=1)).isoformat(),
        event_type="discovery",
        description="Discovery questionnaire completed",
        data={"completion": responses.completion_percentage(questions)},
        outcome=f"Questionnaire {responses.completion_percentage(questions):.0f}% complete",
    ))

    # Step 3: Triage the request
    triage = triage_customer_request(
        "We need to automate our loan document processing pipeline. "
        "Currently 50 analysts review documents manually, taking 3 days per application. "
        "We want to reduce this to under 1 hour with AI-powered extraction and classification. "
        "This is a strategic initiative with board-level visibility and a deadline of Q4.",
        profile,
    )
    result.add_event(ScenarioEvent(
        timestamp=(base_time + timedelta(days=2)).isoformat(),
        event_type="triage",
        description=f"Request triaged: {triage.priority.value} / {triage.complexity.value}",
        data={"priority": triage.priority.value, "team": triage.recommended_team},
        outcome=f"Assigned to {triage.recommended_team}",
    ))

    # Step 4: Generate POC scope
    scope = generate_poc_scope(profile, responses, questions)
    result.add_event(ScenarioEvent(
        timestamp=(base_time + timedelta(days=5)).isoformat(),
        event_type="poc",
        description=f"POC scope generated: {scope.title}",
        data={"timeline_weeks": scope.timeline_weeks, "deliverables": len(scope.deliverables)},
        outcome=f"{scope.timeline_weeks}-week POC with {len(scope.deliverables)} deliverables",
    ))

    # Step 5: Build workshop agenda
    agenda = build_workshop_agenda(
        profile, ["Document AI", "RAG Pipeline", "Fraud Detection"], duration_hours=4
    )
    result.add_event(ScenarioEvent(
        timestamp=(base_time + timedelta(days=10)).isoformat(),
        event_type="workshop",
        description=f"Workshop planned: {agenda.title}",
        data={"duration_minutes": agenda.total_duration_minutes, "items": len(agenda.items)},
        outcome=f"{len(agenda.items)}-item agenda, {agenda.total_duration_minutes} min total",
    ))

    # Step 6: Simulate an incident
    incident = IncidentReport(
        title="Document processing API latency spike",
        description="P99 latency increased from 200ms to 5s on the document extraction endpoint",
        affected_customers=150,
        total_customers=1000,
        service_degradation_percent=35.0,
        revenue_impact_per_hour=5000,
    )
    severity = classify_incident_severity(incident)
    comms = generate_incident_communication(
        incident, severity, CommunicationAudience.CUSTOMER,
        status="mitigating", eta_minutes=45,
    )
    result.add_event(ScenarioEvent(
        timestamp=(base_time + timedelta(days=30)).isoformat(),
        event_type="incident",
        description=f"Incident: {incident.title} ({severity.value})",
        data={"severity": severity.value, "affected": incident.affected_customers},
        outcome=f"Customer comms sent, severity {severity.value}",
    ))

    # Step 7: Calculate health score
    health_metrics = CustomerHealthMetrics(
        api_calls_last_30d=50000,
        api_calls_previous_30d=45000,
        error_rate_percent=3.5,
        support_tickets_open=2,
        support_tickets_resolved_30d=8,
        nps_score=55,
        days_since_last_login=1,
        contract_months_remaining=24,
        feature_adoption_percent=65.0,
    )
    health = calculate_health_score(health_metrics)
    result.add_event(ScenarioEvent(
        timestamp=(base_time + timedelta(days=45)).isoformat(),
        event_type="health_check",
        description=f"Health check: {health['health_status']}",
        data=health,
        outcome=f"Overall score: {health['overall_score']:.1f}, status: {health['health_status']}",
    ))

    # Set final status
    result.final_health_status = health["health_status"]
    result.success = health["health_status"] == "healthy"

    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_customer_profile():
    """Test Solution 1: Customer Profile Model."""
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
    assert profile.tech_stack_overlap(["Python", "AWS", "GCP", "Kubernetes"]) == 0.75
    assert profile.readiness_score() > 0
    assert profile.readiness_score() <= 100
    summary = profile.to_summary()
    assert "Acme Corp" in summary
    assert "fintech" in summary

    # Edge case: non-enterprise by size but enterprise by revenue
    revenue_enterprise = CustomerProfile(
        company_name="SmallButRich", industry="saas",
        size=CompanySize.SMB, employee_count=200,
        ai_maturity=AIMaturity.EXPLORING,
        annual_revenue_mm=600.0,
    )
    assert revenue_enterprise.is_enterprise() is True

    # Edge case: empty tech stack
    assert revenue_enterprise.tech_stack_overlap(["Python"]) == 0.0

    print("  Solution 1 (Customer Profile): PASSED")


def test_discovery_questionnaire():
    """Test Solution 2: Discovery Questionnaire."""
    questions = build_discovery_questionnaire()
    assert len(questions) >= 8

    categories = {q.category for q in questions}
    assert len(categories) >= 4, f"Only {len(categories)} categories: {categories}"

    assert any(q.depends_on is not None for q in questions)
    assert any(q.expected_type == "choice" and q.choices for q in questions)

    response = QuestionnaireResponse()
    assert response.is_complete(questions) is False
    assert response.completion_percentage(questions) == 0.0

    unanswered = response.unanswered_required(questions)
    required_count = sum(1 for q in questions if q.required)
    assert len(unanswered) == required_count

    for q in questions:
        if q.required:
            response.answers[q.id] = "sample answer"
    assert response.is_complete(questions) is True
    assert response.completion_percentage(questions) == 100.0
    assert len(response.unanswered_required(questions)) == 0

    print("  Solution 2 (Discovery Questionnaire): PASSED")


def test_poc_scope():
    """Test Solution 3: POC Scope Generator."""
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
    assert scope.timeline_weeks == 4   # Startup = 4 weeks
    assert len(scope.success_criteria) >= 2
    assert len(scope.deliverables) >= 2
    assert "Production deployment" in scope.out_of_scope

    md = scope.to_markdown()
    assert "Objective" in md
    assert "Success Criteria" in md
    assert "TechStartup Inc" in md

    # Enterprise should get 12 weeks
    enterprise_profile = CustomerProfile(
        company_name="BigCo", industry="finance",
        size=CompanySize.ENTERPRISE, employee_count=20000,
        ai_maturity=AIMaturity.SCALING,
    )
    enterprise_scope = generate_poc_scope(enterprise_profile, responses, questions)
    assert enterprise_scope.timeline_weeks == 12

    print("  Solution 3 (POC Scope): PASSED")


def test_success_criteria():
    """Test Solution 4: Success Criteria Framework."""
    framework = SuccessFramework()
    framework.add_criterion(SuccessCriterion(
        name="Latency", metric="p99_latency_ms", target_value=200.0,
        unit="ms", measurement_method="API monitoring",
        priority=CriteriaPriority.MUST_HAVE,
        lower_is_better=True,
    ))
    framework.add_criterion(SuccessCriterion(
        name="Accuracy", metric="f1_score", target_value=0.9,
        unit="score", measurement_method="Test set evaluation",
        priority=CriteriaPriority.MUST_HAVE,
    ))
    framework.add_criterion(SuccessCriterion(
        name="User Satisfaction", metric="csat", target_value=4.0,
        unit="rating", measurement_method="Survey",
        priority=CriteriaPriority.NICE_TO_HAVE,
    ))

    # Test duplicate prevention
    try:
        framework.add_criterion(SuccessCriterion(
            name="Latency", metric="x", target_value=0, unit="x",
            measurement_method="x", priority=CriteriaPriority.NICE_TO_HAVE,
        ))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    actuals = {"Latency": 150.0, "Accuracy": 0.92, "User Satisfaction": 3.5}
    results = framework.evaluate(actuals)
    # Latency: 150ms actual <= 200ms target (lower_is_better=True) -> met
    # Accuracy: 0.92 actual >= 0.9 target -> met
    # User Satisfaction: 3.5 actual < 4.0 target -> not met
    assert results["Latency"] is True
    assert results["Accuracy"] is True
    assert results["User Satisfaction"] is False
    assert framework.must_haves_met(actuals) is True
    assert 0.0 <= framework.pass_rate(actuals) <= 1.0

    # Test missing actuals count as not met
    results2 = framework.evaluate({"Latency": 150.0})
    assert results2["Accuracy"] is False
    assert results2["User Satisfaction"] is False

    print("  Solution 4 (Success Criteria): PASSED")


def test_triage_classifier():
    """Test Solution 5: Customer Triage."""
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
    assert result2.recommended_team == "technical_support"

    # Test enterprise with urgent keyword
    result3 = triage_customer_request(
        "This is urgent, we have a deadline next week",
        profile,
    )
    assert result3.priority == TriagePriority.HIGH

    print("  Solution 5 (Triage Classifier): PASSED")


def test_workshop_agenda():
    """Test Solution 6: Workshop Agenda Builder."""
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
    assert schedule[0]["title"] == "Welcome & Introductions"

    # Verify time progression
    for i in range(1, len(schedule)):
        assert schedule[i]["time"] >= schedule[i - 1]["time"]

    # Test overflow protection
    try:
        agenda.add_item(AgendaItem("Extra Long Session", 9999, "X", "demo"))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("  Solution 6 (Workshop Agenda): PASSED")


def test_security_responder():
    """Test Solution 7: Security Questionnaire Responder."""
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

    # No match should return None
    no_match = responder.find_best_answer("What is your favorite color?")
    assert no_match is None

    responses = responder.respond_to_questionnaire([
        "How is data encrypted in storage?",
        "What is your favorite color?",
    ])
    assert len(responses) == 2
    assert responses[0]["answer"] != "NEEDS MANUAL REVIEW"
    assert responses[0]["category"] == "encryption"
    assert responses[1]["answer"] == "NEEDS MANUAL REVIEW"
    assert responses[1]["confidence"] == 0.0

    print("  Solution 7 (Security Responder): PASSED")


def test_compliance_checklist():
    """Test Solution 8: Compliance Checklist."""
    checklist = build_compliance_checklist(["SOC2", "HIPAA"])
    soc2_items = checklist.get_by_framework("SOC2")
    hipaa_items = checklist.get_by_framework("HIPAA")
    assert len(soc2_items) >= 3
    assert len(hipaa_items) >= 3
    assert checklist.overall_completion() == 0.0
    assert len(checklist.gaps()) == len(checklist.items)

    # Mark SOC2 items as complete
    for item in soc2_items:
        item.status = ComplianceStatus.VERIFIED
    completion = checklist.completion_by_framework()
    assert completion["SOC2"] == 100.0
    assert completion["HIPAA"] == 0.0

    # Test unsupported framework
    try:
        build_compliance_checklist(["PCI_DSS"])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # Test duplicate control ID prevention
    try:
        checklist.add_item(ComplianceItem(
            control_id=soc2_items[0].control_id,
            framework="SOC2",
            description="Duplicate",
        ))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("  Solution 8 (Compliance Checklist): PASSED")


def test_incident_classifier():
    """Test Solution 9: Incident Severity Classifier."""
    # SEV1: high impact ratio
    report = IncidentReport(
        title="API Gateway Down",
        description="All API requests returning 503",
        affected_customers=950, total_customers=1000,
        service_degradation_percent=95.0,
        revenue_impact_per_hour=50000,
    )
    assert classify_incident_severity(report) == IncidentSeverity.SEV1

    # SEV1: security breach
    breach = IncidentReport(
        title="Unauthorized Access",
        description="Suspicious access detected",
        affected_customers=0, total_customers=1000,
        is_security_breach=True,
    )
    assert classify_incident_severity(breach) == IncidentSeverity.SEV1

    # SEV4: minor issue
    minor = IncidentReport(
        title="Slow response on dashboard",
        description="Dashboard loads in 5s instead of 1s",
        affected_customers=10, total_customers=1000,
        service_degradation_percent=5.0,
    )
    assert classify_incident_severity(minor) == IncidentSeverity.SEV4

    # SEV2: high revenue impact
    rev_impact = IncidentReport(
        title="Payment processing slow",
        description="Payments taking 30s instead of 2s",
        affected_customers=100, total_customers=1000,
        revenue_impact_per_hour=15000,
    )
    assert classify_incident_severity(rev_impact) == IncidentSeverity.SEV2

    print("  Solution 9 (Incident Classifier): PASSED")


def test_incident_communication():
    """Test Solution 10: Incident Communication."""
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
    assert "sev2" in internal
    assert "mitigating" in internal
    assert "500/1000" in internal

    customer = generate_incident_communication(
        report, IncidentSeverity.SEV2, CommunicationAudience.CUSTOMER,
        status="mitigating", eta_minutes=30,
    )
    assert "revenue" not in customer.lower()  # Never leak revenue details
    assert "30" in customer
    assert "apologize" in customer.lower()

    executive = generate_incident_communication(
        report, IncidentSeverity.SEV2, CommunicationAudience.EXECUTIVE,
    )
    assert "SEV2" in executive
    assert "50.0%" in executive
    assert "Determining" in executive  # No ETA provided

    print("  Solution 10 (Incident Communication): PASSED")


def test_escalation():
    """Test Solution 11: Escalation Decision Tree."""
    # SEV1 at 5 min: level 1
    action = evaluate_escalation(IncidentSeverity.SEV1, elapsed_minutes=5)
    assert action.should_escalate is True
    assert action.escalation_level == 1
    assert "on_call_manager" in action.notify
    assert "customer_success" in action.notify  # SEV1 + customer-facing

    # SEV1 at 45 min: level 3
    action2 = evaluate_escalation(IncidentSeverity.SEV1, elapsed_minutes=45)
    assert action2.escalation_level == 3
    assert "vp_engineering" in action2.notify or "cto" in action2.notify

    # SEV4 never escalates
    action3 = evaluate_escalation(IncidentSeverity.SEV4, elapsed_minutes=999)
    assert action3.escalation_level == 0
    assert action3.should_escalate is False

    # Test previous_escalation_level prevents duplicate escalation
    action4 = evaluate_escalation(
        IncidentSeverity.SEV1, elapsed_minutes=5, previous_escalation_level=1
    )
    assert action4.should_escalate is False  # Already at level 1

    print("  Solution 11 (Escalation): PASSED")


def test_health_score():
    """Test Solution 12: Customer Health Score."""
    # Healthy customer
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

    # Critical customer
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

    # Edge case: no previous usage
    edge_metrics = CustomerHealthMetrics(
        api_calls_last_30d=100,
        api_calls_previous_30d=0,
        error_rate_percent=0.0,
        support_tickets_open=0,
        support_tickets_resolved_30d=0,
        nps_score=None,
        days_since_last_login=0,
        contract_months_remaining=12,
        feature_adoption_percent=50.0,
    )
    edge_result = calculate_health_score(edge_metrics)
    assert edge_result["usage_score"] == 50.0  # New customer with some usage
    assert edge_result["satisfaction_score"] == 50.0  # No NPS = neutral

    print("  Solution 12 (Health Score): PASSED")


def test_migration_plan():
    """Test Solution 13: Migration Plan Generator."""
    plan = generate_migration_plan("Acme Corp", "OpenAI", "Anthropic", num_endpoints=5)
    assert plan.customer_name == "Acme Corp"
    assert plan.source_platform == "OpenAI"
    assert plan.target_platform == "Anthropic"
    assert len(plan.tasks) == 5

    phases = plan.tasks_by_phase()
    assert "assessment" in phases
    assert "pilot" in phases
    assert "parallel_run" in phases
    assert "cutover" in phases
    assert "decommission" in phases

    assert plan.total_duration_days() > 0

    # Verify critical path respects dependencies
    path = plan.critical_path()
    assert len(path) == 5
    assert path[0] == "Assessment & Discovery"
    assert path[-1] == "Decommission Legacy"

    # Test parallel_run scales with endpoints
    large_plan = generate_migration_plan("BigCo", "X", "Y", num_endpoints=20)
    parallel_task = [t for t in large_plan.tasks if t.phase == MigrationPhase.PARALLEL_RUN][0]
    assert parallel_task.duration_days == 40  # max(14, 20*2)

    # Test duplicate task prevention
    try:
        plan.add_task(MigrationTask(
            phase=MigrationPhase.ASSESSMENT,
            title="Assessment & Discovery",
            description="Duplicate",
            duration_days=1,
        ))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("  Solution 13 (Migration Plan): PASSED")


def test_communication_matrix():
    """Test Solution 14: Stakeholder Communication Matrix."""
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

    # Test get_recipients_for_update
    risk_recipients = matrix.get_recipients_for_update(UpdateType.RISK_ALERT)
    assert len(risk_recipients) == 1
    assert risk_recipients[0].name == "Jane CTO"

    status_recipients = matrix.get_recipients_for_update(UpdateType.STATUS_REPORT)
    assert len(status_recipients) == 2

    # Test get_due_updates
    due = matrix.get_due_updates(days_since_last_update=5)
    assert any(s.name == "Bob Engineer" for s in due)  # freq=3, 5>=3
    assert not any(s.name == "Jane CTO" for s in due)  # freq=7, 5<7

    due_all = matrix.get_due_updates(days_since_last_update=7)
    assert len(due_all) == 2

    # Test distribution plan
    plan = matrix.generate_distribution_plan(UpdateType.STATUS_REPORT)
    assert len(plan) == 2
    assert all("name" in p and "email" in p for p in plan)

    # Test duplicate email prevention
    try:
        matrix.add_stakeholder(Stakeholder(
            name="Jane Duplicate", role=StakeholderRole.END_USER,
            email="jane@acme.com",
        ))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("  Solution 14 (Communication Matrix): PASSED")


def test_scenario_simulation():
    """Test Solution 15: Full Scenario Simulation."""
    result = run_scenario_simulation("Enterprise Onboarding")
    assert result.scenario_name == "Enterprise Onboarding"
    assert result.total_events >= 7

    # Verify event types
    event_types = {e.event_type for e in result.events}
    expected_types = {"contact", "discovery", "poc", "workshop", "incident", "health_check"}
    assert expected_types.issubset(event_types), f"Missing types: {expected_types - event_types}"

    assert result.final_health_status in ("healthy", "at_risk", "critical")
    assert isinstance(result.success, bool)

    timeline = result.to_timeline()
    assert len(timeline) == result.total_events
    # Each timeline entry should have the expected format
    for entry in timeline:
        assert entry.startswith("[")
        assert "] " in entry
        assert " -> " in entry

    # Verify get_events_by_type
    incidents = result.get_events_by_type("incident")
    assert len(incidents) >= 1

    print("  Solution 15 (Scenario Simulation): PASSED")


if __name__ == "__main__":
    print("Testing Customer Scenario Simulation solutions...\n")
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
    print("\nAll 15 solutions passed!")
