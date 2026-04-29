# Project 2: Debug & Optimize Challenge

## Overview

You have inherited a production AI chat application that is on fire. Five customer
tickets have landed in your queue, each describing a different failure mode. Your job
is to triage every ticket, find the root cause in the codebase, implement a fix, write
tests that prove the fix works, and draft a short customer-facing response.

This exercise mirrors the daily reality of an AI Solutions Engineer: customers rarely
hand you a stack trace and say "line 42 is wrong." They hand you symptoms, emotions,
and a deadline.

## How the Challenge Works

1. **Read all five tickets** in `customer_tickets/` before touching any code.
2. **Explore the broken app** in `broken_app/`. The application is a FastAPI service
   that wraps an LLM API. It compiles and runs, but it has five deliberate bugs.
3. **Map each ticket to a bug.** Some mappings are obvious; others require you to
   think about second-order effects.
4. **Fix each bug** and place your solution files in `solutions/`.
5. **Run the test suite** in `tests/test_fixes.py` to verify your fixes.
6. **Score yourself** using `scoring_rubric.md`.

## Rules

- You may read any file at any time.
- Do NOT look at `solutions/` until you have attempted your own fix.
- Time yourself. A strong candidate finishes all five tickets in under 90 minutes.
- You may use any reference material (docs, search) but not AI coding assistants
  (you are learning to BE one).

## Project Structure

```
project-debug-optimize/
  broken_app/
    main.py          # The buggy FastAPI application
    config.py        # Application configuration
    models.py        # Pydantic data models
  customer_tickets/
    ticket_001_timeout.md
    ticket_002_data_leak.md
    ticket_003_cost_spike.md
    ticket_004_race_condition.md
    ticket_005_quality_drop.md
  solutions/
    ticket_001_solution.py
    ticket_002_solution.py
    ticket_003_solution.py
    ticket_004_solution.py
    ticket_005_solution.py
  tests/
    test_fixes.py
  scoring_rubric.md
  README.md
```

## Scoring Summary

| Category                | Points |
|-------------------------|--------|
| Root cause identified   | 5 each |
| Fix is correct          | 5 each |
| Test coverage           | 3 each |
| Customer communication  | 2 each |
| Prevention / monitoring | 2 each |
| **Total**               | **85** |

See `scoring_rubric.md` for the full rubric.

## Prerequisites

```bash
pip install fastapi uvicorn pydantic openai tiktoken
```

## Running the Broken App

```bash
cd broken_app
uvicorn main:app --reload --port 8000
```

Then send a POST to `http://localhost:8000/chat` with a JSON body:

```json
{
  "user_id": "user_123",
  "message": "Hello, can you help me?"
}
```

## Learning Objectives

- Diagnose production issues from customer-reported symptoms.
- Read and reason about async Python code under concurrency.
- Apply security, cost, and reliability best practices for LLM applications.
- Communicate fixes clearly to non-technical stakeholders.
