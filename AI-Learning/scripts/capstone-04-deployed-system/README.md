# Capstone 4: Flagship Deployed AI System

## Overview

The culminating capstone project: a production-ready AI system that integrates RAG,
intelligent agents, and a full deployment stack. Features FastAPI serving,
Docker containerization, CI/CD via GitHub Actions, comprehensive monitoring and
observability, automated evaluation pipelines, safety guardrails, and cost tracking.

This project demonstrates every skill from the learning path applied together in
a single, deployable system.

## Architecture

```
                         +--------------------+
                         |   Load Balancer    |
                         +--------+-----------+
                                  |
                         +--------v-----------+
                         |   FastAPI + CORS   |
                         |   + Rate Limiting  |
                         |   + Auth Middleware |
                         +--------+-----------+
                                  |
              +-------------------+-------------------+
              |                   |                   |
    +---------v------+  +---------v------+  +---------v------+
    |  RAG Pipeline  |  | Agent System   |  |  Eval Pipeline |
    |  - Retriever   |  | - Orchestrator |  |  - Evaluator   |
    |  - Generator   |  | - Tools        |  |  - Benchmarks  |
    +--------+-------+  +--------+-------+  +--------+-------+
              |                   |                   |
    +---------v------------------v-------------------v------+
    |                   Safety Layer                         |
    |   - Input guardrails  - Output guardrails             |
    |   - PII detection     - Content filtering              |
    +---------------------------+----------------------------+
                                |
    +---------------------------v----------------------------+
    |                  Monitoring Layer                       |
    |   - Prometheus metrics  - Cost tracking                |
    |   - Request logging     - Latency histograms           |
    +--------------------------------------------------------+
```

## Components

| Directory | Description |
|---|---|
| `src/rag/` | Retrieval-augmented generation pipeline |
| `src/agents/` | Agent orchestration and tool management |
| `src/api/` | FastAPI application, routes, and middleware |
| `src/evaluation/` | Automated evaluation and benchmarking |
| `src/safety/` | Input/output guardrails and content filtering |
| `src/monitoring/` | Metrics collection, logging, and cost tracking |

## Features

- **RAG Pipeline**: Hybrid retrieval + reranking + streaming generation
- **Agent Orchestration**: Multi-agent coordination with tool use
- **FastAPI Serving**: Async API with middleware for auth, rate limiting, CORS
- **Safety Guardrails**: PII detection, prompt injection defense, content filtering
- **Monitoring**: Prometheus metrics, structured logging, request tracing
- **Cost Tracking**: Per-request token usage and cost estimation
- **Evaluation**: Automated RAGAS + custom metrics with CI integration
- **CI/CD**: GitHub Actions for testing, linting, building, and deploying
- **Docker**: Multi-service deployment via docker-compose

## Usage

```bash
# Development
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Docker deployment
docker-compose up -d

# Run evaluation suite
python -m src.evaluation.evaluator --dataset eval_data.json

# Run CI locally
act push  # using nektos/act

# View metrics
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana
```

## Project Structure

```
capstone-04-deployed-system/
  README.md
  Dockerfile
  docker-compose.yml
  .github/
    workflows/
      ci.yml
  src/
    __init__.py
    rag/
      __init__.py
      retriever.py
      generator.py
    agents/
      __init__.py
      orchestrator.py
    api/
      __init__.py
      main.py
      middleware.py
    evaluation/
      __init__.py
      evaluator.py
    safety/
      __init__.py
      guardrails.py
    monitoring/
      __init__.py
      metrics.py
      cost_tracker.py
  tests/
    __init__.py
    test_api.py
```

## Dependencies

- fastapi / uvicorn
- langchain / langgraph
- openai
- chromadb
- sentence-transformers
- prometheus-client
- ragas
- pydantic
- pytest / httpx
- docker / docker-compose
