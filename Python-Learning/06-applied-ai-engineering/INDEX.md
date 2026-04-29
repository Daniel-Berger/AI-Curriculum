# Phase 6: Applied AI Engineering - Complete Index

## Overview

Phase 6 bridges the gap between LLM knowledge (Phase 5) and production engineering (Phase 7) by focusing on the **customer-facing skills** needed for Applied AI Engineer and Solutions Engineer roles at companies like Anthropic, OpenAI, Google, and Cohere.

**Estimated Time:** 50 hours
**Prerequisites:** Phase 5 (LLMs & Generative AI)
**Dependencies:** `uv pip install -e ".[applied-ai]"`

---

## Quick Navigation

### Modules

| # | Module | Topic | Lesson | Exercises | Solutions |
|---|--------|-------|--------|-----------|-----------|
| 01 | Customer Integration Patterns | Debugging failures, multi-provider abstraction, retry/circuit breaker | lesson.md | exercises.py (15) | solutions.py |
| 02 | Cost & Performance Optimization | Token counting, cost modeling, caching, model selection, latency | lesson.md | exercises.py (15) | solutions.py |
| 03 | Evaluation & Quality Assurance | Custom eval harnesses, LLM-as-judge, regression testing, hallucination | lesson.md | exercises.py (15) | solutions.py |
| 04 | Conversation & Application Design | Multi-turn context, system prompts, guardrails, HITL, degradation | lesson.md | exercises.py (15) | solutions.py |
| 05 | Enterprise Security & Compliance | PII redaction, API key mgmt, audit logging, SOC2/HIPAA/GDPR | lesson.md | exercises.py (15) | solutions.py |
| 06 | Rapid Prototyping & Demos | Streamlit/Gradio, POC architecture, demo design, customer handoff | lesson.md | exercises.py (15) | solutions.py |
| 07 | Technical Communication | API tutorials, code samples, business-to-tech translation, migration | lesson.md | exercises.py (15) | solutions.py |
| 08 | Multi-Provider & Multi-Modal AI | Unified clients, model routing, vision+text, audio, failover | lesson.md | exercises.py (15) | solutions.py |
| 09 | Observability for LLM Apps | LLM logging, token tracking, quality monitoring, anomaly detection | lesson.md | exercises.py (15) | solutions.py |
| 10 | Customer Scenario Simulation | Full scenarios: triage, POC scoping, workshops, security reviews | lesson.md | exercises.py (15) | solutions.py |

### Projects

| Project | Description | Files |
|---------|-------------|-------|
| Customer POC Builder | Streamlit app with multi-provider support, PII redaction, cost tracking, eval harness | ~10 files |
| Debug & Optimize Challenge | Deliberately broken AI app + 5 customer tickets to diagnose and fix | ~16 files |

### Assessment

| File | Description |
|------|-------------|
| quiz.md | 30 questions across all 10 modules |

---

## Module Details

### 01 - Customer Integration Patterns
**Focus:** What solutions engineers do day-to-day and the technical patterns they use.

Key topics:
- Diagnosing customer integration failures (auth, rate limits, timeouts, model selection)
- Building multi-provider abstraction layers
- Retry with exponential backoff (tenacity) and circuit breaker patterns
- Middleware pipelines for logging, validation, cost tracking, PII detection
- Customer onboarding patterns

### 02 - Cost & Performance Optimization
**Focus:** Making AI affordable and fast for enterprise customers.

Key topics:
- Token pricing models across providers
- Cost modeling and budget enforcement
- Prompt caching (Anthropic, OpenAI)
- Model selection and routing strategies
- Latency profiling and optimization
- Batch processing and throughput management

### 03 - Evaluation & Quality Assurance
**Focus:** Ensuring AI outputs meet quality standards.

Key topics:
- Custom evaluation harness design
- LLM-as-judge evaluation
- Golden datasets and regression testing
- A/B testing frameworks for AI features
- Hallucination detection and citation verification
- Domain-specific custom metrics

### 04 - Conversation & Application Design
**Focus:** Designing robust AI-powered applications.

Key topics:
- Multi-turn context window management
- System prompt engineering and versioning
- Input/output guardrails and safety
- Graceful degradation during failures
- Human-in-the-loop escalation patterns
- Application architecture patterns (chat, Q&A, code gen)

### 05 - Enterprise Security & Compliance
**Focus:** Meeting enterprise security and regulatory requirements.

Key topics:
- PII detection and redaction (Presidio)
- API key management and rotation
- Audit logging for AI systems
- Content moderation pipelines
- SOC 2, HIPAA, GDPR compliance
- Prompt injection defense

### 06 - Rapid Prototyping & Demos
**Focus:** Building compelling demos and POCs quickly.

Key topics:
- Streamlit for AI prototypes
- Gradio for ML demos
- POC architecture and scoping
- Demo data preparation
- Live demo techniques
- Customer handoff best practices

### 07 - Technical Communication
**Focus:** Communicating effectively with technical and non-technical audiences.

Key topics:
- Writing effective API tutorials
- Code sample best practices
- Business-to-technical translation
- Migration guide creation
- Technical presentations
- Customer communication patterns

### 08 - Multi-Provider & Multi-Modal AI
**Focus:** Working across multiple AI providers and modalities.

Key topics:
- Unified clients with LiteLLM
- Cost/quality/latency-based model routing
- Vision + text multimodal processing
- Audio processing integration
- Failover and redundancy
- Provider benchmarking

### 09 - Observability for LLM Apps
**Focus:** Monitoring and debugging AI applications in production.

Key topics:
- LLM request/response logging
- Token usage tracking and budgets
- Quality monitoring over time
- Debugging multi-step chains
- Performance monitoring (p50/p95/p99)
- Anomaly detection and alerting

### 10 - Customer Scenario Simulation
**Focus:** Practicing real-world customer engagement scenarios.

Key topics:
- Customer triage and discovery
- POC scoping and success criteria
- Technical workshop design
- Security review preparation
- Production incident response
- Full scenario walkthroughs

---

## Project Details

### Project 1: Customer POC Builder
**Path:** `project-customer-poc/`

A complete Streamlit application demonstrating a customer POC with:
- Multi-provider LLM support (Anthropic, OpenAI, Google)
- PII detection and redaction
- Real-time cost tracking
- Evaluation harness integration
- Demo mode with synthetic data

### Project 2: Debug & Optimize Challenge
**Path:** `project-debug-optimize/`

A deliberately broken AI application with 5 customer support tickets:
- Identify bugs through customer ticket analysis
- Fix issues spanning security, performance, correctness
- Practice customer communication
- Scored with rubric for self-assessment

---

## File Structure

```
06-applied-ai-engineering/
├── INDEX.md                              # This file
├── COMPLETION_SUMMARY.md                 # File counts and verification
├── quiz.md                               # 30-question assessment
│
├── 01-customer-integration-patterns/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 02-cost-and-performance-optimization/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 03-evaluation-and-quality-assurance/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 04-conversation-and-application-design/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 05-enterprise-security-and-compliance/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 06-rapid-prototyping-and-demos/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 07-technical-communication/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 08-multi-provider-and-multi-modal/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 09-observability-for-llm-apps/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 10-customer-scenario-simulation/
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── project-customer-poc/
│   ├── README.md
│   ├── main.py
│   ├── config.py
│   ├── providers.py
│   ├── evaluator.py
│   ├── security.py
│   ├── cost_tracker.py
│   ├── demo_data.py
│   ├── templates/
│   │   └── system_prompts.py
│   └── tests/
│       └── test_project.py
│
└── project-debug-optimize/
    ├── README.md
    ├── scoring_rubric.md
    ├── broken_app/
    │   ├── main.py
    │   ├── config.py
    │   └── models.py
    ├── customer_tickets/
    │   ├── ticket_001_timeout.md
    │   ├── ticket_002_data_leak.md
    │   ├── ticket_003_cost_spike.md
    │   ├── ticket_004_race_condition.md
    │   └── ticket_005_quality_drop.md
    ├── solutions/
    │   ├── ticket_001_solution.py
    │   ├── ticket_002_solution.py
    │   ├── ticket_003_solution.py
    │   ├── ticket_004_solution.py
    │   └── ticket_005_solution.py
    └── tests/
        └── test_fixes.py
```

---

## How to Get Started

### Sequential Learning
```bash
cd 06-applied-ai-engineering

# Install dependencies
uv pip install -e ".[applied-ai]"

# Start with Module 01
# Read the lesson, attempt exercises, check solutions
cd 01-customer-integration-patterns
# Read lesson.md
# Work through exercises.py
# Check solutions.py

# Continue through modules 02-10...
```

### Project-Based Learning
```bash
# After completing modules, try the projects
cd project-customer-poc
# Read README.md, run the app, explore the code

cd ../project-debug-optimize
# Read the customer tickets, find and fix the bugs
```

---

## Dependencies

Install with:
```bash
uv pip install -e ".[applied-ai]"
```

Key packages:
- **streamlit** - Rapid web app prototyping
- **gradio** - ML demo interfaces
- **litellm** - Multi-provider LLM abstraction
- **instructor** - Structured LLM output
- **presidio-analyzer/anonymizer** - PII detection and redaction
- **tenacity** - Retry logic
- **logfire** - LLM observability

---

## Next Steps After Completion

After completing Phase 6, proceed to:
- **Phase 7: Production Engineering** — Deploy your AI applications
- **Phase 8: Interview & Capstone** — Prepare for SE interviews (includes new Module 05: Solutions Engineer Prep)

---

**Phase 6 Status:** ✅ COMPLETE
**Total Modules:** 10
**Total Exercises:** 150
**Total Projects:** 2
