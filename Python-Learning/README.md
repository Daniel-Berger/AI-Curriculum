# Python & AI/ML Engineering Curriculum

### From Swift/iOS Developer to AI/ML Engineer

A structured, self-paced curriculum designed for experienced Swift/iOS developers transitioning into Python-based AI/ML engineering. This program covers everything from Python fundamentals through production-grade LLM applications, totaling approximately **300 hours** of hands-on learning across 7 phases.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Setup Instructions](#setup-instructions)
- [Phase Overview](#phase-overview)
- [Progress Tracker](#progress-tracker)
- [File Structure](#file-structure)
- [How to Use This Curriculum](#how-to-use-this-curriculum)

---

## Quick Start

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone the repository
git clone <repo-url> Python-Learning
cd Python-Learning

# 3. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[all]"

# 4. Start with Phase 1
cd 01-python-fundamentals/01-syntax-and-types
```

---

## Setup Instructions

### Prerequisites

- **Python 3.11+** (the curriculum targets Python 3.11 and above)
- **Git** for version control
- A code editor (VS Code with the Python extension is recommended)

### Installing uv

[uv](https://github.com/astral-sh/uv) is a fast Python package manager written in Rust. It replaces `pip`, `pip-tools`, and `virtualenv` with a single tool that is orders of magnitude faster.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

### Setting Up the Project

```bash
# Clone the repository
git clone <repo-url> Python-Learning
cd Python-Learning

# Create a virtual environment with uv
uv venv

# Activate the virtual environment
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

### Installing Dependencies

You can install **all** dependencies at once, or install phase-specific groups to keep your environment lean as you progress through the curriculum.

```bash
# Option A: Install everything at once (~300h curriculum)
uv pip install -e ".[all]"

# Option B: Install phase-by-phase (recommended)
uv pip install -e "."                  # Phase 1: Python Fundamentals (base deps)
uv pip install -e ".[data-science]"    # Phase 2: Data Science Foundations
uv pip install -e ".[ml]"             # Phase 3: Machine Learning
uv pip install -e ".[deep-learning]"  # Phase 4: Deep Learning
uv pip install -e ".[llm]"            # Phase 5: LLMs & Generative AI
uv pip install -e ".[production]"     # Phase 6: Production Engineering
```

> **Note:** Each phase's dependency group includes all previous phases, so installing `.[ml]` also installs `.[data-science]` and the base dependencies automatically.

### Verifying the Installation

```bash
# Confirm Python version
python --version

# Run the linter
ruff check .

# Run tests (Phase 1 & 2)
pytest
```

---

## Phase Overview

| Phase | Title | Modules | Est. Hours | Dependencies |
|:-----:|-------|:-------:|:----------:|:------------:|
| 1 | **Python Fundamentals** | 10 + project | 40h | Base |
| 2 | **Data Science Foundations** | 9 + project | 40h | `.[data-science]` |
| 3 | **Machine Learning** | 8 + project | 40h | `.[ml]` |
| 4 | **Deep Learning** | 7 + project | 40h | `.[deep-learning]` |
| 5 | **LLMs & Generative AI** | 12 + 2 projects | 60h | `.[llm]` |
| 6 | **Production Engineering** | 7 + project | 40h | `.[production]` |
| 7 | **Interview & Capstone** | 4 + capstone | 40h | `.[all]` |
| | | **Total** | **~300h** | |

---

## Progress Tracker

Use the checkboxes below to track your progress through each phase and module.

### Phase 1: Python Fundamentals (40h)

- [ ] 01 - Syntax and Types
- [ ] 02 - Control Flow
- [ ] 03 - Data Structures
- [ ] 04 - Functions and Closures
- [ ] 05 - OOP and Protocols
- [ ] 06 - Advanced Python
- [ ] 07 - Error Handling and I/O
- [ ] 08 - Modules, Packages, and Tooling
- [ ] 09 - Testing with pytest
- [ ] 10 - Async and Concurrency
- [ ] Phase 1 Project

### Phase 2: Data Science Foundations (40h)

- [ ] 01 - NumPy Fundamentals
- [ ] 02 - NumPy Advanced
- [ ] 03 - Pandas Basics
- [ ] 04 - Pandas Advanced
- [ ] 05 - Polars: Modern DataFrames
- [ ] 06 - Data Visualization
- [ ] 07 - EDA Workflow
- [ ] 08 - Feature Engineering
- [ ] 09 - Math for ML
- [ ] Phase 2 Project

### Phase 3: Machine Learning (40h)

- [ ] 01 - ML Fundamentals
- [ ] 02 - Regression
- [ ] 03 - Classification
- [ ] 04 - Tree Models and Ensembles
- [ ] 05 - Unsupervised Learning
- [ ] 06 - Model Evaluation
- [ ] 07 - Scikit-Learn Pipelines
- [ ] 08 - Experiment Tracking with MLflow
- [ ] Phase 3 Project

### Phase 4: Deep Learning (40h)

- [ ] 01 - Neural Networks from Scratch
- [ ] 02 - PyTorch Fundamentals
- [ ] 03 - Training Deep Networks
- [ ] 04 - CNNs and Transfer Learning
- [ ] 05 - Sequence Models
- [ ] 06 - Attention and Transformers
- [ ] 07 - Hugging Face Ecosystem
- [ ] Phase 4 Project

### Phase 5: LLMs & Generative AI (60h)

- [ ] 01 - LLM Architecture
- [ ] 02 - Tokenization
- [ ] 03 - API Mastery: Claude & OpenAI
- [ ] 04 - Prompt Engineering
- [ ] 05 - Structured Output with Pydantic
- [ ] 06 - Embeddings and Vector Databases
- [ ] 07 - RAG Fundamentals
- [ ] 08 - Advanced RAG
- [ ] 09 - LangChain Fundamentals
- [ ] 10 - LangGraph and Agents
- [ ] 11 - Tool Use and Function Calling
- [ ] 12 - Fine-Tuning LLMs
- [ ] Phase 5 Project: RAG System
- [ ] Phase 5 Project: AI Agent

### Phase 6: Production Engineering (40h)

- [ ] 01 - FastAPI Fundamentals
- [ ] 02 - FastAPI Advanced
- [ ] 03 - Docker for ML
- [ ] 04 - CI/CD and Testing
- [ ] 05 - Monitoring and Observability
- [ ] 06 - Evaluation and Safety
- [ ] 07 - Cloud Deployment
- [ ] Phase 6 Project

### Phase 7: Interview & Capstone (40h)

- [ ] 01 - System Design
- [ ] 02 - Coding Challenges
- [ ] 03 - ML Fundamentals Review
- [ ] 04 - Behavioral Prep
- [ ] Capstone Project

---

## File Structure

```
Python-Learning/
├── README.md                          # This file
├── pyproject.toml                     # Project config, dependencies, and tooling
│
├── 01-python-fundamentals/            # Phase 1: Core Python (40h)
│   ├── 01-syntax-and-types/
│   ├── 02-control-flow/
│   ├── 03-data-structures/
│   ├── 04-functions-and-closures/
│   ├── 05-oop-and-protocols/
│   ├── 06-advanced-python/
│   ├── 07-error-handling-and-io/
│   ├── 08-modules-packages-tooling/
│   ├── 09-testing-with-pytest/
│   ├── 10-async-and-concurrency/
│   └── project/
│
├── 02-data-science-foundations/       # Phase 2: Data Science (40h)
│   ├── 01-numpy-fundamentals/
│   ├── 02-numpy-advanced/
│   ├── 03-pandas-basics/
│   ├── 04-pandas-advanced/
│   ├── 05-polars-modern-dataframes/
│   ├── 06-data-visualization/
│   ├── 07-eda-workflow/
│   ├── 08-feature-engineering/
│   ├── 09-math-for-ml/
│   └── project/
│
├── 03-machine-learning/               # Phase 3: Classical ML (40h)
│   ├── 01-ml-fundamentals/
│   ├── 02-regression/
│   ├── 03-classification/
│   ├── 04-tree-models-and-ensembles/
│   ├── 05-unsupervised-learning/
│   ├── 06-model-evaluation/
│   ├── 07-sklearn-pipelines/
│   ├── 08-experiment-tracking-mlflow/
│   └── project/
│
├── 04-deep-learning/                  # Phase 4: Deep Learning (40h)
│   ├── 01-neural-networks-from-scratch/
│   ├── 02-pytorch-fundamentals/
│   ├── 03-training-deep-networks/
│   ├── 04-cnns-and-transfer-learning/
│   ├── 05-sequence-models/
│   ├── 06-attention-and-transformers/
│   ├── 07-huggingface-ecosystem/
│   └── project/
│
├── 05-llms-and-genai/                 # Phase 5: LLMs & GenAI (60h)
│   ├── 01-llm-architecture/
│   ├── 02-tokenization/
│   ├── 03-api-mastery-claude-openai/
│   ├── 04-prompt-engineering/
│   ├── 05-structured-output-pydantic/
│   ├── 06-embeddings-and-vector-dbs/
│   ├── 07-rag-fundamentals/
│   ├── 08-advanced-rag/
│   ├── 09-langchain-fundamentals/
│   ├── 10-langgraph-and-agents/
│   ├── 11-tool-use-and-function-calling/
│   ├── 12-fine-tuning-llms/
│   ├── project-rag-system/
│   └── project-ai-agent/
│
├── 06-production-engineering/         # Phase 6: Production (40h)
│   ├── 01-fastapi-fundamentals/
│   ├── 02-fastapi-advanced/
│   ├── 03-docker-for-ml/
│   ├── 04-ci-cd-and-testing/
│   ├── 05-monitoring-and-observability/
│   ├── 06-evaluation-and-safety/
│   ├── 07-cloud-deployment/
│   └── project/
│
└── 07-interview-and-capstone/         # Phase 7: Interview & Capstone (40h)
    ├── 01-system-design/
    ├── 02-coding-challenges/
    ├── 03-ml-fundamentals-review/
    ├── 04-behavioral-prep/
    └── capstone/
```

---

## How to Use This Curriculum

### Designed for Swift/iOS Developers

This curriculum is specifically structured for developers who already have strong programming foundations from Swift and iOS development. Many concepts will map directly to patterns you already know:

| Swift/iOS Concept | Python/ML Equivalent |
|---|---|
| Protocols | Abstract Base Classes, Protocols (typing) |
| Closures | Lambda functions, first-class functions |
| Optionals | `None` handling, `Optional` type hints |
| Generics | Type variables, Generic types |
| Combine / async-await | asyncio, async/await |
| SwiftUI state management | PyTorch tensors, reactive patterns |
| Xcode Instruments | Profiling with cProfile, memory_profiler |
| XCTest | pytest |

### Recommended Workflow

1. **Follow the phases in order.** Each phase builds on the previous one. The dependency groups in `pyproject.toml` reflect this progression.

2. **Work through each module sequentially.** Within a phase, modules are numbered to indicate the recommended order. Earlier modules introduce concepts used in later ones.

3. **Complete the projects.** Each phase concludes with a hands-on project that integrates everything you learned. These projects are where the real learning happens.

4. **Update the progress tracker.** Check off each module as you complete it to maintain momentum and visualize your progress.

5. **Use phase-specific installs.** Only install the dependencies you need for your current phase to keep your environment clean and fast:
   ```bash
   # When starting Phase 3, for example:
   uv pip install -e ".[ml]"
   ```

### Time Commitment

At approximately **300 hours** total, here are some example pacing schedules:

| Schedule | Hours/Week | Duration |
|----------|:----------:|:--------:|
| Intensive (full-time) | 40h | ~8 weeks |
| Aggressive (part-time) | 20h | ~15 weeks |
| Steady | 10h | ~30 weeks |
| Relaxed | 5h | ~60 weeks |

### Tips for Success

- **Code every exercise by hand.** Do not copy-paste. Muscle memory matters, especially when transitioning from a different language.
- **Draw parallels to Swift.** When learning a new concept, think about how you would solve the same problem in Swift. This accelerates understanding.
- **Use the REPL.** Python's interactive interpreter is one of its greatest strengths. Use `python` or `ipython` to experiment constantly.
- **Read error messages carefully.** Python's tracebacks are verbose and informative. Train yourself to read them bottom-up.
- **Build something real.** The capstone project in Phase 7 is your chance to combine everything into a portfolio-worthy project.

---

*Built with `uv` for fast, reproducible Python dependency management.*
