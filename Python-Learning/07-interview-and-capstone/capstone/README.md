# RAG Chat Application Capstone

A production-ready Retrieval-Augmented Generation (RAG) chat application built with FastAPI, LangChain, and ChromaDB. This capstone demonstrates end-to-end ML system design, from data ingestion to serving predictions.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                  (REST API Endpoints)                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼──────┐      ┌──────▼──────┐
   │ Chat      │      │  Document   │
   │ Endpoint  │      │  Management │
   └────┬──────┘      └──────┬──────┘
        │                    │
   ┌────▼────────────────────▼──────────┐
   │      FastAPI Application Layer     │
   │  - Request validation (Pydantic)   │
   │  - Error handling                  │
   │  - Authentication                  │
   └────┬────────────────────────────────┘
        │
   ┌────▼──────────────────────────────┐
   │    RAG Service Layer               │
   │  ┌──────────────────────────────┐ │
   │  │ RAG Service                  │ │
   │  │ - Load documents             │ │
   │  │ - Chunk text                 │ │
   │  │ - Embed chunks               │ │
   │  │ - Retrieve relevant context  │ │
   │  │ - Generate response          │ │
   │  └──────────────────────────────┘ │
   │                                    │
   │  ┌──────────────────────────────┐ │
   │  │ Agent Service                │ │
   │  │ - LangGraph orchestration    │ │
   │  │ - Tool selection             │ │
   │  │ - Action execution           │ │
   │  └──────────────────────────────┘ │
   └────┬──────────────────────────────┘
        │
   ┌────▼────────────────────────────┐
   │    LLM Client Layer              │
   │  - Claude API                    │
   │  - OpenAI Fallback               │
   │  - Streaming support             │
   └────┬────────────────────────────┘
        │
   ┌────▼────────────────────────────┐
   │  External Services               │
   │  ┌──────────┐  ┌──────────┐    │
   │  │  Claude  │  │ ChromaDB │    │
   │  │   API    │  │          │    │
   │  └──────────┘  └──────────┘    │
   │  ┌──────────┐  ┌──────────┐    │
   │  │ Embedder │  │ OpenAI   │    │
   │  │(Sentence │  │  Fallback│    │
   │  │Transformer)└──────────┘    │
   └─────────────────────────────────┘
```

---

## Key Features

### 1. Retrieval-Augmented Generation (RAG)
- Upload documents (TXT, PDF)
- Automatic chunking and embedding
- Semantic search for relevant context
- LLM-generated answers grounded in documents

### 2. Multi-turn Chat
- Streaming responses for low latency
- Conversation history tracking
- Context window management

### 3. Document Management
- Upload new documents
- List available documents
- Query-specific document retrieval

### 4. LangGraph Agent
- Tool selection (retrieval, calculator, web search mock)
- Routing between tools
- Fallback handling

### 5. Production Ready
- Pydantic input validation
- Comprehensive error handling
- Health check and metrics endpoints
- Docker containerization
- Comprehensive test suite

---

## Tech Stack

- **Framework**: FastAPI (async, modern Python web)
- **LLM Orchestration**: LangChain + LangGraph (agent framework)
- **Vector DB**: ChromaDB (local or cloud, persistent)
- **Embeddings**: Sentence-Transformers (open-source)
- **LLM**: Anthropic Claude (primary), OpenAI (fallback)
- **Testing**: pytest with mocks
- **Containerization**: Docker + Docker Compose

---

## Installation

### Local Development

```bash
# Clone repository
git clone <repo>
cd capstone

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"  # optional, for fallback

# Run application
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Application available at http://localhost:8000
# ChromaDB available at http://localhost:8001
```

---

## API Endpoints

### Chat

**POST** `/chat`
- Stream chat response
- Request: `ChatRequest` (message, chat_id, temperature)
- Response: `ChatResponse` (message, sources, tokens)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?", "chat_id": "user123"}'
```

### Document Management

**POST** `/documents/upload`
- Upload document for indexing
- Request: `DocumentUpload` (name, content)
- Response: Document metadata

**GET** `/documents`
- List all indexed documents

**DELETE** `/documents/{doc_id}`
- Remove document from index

### Health & Metrics

**GET** `/health`
- Health check, returns status

**GET** `/metrics`
- System metrics (tokens used, response times, errors)

---

## Configuration

`app/config.py` uses Pydantic Settings for environment-based configuration:

```python
ANTHROPIC_API_KEY: str
OPENAI_API_KEY: str = ""
CHROMA_HOST: str = "localhost"
CHROMA_PORT: int = 8000
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 100
TOP_K_RETRIEVAL: int = 3
```

---

## Project Structure

```
capstone/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # App + ChromaDB services
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app, endpoints
│   ├── models.py             # Pydantic models
│   ├── config.py             # Configuration
│   ├── rag_service.py        # RAG pipeline
│   ├── agent_service.py      # LangGraph agent
│   └── llm_client.py         # LLM abstraction
└── tests/
    ├── __init__.py
    ├── test_app.py           # Integration tests
    ├── test_rag_service.py    # RAG unit tests
    ├── test_models.py         # Pydantic validation
    └── fixtures.py            # Shared test fixtures
```

---

## Data Flow

### Chat Request

1. User sends message to `/chat`
2. `main.py` validates request (Pydantic)
3. Calls `rag_service.generate_response()`
4. RAG service:
   a. Retrieves relevant documents from ChromaDB
   b. Builds context from top-k results
   c. Calls `llm_client.stream_response()`
5. LLM streams response back
6. Response logged, metrics updated
7. Return to user with streaming body

### Document Upload

1. User uploads document to `/documents/upload`
2. `rag_service.load_and_index_document()`
3. RAG service:
   a. Loads document content
   b. Chunks into overlapping segments
   c. Embeds each chunk (Sentence-Transformers)
   d. Stores in ChromaDB with metadata
4. Confirm to user

---

## Error Handling

Comprehensive error handling for:

- **Invalid input**: Pydantic raises validation errors, caught and formatted
- **API errors**: LLM API failures trigger exponential backoff
- **Vector DB errors**: Fallback to in-memory embedding if ChromaDB unavailable
- **Rate limiting**: 429 responses trigger backoff
- **Missing documents**: Return helpful error messages

All errors logged with context for debugging.

---

## Testing

Run tests with pytest:

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_app.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

Tests include:
- Unit tests for each service
- Integration tests for API endpoints
- Pydantic model validation
- Mock LLM and vector DB responses
- Error handling scenarios

---

## Performance Considerations

### Latency
- Embedding on-disk cache (ChromaDB handles)
- Streaming responses for low time-to-first-token
- Batch document processing

### Throughput
- Async FastAPI handles concurrent requests
- Connection pooling to LLM APIs
- ChromaDB vectorstore optimized for fast retrieval

### Cost
- Embedding once per document chunk (one-time)
- Only query-relevant context sent to LLM (reduces tokens)
- Streaming reduces time-to-value

### Monitoring
- `/metrics` endpoint tracks:
  - Total tokens used
  - Average response latency
  - Error rates by type
  - Document retrieval recall

---

## Extensibility

### Adding New Tools to Agent

```python
# In agent_service.py, add to tools list:

@tool
def calculator(expression: str) -> str:
    """Evaluate mathematical expression."""
    return str(eval(expression))

tools = [retriever_tool, calculator_tool]
```

### Switching LLM Providers

Modify `app/llm_client.py`:
```python
# Change llm_client initialization
llm = ChatOpenAI(model="gpt-4", temperature=0.7)
# or
llm = AnthropicChatModel(model="claude-3", temperature=0.7)
```

### Custom Embeddings

Modify `app/rag_service.py`:
```python
embeddings = HuggingFaceEmbeddings(model_name="your-model")
# or
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
```

---

## Deployment

### Cloud Deployment (Heroku/AWS/GCP)

1. Push to Git
2. CI/CD pipeline runs tests
3. Build Docker image
4. Deploy container
5. Scale as needed

### Key Production Considerations

- **Secrets**: Use environment variables (never commit keys)
- **Logging**: Send to centralized service (DataDog, CloudWatch)
- **Monitoring**: Track latency, errors, token usage
- **Rate limiting**: Implement per-user quotas
- **Caching**: Cache embeddings and common queries
- **Persistence**: ChromaDB data must survive restarts

---

## Example Use Cases

1. **Customer Support**: Upload documentation, answer user questions
2. **Research Assistant**: Index papers, extract and summarize
3. **Code Documentation**: Index codebase, answer developer questions
4. **Internal Knowledge Base**: Index company docs, assist employees

---

## Future Enhancements

- [ ] Multi-document retrieval (fusion)
- [ ] Feedback loop (user rates response quality)
- [ ] Fine-tuned embeddings on domain data
- [ ] Longer context windows (document summarization)
- [ ] Web search integration (true internet search)
- [ ] Conversation memory (long-term context)
- [ ] Multi-modal inputs (images, tables)

---

## Troubleshooting

### ChromaDB Connection Error
- Ensure ChromaDB service is running: `docker-compose up`
- Check `CHROMA_HOST` and `CHROMA_PORT` in config

### LLM API Errors
- Verify API keys in environment
- Check rate limits with provider
- See logs for detailed error

### Slow Retrieval
- ChromaDB has many documents: chunk size too small
- Optimize with larger chunks or pre-computed indices

---

## References

- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [RAG Paper](https://arxiv.org/abs/2005.11401)

---

## License

MIT

---

Good luck deploying! This capstone represents a complete ML system from data to serving.
