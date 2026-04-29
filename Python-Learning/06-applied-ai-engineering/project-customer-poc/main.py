"""Customer POC Builder -- Streamlit application.

A multi-provider LLM chat interface with PII redaction, cost tracking,
evaluation, and demo mode.  Designed as a rapid-prototyping reference for
solutions engineers.

Run with:
    streamlit run main.py
"""

from __future__ import annotations

import streamlit as st

from config import AppSettings, PROVIDER_MODELS, ModelConfig
from providers import (
    Message,
    CompletionResult,
    get_provider,
    available_providers,
)
from security import PIIRedactor, RedactionStrategy
from cost_tracker import CostTracker
from evaluator import EvalRunner, EvalCase
from demo_data import (
    DEMO_CUSTOMERS,
    SAMPLE_CONVERSATIONS,
    EVAL_TEST_CASES,
)
from templates.system_prompts import SYSTEM_PROMPTS, DEFAULT_PROMPT_NAME, get_prompt


# ---------------------------------------------------------------------------
# Session-state initialisation
# ---------------------------------------------------------------------------

def _init_session_state() -> None:
    """Ensure all required session-state keys exist."""
    defaults = {
        "messages": [],
        "settings": AppSettings(),
        "cost_tracker": CostTracker(budget_usd=AppSettings().session_budget_usd),
        "redactor": PIIRedactor(strategy=RedactionStrategy.REPLACE),
        "pii_enabled": True,
        "selected_provider": "demo",
        "selected_model_idx": 0,
        "selected_prompt": DEFAULT_PROMPT_NAME,
        "eval_results": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _render_sidebar() -> None:
    """Render sidebar controls for provider, model, prompt, PII, and cost."""
    settings: AppSettings = st.session_state.settings

    st.sidebar.title("Controls")

    # -- Provider selection ---------------------------------------------------
    providers = available_providers(settings)
    provider_idx = providers.index(st.session_state.selected_provider) if st.session_state.selected_provider in providers else 0
    selected_provider = st.sidebar.selectbox(
        "Provider",
        providers,
        index=provider_idx,
        help="Choose an LLM provider. Demo mode requires no API key.",
    )
    st.session_state.selected_provider = selected_provider

    # -- Model selection ------------------------------------------------------
    models = PROVIDER_MODELS.get(selected_provider, PROVIDER_MODELS["demo"])
    model_names = [m.display_name for m in models]
    model_idx = st.sidebar.selectbox(
        "Model",
        range(len(model_names)),
        format_func=lambda i: model_names[i],
        index=0,
    )
    st.session_state.selected_model_idx = model_idx

    # -- System prompt --------------------------------------------------------
    prompt_name = st.sidebar.selectbox(
        "System Prompt",
        list(SYSTEM_PROMPTS.keys()),
        index=list(SYSTEM_PROMPTS.keys()).index(st.session_state.selected_prompt),
    )
    st.session_state.selected_prompt = prompt_name

    # -- PII redaction toggle -------------------------------------------------
    st.session_state.pii_enabled = st.sidebar.toggle(
        "PII Redaction",
        value=st.session_state.pii_enabled,
        help="Automatically redact emails, phones, SSNs, and credit card numbers.",
    )

    # -- Cost tracker ---------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("Cost Tracker")
    tracker: CostTracker = st.session_state.cost_tracker
    report = tracker.generate_report()
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Requests", report.total_requests)
    col2.metric("Tokens", report.total_input_tokens + report.total_output_tokens)
    st.sidebar.metric("Session Cost", f"${report.total_cost_usd:.6f}")
    st.sidebar.progress(
        min(1.0, report.total_cost_usd / max(report.budget_usd, 1e-9)),
        text=f"Budget: ${report.budget_remaining_usd:.4f} remaining",
    )
    if report.budget_exceeded:
        st.sidebar.error("Budget exceeded!")

    # -- Evaluation -----------------------------------------------------------
    st.sidebar.markdown("---")
    if st.sidebar.button("Run Evaluation"):
        _run_evaluation()

    # -- Demo data loader -----------------------------------------------------
    st.sidebar.markdown("---")
    if st.sidebar.button("Load Demo Conversation"):
        _load_demo_conversation()

    # -- Reset ----------------------------------------------------------------
    if st.sidebar.button("Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ---------------------------------------------------------------------------
# Chat logic
# ---------------------------------------------------------------------------

def _get_current_model() -> ModelConfig:
    """Return the ModelConfig for the currently selected provider and model."""
    provider = st.session_state.selected_provider
    models = PROVIDER_MODELS.get(provider, PROVIDER_MODELS["demo"])
    idx = min(st.session_state.selected_model_idx, len(models) - 1)
    return models[idx]


def _send_message(user_input: str) -> None:
    """Process user input through the pipeline and generate a response."""
    settings: AppSettings = st.session_state.settings
    tracker: CostTracker = st.session_state.cost_tracker
    redactor: PIIRedactor = st.session_state.redactor

    # Budget guard.
    if tracker.budget_exceeded:
        st.error("Session budget exceeded. Reset the session to continue.")
        return

    # Optional PII redaction on user input.
    display_input = user_input
    if st.session_state.pii_enabled:
        result = redactor.redact(user_input)
        if result.matches_found > 0:
            user_input = result.redacted_text
            st.info(f"Redacted {result.matches_found} PII occurrence(s) from your message.")

    # Add user message to history.
    st.session_state.messages.append({"role": "user", "content": user_input, "display": display_input})

    # Build message list for the provider.
    chat_messages = [Message(role=m["role"], content=m["content"]) for m in st.session_state.messages]

    # Get provider and model.
    provider = get_provider(st.session_state.selected_provider, settings)
    model = _get_current_model()
    system_prompt = get_prompt(st.session_state.selected_prompt)

    # Call the provider.
    completion: CompletionResult = provider.complete(
        messages=chat_messages,
        model=model,
        system_prompt=system_prompt,
    )

    # Record cost.
    tracker.record_request(
        provider=completion.provider,
        model_config=model,
        input_tokens=completion.input_tokens,
        output_tokens=completion.output_tokens,
        latency_ms=completion.latency_ms,
    )

    # Optional PII redaction on assistant output.
    assistant_content = completion.content
    if st.session_state.pii_enabled:
        result = redactor.redact(assistant_content)
        assistant_content = result.redacted_text

    # Add assistant message to history.
    st.session_state.messages.append({"role": "assistant", "content": assistant_content, "display": assistant_content})


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def _run_evaluation() -> None:
    """Run the built-in evaluation test suite and store results."""
    cases = [
        EvalCase(name=c.name, input_text=c.input_text, expected=c.expected, actual=c.actual)
        for c in EVAL_TEST_CASES
    ]
    runner = EvalRunner(scoring_method="fuzzy_match", pass_threshold=0.4)
    runner.run(cases)
    summary = EvalRunner.summarize(cases)
    st.session_state.eval_results = {"cases": cases, "summary": summary}


def _render_evaluation() -> None:
    """Display evaluation results if available."""
    eval_data = st.session_state.eval_results
    if eval_data is None:
        return

    st.markdown("---")
    st.subheader("Evaluation Results")
    summary = eval_data["summary"]
    cols = st.columns(4)
    cols[0].metric("Total", summary.total_cases)
    cols[1].metric("Passed", summary.passed)
    cols[2].metric("Failed", summary.failed)
    cols[3].metric("Mean Score", f"{summary.mean_score:.2f}")

    for case in eval_data["cases"]:
        icon = "PASS" if case.passed else "FAIL"
        with st.expander(f"[{icon}] {case.name} -- score {case.score:.2f}"):
            st.markdown(f"**Input:** {case.input_text}")
            st.markdown(f"**Expected:** {case.expected}")
            st.markdown(f"**Actual:** {case.actual}")
            st.markdown(f"**Method:** {case.scoring_method}")


# ---------------------------------------------------------------------------
# Demo data loader
# ---------------------------------------------------------------------------

def _load_demo_conversation() -> None:
    """Load a sample conversation into the chat history."""
    import random
    convo = random.choice(SAMPLE_CONVERSATIONS)
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"], "display": m["content"]}
        for m in convo
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for the Streamlit application."""
    _init_session_state()

    settings: AppSettings = st.session_state.settings
    st.set_page_config(page_title=settings.app_title, page_icon=settings.app_icon, layout="wide")
    st.title(f"{settings.app_icon} {settings.app_title}")

    # Show demo-mode banner when no API keys are configured.
    has_keys = any([settings.anthropic_api_key, settings.openai_api_key, settings.google_api_key])
    if not has_keys:
        st.info(
            "Running in **demo mode** (no API keys detected). "
            "Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY to use live providers."
        )

    _render_sidebar()

    # -- Chat history ---------------------------------------------------------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg.get("display", msg["content"]))

    # -- Chat input -----------------------------------------------------------
    user_input = st.chat_input("Type your message...")
    if user_input:
        _send_message(user_input)
        st.rerun()

    # -- Evaluation results ---------------------------------------------------
    _render_evaluation()


if __name__ == "__main__":
    main()
