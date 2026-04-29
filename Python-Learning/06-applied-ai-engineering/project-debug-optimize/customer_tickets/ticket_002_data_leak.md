# Ticket #002 — Customer PII Found in API Logs

**Priority:** CRITICAL / P0
**Customer:** MedTrust Health (HIPAA-regulated, Enterprise plan)
**Reported by:** Priya Sharma, Chief Information Security Officer
**Date opened:** 2026-04-22

---

## Description

During a routine audit of your publicly shared Datadog dashboard (which
we were given read access to during onboarding), our security team
discovered log entries containing full Social Security Numbers and dates
of birth belonging to our patients.

Specifically, DEBUG-level log lines in the `chat_service` logger include
the raw `message` field from our `/chat` requests. Our application sends
patient intake forms through your API for summarization, and those forms
include SSN, DOB, and insurance ID fields.

## Evidence

```
2026-04-20T09:14:33Z DEBUG chat_service: Incoming request from user=medtrust_prod
  message=Patient: Jane Doe, SSN: 321-54-9876, DOB: 1985-03-14, ...
```

## Compliance Concern

- This is a potential **HIPAA violation** for both MedTrust and your
  organization.
- We are required to file a breach notification within 60 days if PHI
  was exposed to unauthorized individuals.
- Our legal team needs a written incident report from you within
  **5 business days**.

## Timeline

| Date       | Event                                       |
|------------|---------------------------------------------|
| 2026-04-20 | PII first appeared in logs (earliest found) |
| 2026-04-22 | Discovered during security audit            |
| 2026-04-22 | This ticket filed                           |
| 2026-04-27 | Deadline for your incident report           |

## Expected Resolution

1. Immediately stop logging raw message content.
2. Purge all historical log entries that contain PII.
3. Implement a PII redaction layer before any data is logged or sent
   to third-party services.
4. Provide a written incident report and remediation plan.
