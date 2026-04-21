# Capstone 2: Production RAG System

## Overview

A production-grade Retrieval-Augmented Generation (RAG) system that ingests documents
from multiple sources (PDF, web, markdown), chunks and embeds them into a vector store,
performs hybrid retrieval with re-ranking, generates answers via LLM, and evaluates
output quality using RAGAS metrics.

## Architecture

```
Documents (PDF/Web/MD)
        |
   DocumentIngester
        |
   ChunkingStrategy (fixed / semantic / recursive)
        |
   EmbeddingService --> Vector DB (ChromaDB / Qdrant)
        |
   HybridRetriever (dense + sparse + reranking)
        |
   RAGGenerator (LLM + retrieved context)
        |
   Response (streamed via FastAPI)
```

## Components

| Module | Description |
|---|---|
| `src/ingestion.py` | Ingest PDF, web pages, and markdown files |
| `src/chunking.py` | Multiple chunking strategies for optimal retrieval |
| `src/embeddings.py` | Embedding generation and management |
| `src/retriever.py` | Hybrid retrieval combining dense, sparse, and reranking |
| `src/generator.py` | LLM-based answer generation with retrieved context |
| `src/evaluation.py` | RAGAS evaluation (faithfulness, relevance, context quality) |
| `src/api.py` | FastAPI application with streaming responses |
| `streamlit_app.py` | Interactive Streamlit UI for the RAG system |

## Features

- **Multi-format Ingestion**: PDF, web scraping, and markdown parsing
- **Flexible Chunking**: Fixed-size, semantic, and recursive strategies
- **Hybrid Retrieval**: Combines dense vector search, sparse BM25, and cross-encoder reranking
- **Streaming Generation**: FastAPI with Server-Sent Events for real-time responses
- **RAGAS Evaluation**: Automated quality metrics for retrieval and generation
- **Interactive UI**: Streamlit-based chat interface with source citations
- **Monitoring**: Request logging, latency tracking, retrieval quality metrics
- **Docker Deployment**: Containerized app with vector database via docker-compose

## Usage

```bash
# Start the full stack
docker-compose up -d

# Ingest documents
curl -X POST http://localhost:8000/ingest \
  -F "files=@document.pdf"

# Query the system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is retrieval-augmented generation?"}'

# Run evaluation
python -m src.evaluation --dataset eval_dataset.json

# Launch Streamlit UI
streamlit run streamlit_app.py
```

## Project Structure

```
capstone-02-rag-system/
  README.md
  Dockerfile
  docker-compose.yml
  streamlit_app.py
  src/
    __init__.py
    ingestion.py
    chunking.py
    embeddings.py
    retriever.py
    generator.py
    evaluation.py
    api.py
  tests/
    __init__.py
    test_retriever.py
```

## Dependencies

- langchain / langchain-community
- openai
- chromadb or qdrant-client
- sentence-transformers
- fastapi / uvicorn
- ragas
- streamlit
- pypdf / beautifulsoup4
- rank_bm25
