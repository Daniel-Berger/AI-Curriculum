"""Test suite for the Customer POC Builder project.

Covers PII detection/redaction, cost calculation, evaluation scoring,
provider factory, and config loading.  All tests run without API keys.
"""

from __future__ import annotations

import os
import sys

import pytest

# Ensure the project root is on sys.path so imports resolve.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import AppSettings, ModelConfig, PII_PATTERNS, PROVIDER_MODELS
from security import PIIRedactor, RedactionStrategy, PIIMatch
from cost_tracker import CostTracker
from evaluator import EvalCase, EvalRunner, exact_match, fuzzy_match, semantic_similarity_mock
from providers import (
    DemoProvider,
    Message,
    get_provider,
    available_providers,
)
from templates.system_prompts import SYSTEM_PROMPTS, get_prompt, DEFAULT_PROMPT_NAME
from demo_data import DEMO_CUSTOMERS, EVAL_TEST_CASES


# ===================================================================
# PII detection and redaction
# ===================================================================

class TestPIIDetection:
    """Tests for security.py PII scanning."""

    def test_detect_email(self) -> None:
        redactor = PIIRedactor()
        matches = redactor.scan("Contact us at support@example.com for help.")
        assert len(matches) == 1
        assert matches[0].pii_type == "email"
        assert matches[0].original == "support@example.com"

    def test_detect_phone(self) -> None:
        redactor = PIIRedactor()
        matches = redactor.scan("Call 555-123-4567 or (800) 555-0199.")
        phone_matches = [m for m in matches if m.pii_type == "phone"]
        assert len(phone_matches) >= 1

    def test_detect_ssn(self) -> None:
        redactor = PIIRedactor()
        matches = redactor.scan("SSN: 123-45-6789")
        ssn_matches = [m for m in matches if m.pii_type == "ssn"]
        assert len(ssn_matches) == 1
        assert ssn_matches[0].original == "123-45-6789"

    def test_detect_credit_card(self) -> None:
        redactor = PIIRedactor()
        matches = redactor.scan("Card: 4111-1111-1111-1111")
        cc_matches = [m for m in matches if m.pii_type == "credit_card"]
        assert len(cc_matches) == 1

    def test_no_pii(self) -> None:
        redactor = PIIRedactor()
        matches = redactor.scan("This sentence has no PII at all.")
        assert len(matches) == 0


class TestPIIRedaction:
    """Tests for security.py redaction pipeline."""

    def test_redact_replace_strategy(self) -> None:
        redactor = PIIRedactor(strategy=RedactionStrategy.REPLACE)
        result = redactor.redact("Email me at test@domain.com please.")
        assert "[EMAIL_REDACTED]" in result.redacted_text
        assert "test@domain.com" not in result.redacted_text
        assert result.matches_found == 1

    def test_redact_mask_strategy(self) -> None:
        redactor = PIIRedactor(strategy=RedactionStrategy.MASK)
        result = redactor.redact("SSN: 123-45-6789")
        assert "123-45-6789" not in result.redacted_text
        assert result.matches_found >= 1

    def test_redact_no_pii_returns_original(self) -> None:
        redactor = PIIRedactor()
        text = "Nothing sensitive here."
        result = redactor.redact(text)
        assert result.redacted_text == text
        assert result.matches_found == 0

    def test_audit_log_populated(self) -> None:
        redactor = PIIRedactor()
        redactor.redact("Email: a@b.com and SSN: 111-22-3333")
        log = redactor.get_audit_log()
        assert len(log) >= 2

    def test_clear_audit_log(self) -> None:
        redactor = PIIRedactor()
        redactor.redact("a@b.com")
        redactor.clear_audit_log()
        assert len(redactor.get_audit_log()) == 0

    def test_multiple_pii_in_one_text(self) -> None:
        redactor = PIIRedactor(strategy=RedactionStrategy.REPLACE)
        text = "Contact john@example.com or call 555-867-5309."
        result = redactor.redact(text)
        assert "[EMAIL_REDACTED]" in result.redacted_text
        assert "[PHONE_REDACTED]" in result.redacted_text
        assert result.matches_found >= 2


# ===================================================================
# Cost calculation
# ===================================================================

class TestCostTracker:
    """Tests for cost_tracker.py."""

    def _model(self) -> ModelConfig:
        return ModelConfig("test-model", "Test", 1e-6, 2e-6)

    def test_record_request_cost(self) -> None:
        tracker = CostTracker(budget_usd=1.0)
        record = tracker.record_request("test", self._model(), input_tokens=1000, output_tokens=500)
        assert record.input_cost_usd == pytest.approx(0.001, abs=1e-6)
        assert record.output_cost_usd == pytest.approx(0.001, abs=1e-6)
        assert record.total_cost_usd == pytest.approx(0.002, abs=1e-6)

    def test_total_cost_accumulates(self) -> None:
        tracker = CostTracker(budget_usd=1.0)
        tracker.record_request("a", self._model(), 100, 100)
        tracker.record_request("b", self._model(), 100, 100)
        assert tracker.total_cost > 0

    def test_budget_exceeded(self) -> None:
        tracker = CostTracker(budget_usd=0.0001)
        tracker.record_request("a", self._model(), 10000, 10000)
        assert tracker.budget_exceeded is True

    def test_budget_not_exceeded(self) -> None:
        tracker = CostTracker(budget_usd=100.0)
        tracker.record_request("a", self._model(), 10, 10)
        assert tracker.budget_exceeded is False

    def test_report_generation(self) -> None:
        tracker = CostTracker(budget_usd=5.0)
        tracker.record_request("p", self._model(), 50, 25)
        report = tracker.generate_report()
        assert report.total_requests == 1
        assert report.total_input_tokens == 50
        assert report.total_output_tokens == 25
        assert report.budget_usd == 5.0

    def test_reset_clears_requests(self) -> None:
        tracker = CostTracker()
        tracker.record_request("p", self._model(), 100, 100)
        tracker.reset()
        assert tracker.total_cost == 0.0
        assert tracker.generate_report().total_requests == 0

    def test_estimate_tokens(self) -> None:
        count = CostTracker.estimate_tokens("This is a short sentence.")
        assert count >= 1


# ===================================================================
# Evaluation scoring
# ===================================================================

class TestEvaluation:
    """Tests for evaluator.py scoring and runner."""

    def test_exact_match_identical(self) -> None:
        assert exact_match("hello", "hello") == 1.0

    def test_exact_match_case_insensitive(self) -> None:
        assert exact_match("Hello", "hello") == 1.0

    def test_exact_match_different(self) -> None:
        assert exact_match("hello", "world") == 0.0

    def test_fuzzy_match_identical(self) -> None:
        assert fuzzy_match("the cat sat", "the cat sat") == 1.0

    def test_fuzzy_match_partial_overlap(self) -> None:
        score = fuzzy_match("the cat sat on the mat", "the dog sat on the mat")
        assert 0.5 < score < 1.0

    def test_fuzzy_match_no_overlap(self) -> None:
        score = fuzzy_match("apple banana", "cherry dragonfruit")
        assert score == 0.0

    def test_semantic_similarity_identical(self) -> None:
        score = semantic_similarity_mock("hello world", "hello world")
        assert score == 1.0

    def test_semantic_similarity_partial(self) -> None:
        score = semantic_similarity_mock("the quick brown fox", "the slow brown fox")
        assert 0.3 < score < 1.0

    def test_eval_runner_scores_cases(self) -> None:
        cases = [
            EvalCase(name="t1", input_text="x", expected="hello", actual="hello"),
            EvalCase(name="t2", input_text="x", expected="hello", actual="goodbye"),
        ]
        runner = EvalRunner(scoring_method="exact_match", pass_threshold=0.5)
        results = runner.run(cases)
        assert results[0].passed is True
        assert results[1].passed is False

    def test_eval_runner_summary(self) -> None:
        cases = [
            EvalCase(name="t1", input_text="x", expected="a", actual="a", score=1.0, passed=True, scoring_method="exact_match"),
            EvalCase(name="t2", input_text="x", expected="a", actual="b", score=0.0, passed=False, scoring_method="exact_match"),
        ]
        summary = EvalRunner.summarize(cases)
        assert summary.total_cases == 2
        assert summary.passed == 1
        assert summary.failed == 1
        assert summary.pass_rate == 0.5

    def test_eval_runner_invalid_method(self) -> None:
        with pytest.raises(ValueError):
            EvalRunner(scoring_method="nonexistent")


# ===================================================================
# Provider factory
# ===================================================================

class TestProviders:
    """Tests for providers.py factory and demo provider."""

    def test_demo_provider_returns_result(self) -> None:
        provider = DemoProvider()
        model = ModelConfig("mock", "Mock", 0.0, 0.0)
        result = provider.complete(
            [Message(role="user", content="Hello")],
            model=model,
        )
        assert result.content
        assert result.provider == "demo"

    def test_get_provider_falls_back_to_demo(self) -> None:
        settings = AppSettings(ANTHROPIC_API_KEY="", OPENAI_API_KEY="", GOOGLE_API_KEY="")
        provider = get_provider("anthropic", settings)
        assert provider.provider_name == "demo"

    def test_available_providers_always_includes_demo(self) -> None:
        settings = AppSettings(ANTHROPIC_API_KEY="", OPENAI_API_KEY="", GOOGLE_API_KEY="")
        providers = available_providers(settings)
        assert "demo" in providers

    def test_available_providers_with_keys(self) -> None:
        settings = AppSettings(ANTHROPIC_API_KEY="sk-test", OPENAI_API_KEY="sk-test", GOOGLE_API_KEY="")
        providers = available_providers(settings)
        assert "anthropic" in providers
        assert "openai" in providers
        assert "google" not in providers

    def test_demo_provider_stream(self) -> None:
        provider = DemoProvider()
        model = ModelConfig("mock", "Mock", 0.0, 0.0)
        chunks = list(provider.stream([Message(role="user", content="Hi")], model=model))
        assert len(chunks) > 0
        full = "".join(chunks)
        assert len(full) > 0


# ===================================================================
# Config loading
# ===================================================================

class TestConfig:
    """Tests for config.py."""

    def test_default_settings(self) -> None:
        settings = AppSettings(ANTHROPIC_API_KEY="", OPENAI_API_KEY="", GOOGLE_API_KEY="")
        assert settings.app_title == "Customer POC Builder"
        assert settings.session_budget_usd > 0

    def test_provider_models_populated(self) -> None:
        assert "anthropic" in PROVIDER_MODELS
        assert "openai" in PROVIDER_MODELS
        assert "demo" in PROVIDER_MODELS
        for models in PROVIDER_MODELS.values():
            assert len(models) >= 1

    def test_pii_patterns_compile(self) -> None:
        for name, pattern in PII_PATTERNS.items():
            assert pattern.pattern  # pattern string is non-empty

    def test_system_prompts_available(self) -> None:
        assert len(SYSTEM_PROMPTS) >= 4
        assert DEFAULT_PROMPT_NAME in SYSTEM_PROMPTS

    def test_get_prompt_returns_default_for_unknown(self) -> None:
        prompt = get_prompt("this_does_not_exist")
        assert prompt == SYSTEM_PROMPTS[DEFAULT_PROMPT_NAME]

    def test_demo_data_loaded(self) -> None:
        assert len(DEMO_CUSTOMERS) >= 1
        assert len(EVAL_TEST_CASES) >= 1
