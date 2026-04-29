"""Cost tracking for LLM API usage.

Provides approximate token counting, per-request cost calculation, session
cost aggregation, budget enforcement, and cost-report generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from config import ModelConfig


@dataclass
class RequestCost:
    """Cost record for a single LLM request."""

    timestamp: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    latency_ms: float


@dataclass
class CostReport:
    """Aggregated cost report for the current session."""

    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    budget_usd: float
    budget_remaining_usd: float
    budget_exceeded: bool
    requests: List[RequestCost] = field(default_factory=list)


class CostTracker:
    """Tracks token usage and costs across the lifetime of a session."""

    def __init__(self, budget_usd: float = 1.00) -> None:
        self.budget_usd = budget_usd
        self._requests: List[RequestCost] = []

    # -- token counting --------------------------------------------------------

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Return an approximate token count using a simple word-split heuristic.

        Real tokenizers (tiktoken, etc.) are more accurate, but this is good
        enough for cost estimation in a demo context.  Roughly 1 token per
        0.75 words for English text.
        """
        words = text.split()
        return max(1, int(len(words) / 0.75))

    # -- cost calculation ------------------------------------------------------

    def record_request(
        self,
        provider: str,
        model_config: ModelConfig,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float = 0.0,
    ) -> RequestCost:
        """Calculate and store the cost for a single request."""
        input_cost = input_tokens * model_config.cost_per_input_token
        output_cost = output_tokens * model_config.cost_per_output_token
        total = input_cost + output_cost

        record = RequestCost(
            timestamp=datetime.now(timezone.utc).isoformat(),
            provider=provider,
            model=model_config.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_usd=round(input_cost, 8),
            output_cost_usd=round(output_cost, 8),
            total_cost_usd=round(total, 8),
            latency_ms=latency_ms,
        )
        self._requests.append(record)
        return record

    # -- budget enforcement ----------------------------------------------------

    @property
    def total_cost(self) -> float:
        """Return the cumulative cost of all recorded requests."""
        return sum(r.total_cost_usd for r in self._requests)

    @property
    def budget_remaining(self) -> float:
        """Return how much of the session budget is left."""
        return max(0.0, self.budget_usd - self.total_cost)

    @property
    def budget_exceeded(self) -> bool:
        """Return True if cumulative cost has exceeded the budget."""
        return self.total_cost > self.budget_usd

    # -- reporting -------------------------------------------------------------

    def generate_report(self) -> CostReport:
        """Build an aggregated cost report for the session."""
        total_input = sum(r.input_tokens for r in self._requests)
        total_output = sum(r.output_tokens for r in self._requests)
        return CostReport(
            total_requests=len(self._requests),
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            total_cost_usd=round(self.total_cost, 8),
            budget_usd=self.budget_usd,
            budget_remaining_usd=round(self.budget_remaining, 8),
            budget_exceeded=self.budget_exceeded,
            requests=list(self._requests),
        )

    def reset(self) -> None:
        """Clear all recorded requests (start a new session)."""
        self._requests.clear()
