# Customer POC Builder

A Streamlit application demonstrating a **Customer Proof-of-Concept Builder** with
multi-provider LLM support, PII redaction, cost tracking, and an evaluation harness.

**Phase 6 -- Applied AI Engineering** project for Swift/iOS developers transitioning
to AI/ML engineering and solutions-engineer roles.

---

## Architecture

```
main.py                  Streamlit UI -- chat, sidebar controls, eval display
  |
  +-- config.py          Pydantic Settings -- env vars, model configs, costs
  +-- providers.py       Multi-provider LLM client (Anthropic / OpenAI / Google)
  +-- security.py        PII detection and redaction pipeline
  +-- cost_tracker.py    Token counting, per-request cost, budget enforcement
  +-- evaluator.py       Evaluation harness -- scoring, test suites, summaries
  +-- demo_data.py       Synthetic conversations, docs, eval cases, profiles
  +-- templates/
  |     system_prompts.py  System-prompt templates for different use cases
  +-- tests/
        test_project.py    pytest suite covering every module
```

## Features

- **Multi-provider chat** -- switch between Anthropic, OpenAI, and Google models
  from a sidebar dropdown.
- **Demo mode** -- runs entirely without API keys using mock providers that return
  realistic synthetic responses.
- **PII redaction** -- toggle automatic scanning and masking of emails, phone
  numbers, SSNs, and credit-card numbers before messages reach the model.
- **Cost tracking** -- approximate token counts, per-request costs, session
  totals, and configurable budget limits displayed in the sidebar.
- **Evaluation harness** -- run a built-in test suite that scores model responses
  with exact-match, fuzzy, and mock-semantic-similarity metrics.
- **System-prompt templates** -- preconfigured prompts for customer support,
  document Q&A, code assistance, and general chat.

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt` (created on first run or install
  manually):

```
streamlit>=1.30
pydantic>=2.0
pydantic-settings>=2.0
```

Optional (only needed when connecting to real providers):

```
anthropic
openai
google-generativeai
```

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install streamlit pydantic pydantic-settings

# 3. (Optional) Set API keys for live provider access
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AI..."

# 4. Run the app
streamlit run main.py
```

The app starts in **demo mode** automatically when no API keys are present.

## Running Tests

```bash
pytest tests/test_project.py -v
```

## How to Use

1. Launch the app with `streamlit run main.py`.
2. Use the **sidebar** to select a provider, a system-prompt template, and
   toggle PII redaction.
3. Type messages in the chat input. Responses come from the selected provider
   (or the mock provider in demo mode).
4. Monitor token usage and costs in the sidebar cost-tracker panel.
5. Click **Run Evaluation** in the sidebar to execute the built-in test suite
   and view scoring results.

## Project Goals

This project exercises skills that map directly to solutions-engineer
responsibilities:

| Skill area                  | Where it appears             |
|-----------------------------|------------------------------|
| Multi-provider integration  | `providers.py`               |
| Security / compliance       | `security.py`                |
| Cost awareness              | `cost_tracker.py`            |
| Evaluation and quality      | `evaluator.py`               |
| Rapid prototyping           | `main.py` + Streamlit        |
| Configuration management    | `config.py` + Pydantic       |
| Testing                     | `tests/test_project.py`      |

---

*Part of the AI/ML Engineering Curriculum -- Phase 6: Applied AI Engineering.*
