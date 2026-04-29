# Phase 6: Applied AI Engineering - Completion Summary

## Overview

Phase 6 adds **Applied AI Engineering** content focused on customer-facing skills needed for Solutions Engineer and Applied AI Engineer roles at companies like Anthropic, OpenAI, Google, and Cohere.

---

## File Inventory

### Module Content (30 files)

| Module | lesson.md | exercises.py | solutions.py |
|--------|:---------:|:------------:|:------------:|
| 01 - Customer Integration Patterns | Yes | Yes (15 exercises) | Yes |
| 02 - Cost & Performance Optimization | Yes | Yes (15 exercises) | Yes |
| 03 - Evaluation & Quality Assurance | Yes | Yes (15 exercises) | Yes |
| 04 - Conversation & Application Design | Yes | Yes (15 exercises) | Yes |
| 05 - Enterprise Security & Compliance | Yes | Yes (15 exercises) | Yes |
| 06 - Rapid Prototyping & Demos | Yes | Yes (15 exercises) | Yes |
| 07 - Technical Communication | Yes | Yes (15 exercises) | Yes |
| 08 - Multi-Provider & Multi-Modal AI | Yes | Yes (15 exercises) | Yes |
| 09 - Observability for LLM Apps | Yes | Yes (15 exercises) | Yes |
| 10 - Customer Scenario Simulation | Yes | Yes (15 exercises) | Yes |

### Project 1: Customer POC Builder (10 files)

| File | Purpose |
|------|---------|
| README.md | Project documentation |
| main.py | Streamlit application |
| config.py | Pydantic Settings configuration |
| providers.py | Multi-provider LLM client |
| evaluator.py | Evaluation harness |
| security.py | PII redaction pipeline |
| cost_tracker.py | Cost tracking system |
| demo_data.py | Demo scenarios and data |
| templates/system_prompts.py | System prompt templates |
| tests/test_project.py | Pytest test suite |

### Project 2: Debug & Optimize Challenge (16 files)

| File | Purpose |
|------|---------|
| README.md | Challenge overview |
| scoring_rubric.md | Scoring guide |
| broken_app/main.py | Deliberately buggy FastAPI app |
| broken_app/config.py | Config with security flaw |
| broken_app/models.py | Overly permissive Pydantic models |
| customer_tickets/ticket_001_timeout.md | Timeout customer ticket |
| customer_tickets/ticket_002_data_leak.md | Data leak customer ticket |
| customer_tickets/ticket_003_cost_spike.md | Cost spike customer ticket |
| customer_tickets/ticket_004_race_condition.md | Race condition customer ticket |
| customer_tickets/ticket_005_quality_drop.md | Quality degradation customer ticket |
| solutions/ticket_001_solution.py | Timeout fix |
| solutions/ticket_002_solution.py | Data leak fix |
| solutions/ticket_003_solution.py | Cost calculation fix |
| solutions/ticket_004_solution.py | Race condition fix |
| solutions/ticket_005_solution.py | Quality degradation fix |
| tests/test_fixes.py | Tests for all fixes |

### Support Files (3 files)

| File | Purpose |
|------|---------|
| INDEX.md | Module listing and navigation |
| COMPLETION_SUMMARY.md | This file |
| quiz.md | 30-question assessment |

---

## Totals

| Category | Count |
|----------|-------|
| Modules | 10 |
| Lesson files | 10 |
| Exercise files | 10 |
| Solution files | 10 |
| Total exercises | 150 |
| Project 1 files | 10 |
| Project 2 files | 16 |
| Support files | 3 |
| **Total files** | **59** |

---

## Key Topics Covered

- Customer integration patterns and debugging
- Cost optimization and performance profiling
- Evaluation harnesses and quality assurance
- Conversation design and application architecture
- Enterprise security, PII redaction, and compliance
- Rapid prototyping with Streamlit and Gradio
- Technical communication and documentation
- Multi-provider and multi-modal AI systems
- Observability and monitoring for LLM apps
- Customer scenario simulation and incident response

---

## Dependencies Added

```toml
[project.optional-dependencies]
applied-ai = [
    "python-learning[llm]",
    "streamlit>=1.35",
    "gradio>=4.30",
    "litellm>=1.40",
    "instructor>=1.3",
    "presidio-analyzer>=2.2",
    "presidio-anonymizer>=2.2",
    "tenacity>=8.3",
    "logfire>=0.50",
]
```

---

## Changes to Existing Files

| File | Change |
|------|--------|
| pyproject.toml | Added `applied-ai` dependency group, updated `production` to chain from it |
| README.md | Updated to 8 phases, ~350h, new phase table entry, progress tracker, file structure |
| 07-production-engineering/INDEX.md | Updated phase number references (6 → 7) |
| 08-interview-and-capstone/INDEX.md | Updated phase number references (7 → 8) |
| 08-interview-and-capstone/PHASE-8-COMPLETE.md | Renamed from PHASE-7, updated references |

---

**Phase 6 Status:** COMPLETE
