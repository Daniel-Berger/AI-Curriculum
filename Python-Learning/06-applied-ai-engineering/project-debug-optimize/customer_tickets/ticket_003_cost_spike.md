# Ticket #003 — Unexpected 10x Cost Increase

**Priority:** High
**Customer:** RetailEdge Inc. (Growth plan)
**Reported by:** Marcus Chen, VP of Engineering
**Date opened:** 2026-04-23

---

## Description

Our March invoice was $4,200. Our April invoice (so far) is showing
$41,500 — roughly 10x higher. Our usage patterns have not changed. We
send approximately the same number of requests per day (~8,000) with
similar prompt lengths.

When we query your `/usage/retailedge_prod` endpoint the per-request
costs look absurdly high. A simple 500-token request is showing a cost
of $8.00, which is orders of magnitude above the published pricing of
$0.01 / 1K input tokens and $0.03 / 1K output tokens.

## Usage Data (sample from /usage endpoint)

```json
{
  "user_id": "retailedge_prod",
  "total_records": 8012,
  "total_cost_usd": 41523.67,
  "records": [
    {
      "input_tokens": 350,
      "output_tokens": 150,
      "cost_usd": 8.00
    },
    {
      "input_tokens": 1200,
      "output_tokens": 400,
      "cost_usd": 24.00
    }
  ]
}
```

## Expected vs Actual

| Metric            | Expected        | Actual          |
|-------------------|-----------------|-----------------|
| Cost per request  | ~$0.005 - $0.02 | ~$5.00 - $24.00 |
| Monthly bill      | ~$4,000         | ~$41,500        |
| Multiplier        | 1x              | ~1000x          |

## Impact

- We have frozen all non-essential API usage until this is resolved.
- Our finance team is disputing the April invoice.
- If this is a billing bug on your end, we need a corrected invoice ASAP.

## Questions

1. Is there a known billing bug?
2. Did pricing change without notice?
3. Can you provide an audit trail of how cost_usd is calculated?
