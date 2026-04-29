# Ticket #005 — Significant Response Quality Degradation

**Priority:** Medium
**Customer:** EduSpark Learning (Growth plan)
**Reported by:** Tom Alvarez, Product Manager
**Date opened:** 2026-04-25

---

## Description

Response quality from the `/chat` endpoint has degraded noticeably over
the past week. Our tutoring application relies on multi-turn conversations
that build on previous context. Lately, the model seems to "forget"
earlier parts of the conversation and gives generic or contradictory
answers.

## Before / After Examples

**Before (April 15, turn 12 of a conversation):**
> Student: "So how does the quadratic formula relate to what we discussed
> about completing the square?"
>
> Model: "Great question! In turn 4 we walked through completing the
> square for x^2 + 6x + 5. The quadratic formula is actually derived BY
> completing the square on the general form ax^2 + bx + c = 0..."

**After (April 25, turn 12 of a conversation):**
> Student: "So how does the quadratic formula relate to what we discussed
> about completing the square?"
>
> Model: "The quadratic formula is x = (-b +/- sqrt(b^2 - 4ac)) / 2a.
> It is used to solve quadratic equations. Would you like me to explain
> further?"

## Quality Metrics (internal, measured by our eval pipeline)

| Metric                  | Week of Apr 14 | Week of Apr 21 |
|-------------------------|----------------|----------------|
| Context recall score    | 0.91           | 0.38           |
| Answer relevance score  | 0.88           | 0.55           |
| Student satisfaction    | 4.6 / 5        | 2.9 / 5        |

## Observations

- Quality is fine for short conversations (1-3 turns).
- Degradation starts around turn 8-10 and gets worse each turn.
- Our average conversation length has increased from 8 turns to 14 turns
  over the past month due to a new "deep dive" feature.
- We have not changed our prompts or integration code.

## Expected Behavior

The model should maintain awareness of the full conversation history for
at least 20 turns and produce contextually grounded responses throughout.
