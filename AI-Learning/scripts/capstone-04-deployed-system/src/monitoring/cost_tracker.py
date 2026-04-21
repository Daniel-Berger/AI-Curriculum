"""
Cost Tracker Module
===================

Tracks per-request and aggregate costs for LLM API usage across the
deployed system. Supports multiple providers and models with configurable
pricing. Emits cost metrics for monitoring dashboards and alerts.

Features:
- Per-request cost estimation based on token usage
- Aggregate cost tracking (hourly, daily, monthly)
- Budget alerts and limits
- Cost breakdown by model, endpoint, and user/API key
- Historical cost reporting
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Pricing configuration (USD per 1K tokens)
# ---------------------------------------------------------------------------

DEFAULT_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-5-haiku": {"input": 0.0008, "output": 0.004},
    "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
    "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
}


@dataclass
class CostEntry:
    """A single cost tracking entry.

    Attributes
    ----------
    request_id : str
        Unique request identifier.
    model : str
        Model used.
    input_tokens : int
        Input tokens consumed.
    output_tokens : int
        Output tokens generated.
    input_cost_usd : float
        Cost for input tokens.
    output_cost_usd : float
        Cost for output tokens.
    total_cost_usd : float
        Total cost for this request.
    endpoint : str
        API endpoint that triggered this usage.
    api_key_id : str
        Masked API key identifier.
    timestamp : datetime
        When the cost was incurred.
    """

    request_id: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    endpoint: str = ""
    api_key_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CostSummary:
    """Aggregate cost summary.

    Attributes
    ----------
    total_cost_usd : float
        Total cost in the period.
    total_requests : int
        Number of requests.
    total_input_tokens : int
        Total input tokens.
    total_output_tokens : int
        Total output tokens.
    cost_by_model : dict
        Cost breakdown by model.
    cost_by_endpoint : dict
        Cost breakdown by endpoint.
    period_start : datetime
        Start of the summary period.
    period_end : datetime
        End of the summary period.
    """

    total_cost_usd: float = 0.0
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    cost_by_model: Dict[str, float] = field(default_factory=dict)
    cost_by_endpoint: Dict[str, float] = field(default_factory=dict)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class CostTracker:
    """Track and manage LLM API costs.

    Parameters
    ----------
    pricing : dict, optional
        Model pricing configuration. Uses DEFAULT_PRICING if not provided.
    daily_budget_usd : float, optional
        Daily budget limit. Alerts when exceeded.
    monthly_budget_usd : float, optional
        Monthly budget limit.

    Examples
    --------
    >>> tracker = CostTracker(daily_budget_usd=50.0)
    >>> entry = tracker.record_usage(
    ...     model="gpt-4o",
    ...     input_tokens=1000,
    ...     output_tokens=500,
    ...     request_id="req-123",
    ... )
    >>> print(f"Cost: ${entry.total_cost_usd:.4f}")
    """

    def __init__(
        self,
        pricing: Optional[Dict[str, Dict[str, float]]] = None,
        daily_budget_usd: Optional[float] = None,
        monthly_budget_usd: Optional[float] = None,
    ) -> None:
        self.pricing = pricing or DEFAULT_PRICING
        self.daily_budget_usd = daily_budget_usd
        self.monthly_budget_usd = monthly_budget_usd
        self._entries: List[CostEntry] = []

    def estimate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate the cost for a given token usage.

        Parameters
        ----------
        model : str
            Model identifier.
        input_tokens : int
            Number of input tokens.
        output_tokens : int
            Number of output tokens.

        Returns
        -------
        float
            Estimated cost in USD.

        Raises
        ------
        ValueError
            If the model is not in the pricing configuration.
        """
        if model not in self.pricing:
            raise ValueError(
                f"Unknown model '{model}'. Available: {list(self.pricing.keys())}"
            )
        rates = self.pricing[model]
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        return input_cost + output_cost

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_id: str = "",
        endpoint: str = "",
        api_key_id: str = "",
    ) -> CostEntry:
        """Record token usage and compute cost.

        Parameters
        ----------
        model : str
            Model used.
        input_tokens : int
            Input tokens consumed.
        output_tokens : int
            Output tokens generated.
        request_id : str
            Request identifier.
        endpoint : str
            API endpoint.
        api_key_id : str
            Masked API key.

        Returns
        -------
        CostEntry
            The recorded cost entry.
        """
        raise NotImplementedError

    def get_daily_summary(
        self, date: Optional[datetime] = None
    ) -> CostSummary:
        """Get cost summary for a specific day.

        Parameters
        ----------
        date : datetime, optional
            Day to summarize. Defaults to today.

        Returns
        -------
        CostSummary
            Daily cost summary.
        """
        raise NotImplementedError

    def get_monthly_summary(
        self, year: int, month: int
    ) -> CostSummary:
        """Get cost summary for a specific month.

        Parameters
        ----------
        year : int
            Year.
        month : int
            Month (1-12).

        Returns
        -------
        CostSummary
            Monthly cost summary.
        """
        raise NotImplementedError

    def check_budget(self) -> Dict[str, Any]:
        """Check current spending against budget limits.

        Returns
        -------
        dict
            Keys: 'daily_spent', 'daily_budget', 'daily_remaining',
            'monthly_spent', 'monthly_budget', 'monthly_remaining',
            'daily_exceeded', 'monthly_exceeded'.
        """
        raise NotImplementedError

    def export_entries(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Export cost entries as a list of dicts for reporting.

        Parameters
        ----------
        start_date : datetime, optional
            Filter entries after this date.
        end_date : datetime, optional
            Filter entries before this date.

        Returns
        -------
        list of dict
            Serialized cost entries.
        """
        raise NotImplementedError
