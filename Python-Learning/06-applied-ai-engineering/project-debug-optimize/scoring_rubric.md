# Scoring Rubric — Debug & Optimize Challenge

Total possible: **85 points**

Score yourself honestly. In a real interview, a hiring manager would evaluate
your work against this rubric during a debrief.

---

## Per-Ticket Scoring (5 tickets x 17 points each = 85)

### 1. Root Cause Identification (5 points)

| Points | Criteria |
|--------|----------|
| 5      | Correctly identifies the exact line(s) of code and explains WHY the bug causes the customer-reported symptom. |
| 3      | Identifies the general area (e.g., "something wrong with cost calculation") but misses the specific mechanism. |
| 1      | Vaguely points at the right file but cannot articulate the root cause. |
| 0      | Wrong diagnosis or no attempt. |

### 2. Fix Quality (5 points)

| Points | Criteria |
|--------|----------|
| 5      | Fix is correct, minimal, production-ready, and handles edge cases. |
| 3      | Fix resolves the primary issue but has minor gaps (e.g., no edge-case handling, overly broad changes). |
| 1      | Fix partially works but introduces a new issue or is incomplete. |
| 0      | Fix is wrong or not attempted. |

### 3. Test Coverage (3 points)

| Points | Criteria |
|--------|----------|
| 3      | Tests cover the happy path, the failure mode, and at least one edge case. |
| 2      | Tests cover the happy path and the failure mode. |
| 1      | A single test exists but does not thoroughly validate the fix. |
| 0      | No tests. |

### 4. Customer Communication (2 points)

| Points | Criteria |
|--------|----------|
| 2      | Drafts a clear, empathetic, non-technical response that acknowledges the impact, explains what happened (without blame), and states the remediation timeline. |
| 1      | Response is technically accurate but too jargon-heavy or dismissive of the customer's concern. |
| 0      | No customer response drafted. |

### 5. Prevention Measures (2 points)

| Points | Criteria |
|--------|----------|
| 2      | Proposes at least two concrete prevention measures (e.g., monitoring alert, CI check, architectural change) that would catch this class of bug before it reaches production. |
| 1      | Proposes one reasonable prevention measure. |
| 0      | No prevention measures proposed. |

---

## Grading Scale

| Score   | Rating         | Interpretation |
|---------|----------------|----------------|
| 75 - 85 | Exceptional   | Senior Solutions Engineer level. Ready for customer-facing escalations. |
| 60 - 74 | Strong        | Solid debugging skills. Needs minor coaching on communication or prevention. |
| 45 - 59 | Developing    | Can find bugs but struggles with production-quality fixes or customer empathy. |
| 30 - 44 | Needs Work    | Misses root causes or writes incomplete fixes. Needs mentorship. |
| < 30    | Not Yet Ready | Revisit fundamentals before attempting production debugging. |

---

## Bonus Points (unscored, but noteworthy)

- **Speed:** Completed all 5 tickets in under 60 minutes.
- **Cross-ticket insight:** Noticed that tickets 003 and 005 are related
  (unbounded history drives up both cost and quality degradation).
- **Architectural recommendation:** Proposed replacing the in-memory store
  with a proper database or cache (Redis) to solve tickets 004 and 005
  simultaneously.
- **Runbook:** Created an on-call runbook or decision tree for triaging
  similar issues in the future.
