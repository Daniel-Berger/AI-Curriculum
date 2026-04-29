# Ticket #001 — Integration Timeouts on Large Prompts

**Priority:** High
**Customer:** Acme Financial Services (Enterprise plan)
**Reported by:** Jordan Lee, Senior Backend Engineer
**Date opened:** 2026-04-21

---

## Description

Our integration with your `/chat` endpoint is timing out after 30 seconds
whenever we send prompts longer than ~2,000 words. Shorter prompts work
fine, but our compliance workflow requires us to include the full text of
a regulatory document and ask the model to summarize it.

We have our HTTP client timeout set to 30 s, which has been fine for the
last three months. The problem started this week without any changes on
our end.

## Steps to Reproduce

1. POST to `/chat` with a `message` field containing ~3,000 words of text.
2. Wait. The request hangs for 40-60 seconds, then our client aborts.
3. Retry the same request — sometimes it works on the second try,
   sometimes it hangs again.

## Logs (from our side)

```
2026-04-21T14:32:07Z ERROR HttpClient: POST /chat timed out after 30000ms
2026-04-21T14:32:07Z WARN  RetryPolicy: attempt 1 of 3 failed (timeout)
2026-04-21T14:33:12Z ERROR HttpClient: POST /chat timed out after 30000ms
2026-04-21T14:33:12Z WARN  RetryPolicy: attempt 2 of 3 failed (timeout)
2026-04-21T14:34:15Z INFO  HttpClient: POST /chat responded 200 in 28412ms
```

## Impact

- 40% of our compliance-summary requests are failing.
- Our SLA with internal stakeholders requires < 10 s p95 latency.
- We are evaluating a fallback to a competitor API if this is not
  resolved within 48 hours.

## Expected Behavior

The endpoint should either stream partial results so our client can stay
alive, or return within a reasonable timeout with an appropriate error so
we can retry intelligently.
