# AI/ML Engineering Bootcamp

**iOS Engineer → AI Engineer** | 16 Weeks | ~640 Hours

A structured, full-time bootcamp designed for a senior iOS/Swift engineer transitioning to AI engineering. Covers Python foundations through production LLM systems, optimized for the 2026 AI engineer job market.

**Target Role:** AI Engineer ($145K-$200K+) | Forward Deployment Engineer ($238K-$550K+)

---

## Quick Start

```bash
# Create virtual environment (Python 3.11+ required; 3.13 available on this system)
python3.13 -m venv .venv
source .venv/bin/activate

# Install Phase 1 dependencies
pip install -e .

# Install all dependencies (when ready)
pip install -e ".[all]"

# Launch Jupyter
jupyter lab
```

---

## Progress Tracker

### Phase 1: Foundations (Weeks 1-5) — 25% of interview questions

#### Module 1: Python Foundations for Swift Engineers — Week 1
- [ ] 1.1 Python Syntax & Control Flow (Swift comparisons)
- [ ] 1.2 Data Structures (list, dict, set, tuple vs Swift equivalents)
- [ ] 1.3 Object-Oriented Python (protocols → ABCs, structs → dataclasses)
- [ ] 1.4 Advanced Python (decorators, generators, context managers)
- [ ] 1.5 File I/O & Error Handling
- [ ] 1.6 Python Ecosystem (venvs, pip/uv, testing, linting)
- [ ] 1.P Project: CLI Data Processing Tool

#### Module 2: Math & Numerical Computing — Week 2
- [ ] 2.1 NumPy Arrays, Broadcasting & Vectorization
- [ ] 2.2 Linear Algebra Essentials (vectors, matrices, SVD)
- [ ] 2.3 Calculus for ML (gradients, chain rule, optimization)
- [ ] 2.4 Probability & Statistics (distributions, Bayes, hypothesis testing)
- [ ] 2.5 Pandas (DataFrames, groupby, merge, missing data)
- [ ] 2.P Project: Linear Regression from Scratch & Gradient Descent Visualizer

#### Module 3: Data Visualization & EDA — Week 3 (first half)
- [ ] 3.1 Matplotlib & Seaborn Deep Dive
- [ ] 3.2 Exploratory Data Analysis Workflow
- [ ] 3.3 Feature Engineering (encoding, scaling, domain features)
- [ ] 3.P Project: Full EDA Report on Kaggle Dataset

#### Module 4: Classical Machine Learning — Weeks 3-5
- [ ] 4.1 Regression (Linear, Ridge, Lasso, ElasticNet)
- [ ] 4.2 Classification (Logistic Regression, SVM, KNN, Naive Bayes)
- [ ] 4.3 Tree-Based Models (Decision Trees, Random Forest, XGBoost, LightGBM)
- [ ] 4.4 Unsupervised Learning (K-Means, DBSCAN, PCA, t-SNE)
- [ ] 4.5 Model Evaluation & Hyperparameter Tuning
- [ ] 4.6 Sklearn Pipelines & Production Patterns
- [ ] **CAPSTONE 1: End-to-End ML Pipeline** (`scripts/capstone-01-ml-pipeline/`)

### Phase 2: Deep Learning & NLP (Weeks 6-8)

#### Module 5: Deep Learning Foundations — Weeks 6-7
- [ ] 5.1 Neural Networks from Scratch (forward/backward pass)
- [ ] 5.2 PyTorch Fundamentals (tensors, autograd, nn.Module)
- [ ] 5.3 Training Deep Networks (optimizers, scheduling, regularization)
- [ ] 5.4 CNNs (convolutions, architectures, transfer learning)
- [ ] 5.5 Sequence Models (RNNs, LSTMs, attention preview)
- [ ] 5.P Project: MNIST from Scratch + Transfer Learning

#### Module 6: NLP & Transformers — Week 8
- [ ] 6.1 Text Preprocessing & Word Embeddings (Word2Vec, GloVe)
- [ ] 6.2 Attention Mechanism (implement from scratch)
- [ ] 6.3 Transformer Architecture Deep Dive
- [ ] 6.4 Hugging Face Ecosystem (Transformers, Datasets, Tokenizers)
- [ ] 6.5 BERT vs GPT Family & Scaling Laws
- [ ] 6.P Project: Attention from Scratch + HuggingFace Text Classification

### Phase 3: LLMs, RAG & Agents (Weeks 9-13) — 75% of interview questions

#### Module 7: LLM Fundamentals & APIs — Week 9
- [ ] 7.1 LLM Architecture (RLHF, DPO, Constitutional AI)
- [ ] 7.2 Tokenization (BPE, SentencePiece, token economics)
- [ ] 7.3 Inference Parameters (temperature, top-p/k, streaming, KV cache)
- [ ] 7.4 Claude/Anthropic API Mastery
- [ ] 7.5 OpenAI API & Multi-Provider Patterns
- [ ] 7.P Project: Multi-Turn Chatbot with Tool Use + Cost Analyzer

#### Module 8: Prompt Engineering for Production — Week 10 (first half)
- [ ] 8.1 Design Principles (clarity, specificity, instruction hierarchy)
- [ ] 8.2 Advanced Techniques (CoT, ToT, self-consistency, few-shot)
- [ ] 8.3 Structured Output (JSON mode, Pydantic validation)
- [ ] 8.4 Prompt Testing & Evaluation
- [ ] 8.P Project: Prompt Evaluation Framework

#### Module 9: RAG Architecture — Weeks 10-12 *(highest interview weight)*
- [ ] 9.1 Embeddings & Similarity (models, metrics, visualization)
- [ ] 9.2 Vector Databases (Pinecone, Chroma, FAISS, Weaviate, Qdrant)
- [ ] 9.3 Chunking Strategies (fixed, semantic, recursive, document-aware)
- [ ] 9.4 Retrieval Methods (dense, sparse/BM25, hybrid, re-ranking)
- [ ] 9.5 RAG Evaluation (RAGAS framework)
- [ ] 9.6 Advanced RAG (multi-step, HyDE, self-RAG, corrective RAG, GraphRAG)
- [ ] **CAPSTONE 2: Production RAG System** (`scripts/capstone-02-rag-system/`)

#### Module 10: AI Agents & Tool Use — Weeks 12-13
- [ ] 10.1 Agent Architectures (ReAct, Plan-and-Execute, Reflexion)
- [ ] 10.2 LangChain Fundamentals (chains, memory, retrievers)
- [ ] 10.3 LangGraph (state machines, conditional edges, HITL)
- [ ] 10.4 Tool Use & Function Calling (Claude + OpenAI)
- [ ] 10.5 Multi-Agent Systems & MCP
- [ ] **CAPSTONE 3: Production AI Agent** (`scripts/capstone-03-ai-agent/`)

### Phase 4: Production & Interview Prep (Weeks 14-16)

#### Module 11: Fine-Tuning LLMs — Week 14 (first half)
- [ ] 11.1 When to Fine-Tune vs RAG vs Prompt Engineering
- [ ] 11.2 LoRA, QLoRA & PEFT
- [ ] 11.3 Dataset Preparation & Training
- [ ] 11.4 Deployment (quantization, vLLM, model merging)
- [ ] 11.P Project: Fine-Tune 7B Model with QLoRA

#### Module 12: MLOps & Deployment — Weeks 14-15
- [ ] 12.1 Docker for ML (multi-stage builds, GPU, compose)
- [ ] 12.2 FastAPI (async, streaming, validation, middleware)
- [ ] 12.3 CI/CD for ML (GitHub Actions, model validation gates)
- [ ] 12.4 Monitoring & Observability (LLM metrics, drift, cost tracking)
- [ ] 12.5 Cloud Deployment (AWS SageMaker, GCP Vertex AI)

#### Module 13: Evaluation & Safety — Week 15
- [ ] 13.1 LLM Evaluation Frameworks (automated + human evals)
- [ ] 13.2 Red-Teaming & Adversarial Testing
- [ ] 13.3 Guardrails (input/output validation, PII detection)
- [ ] 13.4 Responsible AI (bias, fairness, transparency)
- [ ] **CAPSTONE 4: Flagship Deployed System** (`scripts/capstone-04-deployed-system/`)

#### Module 14: Interview Prep — Week 16
- [ ] 14.1 System Design Practice (RAG + Agent problems)
- [ ] 14.2 ML Fundamentals Speed Review
- [ ] 14.3 Coding Challenges (Python data manipulation, API integration)
- [ ] 14.4 Behavioral Prep (STAR format, 5 stories)
- [ ] 14.5 Job Search Strategy (resume, GitHub, LinkedIn, networking)

---

## Certification Track (Parallel)
- [ ] Google Professional ML Engineer (PMLE) — Weeks 10-16, 5-7 hrs/week
- [ ] AWS ML Specialty (optional) — if targeting AWS-heavy companies

---

## Project Structure

```
AI-Learning/
├── pyproject.toml                        # Dependencies (phased)
├── README.md                             # This file (progress tracker)
├── notebooks/
│   ├── module-01-python-foundations/      # Week 1
│   ├── module-02-math-and-numerical/     # Week 2
│   ├── module-03-data-viz-and-eda/       # Week 3a
│   ├── module-04-classical-ml/           # Weeks 3b-5
│   ├── module-05-deep-learning/          # Weeks 6-7
│   ├── module-06-nlp-and-transformers/   # Week 8
│   ├── module-07-llm-fundamentals/       # Week 9
│   ├── module-08-prompt-engineering/     # Week 10a
│   ├── module-09-rag-architecture/       # Weeks 10b-12
│   ├── module-10-agents-and-tool-use/    # Weeks 12-13
│   ├── module-11-fine-tuning/            # Week 14a
│   ├── module-12-mlops-and-deployment/   # Weeks 14b-15a
│   ├── module-13-evaluation-and-safety/  # Week 15b
│   └── module-14-interview-prep/         # Week 16
├── scripts/
│   ├── utils/
│   ├── capstone-01-ml-pipeline/          # Week 5
│   ├── capstone-02-rag-system/           # Week 12
│   ├── capstone-03-ai-agent/             # Week 13
│   └── capstone-04-deployed-system/      # Week 15
├── resources/
│   ├── cheatsheets/
│   ├── interview-questions/
│   └── reading-list.md
└── data/
```

---

## Key Resources

- [Anthropic API Docs](https://docs.anthropic.com)
- [Andrew Ng ML Specialization](https://www.coursera.org/specializations/machine-learning-introduction) (free)
- [Fast.ai](https://www.fast.ai/)
- [HuggingFace NLP Course](https://huggingface.co/learn/nlp-course)
- [3Blue1Brown Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra)
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [LangChain Docs](https://python.langchain.com/)
- [RAGAS Docs](https://docs.ragas.io/)

See [`resources/reading-list.md`](resources/reading-list.md) for the complete curated reading list.
