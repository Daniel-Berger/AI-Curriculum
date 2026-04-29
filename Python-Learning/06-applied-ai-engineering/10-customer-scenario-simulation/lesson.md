# Customer Scenario Simulation

This lesson simulates the full lifecycle of a Solutions Engineer (SE) at companies like Anthropic, OpenAI, Google, or Cohere. You will walk through realistic customer engagements from first contact through production deployment, learning the frameworks, communication patterns, and technical tools that separate great SEs from good ones.

---

## The Solutions Engineer Workflow

A Solutions Engineer sits at the intersection of engineering, sales, and customer success. You solve real technical problems while building relationships that drive revenue.

### End-to-End Customer Engagement Lifecycle

```
Discovery ──> Deep-Dive ──> POC Scoping ──> POC Execution
    │              │             │                │
    ▼              ▼             ▼                ▼
POC Review ──> Prod Planning ──> Go-Live ──> Ongoing Success
```

| Stage | Duration | Your Role |
|-------|----------|-----------|
| Discovery | 1-2 calls | Technical advisor: qualify need, assess fit |
| Deep-Dive | 1-3 sessions | Engineer: architecture review, API walkthrough |
| POC Scoping | 1-2 weeks | Project manager: define success criteria |
| POC Execution | 2-6 weeks | Developer + coach: build and iterate |
| POC Review | 1 session | Presenter: results and go/no-go |
| Production Planning | 2-4 weeks | Architect: security review, scaling plan |
| Go-Live | 1-2 weeks | On-call engineer: deploy, monitor, troubleshoot |
| Ongoing Success | Indefinite | Trusted advisor: optimization, expansion |

> **Swift Developer Note:** Think of this lifecycle like Apple's DTS (Developer Technical Support) but far more hands-on. Where DTS gives a code-level answer to one question, an SE embeds with a customer team for months. It is closer to a WWDC lab session that lasts for months where you are debugging their production system.

### Tracking Engagements Programmatically

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class EngagementStage(Enum):
    DISCOVERY = "discovery"
    DEEP_DIVE = "deep_dive"
    POC_SCOPING = "poc_scoping"
    POC_EXECUTION = "poc_execution"
    POC_REVIEW = "poc_review"
    GO_LIVE = "go_live"
    ONGOING = "ongoing"


class Priority(Enum):
    P0_CRITICAL = 0
    P1_HIGH = 1
    P2_MEDIUM = 2
    P3_LOW = 3


@dataclass
class CustomerEngagement:
    company: str
    contact: str
    stage: EngagementStage
    priority: Priority
    use_case: str
    arr_potential: int
    next_action: str = ""
    next_action_date: Optional[datetime] = None
    blockers: list[str] = field(default_factory=list)

    @property
    def is_overdue(self) -> bool:
        if self.next_action_date is None:
            return False
        return datetime.now() > self.next_action_date

    @property
    def health_score(self) -> str:
        if self.is_overdue:
            return "RED"
        if self.blockers:
            return "YELLOW"
        return "GREEN"


class EngagementTracker:
    def __init__(self):
        self.engagements: list[CustomerEngagement] = []

    def add(self, engagement: CustomerEngagement) -> None:
        self.engagements.append(engagement)

    def daily_summary(self) -> str:
        lines = [f"=== SE Daily Summary ({datetime.now():%Y-%m-%d}) ===\n"]
        for health in ["RED", "YELLOW", "GREEN"]:
            matching = [e for e in self.engagements if e.health_score == health]
            if matching:
                lines.append(f"\n--- {health} ---")
                for eng in matching:
                    flag = " [OVERDUE]" if eng.is_overdue else ""
                    lines.append(
                        f"  {eng.company} ({eng.stage.value}){flag}"
                        f"\n    Next: {eng.next_action}"
                        f"\n    ARR: ${eng.arr_potential:,}"
                    )
        return "\n".join(lines)
```

---

## Customer Triage and Discovery

Discovery determines whether a customer is a good fit and what their real needs are. Getting this wrong wastes weeks of engineering time.

### The BANT Framework for AI Solutions

| Factor | Green Flag | Red Flag |
|--------|------------|----------|
| **Budget** | "$10K-100K+/month committed" | "We're exploring, no budget yet" |
| **Authority** | CTO/VP Eng on the call | "I'll need to check with my manager" |
| **Need** | Clear pain point with quantifiable cost | "Competitors have AI, so we want it too" |
| **Timeline** | "Q2 launch, board committed" | "Sometime this year, no rush" |

### Qualification Scoring

```python
def calculate_qualification_score(
    budget: int,          # 1-5
    authority: int,       # 1-5
    need: int,            # 1-5
    timeline: int,        # 1-5
    technical_fit: int,   # 1-5
    strategic_value: int, # 1-5
) -> dict:
    weights = {
        "budget": 0.20, "authority": 0.10, "need": 0.25,
        "timeline": 0.15, "technical_fit": 0.20, "strategic_value": 0.10,
    }
    scores = dict(zip(weights.keys(), [budget, authority, need, timeline, technical_fit, strategic_value]))
    normalized = sum(scores[k] * weights[k] for k in weights) / 5.0 * 100

    if normalized >= 75:
        return {"score": normalized, "action": "HOT - Schedule deep-dive within 48 hours"}
    elif normalized >= 50:
        return {"score": normalized, "action": "WARM - Schedule deep-dive within 1 week"}
    elif normalized >= 30:
        return {"score": normalized, "action": "COOL - Send resources, revisit in 2 weeks"}
    return {"score": normalized, "action": "COLD - Add to nurture campaign"}

# Enterprise healthcare company with regulatory deadline
result = calculate_qualification_score(budget=4, authority=5, need=5, timeline=4, technical_fit=4, strategic_value=5)
print(f"Score: {result['score']:.0f} -> {result['action']}")
# Score: 88 -> HOT - Schedule deep-dive within 48 hours
```

### Discovery Call Follow-Up Generator

```python
def generate_follow_up(company: str, use_case: str, pain_points: list[str],
                       timeline: str, next_steps: list[str]) -> str:
    return f"""Subject: Follow-up: {company} x [Your Company] - {use_case}

Hi {company} team,

Thank you for discussing your {use_case} use case today.

**What we heard:**
- Key pain points: {', '.join(pain_points)}
- Timeline: {timeline}

**Next steps:**
{chr(10).join(f'- {step}' for step in next_steps)}

Please let me know if I missed anything.

Best regards,
[Your Name], Solutions Engineer"""
```

> **Swift Developer Note:** This qualification process parallels how App Review triages submissions by risk level. The key difference: you are trying to help customers succeed, not gatekeep.

---

## POC Scoping

A well-scoped POC is the single most important SE deliverable. Scope it too broadly and it never ships. Too narrowly and the customer does not see enough value.

### POC Scope Document Generator

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class SuccessCriterion:
    metric: str
    target: str
    measurement: str
    priority: str = "must-have"  # or "nice-to-have"


@dataclass
class POCScope:
    customer: str
    use_case: str
    start_date: datetime
    duration_weeks: int
    in_scope: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    success_criteria: list[SuccessCriterion] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    def generate_markdown(self) -> str:
        end = self.start_date + timedelta(weeks=self.duration_weeks)
        criteria = "\n".join(
            f"| {c.metric} | {c.target} | {c.measurement} | {c.priority} |"
            for c in self.success_criteria
        )
        return f"""# POC: {self.customer} - {self.use_case}
**Duration:** {self.duration_weeks} weeks ({self.start_date:%Y-%m-%d} to {end:%Y-%m-%d})

## In Scope
{chr(10).join(f'- {s}' for s in self.in_scope)}

## Out of Scope
{chr(10).join(f'- {s}' for s in self.out_of_scope)}

## Success Criteria
| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
{criteria}

## Risks
{chr(10).join(f'- {r}' for r in self.risks)}

## Go/No-Go at Week {self.duration_weeks}
- **GO:** All must-have criteria met -> production planning
- **EXTEND:** Most criteria met, need 1-2 more weeks
- **PIVOT:** Criteria not met, alternative approach identified
- **NO-GO:** Fundamental blockers -> document learnings, disengage"""

poc = POCScope(
    customer="Acme Healthcare",
    use_case="Clinical Note Summarization",
    start_date=datetime(2026, 5, 1),
    duration_weeks=4,
    in_scope=["Summarization of de-identified notes", "Quality eval on 500 samples"],
    out_of_scope=["Real-time EHR integration", "PHI handling"],
    success_criteria=[
        SuccessCriterion("Accuracy", ">= 90% physician approval", "Blind review of 100 summaries"),
        SuccessCriterion("Latency (p95)", "< 5 seconds", "API response time logs"),
    ],
    risks=["De-identified data may contain quasi-identifiers", "Physician availability may slip"],
)
print(poc.generate_markdown())
```

### Time-Boxing Rules

| POC Type | Duration | Max Extension |
|----------|----------|---------------|
| Simple API integration | 2 weeks | +1 week |
| RAG pipeline | 3-4 weeks | +2 weeks |
| Multi-model workflow | 4-6 weeks | +2 weeks |
| Enterprise + compliance | 6-8 weeks | +3 weeks |

The iron rule: if a POC is clearly failing at Week 2, do not drag it to Week 6 hoping it improves.

---

## Technical Workshop Design

Workshops are your highest-leverage activity. A great workshop compresses weeks of learning into hours of guided, hands-on work.

### Workshop Planning

```python
@dataclass
class WorkshopAgendaItem:
    title: str
    duration_min: int
    format: str  # "lecture", "demo", "hands-on", "discussion", "break"

@dataclass
class Workshop:
    title: str
    customer: str
    duration_hours: float
    agenda: list[WorkshopAgendaItem]
    prerequisites: list[str]

    def run_of_show(self) -> str:
        lines = [f"# {self.title} ({self.customer})\n"]
        lines.append("| Time | Topic | Format | Duration |")
        lines.append("|------|-------|--------|----------|")
        minutes = 0
        for item in self.agenda:
            lines.append(f"| {minutes//60}:{minutes%60:02d} | {item.title} | {item.format} | {item.duration_min}m |")
            minutes += item.duration_min
        return "\n".join(lines)

workshop = Workshop(
    title="Prompt Engineering with Claude",
    customer="Acme Healthcare",
    duration_hours=3,
    prerequisites=["API key working", "Python 3.10+", "anthropic SDK installed"],
    agenda=[
        WorkshopAgendaItem("Setup + Environment Check", 15, "hands-on"),
        WorkshopAgendaItem("Anatomy of a Great System Prompt", 30, "lecture+demo"),
        WorkshopAgendaItem("Exercise: Write Prompts for Your Use Case", 30, "hands-on"),
        WorkshopAgendaItem("Break", 10, "break"),
        WorkshopAgendaItem("Few-Shot and Chain-of-Thought", 25, "lecture+demo"),
        WorkshopAgendaItem("Exercise: Build Eval Harness", 30, "hands-on"),
        WorkshopAgendaItem("Break", 10, "break"),
        WorkshopAgendaItem("Production Patterns", 20, "demo"),
        WorkshopAgendaItem("Open Lab: Your Integration", 30, "hands-on"),
        WorkshopAgendaItem("Wrap-Up + Q&A", 10, "discussion"),
    ],
)
print(workshop.run_of_show())
```

### Best Practices

1. **70/30 rule**: 70% hands-on, 30% lecture. Adults learn by doing.
2. **Bring their data**: Use the customer's actual use case, not generic examples.
3. **Pre-flight checklist**: Send setup instructions 3 days before. Have backup API keys.
4. **Leave behind materials**: Notebooks, prompt templates, and a cheat sheet.

> **Swift Developer Note:** These workshops are the WWDC lab experience, but you are the Apple engineer. Remember how valuable those 1:1 sessions felt? That is exactly what you are creating. The best lab engineers taught you to fish -- do the same.

---

## Security Review Scenarios

Enterprise customers require security review before sending data to your API. This is non-negotiable for regulated industries and standard for companies over 500 employees.

### Security Knowledge Base

```python
SECURITY_KB = {
    "data_training": {
        "q": "Is customer data used to train your models?",
        "a": "No. API data is not used for training. Data is retained 30 days "
             "for abuse monitoring, then deleted. Zero-retention available.",
        "docs": ["Data Processing Agreement", "Privacy Policy"],
    },
    "soc2": {
        "q": "Are you SOC 2 Type II certified?",
        "a": "Yes. Report available under NDA.",
        "docs": ["SOC 2 Type II Report"],
    },
    "baa": {
        "q": "Can you sign a BAA for HIPAA?",
        "a": "Yes. BAA covers data processed through our API. Customer is "
             "responsible for de-identification when BAA is not in place.",
        "docs": ["BAA Template", "HIPAA Compliance Guide"],
        "requires_legal": True,
    },
    "encryption": {
        "q": "How is data encrypted?",
        "a": "TLS 1.2+ in transit, AES-256 at rest.",
        "docs": ["Infrastructure Architecture Doc"],
    },
}

def answer_security_question(topic: str) -> str:
    entry = SECURITY_KB.get(topic)
    if not entry:
        return "No pre-approved answer. Escalate to security team."
    result = f"Q: {entry['q']}\nA: {entry['a']}\nDocs: {', '.join(entry['docs'])}"
    if entry.get("requires_legal"):
        result += "\n** Requires legal review before sending **"
    return result
```

### Security Call Preparation Checklist

**Before:** Request questionnaire in advance. Pre-fill from KB. Flag items needing legal input. Have SOC 2, DPA, and architecture diagrams ready.

**During:** Do not guess. Say "I will follow up with our security team" for unknowns. Differentiate capabilities from contractual commitments. Take detailed notes.

**After:** Written follow-up within 24 hours. Track all action items with deadlines.

> **Swift Developer Note:** If you have been through App Review rejections with vague reasoning, you know the frustration of opaque security processes. Be the opposite. Enterprise security teams respect transparency far more than hand-waving.

---

## Production Incident Response

How you handle incidents defines your customer relationship more than any demo ever will.

### Severity Classification and SLAs

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class Severity(Enum):
    P0 = "P0 - Critical"    # Production down
    P1 = "P1 - High"        # Major feature degraded
    P2 = "P2 - Medium"      # Minor issue, low impact
    P3 = "P3 - Low"         # Cosmetic / feature request

SLA_TARGETS = {
    Severity.P0: {"first_response_min": 15, "update_freq_min": 60, "resolve_hrs": 4},
    Severity.P1: {"first_response_min": 60, "update_freq_min": 240, "resolve_hrs": 24},
    Severity.P2: {"first_response_min": 480, "update_freq_min": 1440, "resolve_hrs": 72},
    Severity.P3: {"first_response_min": 1440, "update_freq_min": None, "resolve_hrs": None},
}

@dataclass
class Incident:
    id: str
    customer: str
    severity: Severity
    title: str
    reported_at: datetime
    updates: list[dict] = field(default_factory=list)

    def add_update(self, status: str, message: str, internal: bool = False):
        self.updates.append({
            "time": datetime.now(), "status": status,
            "message": message, "internal": internal,
        })

    def customer_update_email(self) -> str:
        public = [u for u in self.updates if not u["internal"]]
        latest = public[-1] if public else {"message": "Investigating..."}
        sla = SLA_TARGETS[self.severity]
        return f"""Subject: [{self.severity.value}] {self.title} - Update

Incident: {self.id} | Status: {latest.get('status', 'investigating')}
Reported: {self.reported_at:%Y-%m-%d %H:%M UTC}

**Current Status:** {latest['message']}

Next update within {sla['update_freq_min']} minutes or sooner if status changes.
"""
```

### Communication Templates

```python
def incident_ack(customer: str, findings: str, next_update_min: int) -> str:
    return f"""Hi {customer},

We are aware of the issue and actively investigating.

**What we know:** {findings}
**Next update:** Within {next_update_min} minutes.

I will be your point of contact throughout this incident.

Best, [Your Name]"""

def incident_resolution(customer: str, root_cause: str, resolution: str, duration: str) -> str:
    return f"""Hi {customer},

The incident has been resolved.

**Root cause:** {root_cause}
**Resolution:** {resolution}
**Duration:** {duration}

We will schedule a post-incident review within 5 business days.

Best, [Your Name]"""
```

### Golden Rules of Incident Communication

1. **Acknowledge fast**, even without information. Silence is the worst response.
2. **Never blame the customer.** Even if their code caused it.
3. **Be specific about timelines.** "Within 30 minutes" beats "soon."
4. **Own the follow-through.** You are the customer's advocate even after escalating.

---

## Escalation Management

Knowing when to escalate is critical. Too early and you lose credibility; too late and the customer loses trust.

### Escalation Decision Framework

```python
def should_escalate(
    production_impact: bool,
    customer_tier: str,
    se_can_resolve: bool,
    hours_spent: float,
    data_security_concern: bool,
    exec_involved: bool,
) -> dict:
    # Immediate triggers
    if data_security_concern:
        return {"escalate": True, "to": "security", "urgency": "immediate",
                "channel": "#security-incidents + page on-call"}
    if production_impact and customer_tier == "enterprise":
        return {"escalate": True, "to": "engineering", "urgency": "immediate",
                "channel": "#eng-oncall + PagerDuty"}
    if exec_involved:
        return {"escalate": True, "to": "management", "urgency": "today",
                "channel": "SE Manager DM"}

    # Judgment-based
    if not se_can_resolve and hours_spent > 4:
        return {"escalate": True, "to": "engineering", "urgency": "today",
                "channel": "#eng-support with detailed writeup"}
    return {"escalate": False, "to": "none", "urgency": "n/a", "channel": "continue direct"}
```

### Escalation Anti-Patterns

| Anti-Pattern | Why It Is Bad | Do This Instead |
|-------------|---------------|-----------------|
| Throw it over the wall | Engineering gets incomplete context | Provide repro steps, logs, your hypothesis |
| Escalate without trying | Lose credibility with engineering | Investigate 30-60 min first |
| Escalate silently | Customer does not know help is coming | Tell them: "I am bringing in a specialist" |
| Disappear after escalating | Customer feels abandoned | Stay as point of contact, relay updates |

### Internal Escalation Template

```python
def escalation_message(customer: str, tier: str, arr: str, issue: str,
                       tried: list[str], hypothesis: str, request_ids: list[str]) -> str:
    tried_str = "\n".join(f"  - {t}" for t in tried)
    ids_str = "\n".join(f"  - {r}" for r in request_ids)
    return f"""**Escalation: {customer}** ({tier}, {arr} ARR)

**Issue:** {issue}

**What I tried:**
{tried_str}

**My hypothesis:** {hypothesis}

**Request IDs:**
{ids_str}

**Ask:** Need engineering investigation. Happy to hop on a call."""
```

---

## Full Scenario Walkthroughs

### Scenario 1: Enterprise Migration -- OpenAI to Anthropic

**Context:** FinCorp (Fortune 500 financial services) processes 50K financial documents/day on GPT-4. Their CISO wants stronger data privacy. They are evaluating Claude.

**Discovery phase:** Research FinCorp before the call. Prepare API migration mapping, pricing comparison, and privacy policy differences.

```python
# API migration mapping
MIGRATION_MAP = {
    "gpt-4": "claude-sonnet-4-20250514",
    "gpt-4o-mini": "claude-haiku-3-20240307",
}
KEY_DIFFERENCES = [
    "System prompt is top-level parameter, not a message role",
    "No response_format -- use tool_use for structured JSON",
    "max_tokens is required (OpenAI defaults to inf)",
    "Different SSE event format for streaming",
    "Anthropic does not offer embeddings -- need Voyage/Cohere",
]

# Cost estimate
docs_per_day = 50_000
monthly_cost = (docs_per_day * 4000 / 1e6 * 3.0 + docs_per_day * 1000 / 1e6 * 15.0) * 30
print(f"Estimated monthly: ${monthly_cost:,.0f}")
```

**POC approach:** Process 1,000 representative documents through Claude, compare quality and cost. Migrate in phases: non-critical first, then dual-write, then full cutover.

### Scenario 2: Startup Cost Optimization

**Context:** QuickBot (Series A, 20 people) launched a support chatbot on Claude Opus. Monthly cost: $45K (budget: $10K). Latency: 8s (target: <3s).

```python
# Optimization analysis
strategies = {
    "Switch Opus -> Sonnet": {"cost_reduction": "60-70%", "latency_improvement": "50%"},
    "Route simple queries to Haiku": {"cost_reduction": "additional 30%", "latency": "1.5s for simple"},
    "Prompt caching (system prompt)": {"cost_reduction": "20-30% on input tokens"},
    "Trim conversation history": {"cost_reduction": "15-20%", "latency": "faster TTFT"},
}
# Combined: $45K -> ~$6K/month, 8s -> 2.5s latency
```

**Recommendation:** Combine model routing (Haiku for FAQ, Sonnet for complex), prompt caching, and history trimming. Expected: $6K/month, 2.5s latency.

### Scenario 3: Healthcare HIPAA Compliance

**Context:** MedAssist wants clinical decision support with Claude. They handle PHI.

```python
HIPAA_CHECKLIST = [
    ("Legal", "BAA signed", "shared"),
    ("Legal", "DPA reviewed", "shared"),
    ("Data", "PHI de-identification pipeline", "customer"),
    ("Data", "Minimum necessary standard applied", "customer"),
    ("Data", "Zero-retention confirmed", "provider"),
    ("Access", "Role-based API key management", "customer"),
    ("Access", "Audit logging for all API calls", "customer"),
    ("Technical", "Output filtering for PHI in responses", "customer"),
    ("Technical", "Error handling does not expose PHI", "customer"),
    ("Risk", "Human-in-the-loop for clinical decisions", "customer"),
]
for category, item, owner in HIPAA_CHECKLIST:
    print(f"[{category}] {item} (Owner: {owner})")
```

**The critical conversation:** When the customer asks "Can you guarantee Claude will never hallucinate a wrong dosage?" -- the right answer is: "No AI system can guarantee that. We recommend human-in-the-loop architecture where Claude generates drafts and clinicians review before action."

> **Swift Developer Note:** This mirrors Apple's HealthKit approach: even though your app reads heart rate data, Apple requires disclaimers that it is not medical-grade. Same principle with AI -- the technology is powerful but guardrails and human oversight are non-negotiable.

### Scenario 4: RAG Hallucination Debugging

**Context:** LegalTech built a RAG system for legal research. Lawyers report fabricated case citations.

```python
def diagnose_rag_hallucination(retrieval_scores: list[float], system_prompt: str) -> list[str]:
    """Systematic RAG hallucination diagnosis."""
    issues = []

    # Check retrieval quality
    avg_score = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0
    if avg_score < 0.7:
        issues.append("LOW RETRIEVAL QUALITY: Avg score {:.2f}. Improve chunking or embeddings.".format(avg_score))

    # Check grounding instructions
    grounding_phrases = ["only use the provided", "do not make up", "if you don't know"]
    if not any(p in system_prompt.lower() for p in grounding_phrases):
        issues.append("MISSING GROUNDING: Add 'Only answer from provided context' to system prompt.")

    # Check citation enforcement
    if "cite" not in system_prompt.lower():
        issues.append("NO CITATION FORMAT: Add '[Source: doc_name, page X]' requirement.")

    return issues

issues = diagnose_rag_hallucination(
    retrieval_scores=[0.82, 0.75, 0.45],
    system_prompt="You are a legal assistant. Be thorough and cite relevant cases."
)
for issue in issues:
    print(f"  - {issue}")
```

**Root causes found:** (1) Prompt says "be thorough" but not "only use provided context," encouraging gap-filling from training data. (2) No citation format enforced. (3) Low-relevance chunks adding noise. **Fix:** Rewrite system prompt with explicit grounding, add citation format requirement, filter chunks below 0.65 relevance.

---

## Swift Developer Comparison

### Apple DTS vs. AI Solutions Engineering

| Aspect | Apple DTS | AI Solutions Engineer |
|--------|-----------|----------------------|
| Engagement | Reactive: developer submits ticket | Proactive: you build relationships |
| Scope | One specific question | Embed for weeks/months |
| Revenue | Indirect (App Store) | Direct (API usage = revenue) |
| Success metric | Ticket resolved | Customer in production, growing |

### WWDC Labs vs. Technical Workshops

| Aspect | WWDC Lab | SE Workshop |
|--------|----------|-------------|
| Duration | 10-30 min | 2-4 hours |
| Follow-up | None | Weeks of engagement |
| Materials | Apple sample code | Custom notebooks with their data |

### Transferable Skills

1. **Debugging under pressure**: Crash reports from millions of users translates to production incidents.
2. **API design intuition**: Years with Apple APIs gives you a sense for good vs. frustrating integration experiences.
3. **User empathy**: You built for end users. Now your "user" is a developer.

> **Swift Developer Note:** The biggest mindset shift is moving from being the person asking for help (filing radars, attending labs) to being the person providing it. Every frustration you felt dealing with opaque Apple processes is a lesson in what NOT to do as an SE.

---

## Interview Focus

SE interviews heavily feature scenario-based questions. Interviewers want to see how you think through ambiguous situations.

### Interview Formats

| Format | Duration | Tests |
|--------|----------|-------|
| Mock customer call | 30-45 min | Communication, technical depth, empathy |
| Technical deep-dive | 45-60 min | Architecture, debugging, system design |
| Case study presentation | 30+15 min | Structured thinking, prioritization |
| Role-play escalation | 20-30 min | Judgment, composure |

### Sample Scenarios with Frameworks

```python
SCENARIOS = [
    {
        "question": "Customer tested Claude vs GPT-4. GPT-4 won 7/10 cases. Why use Claude?",
        "framework": "Acknowledge -> Investigate -> Reframe -> Demonstrate",
        "response": (
            "Thank you for sharing that data. I'd love to understand your eval "
            "methodology. Often prompts optimized for GPT-4 need adjustment for "
            "Claude. I'd be happy to help optimize and re-run the comparison. "
            "Once prompts are tuned for each model, we can evaluate on quality "
            "plus cost, safety, and support."
        ),
    },
    {
        "question": "CEO says your API caused 4-hour outage, $200K lost. Status page shows no incidents.",
        "framework": "Empathy -> Investigate -> Communicate -> Resolve",
        "response": (
            "I take this seriously. I'm pulling your account's request logs now. "
            "I'm looping in my manager for executive visibility. Can we schedule "
            "a call within 2 hours with your engineering team to compare logs? "
            "Regardless of root cause, we'll help implement safeguards."
        ),
    },
    {
        "question": "POC is failing after 3 weeks. Sales wants you to make it work. $500K deal.",
        "framework": "Integrity -> Evidence -> Alternatives -> Communication",
        "response": (
            "I need to be honest. Here is the evidence showing the gap. I've "
            "tried approaches X, Y, Z. Options: pivot to a use case that does "
            "work, or pause and revisit when our roadmap addresses the gap. "
            "I'd rather be transparent now than have you sign and be disappointed."
        ),
    },
    {
        "question": "Healthcare customer asks you to sign off their architecture as 'HIPAA compliant.'",
        "framework": "Boundary-setting -> Education -> Support",
        "response": (
            "I can't certify your compliance -- that requires your own auditor. "
            "What I can do: provide our BAA, SOC 2 report, and review your "
            "architecture for best practices. I'd recommend engaging compliance "
            "counsel for the formal assessment."
        ),
    },
]
```

### Role-Play Tips

1. **Practice out loud.** Reading and speaking are different skills. Record yourself.
2. **Ask clarifying questions.** Never launch into solutions without understanding the problem.
3. **Time yourself.** Initial responses: 60-90 seconds. Longer is monologuing.
4. **Show reasoning.** "First I would X, because Y. Then I'd check Z, because..."
5. **Admit unknowns.** "I'm not sure about that specific requirement, but here's how I'd find out."

### Mock Call Structure

```
0:00 - 2:00   Introduction and rapport
2:00 - 10:00  Discovery questions (80% customer talking)
10:00 - 20:00 Technical discussion and demo
20:00 - 25:00 Summarize, propose next steps
25:00 - 30:00 Handle objections, close
```

The biggest mistake: presenting solutions at minute 2 without understanding the problem.

---

## Health Check Script

SEs monitor customer API health proactively, not waiting for panicked emails.

```python
import time
from dataclasses import dataclass
from datetime import datetime


@dataclass
class HealthCheck:
    name: str
    status: str  # "pass", "warn", "fail"
    details: str

def check_rate_limits(current_rpm: int, max_rpm: int) -> HealthCheck:
    pct = current_rpm / max_rpm * 100
    if pct > 90:
        return HealthCheck("Rate Limits", "fail", f"At {pct:.0f}% of limit")
    elif pct > 70:
        return HealthCheck("Rate Limits", "warn", f"At {pct:.0f}% of limit")
    return HealthCheck("Rate Limits", "pass", f"At {pct:.0f}% of limit")

def check_error_rate(total: int, errors: int) -> HealthCheck:
    if total == 0:
        return HealthCheck("Error Rate", "warn", "No requests -- integration may be down")
    rate = errors / total * 100
    if rate > 5:
        return HealthCheck("Error Rate", "fail", f"{rate:.1f}% error rate")
    elif rate > 1:
        return HealthCheck("Error Rate", "warn", f"{rate:.1f}% error rate")
    return HealthCheck("Error Rate", "pass", f"{rate:.1f}% error rate")

def run_health_check(customer: str) -> str:
    checks = [
        check_rate_limits(current_rpm=45, max_rpm=60),
        check_error_rate(total=5000, errors=150),
    ]
    icons = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}
    lines = [f"Health Report: {customer} ({datetime.now():%Y-%m-%d %H:%M})", "=" * 40]
    for c in checks:
        lines.append(f"{icons[c.status]} {c.name}: {c.details}")

    fails = sum(1 for c in checks if c.status == "fail")
    lines.append(f"\nOverall: {'UNHEALTHY' if fails else 'HEALTHY'}")
    return "\n".join(lines)

print(run_health_check("Acme Healthcare"))
```

---

## Exercises

1. **Engagement Tracker**: Extend `EngagementTracker` to send alerts when health turns RED and generate weekly summaries grouped by stage.

2. **Mock Discovery Call**: Write complete discovery notes for a fintech company wanting fraud detection with Claude. Calculate their qualification score and generate the follow-up email.

3. **POC Scope**: Create a full POC scope document for the fraud detection use case with 4+ success criteria, 3 milestones, and 3 risks.

4. **Incident Simulation**: Write a complete incident timeline (6+ updates) for a RAG pipeline returning empty responses after an API version upgrade.

5. **Security KB**: Add 5 new entries covering data residency (EU), penetration testing, disaster recovery, subprocessors, and employee background checks.

6. **Interview Role-Play**: Pick one scenario and write both sides of the conversation -- interviewer questions and your responses -- for a 10-minute exchange (~1500 words).

7. **Health Dashboard**: Extend the health check to track results over 7 days and report trends (improving, stable, degrading).
