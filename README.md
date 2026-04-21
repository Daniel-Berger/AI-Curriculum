# AI-Curriculum

A comprehensive, hands-on curriculum for transitioning from iOS/Swift engineering to AI/ML engineering. Two complementary learning paths covering Python fundamentals through production-grade LLM systems, RAG pipelines, and AI agents.

---

## What's Inside

This repo contains two structured learning tracks totaling **~940 hours** of material:

### [`Python-Learning/`](Python-Learning/) — Self-Paced Track (~300h)

A 7-phase, exercise-driven curriculum with lessons, exercises, solutions, and capstone projects. Each module includes Swift-to-Python comparisons for developers coming from an iOS background.

| Phase | Topic | Hours |
|:-----:|-------|:-----:|
| 1 | Python Fundamentals | 40h |
| 2 | Data Science Foundations (NumPy, Pandas, Polars) | 40h |
| 3 | Machine Learning (scikit-learn, XGBoost, MLflow) | 40h |
| 4 | Deep Learning (PyTorch, CNNs, Transformers) | 40h |
| 5 | LLMs & GenAI (RAG, Agents, LangChain, Fine-Tuning) | 60h |
| 6 | Production Engineering (FastAPI, Docker, CI/CD, Cloud) | 40h |
| 7 | Interview Prep & Capstone | 40h |

### [`AI-Learning/`](AI-Learning/) — Intensive Bootcamp Track (~640h)

A 16-week, full-time bootcamp format with Jupyter notebooks, 4 capstone projects, interview prep resources, and a curated reading list.

**Capstone projects included:**
1. End-to-End ML Pipeline
2. Production RAG System
3. Production AI Agent
4. Flagship Deployed System (full-stack with Docker, CI/CD, monitoring)

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Git**
- A code editor (VS Code recommended)

### Quick Start

```bash
# Clone the repo
git clone git@github.com:Daniel-Berger/AI-Curriculum.git
cd AI-Curriculum

# --- Python-Learning track ---
cd Python-Learning
python3 -m venv .venv
source .venv/bin/activate
pip install -e "."               # Phase 1 deps only
# pip install -e ".[all]"       # or install everything at once

# --- AI-Learning track ---
cd ../AI-Learning
python3 -m venv .venv
source .venv/bin/activate
pip install -e "."
jupyter lab                      # launch notebooks
```

> **Tip:** You can also use [uv](https://github.com/astral-sh/uv) for faster dependency management — `uv venv && uv pip install -e ".[all]"`

---

## Repo Structure

```
AI-Curriculum/
├── Python-Learning/                 # Self-paced track (7 phases)
│   ├── 01-python-fundamentals/      #   Syntax, OOP, async, testing
│   ├── 02-data-science-foundations/  #   NumPy, Pandas, Polars, EDA
│   ├── 03-machine-learning/         #   Regression, classification, ensembles
│   ├── 04-deep-learning/            #   PyTorch, CNNs, attention, HuggingFace
│   ├── 05-llms-and-genai/           #   APIs, RAG, agents, fine-tuning
│   ├── 06-production-engineering/   #   FastAPI, Docker, CI/CD, monitoring
│   ├── 07-interview-and-capstone/   #   System design, coding, behavioral
│   └── pyproject.toml               #   Phased dependency groups
│
├── AI-Learning/                     # Bootcamp track (16 weeks)
│   ├── notebooks/                   #   Jupyter notebooks by module
│   ├── scripts/                     #   4 capstone projects
│   ├── resources/                   #   Cheatsheets, interview Qs, reading list
│   └── pyproject.toml
│
└── README.md                        # You are here
```

---

## How to Use This Repo

**Pick a track** (or use both):

- **Python-Learning** is best if you prefer reading markdown lessons, writing exercises in `.py` files, and working at your own pace. Each module has a `lesson.md`, `exercises.py`, `solutions.py`, and a `swift_comparison.md` bridging iOS concepts to Python equivalents.

- **AI-Learning** is best if you prefer Jupyter notebooks, want a more intensive bootcamp schedule, and want to build full capstone projects with Docker and CI/CD.

**Work through the phases in order** — each phase builds on the previous one. The dependency groups in `pyproject.toml` let you install only what you need for your current phase.

---

## Topics Covered

- **Python** — syntax, data structures, OOP, async/await, testing, packaging
- **Data Science** — NumPy, Pandas, Polars, Matplotlib, Seaborn, feature engineering
- **Machine Learning** — scikit-learn, XGBoost, LightGBM, model evaluation, MLflow
- **Deep Learning** — PyTorch, CNNs, RNNs, attention, transformers, HuggingFace
- **LLMs & GenAI** — Claude/OpenAI APIs, prompt engineering, embeddings, vector databases
- **RAG** — chunking strategies, retrieval methods, RAGAS evaluation, advanced RAG patterns
- **AI Agents** — ReAct, LangChain, LangGraph, tool use, multi-agent systems
- **Production** — FastAPI, Docker, CI/CD, monitoring, cloud deployment, guardrails
- **Interview Prep** — system design, ML fundamentals review, coding challenges, behavioral

---

## License

This project is for personal educational use.
