# Ticket #004 — Users Seeing Each Other's Conversations

**Priority:** CRITICAL / P0
**Customer:** LegalPad Pro (Enterprise plan, SOC 2 compliant)
**Reported by:** Aisha Nguyen, Head of Product
**Date opened:** 2026-04-24

---

## Description

Multiple users on our platform have reported seeing chat responses that
clearly belong to someone else's conversation. One attorney received a
response that referenced a completely different client's case details.

This is a **data isolation failure** and a potential breach of
attorney-client privilege. We need an immediate root cause analysis.

## Reproduction

- **Reproduction rate:** ~5% of requests during peak hours (200+ concurrent users).
- **Not reproducible** when traffic is low (< 20 concurrent users).
- We cannot reproduce in our staging environment (single-user testing).

## Impacted Users (sample)

| User ID         | Timestamp            | Issue                              |
|-----------------|----------------------|------------------------------------|
| legalpad_u_4821 | 2026-04-24T10:02:14Z | Received response with wrong case  |
| legalpad_u_1190 | 2026-04-24T10:02:15Z | Context from another user in reply |
| legalpad_u_7733 | 2026-04-24T10:05:44Z | System prompt changed mid-convo    |

## Observations

- The issue correlates with high concurrency. Our peak is ~250 requests
  per second between 9-11 AM ET.
- Two users who hit the endpoint within the same millisecond seem most
  likely to experience cross-contamination.
- Restarting the service temporarily fixes the issue (presumably clears
  some shared state).

## Expected Behavior

Each user's conversation MUST be fully isolated. No user should ever see
messages, context, or responses belonging to another user, regardless of
concurrency level.

## Urgency

Our General Counsel has been notified. If we cannot confirm a fix within
24 hours, we are contractually required to disable the integration and
notify affected clients.
