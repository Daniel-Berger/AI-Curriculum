# Phase 5 Project: Production RAG System

Build a production-quality Retrieval-Augmented Generation (RAG) system that can answer questions from a document collection. This project integrates concepts from all 12 modules of Phase 5.

---

## Learning Objectives

This project reinforces the following Phase 5 concepts:

| Module | Concept Applied |
|--------|----------------|
| 01 - LLM Architecture | Understanding decoder-only model behavior in generation |
| 02 - Tokenization | Chunk sizing relative to token limits |
| 03 - API Mastery | Abstracted LLM clients for Claude and OpenAI |
| 04 - Prompt Engineering | RAG-specific system and user prompt templates |
| 05 - Structured Output | Pydantic Settings for configuration management |
| 06 - Embeddings & Vector DBs | Embedding service and ChromaDB vector store |
| 07 - RAG Fundamentals | Core load -> chunk -> embed -> retrieve -> generate pipeline |
| 08 - Advanced RAG | Re-ranking, overlap chunking, metadata filtering |
| 09 - LangChain Fundamentals | Pipeline composition pattern (implemented from scratch) |
| 10 - LangGraph & Agents | Orchestration patterns applied to pipeline design |
| 11 - Tool Use | Mock/real LLM client swapping via ABC interface |
| 12 - Fine-Tuning | Understanding when RAG vs. fine-tuning is appropriate |

---

## Architecture

```
                        +------------------+
                        |   User Question  |
                        +--------+---------+
                                 |
                    +------------v------------+
                    |      RAGPipeline        |
                    |  (Orchestrator)         |
                    +---+--------+-------+---+
                        |        |       |
               +--------v--+  +-v----+  +v-----------+
               | VectorStore|  |Chunker|  |DocumentLoader|
               | (ChromaDB) |  +------+  +-------------+
               +-----+------+
                     |
            +--------v--------+
            | EmbeddingService |
            | (sentence-       |
            |  transformers    |
            |  or mock)        |
            +-----------------+
                     |
            +--------v--------+
            |   LLM Client     |
            | (Claude/OpenAI/  |
            |  Mock)           |
            +-----------------+
                     |
            +--------v--------+
            |   LLMResponse    |
            |  (answer +       |
            |   metadata)      |
            +-----------------+
```

### Data Flow

```
1. INGEST:  Files -> DocumentLoader -> [Documents]
                                          |
                                       Chunker -> [Chunks]
                                                     |
                                          EmbeddingService -> [Vectors]
                                                                  |
                                                           VectorStore (store)

2. QUERY:   Question -> EmbeddingService -> query vector
                                               |
                                        VectorStore (search) -> [RetrievalResults]
                                                                      |
                                                              format context
                                                                      |
                                                              LLM Client -> Answer
```

---

## Features

- **Document Loading**: Load `.txt` and `.md` files from a file or directory
- **Recursive Chunking**: Split documents with configurable size and overlap, using paragraph/sentence/word boundaries
- **Embedding**: Pluggable embedding service (mock for testing, sentence-transformers for production)
- **Vector Storage**: ChromaDB-backed storage with in-memory fallback
- **Retrieval**: Top-k similarity search with optional keyword-based re-ranking
- **Generation**: Abstracted LLM client supporting Claude, OpenAI, and mock providers
- **Streaming**: Token-by-token streaming support for all LLM clients
- **Configuration**: Pydantic Settings with environment variable loading

---

## Requirements

- Python 3.11+
- Dependencies (installed via the base `pyproject.toml` with `.[llm]`):
  - `pydantic` and `pydantic-settings` -- configuration management
  - `chromadb` -- vector database (optional; falls back to in-memory)
  - `sentence-transformers` -- embedding models (optional; mock available)
  - `anthropic` -- Claude API client (optional; mock available)
  - `openai` -- OpenAI API client (optional; mock available)

---

## Usage

```python
from config import RAGConfig
from llm_client import MockLLMClient
from rag_pipeline import RAGPipeline

# 1. Configure
config = RAGConfig(chunk_size=500, chunk_overlap=50, top_k=3)

# 2. Initialize with a mock LLM (no API key needed)
pipeline = RAGPipeline(config=config, llm_client=MockLLMClient())

# 3. Ingest documents
pipeline.ingest("./sample_docs")
print(f"Ingested {pipeline.chunk_count} chunks")

# 4. Query
response = pipeline.query("What is the Transformer architecture?")
print(response.content)

# 5. Query with sources (for citations)
response, sources = pipeline.query_with_sources("How does Python handle types?")
print(response.content)
for src in sources:
    print(f"  [{src.rank}] {src.chunk.doc_source} (score: {src.score:.2f})")
```

### Using a Real LLM

```python
from llm_client import ClaudeLLMClient

# Set ANTHROPIC_API_KEY environment variable first
client = ClaudeLLMClient()
pipeline = RAGPipeline(config=config, llm_client=client)
```

---

## Project Structure

```
project-rag-system/
├── README.md              # This file
├── config.py              # Pydantic Settings configuration
├── llm_client.py          # Abstracted LLM clients (Claude, OpenAI, Mock)
├── rag_pipeline.py        # Core pipeline: loader, chunker, store, retriever
├── test_rag.py            # pytest test suite (30+ tests)
└── sample_docs/           # Sample documents to RAG over
    ├── python_basics.txt
    ├── machine_learning_overview.txt
    └── llm_architectures.txt
```

---

## Running Tests

```bash
# Run all tests (no API keys required -- uses mocks)
pytest test_rag.py -v

# Run with coverage
pytest test_rag.py --cov=rag_pipeline --cov=llm_client --cov=config -v

# Run a specific test class
pytest test_rag.py::TestChunker -v

# Run a specific test
pytest test_rag.py::TestRAGPipeline::test_full_pipeline_end_to_end -v
```

---

## Swift/iOS Developer Notes

If you are coming from Swift, here are some key parallels in this project:

| Swift Pattern | Python Equivalent Used Here |
|---------------|----------------------------|
| `protocol LLMClient { }` | `BaseLLMClient` ABC with `@abstractmethod` |
| `struct Config: Codable` | `RAGConfig(BaseSettings)` with Pydantic |
| `AsyncStream<String>` | `Generator[str, None, None]` for streaming |
| `FileManager` + `Data(contentsOf:)` | `pathlib.Path` + `.read_text()` |
| `let config = Config()` (immutable) | `@dataclass(frozen=True)` |
| Keychain Services for API keys | Environment variables (`os.environ`) |
| Core Data / GRDB | ChromaDB vector store |
| XCTest mocks / protocols | MockLLMClient conforming to BaseLLMClient |
| Result<Success, Failure> | Exceptions + `try/except` |
| Combine pipeline operators | Method chaining in RAGPipeline |
