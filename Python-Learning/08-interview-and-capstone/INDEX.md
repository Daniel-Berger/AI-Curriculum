# Phase 8: Interview Prep & Capstone - Complete Index

## Quick Navigation

### 01-System Design (Pre-existing)
- **lesson.md**: System design fundamentals
- **exercises.py**: Design challenges
- **solutions.py**: Complete design solutions

### 02-Coding Challenges ⭐ NEW
- **lesson.md**: Common interview patterns
  - Data manipulation, API integration, algorithms, ML coding
  - Complexity analysis, common mistakes, interview strategy

- **exercises.py**: 20 coding challenges
  - 5 Data Manipulation: JSON parsing, time series, pivoting, merging, cleaning
  - 5 API Integration: clients, pagination, retries, streaming, batching
  - 5 Algorithms: LRU cache, similarity, TF-IDF, K-means, binary search
  - 5 ML Coding: cross-validation, pipelines, engineering, metrics, confusion matrix

- **solutions.py**: Full implementations with analysis
  - Each exercise solved completely
  - Complexity analysis, edge cases, usage examples

**How to Use**: Attempt exercises first, then review solutions. Practice similar problems online.

---

### 03-ML Fundamentals Review ⭐ NEW
- **lesson.md**: Night-before interview speed review (500+ lines)
  - Python essentials (built-ins, comprehensions, decorators, classes)
  - NumPy & SciPy quick reference
  - Pandas mastery (groupby, merge, pivot, time series)
  - ML algorithms cheat sheet (regression, classification, clustering, dimensionality reduction)
  - Deep learning summary (CNN, RNN, LSTM, Transformers)
  - LLMs & Transformers (tokenization, attention, prompting, RAG, fine-tuning)
  - ML algorithm decision tree (which algorithm for which problem)
  - Python ML stack (all important imports)
  - Interview red flags and last-minute tips

- **exercises.py**: 15 rapid-fire review questions
  - Questions span all 8 phases of curriculum
  - Mix of conceptual and practical
  - Designed for quick refresh

- **solutions.py**: Concise answers with explanations
  - Quick reference formulas (all important equations)
  - Algorithm decision tree (complete guide)

**How to Use**: Read lesson.md the night before interview. Use exercises for self-assessment. Reference solutions.py during prep.

---

### 04-Behavioral Prep ⭐ NEW
- **lesson.md**: Complete behavioral interview guide (400+ lines)
  - STAR method framework with detailed example
  - Your career transition narrative (iOS → ML)
  - Transferable skills to emphasize
  - 10 STAR story templates:
    1. Tell me about a time you failed
    2. Tell me about learning something new
    3. Tell me about a disagreement
    4. Tell me about a difficult person
    5. Tell me about competing priorities
    6. Tell me about taking initiative
    7. Tell me about your proudest accomplishment
    8. Tell me about making decisions with incomplete information
    9. Tell me about giving/receiving feedback
    10. Tell me about improving a process
  - Questions to ask interviewers
  - Salary negotiation tips and market ranges
  - Interview day tips (before, during, after)
  - Thank you email template
  - Red flags to watch for

**How to Use**: Prepare your 10 stories, practice telling them out loud. Reference questions to ask. Use salary tips for negotiation.

---

### Capstone: Complete RAG Chat System ⭐ NEW

**Path**: `/capstone/`

#### Documentation
- **README.md**: Complete system documentation (250+ lines)
  - Architecture diagram (ASCII)
  - Feature overview (RAG, multi-turn chat, document management, agent)
  - Tech stack explanation
  - API endpoints with examples
  - Configuration reference
  - Data flow explanation
  - Error handling strategy
  - Performance considerations
  - Extensibility guide
  - Deployment instructions
  - Example use cases
  - Future enhancements

#### Application Code

**app/main.py** (250+ lines)
- FastAPI application entry point
- Startup/shutdown lifecycle management
- `/chat` endpoint with streaming
- `/documents/upload`, `/documents`, `/documents/{doc_id}` endpoints
- `/health` health check, `/metrics` monitoring
- Comprehensive error handling
- Pydantic request validation

**app/models.py** (150+ lines)
- ChatRequest/ChatResponse models
- DocumentUpload/Document models
- HealthResponse/MetricsResponse models
- Internal models (ChunkMetadata, RetrievalResult, AgentToolCall)
- Pydantic validators for input safety

**app/config.py** (40 lines)
- Environment-based configuration with Pydantic Settings
- API keys, ChromaDB settings, RAG parameters
- LLM configuration, agent settings
- Centralized, clean config management

**app/rag_service.py** (350+ lines)
- RAG pipeline implementation
- Document loading and chunking (overlapping chunks)
- Vector store integration (mocked, pluggable)
- Semantic chunk retrieval with similarity scoring
- Context building for LLM
- Document metadata management
- Full document lifecycle (create, list, delete)

**app/agent_service.py** (300+ lines)
- LangGraph-based agent orchestration
- Tool selection (retrieval, calculator, web search)
- Tool execution and result handling
- Streaming response support
- Fallback and error handling
- Multi-turn conversation support

**app/llm_client.py** (200+ lines)
- Unified LLM client abstraction
- Claude and OpenAI support
- Mock fallback for testing
- Response streaming
- Token counting and cost estimation
- Prompt building

#### Infrastructure

**Dockerfile** (Multi-stage)
- Builder stage: compile dependencies
- Runtime stage: minimal production image
- Health check configuration
- Port exposure and environment setup

**docker-compose.yml**
- FastAPI app service with auto-reload
- ChromaDB vector database service
- Shared network and volumes
- Health checks for both services
- One-command local deployment: `docker-compose up`

**requirements.txt**
- All Python dependencies
- Pinned versions for reproducibility
- Development and testing tools

#### Testing

**tests/test_app.py** (500+ lines)
- 15+ comprehensive test classes
- Chat endpoint tests (valid, invalid, edge cases)
- Document management tests
- Health/metrics endpoint tests
- Pydantic model validation tests
- RAG service unit tests
- LLM client tests
- End-to-end integration tests
- Error handling scenarios
- Mock strategies

**How to Run Tests**: `pytest tests/ -v`

**How to Use Capstone**:
1. Read README.md to understand architecture
2. Walk through main.py → understand request flow
3. Study rag_service.py → understand data pipeline
4. Review agent_service.py → understand orchestration
5. Look at models.py → understand contracts
6. Run tests: `pytest tests/ -v`
7. Deploy: `docker-compose up`

---

### Quiz ⭐ NEW
**Path**: `/quiz.md`

Comprehensive 20-question self-assessment covering all 8 phases.

**Question Breakdown**:
- 5 Easy questions (basics, operators, data structures)
- 8 Medium questions (algorithms, metrics, deployment)
- 7 Hard questions (detailed scenarios requiring deep understanding)

**Question Topics**:
1. Lambda functions and Python basics
2. NumPy vectorization
3. Pandas groupby operations
4. Regression vs classification
5. ReLU activation
6. Overfitting diagnosis
7. StandardScaler normalization
8. Cross-validation purpose
9. Confusion matrix and recall
10. Transfer learning advantages
11. Transformer attention heads
12. Production data drift
13. RAG explanation
14. Class imbalance and metrics
15. Data leakage in preprocessing
16. Semantic search architecture
17. End-to-end ML system design
18. Fine-tuning regularization
19. Clustering algorithm comparison
20. Cost-aware classification thresholds

**How to Use**:
1. Take under timed conditions (45 minutes)
2. No notes or looking up answers
3. Review answers and explanations
4. Target: 18+/20 for interview readiness
5. Retake after studying weak areas

---

### Summary Document
**Path**: `/PHASE-8-COMPLETE.md`

Complete summary of everything created, with:
- File inventory (22 files, 6000+ lines)
- Learning outcomes
- How to use each component
- Study timeline recommendations
- Next steps before interview

---

## Complete File List

```
08-interview-and-capstone/
├── INDEX.md (this file)
├── PHASE-8-COMPLETE.md (summary)
├── quiz.md (20-question assessment)
│
├── 01-system-design/ (pre-existing)
│   ├── lesson.md
│   ├── exercises.py
│   └── solutions.py
│
├── 02-coding-challenges/ (NEW)
│   ├── lesson.md (300 lines) - patterns
│   ├── exercises.py (300+ lines) - 20 challenges
│   └── solutions.py (700+ lines) - full solutions
│
├── 03-ml-fundamentals-review/ (NEW)
│   ├── lesson.md (500+ lines) - complete review
│   ├── exercises.py (300+ lines) - 15 questions
│   └── solutions.py (500+ lines) - answers + formulas
│
├── 04-behavioral-prep/ (NEW)
│   └── lesson.md (400+ lines) - soft skills guide
│
└── capstone/ (NEW - complete system)
    ├── README.md (250+ lines) - full documentation
    ├── Dockerfile - multi-stage build
    ├── docker-compose.yml - local deployment
    ├── requirements.txt - dependencies
    │
    ├── app/
    │   ├── __init__.py
    │   ├── main.py (250+ lines) - FastAPI app
    │   ├── models.py (150+ lines) - Pydantic models
    │   ├── config.py (40 lines) - settings
    │   ├── rag_service.py (350+ lines) - RAG pipeline
    │   ├── agent_service.py (300+ lines) - orchestration
    │   └── llm_client.py (200+ lines) - LLM abstraction
    │
    └── tests/
        ├── __init__.py
        └── test_app.py (500+ lines) - 15+ test classes
```

---

## Study Plan Recommendation

### Week 1: Coding Patterns
- Read: 02-coding-challenges/lesson.md (2 hours)
- Do: Attempt 5 data manipulation exercises
- Review: Solutions and complexity analysis

### Week 2: More Coding Practice
- Do: Attempt remaining 15 coding challenges
- Practice: Similar problems on LeetCode
- Review: Solutions for weak patterns

### Week 3: ML Fundamentals
- Read: 03-ml-fundamentals-review/lesson.md (3 hours)
- Do: 15 rapid-fire questions
- Review: Solutions, focus on weak areas
- Practice: Teach concepts to someone else

### Week 4: System Design & Capstone
- Read: capstone/README.md (1 hour)
- Study: Walk through capstone code (2 hours)
- Understand: Data flow, architecture, design decisions
- Practice: Explain capstone to yourself

### Week 5: Behavioral Prep
- Read: 04-behavioral-prep/lesson.md (2 hours)
- Prepare: Your 10 STAR stories
- Practice: Tell stories out loud (record yourself)
- Research: Company, role, interviewer backgrounds

### Final 2 Days: Polish & Review
- Day 1: Take quiz.md (45 minutes timed)
- Review weak areas
- Final review of lesson.md files
- Prepare questions to ask
- Get good sleep!

---

## Interview Day Checklist

Before Interview:
- [ ] 10 STAR stories prepared and practiced
- [ ] 5+ good questions to ask interviewers
- [ ] Understand capstone architecture completely
- [ ] Know ML fundamentals (reviewed lesson.md)
- [ ] Know coding patterns and complexity analysis
- [ ] Comfortable with salary negotiation framework
- [ ] Clothing prepared (slightly formal)
- [ ] Resume reviewed (remember everything on it)
- [ ] Route to interview location checked

After Interview:
- [ ] Thank you email sent within 2 hours
- [ ] Personalized with something specific from interview
- [ ] Restate interest and unique value
- [ ] Keep it short (30 seconds to read)

---

## Key Resources

### For Coding
- LeetCode (practice similar problems)
- HackerRank (Python, SQL)
- Codewars (fun challenges)

### For ML
- scikit-learn documentation
- fast.ai (excellent ML course)
- Hugging Face (transformers, fine-tuning)

### For System Design
- "Designing Machine Learning Systems" by Chip Huyen
- "Designing Data-Intensive Applications" by Kleppmann
- High Scalability blog

### For LLMs
- Anthropic docs (Claude API)
- OpenAI docs (GPT, embeddings)
- LangChain documentation

---

## Final Tips

1. **Practice out loud**: Don't just read, actually speak your answers
2. **Time yourself**: Interview is fast, practice thinking on your feet
3. **Know your numbers**: Complexity of your algorithms, token costs, latency targets
4. **Explain your reasoning**: Interviewers want to hear your thought process
5. **Ask for clarification**: If something is unclear, ask (shows good engineering)
6. **Be honest about gaps**: "I haven't done X, but I'd approach it by..." is better than guessing
7. **Show your work**: Walk through examples, don't just give high-level answers
8. **Enjoy it**: Interviews are conversations, not interrogations. Be yourself.

---

**You're ready! Go crush this interview! 🚀**

Good luck! Come back and share how it went! :)
