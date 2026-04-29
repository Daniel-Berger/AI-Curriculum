# Module 01: System Design for AI/ML Interviews

## Introduction for Swift Developers

If you've designed iOS app architectures with MVVM, coordinators, and clean architecture,
you already think in components, data flow, and separation of concerns. System design for
AI/ML interviews uses the same muscles -- but the components are vector databases, embedding
services, inference servers, and feature stores instead of view models, repositories, and
network layers.

The good news: your experience reasoning about offline/online sync, push notification
pipelines, and Core Data architectures translates directly. You understand latency budgets,
caching strategies, and graceful degradation. Now we apply those concepts at ML scale.

This module presents four complete system design problems, each structured the way you
should approach them in a 45-minute interview.

---

## The System Design Framework

Before diving into problems, internalize this framework. Every system design answer should
follow these steps:

```
1. REQUIREMENTS CLARIFICATION  (3-5 min)
   - Functional requirements (what does it do?)
   - Non-functional requirements (scale, latency, availability)
   - Constraints and assumptions

2. HIGH-LEVEL DESIGN           (5-10 min)
   - ASCII architecture diagram
   - Key components and their responsibilities
   - Data flow (request path)

3. COMPONENT DEEP-DIVE         (15-20 min)
   - Pick 2-3 critical components
   - Data models, algorithms, storage choices
   - API contracts

4. SCALING & RELIABILITY       (5-10 min)
   - Bottleneck identification
   - Horizontal scaling strategies
   - Failure modes and mitigation

5. TRADEOFFS & EXTENSIONS      (5 min)
   - Key decisions and their tradeoffs
   - Future improvements
   - Monitoring and evaluation
```

---

## Problem 1: Design a Recommendation System

### Scenario

You are designing a recommendation system for an e-commerce platform with 50M users and
10M products. The system should provide personalized product recommendations on the
homepage, product pages ("similar items"), and email campaigns.

### Step 1: Requirements Clarification

**Functional Requirements:**
- Personalized homepage recommendations (top-N items for a user)
- "Customers who bought X also bought Y" on product pages
- Email campaign recommendations (batch, generated daily)
- New user recommendations (cold start)

**Non-Functional Requirements:**
- Latency: < 100ms for real-time recommendations (p99)
- Scale: 50M users, 10M products, 500M interactions/day
- Freshness: Incorporate last-hour behavior within 1 hour
- Availability: 99.9% uptime (recommendations are revenue-critical)

**Assumptions:**
- Interaction types: view, click, add-to-cart, purchase (implicit feedback)
- Product catalog updated daily, user behavior is continuous
- We have historical data for training

### Step 2: High-Level Design

```
                        ┌─────────────────────────────────────────┐
                        │            Client Applications          │
                        │    (Web, iOS App, Email Service)         │
                        └──────────────┬──────────────────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │       API Gateway         │
                        │   (Rate Limit, Auth)      │
                        └──────────┬───────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                              ▼
         ┌──────────────────┐           ┌──────────────────┐
         │  Real-Time Recs  │           │  Batch Recs      │
         │  Service         │           │  Service          │
         └────────┬─────────┘           └────────┬─────────┘
                  │                               │
         ┌────────┴─────────┐            ┌───────┴────────┐
         ▼                  ▼            ▼                │
  ┌─────────────┐  ┌──────────────┐  ┌──────────┐       │
  │ Feature     │  │ Embedding    │  │ Offline  │       │
  │ Store       │  │ Index (ANN)  │  │ Training │       │
  │ (Redis)     │  │ (FAISS/      │  │ Pipeline │       │
  │             │  │  Pinecone)   │  │ (Spark)  │       │
  └──────┬──────┘  └──────┬───────┘  └─────┬────┘       │
         │                │                 │            │
         └────────┬───────┘                 │            │
                  ▼                         ▼            ▼
         ┌──────────────────┐       ┌──────────────────────┐
         │   Event Stream   │       │   Data Warehouse     │
         │   (Kafka)        │◄─────►│   (S3 + Parquet)     │
         └──────────────────┘       └──────────────────────┘
```

### Step 3: Component Deep-Dive

#### A. Recommendation Approaches

**Collaborative Filtering** -- "Users like you also liked..."
```python
# User-Item interaction matrix (sparse)
# R[u][i] = rating/interaction score

# Matrix Factorization: R ≈ U × V^T
# U: user embeddings (50M × k), V: item embeddings (10M × k)
# k = embedding dimension (typically 64-256)

import numpy as np

class MatrixFactorization:
    """Simplified collaborative filtering via matrix factorization."""

    def __init__(self, n_factors: int = 128, lr: float = 0.01,
                 reg: float = 0.02, n_epochs: int = 20):
        self.n_factors = n_factors
        self.lr = lr
        self.reg = reg
        self.n_epochs = n_epochs

    def fit(self, interactions: list[tuple[int, int, float]]):
        """Train on (user_id, item_id, rating) tuples."""
        n_users = max(u for u, _, _ in interactions) + 1
        n_items = max(i for _, i, _ in interactions) + 1

        # Initialize embeddings randomly
        self.user_factors = np.random.normal(0, 0.1, (n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.1, (n_items, self.n_factors))

        for epoch in range(self.n_epochs):
            np.random.shuffle(interactions)
            for u, i, r in interactions:
                pred = self.user_factors[u] @ self.item_factors[i]
                error = r - pred
                # SGD update with L2 regularization
                self.user_factors[u] += self.lr * (
                    error * self.item_factors[i] - self.reg * self.user_factors[u]
                )
                self.item_factors[i] += self.lr * (
                    error * self.user_factors[u] - self.reg * self.item_factors[i]
                )

    def predict(self, user_id: int, item_id: int) -> float:
        return float(self.user_factors[user_id] @ self.item_factors[item_id])

    def recommend(self, user_id: int, top_k: int = 10) -> list[int]:
        scores = self.user_factors[user_id] @ self.item_factors.T
        return list(np.argsort(scores)[-top_k:][::-1])
```

**Content-Based Filtering** -- "Because you liked items with these features..."
```python
# Item feature vectors (category, brand, price range, description embeddings)
# User profile = weighted average of interacted item features

class ContentBasedRecommender:
    def __init__(self, item_features: dict[int, np.ndarray]):
        self.item_features = item_features

    def build_user_profile(
        self, interactions: list[tuple[int, float]]
    ) -> np.ndarray:
        """Build user profile from (item_id, weight) interactions."""
        profile = np.zeros_like(next(iter(self.item_features.values())))
        total_weight = 0.0
        for item_id, weight in interactions:
            profile += weight * self.item_features[item_id]
            total_weight += weight
        return profile / max(total_weight, 1e-8)

    def recommend(self, user_profile: np.ndarray, top_k: int = 10,
                  exclude: set[int] | None = None) -> list[int]:
        """Recommend items most similar to user profile."""
        exclude = exclude or set()
        scores = {}
        for item_id, features in self.item_features.items():
            if item_id not in exclude:
                # Cosine similarity
                scores[item_id] = float(
                    np.dot(user_profile, features) /
                    (np.linalg.norm(user_profile) * np.linalg.norm(features) + 1e-8)
                )
        return sorted(scores, key=scores.get, reverse=True)[:top_k]
```

**Hybrid Approach (Production)** -- Combine both:
```python
class HybridRecommender:
    """Two-stage recommendation: candidate generation + ranking."""

    def recommend(self, user_id: int, context: dict) -> list[int]:
        # Stage 1: Candidate Generation (fast, broad)
        # Pull ~1000 candidates from multiple sources
        collab_candidates = self.collab_model.recommend(user_id, top_k=500)
        content_candidates = self.content_model.recommend(user_id, top_k=300)
        popular_candidates = self.popularity_model.recommend(top_k=200)

        all_candidates = set(collab_candidates + content_candidates
                             + popular_candidates)

        # Stage 2: Ranking (slower, precise)
        # Score each candidate with a learned ranking model
        features = self.feature_store.get_features(user_id, all_candidates)
        scores = self.ranking_model.predict(features)

        # Stage 3: Post-processing
        ranked = sorted(zip(all_candidates, scores),
                        key=lambda x: x[1], reverse=True)

        # Apply business rules (diversity, freshness, already purchased)
        return self.apply_business_rules(ranked, context)[:50]
```

#### B. Feature Store (Redis)

```python
# Feature store schema
user_features = {
    "user:12345": {
        "embedding": [0.1, -0.3, ...],          # 128-dim
        "recent_categories": ["electronics", "books"],
        "avg_price": 45.99,
        "purchase_count_30d": 7,
        "last_active": "2026-04-20T10:30:00Z",
    }
}

item_features = {
    "item:67890": {
        "embedding": [0.2, 0.5, ...],           # 128-dim
        "category": "electronics",
        "price": 29.99,
        "avg_rating": 4.2,
        "popularity_score": 0.87,
    }
}

# Redis commands for low-latency access
# SET user:12345:embedding <binary>
# GET user:12345:embedding              -> ~0.2ms
# HGETALL user:12345:features           -> ~0.3ms
```

#### C. Embedding Index (Approximate Nearest Neighbor)

```python
import faiss  # Facebook AI Similarity Search

# Build index for 10M item embeddings
dimension = 128
n_items = 10_000_000

# IVF (Inverted File) + PQ (Product Quantization) for scale
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFPQ(
    quantizer,
    dimension,
    n_list=4096,       # number of clusters
    m=16,              # number of sub-quantizers
    nbits=8,           # bits per sub-quantizer
)

# Train on a sample, then add all vectors
index.train(sample_vectors)
index.add(all_item_vectors)

# Search: find 100 nearest neighbors in ~1ms
distances, indices = index.search(user_embedding.reshape(1, -1), k=100)
```

### Step 4: Scaling Discussion

**Cold Start Problem:**
- New users: Show popular/trending items, ask for preferences onboarding
- New items: Use content features (description embedding, category, price)
- Exploration vs exploitation: epsilon-greedy or Thompson sampling

**Scaling Bottlenecks:**
- Feature store reads: Shard Redis by user_id hash, use read replicas
- ANN index: Partition by category, replicate across regions
- Training pipeline: Incremental updates (not full retrains)
- Real-time updates: Kafka stream -> update user features in near-real-time

**A/B Testing:**
```
                    ┌──────────────────┐
    Request ──────► │  Traffic Router  │
                    │  (hash user_id)  │
                    └───┬──────────┬───┘
                        │          │
                   50%  ▼     50%  ▼
               ┌──────────┐  ┌──────────┐
               │ Model A  │  │ Model B  │
               │ (control)│  │ (variant)│
               └──────────┘  └──────────┘
                        │          │
                        ▼          ▼
                    ┌──────────────────┐
                    │  Metrics Logger  │
                    │  (CTR, revenue,  │
                    │   engagement)    │
                    └──────────────────┘
```

### Step 5: Tradeoffs

| Decision | Option A | Option B | Our Choice |
|----------|----------|----------|------------|
| Embedding index | FAISS (self-hosted) | Pinecone (managed) | FAISS -- cost at scale |
| Feature store | Redis | DynamoDB | Redis -- lower latency |
| Training | Batch (daily) | Online (streaming) | Hybrid -- batch + hourly incremental |
| Ranking model | Logistic Regression | Deep model (DLRM) | Start LR, graduate to deep |

---

## Problem 2: Design a RAG Pipeline at Scale

### Scenario

You are building a Retrieval-Augmented Generation (RAG) system for a legal tech company.
The system must answer questions about legal documents (contracts, case law, regulations)
for 10K enterprise users across 500 organizations, each with their own private document
collections.

### Step 1: Requirements Clarification

**Functional Requirements:**
- Users upload documents (PDF, DOCX, HTML) to their organization's collection
- Natural language questions answered with citations to source documents
- Support for multi-turn conversations with follow-up questions
- Document-level access control (some docs visible only to certain users)

**Non-Functional Requirements:**
- Query latency: < 5 seconds end-to-end (including LLM generation)
- Ingestion: Handle 10K documents/day across all tenants
- Accuracy: Must cite sources; hallucination rate < 5%
- Security: Strict tenant isolation, SOC 2 compliance

**Assumptions:**
- Average document: 20 pages, ~8K tokens
- Average query: 50-100 tokens
- Peak concurrent queries: 500/second

### Step 2: High-Level Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Document Ingestion Pipeline                  │
│                                                                     │
│  Upload ──► Parse ──► Chunk ──► Embed ──► Store ──► Index          │
│  (S3)      (Tika)   (Custom)  (Model)   (VectorDB) (Metadata)     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        Query Pipeline                               │
│                                                                     │
│  Query ──► Rewrite ──► Retrieve ──► Rerank ──► Generate ──► Cite   │
│  (User)   (LLM)      (VectorDB)   (Cross-     (LLM)       (Post-  │
│                                     Encoder)               process) │
└─────────────────────────────────────────────────────────────────────┘

                    ┌───────────────────────┐
                    │    Architecture       │
                    └───────────┬───────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ API Gateway   │   │ Ingestion Workers │   │ Background Jobs   │
│ (FastAPI)     │   │ (Celery/SQS)      │   │ (Cron/Airflow)    │
│               │   │                   │   │                   │
│ - Auth/RBAC   │   │ - Parse docs      │   │ - Re-embed on     │
│ - Rate limit  │   │ - Chunk           │   │   model update    │
│ - Route query │   │ - Embed           │   │ - Usage analytics │
│ - Stream resp │   │ - Store           │   │ - Cache warmup    │
└───────┬───────┘   └───────┬───────────┘   └───────────────────┘
        │                   │
        ▼                   ▼
┌───────────────────────────────────────────┐
│              Data Layer                   │
│                                           │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Vector DB│  │ Metadata │  │ Cache  │ │
│  │ (Qdrant) │  │ (Postgres)│  │(Redis) │ │
│  └──────────┘  └──────────┘  └────────┘ │
└───────────────────────────────────────────┘
```

### Step 3: Component Deep-Dive

#### A. Chunking Service

Chunking strategy dramatically affects retrieval quality:

```python
from dataclasses import dataclass
from enum import Enum

class ChunkStrategy(Enum):
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    HIERARCHICAL = "hierarchical"

@dataclass
class Chunk:
    id: str
    text: str
    document_id: str
    org_id: str
    metadata: dict          # page number, section, headers
    parent_chunk_id: str | None  # for hierarchical chunking
    embedding: list[float] | None = None

def chunk_document(
    text: str,
    strategy: ChunkStrategy = ChunkStrategy.HIERARCHICAL,
    chunk_size: int = 512,
    overlap: int = 50,
) -> list[Chunk]:
    """
    Hierarchical chunking: create parent chunks (large context)
    and child chunks (precise retrieval).

    Parent: 2048 tokens -- used for LLM context
    Child:  512 tokens  -- used for embedding search
    Each child points to its parent.
    """
    if strategy == ChunkStrategy.HIERARCHICAL:
        parents = split_by_sections(text, max_tokens=2048)
        children = []
        for parent in parents:
            child_texts = split_with_overlap(
                parent.text, chunk_size=chunk_size, overlap=overlap
            )
            for child_text in child_texts:
                children.append(Chunk(
                    id=generate_id(),
                    text=child_text,
                    document_id=parent.document_id,
                    org_id=parent.org_id,
                    metadata=parent.metadata,
                    parent_chunk_id=parent.id,
                ))
        return parents + children
    # ... other strategies
```

#### B. Query Processing Pipeline

```python
class RAGQueryPipeline:
    """Multi-stage retrieval with query rewriting and reranking."""

    async def answer(self, query: str, org_id: str,
                     conversation_history: list[dict]) -> dict:
        # Stage 1: Query rewriting (handle follow-ups, expand acronyms)
        rewritten_query = await self.rewrite_query(
            query, conversation_history
        )

        # Stage 2: Multi-query retrieval (generate sub-questions)
        sub_queries = await self.decompose_query(rewritten_query)

        # Stage 3: Retrieve from vector DB (with tenant filter)
        all_chunks = []
        for sq in sub_queries:
            chunks = await self.vector_db.search(
                query=sq,
                filter={"org_id": org_id},
                top_k=20,
            )
            all_chunks.extend(chunks)

        # Stage 4: Deduplicate and rerank
        unique_chunks = deduplicate(all_chunks)
        reranked = await self.reranker.rerank(
            query=rewritten_query,
            documents=unique_chunks,
            top_k=10,
        )

        # Stage 5: Generate answer with citations
        answer = await self.llm.generate(
            system_prompt=RAG_SYSTEM_PROMPT,
            context=format_chunks(reranked),
            query=rewritten_query,
        )

        # Stage 6: Post-process (extract citations, verify)
        return self.post_process(answer, reranked)
```

#### C. Vector Database Selection

| Feature | Qdrant | Pinecone | Weaviate | pgvector |
|---------|--------|----------|----------|----------|
| Multi-tenant | Payload filtering | Namespaces | Multi-tenancy | Row-level security |
| Scale | Horizontal | Managed | Horizontal | Limited |
| Filtering | Rich | Metadata | GraphQL | SQL |
| Self-hosted | Yes | No | Yes | Yes |
| Latency (p99) | ~5ms | ~10ms | ~8ms | ~20ms |

**Our choice: Qdrant** -- best multi-tenant filtering, self-hostable for compliance.

#### D. Caching Strategy

```python
# Three-level cache
class RAGCache:
    """
    L1: Exact query match (Redis, TTL 1 hour)
    L2: Semantic similarity cache (if query embedding is >0.95
        similar to a cached query, return cached answer)
    L3: Chunk-level cache (avoid re-embedding unchanged documents)
    """

    async def get_or_compute(self, query: str, org_id: str) -> dict:
        cache_key = f"{org_id}:{hash(query)}"

        # L1: Exact match
        if cached := await self.redis.get(cache_key):
            return json.loads(cached)

        # L2: Semantic similarity
        query_embedding = await self.embed(query)
        similar = await self.semantic_cache.search(
            query_embedding, threshold=0.95
        )
        if similar:
            return similar.answer

        # L3: Compute fresh
        answer = await self.pipeline.answer(query, org_id)

        # Store in both caches
        await self.redis.set(cache_key, json.dumps(answer), ex=3600)
        await self.semantic_cache.store(query_embedding, answer)

        return answer
```

### Step 4: Scaling Discussion

**Multi-Tenant Architecture:**
```
Option A: Shared collection with metadata filtering
  - Pro: Simple, efficient resource usage
  - Con: Noisy neighbor risk, harder compliance story

Option B: Collection-per-tenant
  - Pro: Strong isolation, easy to delete tenant data
  - Con: Overhead per collection, harder to manage

Option C: Hybrid (our choice)
  - Small tenants: Shared collection with payload filtering
  - Enterprise tenants: Dedicated collection
  - Partition key: org_id in all queries
```

**Monitoring and Evaluation:**
- Retrieval metrics: MRR@10, Recall@K, precision
- Generation metrics: faithfulness (does answer match retrieved context?),
  answer relevance, citation accuracy
- Operational: latency percentiles, cache hit rate, error rate
- Use LLM-as-judge for automated evaluation at scale

### Step 5: Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Chunk size 512 | Smaller = more precise retrieval, but less context per chunk |
| Reranking stage | +100ms latency, but significantly better relevance |
| Hierarchical chunking | More storage/complexity, but retrieve child -> return parent context |
| Query decomposition | Extra LLM call cost, but handles complex multi-part questions |

---

## Problem 3: Design an LLM-Powered Chatbot

### Scenario

You are designing a customer support chatbot for a SaaS company. The chatbot should handle
common questions, perform actions (check order status, initiate refunds, update account),
and escalate to human agents when appropriate. The company handles 100K support
conversations per day.

### Step 1: Requirements Clarification

**Functional Requirements:**
- Natural language conversation with context across turns
- Tool use: query order DB, initiate refunds, update settings
- Knowledge base: answer product questions from documentation
- Escalation: transfer to human agent with conversation context
- Multi-language support (English, Spanish, French, German)

**Non-Functional Requirements:**
- First token latency: < 1 second
- Availability: 99.95% (support is 24/7)
- Concurrent conversations: 10K simultaneous
- Cost: < $0.05 per conversation (average 8 turns)
- Safety: Never share other users' PII, never make unauthorized actions

### Step 2: High-Level Design

```
┌───────────────────────────────────────────────────────────────┐
│                    Client Layer                                │
│   Web Widget    Mobile SDK    API Integration    Slack Bot     │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                  API Gateway (Kong/AWS ALB)                   │
│     Rate Limiting │ Auth │ WebSocket Upgrade │ Load Balance   │
└──────────────────────┬───────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐     ┌──────────────────┐
│  Chat Service    │     │  Admin Service   │
│  (FastAPI)       │     │  (Dashboard)     │
│                  │     │                  │
│  - Session mgmt  │     │  - Analytics     │
│  - Streaming     │     │  - Config        │
│  - Tool routing  │     │  - Agent queue   │
└────────┬─────────┘     └──────────────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌────────┐ ┌──────────────────────────────────────────┐
│Session │ │         LLM Orchestration Layer           │
│Store   │ │                                           │
│(Redis) │ │  ┌──────────┐  ┌───────────┐  ┌───────┐ │
│        │ │  │ Intent    │  │ Tool      │  │ Safety│ │
│        │ │  │ Classifier│  │ Executor  │  │ Layer │ │
│        │ │  └──────────┘  └───────────┘  └───────┘ │
│        │ │                                           │
│        │ │  ┌──────────┐  ┌───────────┐  ┌───────┐ │
│        │ │  │ RAG      │  │ Response  │  │ Human │ │
│        │ │  │ Module   │  │ Generator │  │ Handoff│ │
│        │ │  └──────────┘  └───────────┘  └───────┘ │
│        │ └──────────────────────────────────────────┘
└────────┘
```

### Step 3: Component Deep-Dive

#### A. Session Management and Context

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ConversationState(Enum):
    ACTIVE = "active"
    WAITING_FOR_TOOL = "waiting_for_tool"
    ESCALATED = "escalated"
    RESOLVED = "resolved"

@dataclass
class Session:
    session_id: str
    user_id: str
    state: ConversationState = ConversationState.ACTIVE
    messages: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_context_window(self, max_tokens: int = 4096) -> list[dict]:
        """
        Sliding window with summarization:
        - Keep system prompt + last N messages within token budget
        - If conversation is long, summarize earlier turns
        """
        system_msg = self.messages[0]  # System prompt always included
        recent = []
        token_count = count_tokens(system_msg["content"])

        for msg in reversed(self.messages[1:]):
            msg_tokens = count_tokens(msg["content"])
            if token_count + msg_tokens > max_tokens:
                break
            recent.insert(0, msg)
            token_count += msg_tokens

        # If we dropped messages, add a summary
        if len(recent) < len(self.messages) - 1:
            dropped = self.messages[1:len(self.messages) - len(recent)]
            summary = summarize_messages(dropped)
            recent.insert(0, {"role": "system", "content": f"Earlier: {summary}"})

        return [system_msg] + recent
```

#### B. Tool Use Architecture

```python
from typing import Callable, Any

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict          # JSON Schema
    handler: Callable
    requires_confirmation: bool = False  # For destructive actions
    permission_level: str = "read"       # read, write, admin

TOOLS = [
    Tool(
        name="check_order_status",
        description="Look up the status of a customer order by order ID",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID"}
            },
            "required": ["order_id"],
        },
        handler=check_order_status,
        requires_confirmation=False,
        permission_level="read",
    ),
    Tool(
        name="initiate_refund",
        description="Initiate a refund for an order. Requires confirmation.",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "reason": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["order_id", "reason"],
        },
        handler=initiate_refund,
        requires_confirmation=True,   # User must confirm
        permission_level="write",
    ),
]

class ToolExecutor:
    """Execute tools with validation, auth, and audit logging."""

    async def execute(self, tool_name: str, params: dict,
                      user_context: dict) -> dict:
        tool = self.tool_registry[tool_name]

        # Permission check
        if not self.check_permission(tool, user_context):
            return {"error": "Insufficient permissions"}

        # Confirmation check for destructive actions
        if tool.requires_confirmation:
            return {"status": "needs_confirmation", "action": tool_name,
                    "params": params}

        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                tool.handler(**params), timeout=10.0
            )
            await self.audit_log(tool_name, params, result, user_context)
            return result
        except asyncio.TimeoutError:
            return {"error": "Tool execution timed out"}
```

#### C. Safety Layers

```python
class SafetyPipeline:
    """Multi-layer safety checks for chatbot responses."""

    async def check_input(self, message: str, user_context: dict) -> dict:
        """Pre-LLM safety checks on user input."""
        checks = await asyncio.gather(
            self.pii_detector.scan(message),
            self.injection_detector.check(message),
            self.toxicity_classifier.classify(message),
        )
        return {
            "contains_pii": checks[0].has_pii,
            "injection_attempt": checks[1].is_injection,
            "toxicity_score": checks[2].score,
            "allow": all(c.safe for c in checks),
        }

    async def check_output(self, response: str,
                           user_context: dict) -> dict:
        """Post-LLM safety checks on generated response."""
        # Never leak other users' data
        if self.contains_foreign_pii(response, user_context):
            return {"allow": False, "reason": "response_contains_pii"}

        # Check for harmful content
        if await self.toxicity_classifier.classify(response).score > 0.8:
            return {"allow": False, "reason": "toxic_response"}

        # Verify tool calls are authorized
        tool_calls = extract_tool_calls(response)
        for tc in tool_calls:
            if not self.authorize_tool(tc, user_context):
                return {"allow": False, "reason": "unauthorized_tool_call"}

        return {"allow": True}
```

#### D. Streaming Architecture

```python
from fastapi import WebSocket
from fastapi.responses import StreamingResponse

# Option 1: Server-Sent Events (SSE) -- simpler, HTTP-based
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        session = await get_or_create_session(request.session_id)

        async for token in llm.stream(
            messages=session.get_context_window(),
            tools=TOOLS,
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

# Option 2: WebSocket -- bidirectional, better for real-time
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    session = await create_session()

    try:
        while True:
            data = await websocket.receive_json()
            async for token in process_message(session, data["message"]):
                await websocket.send_json({"type": "token", "data": token})
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        await cleanup_session(session)
```

### Step 4: Scaling Discussion

**Rate Limiting and Cost Control:**
```python
class CostAwareRateLimiter:
    """Rate limit based on both requests AND token usage."""

    async def check_limit(self, user_id: str) -> bool:
        # Per-user limits
        requests_today = await self.redis.incr(f"req:{user_id}:{today()}")
        tokens_today = await self.redis.get(f"tok:{user_id}:{today()}")

        return (
            requests_today <= self.max_requests_per_day    # 100 conversations
            and tokens_today <= self.max_tokens_per_day    # 50K tokens
        )

    def estimate_cost(self, messages: list[dict]) -> float:
        """Estimate LLM cost before making the call."""
        input_tokens = sum(count_tokens(m["content"]) for m in messages)
        estimated_output = 500  # conservative estimate
        return (input_tokens * 0.003 + estimated_output * 0.015) / 1000
```

**Horizontal Scaling:**
- Stateless chat service (session in Redis) -> auto-scale on CPU/connections
- LLM calls are I/O-bound -> high concurrency with async
- Separate queue for tool execution (don't block LLM streaming)

### Step 5: Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| SSE vs WebSocket | SSE simpler (HTTP), WebSocket better for typing indicators |
| Context window management | Summarize old messages (loses detail) vs truncate (loses context) |
| Tool confirmation UX | Safer but adds friction; skip for read-only tools |
| LLM provider | Claude (better reasoning) vs GPT-4 (more tools ecosystem) vs open-source (privacy) |

---

## Problem 4: Design a Real-Time Content Moderation System

### Scenario

You are designing a content moderation system for a social media platform with 200M
monthly active users. The system must moderate text posts, images, and short videos
in near-real-time before they appear in feeds.

### Step 1: Requirements Clarification

**Functional Requirements:**
- Moderate text (hate speech, harassment, spam, misinformation)
- Moderate images (violence, nudity, illegal content)
- Moderate video (10-60 second clips)
- Human review queue for borderline cases
- Appeal process for false positives
- Policy configurability (different rules per region/community)

**Non-Functional Requirements:**
- Latency: < 500ms for text, < 2s for images, < 30s for video
- Scale: 50M posts/day (text), 10M images/day, 2M videos/day
- False positive rate: < 1% (wrongly removing safe content)
- False negative rate: < 5% (missing violating content)
- Availability: 99.99% (content pipeline depends on this)

### Step 2: High-Level Design

```
┌───────────────┐
│ Content Upload │
│   Service      │
└───────┬───────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│                    Content Router                             │
│                                                               │
│   Determine content type(s) → route to appropriate pipeline  │
└───┬──────────────────┬──────────────────┬────────────────────┘
    │                  │                  │
    ▼                  ▼                  ▼
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│  Text    │   │   Image      │   │   Video      │
│  Pipeline│   │   Pipeline   │   │   Pipeline   │
│          │   │              │   │              │
│ 1.Toxic  │   │ 1.NSFW det  │   │ 1.Keyframe  │
│ 2.Spam   │   │ 2.Violence  │   │   extraction │
│ 3.PII    │   │ 3.OCR→text  │   │ 2.Per-frame  │
│ 4.Misinfo│   │ 4.Face det  │   │   analysis   │
└────┬─────┘   └──────┬───────┘   │ 3.Audio     │
     │                │           │   transcript │
     │                │           └──────┬───────┘
     └────────┬───────┘                  │
              │                          │
              ▼                          │
     ┌─────────────────┐                 │
     │  Decision Engine │◄───────────────┘
     │                  │
     │  Aggregate scores│
     │  Apply policy    │
     │  Route decision  │
     └───┬─────────┬────┘
         │         │
    ┌────┘    ┌────┘
    ▼         ▼
┌────────┐ ┌──────────────┐
│ Auto   │ │ Human Review │
│ Action │ │ Queue        │
│        │ │              │
│ Allow  │ │ Priority     │
│ Remove │ │ ranked by    │
│ Warn   │ │ severity +   │
│ Shadow │ │ confidence   │
│ ban    │ │ gap          │
└────────┘ └──────┬───────┘
                  │
                  ▼
           ┌────────────┐
           │  Feedback   │
           │  Loop       │
           │             │
           │ Retrain on  │
           │ human       │
           │ decisions   │
           └────────────┘
```

### Step 3: Component Deep-Dive

#### A. Text Moderation Pipeline

```python
from dataclasses import dataclass
from enum import Enum

class ViolationType(Enum):
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    SPAM = "spam"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    MISINFORMATION = "misinformation"
    PII_EXPOSURE = "pii_exposure"
    SAFE = "safe"

@dataclass
class ModerationResult:
    content_id: str
    violation_type: ViolationType
    confidence: float          # 0.0 to 1.0
    action: str                # allow, review, remove, shadow_ban
    explanation: str
    model_version: str
    latency_ms: float

class TextModerationPipeline:
    """
    Multi-model ensemble for text moderation.

    Stage 1: Fast classifier (distilled BERT, <10ms)
             - Catches 90% of clear violations cheaply
    Stage 2: Full classifier (larger model, <50ms)
             - Only for borderline cases from Stage 1
    Stage 3: LLM judge (expensive, <500ms)
             - Only for high-stakes borderline cases
    """

    async def moderate(self, text: str, context: dict) -> ModerationResult:
        # Stage 1: Fast screening
        fast_result = await self.fast_classifier.predict(text)

        if fast_result.confidence > 0.95:
            return fast_result  # High confidence either way

        # Stage 2: Full analysis (only for borderline)
        full_result = await self.full_classifier.predict(
            text, context=context
        )

        if full_result.confidence > 0.85:
            return full_result

        # Stage 3: LLM judge (only for really tricky cases)
        llm_result = await self.llm_judge.evaluate(
            text,
            context=context,
            policy=self.get_policy(context.get("region")),
        )

        return self.aggregate_results(fast_result, full_result, llm_result)
```

#### B. Image Moderation Pipeline

```python
class ImageModerationPipeline:
    """Multi-model image analysis."""

    async def moderate(self, image_url: str, context: dict) -> ModerationResult:
        # Run all models in parallel for speed
        results = await asyncio.gather(
            self.nsfw_detector.predict(image_url),      # NSFW content
            self.violence_detector.predict(image_url),   # Violence/gore
            self.ocr_engine.extract_text(image_url),     # Text in images
            self.face_detector.detect(image_url),        # Face detection (privacy)
            return_exceptions=True,
        )

        nsfw_result, violence_result, ocr_text, faces = results

        # If image contains text, run text pipeline on OCR output
        text_violation = None
        if ocr_text and len(ocr_text) > 10:
            text_violation = await self.text_pipeline.moderate(
                ocr_text, context
            )

        return self.aggregate_image_results(
            nsfw_result, violence_result, text_violation, faces, context
        )
```

#### C. Decision Engine with Policy Rules

```python
@dataclass
class ModerationPolicy:
    """Region/community-specific moderation policy."""
    region: str
    thresholds: dict[ViolationType, float]  # confidence threshold per type
    auto_remove_types: set[ViolationType]   # always remove, no review needed
    escalation_types: set[ViolationType]    # always send to human review

class DecisionEngine:
    def decide(self, results: list[ModerationResult],
               policy: ModerationPolicy) -> str:
        """
        Decision matrix:

        Confidence > 0.95 + auto_remove_type  -> REMOVE
        Confidence > 0.95 + escalation_type   -> REMOVE + HUMAN_REVIEW
        Confidence 0.7-0.95                   -> HUMAN_REVIEW
        Confidence < 0.7                      -> ALLOW (log for analysis)
        """
        max_result = max(results, key=lambda r: r.confidence)

        if max_result.violation_type == ViolationType.SAFE:
            return "allow"

        threshold = policy.thresholds.get(
            max_result.violation_type, 0.85
        )

        if max_result.confidence > 0.95:
            if max_result.violation_type in policy.auto_remove_types:
                return "remove"
            return "remove_and_review"
        elif max_result.confidence > threshold:
            return "review"
        else:
            return "allow_and_log"
```

#### D. Human Review Queue

```python
class ReviewQueue:
    """
    Priority queue for human reviewers.
    Priority = severity_weight * (1 - confidence) * reach_multiplier
    """

    def calculate_priority(self, result: ModerationResult,
                           user_context: dict) -> float:
        severity_weights = {
            ViolationType.SELF_HARM: 10.0,
            ViolationType.VIOLENCE: 8.0,
            ViolationType.HATE_SPEECH: 7.0,
            ViolationType.HARASSMENT: 6.0,
            ViolationType.MISINFORMATION: 5.0,
            ViolationType.SPAM: 2.0,
        }

        severity = severity_weights.get(result.violation_type, 1.0)
        uncertainty = 1.0 - result.confidence
        reach = min(user_context.get("follower_count", 100) / 1000, 10.0)

        return severity * uncertainty * (1 + reach)
```

### Step 4: Scaling Discussion

**Latency Optimization:**
- GPU inference servers with batching (process multiple images together)
- Model distillation for fast first-pass screening
- Async pipeline: post appears immediately, moderation runs async
  (with "optimistic serving" for high-reputation accounts)

**Feedback Loop:**
- Human review decisions become training data
- Weekly model retraining with active learning (prioritize uncertain samples)
- Track false positive/negative rates per violation type

### Step 5: Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Pre-publish vs post-publish moderation | Safety vs user experience (latency) |
| Multi-stage cascade | Lower cost but higher latency for borderline cases |
| Regional policies | Legal compliance but operational complexity |
| Optimistic serving for verified accounts | Better UX but reputation-dependent trust |
| Shadow banning | Reduces spam motivation but ethical concerns |

---

## Summary: Interview Tips for System Design

1. **Always start with requirements.** Never jump into architecture. Ask clarifying
   questions even if you think you know the answer.

2. **Draw the diagram first.** ASCII art on a whiteboard or shared doc. Label every
   component and arrow.

3. **Be opinionated but flexible.** "I'd choose Qdrant because of its multi-tenant
   filtering, but Pinecone would work if we prefer managed infrastructure."

4. **Quantify everything.** "With 50M users and 10M items, the embedding index is
   10M * 128 * 4 bytes = ~5 GB -- fits in memory on a single machine."

5. **Discuss tradeoffs, not just decisions.** Every choice has a cost. Show you
   understand both sides.

6. **Relate to your experience.** "This is similar to how iOS apps handle offline
   sync -- you need an optimistic UI with eventual consistency."

---

## SE-Specific System Design Problems

The following problems focus on system design scenarios commonly encountered in
Solutions Engineer interviews. Unlike the problems above (which emphasize pure
infrastructure), these emphasize customer constraints, multi-tenant architectures,
integration patterns, and business requirements that SEs must navigate daily.

---

### Problem 6: Multi-Tenant AI Platform

**Prompt**: "Design a multi-tenant AI platform that serves multiple enterprise
customers with different models, data isolation requirements, and usage patterns."

### Step 1: Requirements Clarification

**Functional Requirements:**
- Serve multiple enterprise customers (tenants) from a single platform
- Each tenant can configure their own models, prompts, and workflows
- Tenants can bring their own fine-tuned models
- Real-time inference API with streaming support
- Batch processing for large-volume offline jobs
- Usage tracking and billing per tenant

**Non-Functional Requirements:**
- Strong data isolation between tenants (no data leakage)
- Tenant-specific rate limits and quotas
- 99.9% availability per tenant (one tenant's issues cannot affect others)
- P99 latency < 2 seconds for real-time inference
- Support 100+ enterprise tenants, scaling to 1,000+
- SOC 2 and HIPAA compliance

**Clarifying Questions to Ask:**
- "What level of data isolation is required? Logical or physical?"
- "Do tenants need dedicated GPU resources or can they share?"
- "What's the expected request volume per tenant? How bursty is traffic?"
- "Do tenants need to deploy custom models or only use pre-built ones?"

### Step 2: High-Level Architecture

```
                    ┌─────────────────────────────────┐
                    │          API Gateway             │
                    │   (Auth, Rate Limiting, Routing) │
                    └──────────┬──────────────────────┘
                               │
                    ┌──────────▼──────────────────────┐
                    │      Tenant Router Service       │
                    │  (Config lookup, model routing)   │
                    └──────────┬──────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼──────┐ ┌──────▼───────┐ ┌──────▼───────┐
    │  Shared Model   │ │  Dedicated   │ │   Batch      │
    │  Pool (GPU)     │ │  Model Pool  │ │   Processing │
    │  (Small/Med     │ │  (Enterprise │ │   Queue      │
    │   tenants)      │ │   tenants)   │ │              │
    └────────┬────────┘ └──────┬───────┘ └──────┬───────┘
             │                 │                │
    ┌────────▼─────────────────▼────────────────▼──────┐
    │              Data Layer (Per-Tenant)              │
    │  ┌──────────┐ ┌───────────┐ ┌──────────────┐     │
    │  │ Vector DB│ │ Model     │ │ Prompt/Config│     │
    │  │ (tenant  │ │ Registry  │ │ Store        │     │
    │  │  scoped) │ │           │ │              │     │
    │  └──────────┘ └───────────┘ └──────────────┘     │
    └──────────────────────────────────────────────────┘
             │
    ┌────────▼─────────────────────────────────────────┐
    │           Observability & Billing                │
    │  ┌──────────┐ ┌───────────┐ ┌──────────────┐     │
    │  │ Usage    │ │ Metrics/  │ │ Audit        │     │
    │  │ Metering │ │ Logging   │ │ Log          │     │
    │  └──────────┘ └───────────┘ └──────────────┘     │
    └──────────────────────────────────────────────────┘
```

### Step 3: Component Deep-Dive

**Tenant Router Service:**
This is the brain of the system. For each request, it:
1. Looks up the tenant's configuration (which model, which prompt template, which parameters)
2. Determines the routing tier (shared pool vs. dedicated pool)
3. Applies tenant-specific rate limits
4. Routes to the appropriate inference backend

```python
class TenantRouter:
    def __init__(self, config_store, rate_limiter):
        self.config_store = config_store
        self.rate_limiter = rate_limiter

    async def route_request(self, tenant_id: str, request: InferenceRequest):
        # 1. Get tenant config
        config = await self.config_store.get_tenant_config(tenant_id)
        if not config:
            raise TenantNotFoundError(tenant_id)

        # 2. Check rate limits
        if not await self.rate_limiter.check(tenant_id, request.estimated_tokens):
            raise RateLimitExceededError(tenant_id, config.rate_limit)

        # 3. Select model and backend
        model = config.model_mapping.get(request.model_alias, config.default_model)
        backend = self._select_backend(config.tier, model, request.priority)

        # 4. Apply tenant-specific prompt template
        processed_request = self._apply_template(request, config.prompt_templates)

        # 5. Route to backend
        return await backend.inference(processed_request, tenant_context={
            "tenant_id": tenant_id,
            "isolation_level": config.isolation_level,
            "data_region": config.data_region,
        })

    def _select_backend(self, tier: str, model: str, priority: str):
        if tier == "dedicated":
            return self.dedicated_pool.get_backend(model)
        elif priority == "batch":
            return self.batch_queue
        else:
            return self.shared_pool.get_backend(model)
```

**Data Isolation Strategy:**

Three tiers based on customer requirements and contract value:

| Tier | Isolation Level | How It Works | Use Case |
|------|----------------|--------------|----------|
| Standard | Logical | Shared DB with tenant_id column, row-level security | SMB customers |
| Premium | Schema | Separate database schema per tenant, shared cluster | Mid-market |
| Enterprise | Physical | Dedicated database instance and GPU allocation | Enterprise/regulated |

```python
class DataIsolationManager:
    def get_connection(self, tenant_id: str, isolation_level: str):
        if isolation_level == "physical":
            return self._get_dedicated_connection(tenant_id)
        elif isolation_level == "schema":
            conn = self._get_shared_connection()
            conn.execute(f"SET search_path TO tenant_{tenant_id}")
            return conn
        else:
            conn = self._get_shared_connection()
            conn.set_tenant_filter(tenant_id)  # Row-level security
            return conn
```

**Usage Metering and Billing:**

```python
class UsageMeter:
    """Track usage per tenant for billing and rate limiting."""

    async def record_usage(self, tenant_id: str, usage: UsageRecord):
        await self.usage_store.insert({
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow(),
            "model": usage.model,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "latency_ms": usage.latency_ms,
            "request_type": usage.request_type,  # real-time or batch
        })

        # Update running totals for rate limiting
        await self.rate_limiter.update_usage(
            tenant_id,
            tokens=usage.input_tokens + usage.output_tokens,
        )
```

### Step 4: Scaling Discussion

**Noisy Neighbor Prevention:**
- Dedicated GPU queues for enterprise tenants prevent resource contention
- Shared pool uses fair-share scheduling (weighted by contract tier)
- Circuit breakers per tenant: if one tenant causes errors, isolate them
- Request queuing with per-tenant priority lanes

**Horizontal Scaling:**
- Tenant Router is stateless -- scale horizontally behind a load balancer
- Model pools scale independently based on GPU utilization
- Add new GPU nodes without downtime using rolling deployment
- Batch processing queue auto-scales based on queue depth

**Multi-Region:**
- Deploy in US, EU, and APAC regions for data residency
- Tenant config specifies allowed regions
- Cross-region model replication for availability

### Step 5: Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Shared vs dedicated GPU pools | Cost efficiency vs isolation guarantees |
| Logical vs physical data isolation | Operational simplicity vs security assurance |
| Per-tenant model instances | Better isolation but higher cost and cold-start latency |
| Centralized vs distributed config | Simpler management vs single point of failure |
| Batch queue priority | Cost savings for tenants vs complexity in scheduling |

**What makes this an SE-specific problem:**
Unlike a pure infrastructure design, the SE must consider how to onboard new
tenants quickly, how to handle tenant-specific customization without code changes,
and how to explain the isolation guarantees to security-conscious customers during
the sales process.

---

### Problem 7: Customer Onboarding Pipeline

**Prompt**: "Design an automated customer onboarding pipeline for an AI API company
that takes a new customer from sign-up to production deployment in under 2 weeks."

### Step 1: Requirements Clarification

**Functional Requirements:**
- Self-service sign-up with immediate API key provisioning
- Guided onboarding flow (documentation, tutorials, sandbox environment)
- Automated POC environment setup with sample data
- Technical validation checkpoints (first API call, first integration, first production call)
- SE assignment and engagement triggers
- Customer health monitoring from day 1
- Integration with CRM (Salesforce), support (Zendesk), and billing (Stripe)

**Non-Functional Requirements:**
- Time to first API call: < 5 minutes after sign-up
- Time to production: < 2 weeks for standard use cases
- Support 500 new customers per month
- Personalized experience based on customer segment (startup, mid-market, enterprise)
- Track every customer interaction for analytics

**Clarifying Questions:**
- "What's the breakdown of self-service vs sales-assisted customers?"
- "What are the most common reasons customers get stuck during onboarding?"
- "How do we define 'production deployment' for tracking purposes?"
- "What existing tools does the team use today?"

### Step 2: High-Level Architecture

```
    ┌──────────────────────────────────────────────────────┐
    │                  Customer Journey                    │
    │  Sign-up → Sandbox → Build → Validate → Production  │
    └──────────┬───────────────────────────────────────────┘
               │
    ┌──────────▼──────────────────────────────────────────┐
    │             Onboarding Orchestrator                  │
    │   (State machine tracking each customer's progress)  │
    └──────────┬──────────────────────────────────────────┘
               │
    ┌──────────┼──────────────┬──────────────────┐
    │          │              │                  │
    ▼          ▼              ▼                  ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐
│Provisio│ │ Guide  │ │ Health   │ │  SE          │
│ning    │ │ Engine │ │ Monitor  │ │  Assignment  │
│Service │ │        │ │          │ │  Engine      │
└───┬────┘ └───┬────┘ └────┬─────┘ └──────┬───────┘
    │          │           │              │
    ▼          ▼           ▼              ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐
│API Keys│ │Docs/   │ │Usage     │ │CRM           │
│Sandbox │ │Tutoria │ │Analytics │ │(Salesforce)  │
│Env     │ │ls/SDK  │ │Alerts    │ │Slack/Email   │
└────────┘ └────────┘ └──────────┘ └──────────────┘
```

### Step 3: Component Deep-Dive

**Onboarding State Machine:**

Each customer progresses through defined stages with automated triggers:

```python
from enum import Enum
from datetime import datetime, timedelta

class OnboardingStage(Enum):
    SIGNED_UP = "signed_up"
    API_KEY_CREATED = "api_key_created"
    FIRST_API_CALL = "first_api_call"
    SANDBOX_ACTIVE = "sandbox_active"
    INTEGRATION_STARTED = "integration_started"
    FIRST_PRODUCTION_CALL = "first_production_call"
    PRODUCTION_STABLE = "production_stable"
    STALLED = "stalled"

class OnboardingOrchestrator:
    """State machine for customer onboarding."""

    STAGE_SLA = {
        OnboardingStage.SIGNED_UP: timedelta(minutes=5),      # Should create key quickly
        OnboardingStage.API_KEY_CREATED: timedelta(hours=24),  # Should make first call in 24h
        OnboardingStage.FIRST_API_CALL: timedelta(days=3),     # Should explore sandbox in 3 days
        OnboardingStage.SANDBOX_ACTIVE: timedelta(days=7),     # Should start integrating in a week
        OnboardingStage.INTEGRATION_STARTED: timedelta(days=14), # Should hit production in 2 weeks
    }

    async def advance_stage(self, customer_id: str, event: str):
        customer = await self.get_customer(customer_id)
        new_stage = self._determine_stage(customer, event)

        if new_stage != customer.current_stage:
            await self._update_stage(customer_id, new_stage)
            await self._trigger_actions(customer_id, new_stage)
            await self._notify_stakeholders(customer_id, new_stage)

    async def check_stalled_customers(self):
        """Run periodically to detect customers stuck at a stage."""
        for customer in await self.get_active_onboarding():
            sla = self.STAGE_SLA.get(customer.current_stage)
            if sla and customer.stage_entered_at + sla < datetime.utcnow():
                await self._handle_stall(customer)

    async def _handle_stall(self, customer):
        """Escalate stalled customers based on segment."""
        if customer.segment == "enterprise":
            # Immediately notify assigned SE
            await self.notify_se(customer, "Customer stalled at {customer.current_stage}")
        elif customer.segment == "mid_market":
            # Send automated help email, notify SE if still stalled in 24h
            await self.send_help_email(customer)
        else:
            # Self-service: send automated email with relevant resources
            await self.send_help_email(customer)
```

**SE Assignment Engine:**

Automatically assign SEs based on customer segment, industry, and SE capacity:

```python
class SEAssignmentEngine:
    """Assign SEs to customers based on fit and capacity."""

    async def assign_se(self, customer: Customer) -> str:
        if customer.segment == "self_service":
            return None  # No SE assigned for self-service

        # Get available SEs
        available_ses = await self.get_available_ses()

        # Score each SE for this customer
        scored = []
        for se in available_ses:
            score = self._calculate_fit_score(se, customer)
            scored.append((se, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        best_se = scored[0][0]

        await self.create_assignment(best_se.id, customer.id)
        await self.notify_se(best_se, customer)
        await self.update_crm(customer.id, se_id=best_se.id)

        return best_se.id

    def _calculate_fit_score(self, se, customer) -> float:
        score = 0.0

        # Industry expertise (40% weight)
        if customer.industry in se.industry_expertise:
            score += 40

        # Current capacity (30% weight) -- fewer accounts = higher score
        capacity_score = max(0, 30 - (se.active_accounts * 2))
        score += capacity_score

        # Timezone alignment (15% weight)
        if abs(se.timezone_offset - customer.timezone_offset) <= 3:
            score += 15

        # Language match (15% weight)
        if customer.preferred_language in se.languages:
            score += 15

        return score
```

**Health Monitoring from Day 1:**

```python
class OnboardingHealthMonitor:
    """Monitor customer health signals during onboarding."""

    async def daily_health_check(self):
        for customer in await self.get_onboarding_customers():
            signals = {
                "api_calls_today": await self.get_api_calls(customer.id, days=1),
                "api_calls_week": await self.get_api_calls(customer.id, days=7),
                "errors_today": await self.get_error_count(customer.id, days=1),
                "docs_pages_viewed": await self.get_docs_views(customer.id),
                "support_tickets": await self.get_ticket_count(customer.id),
                "days_since_signup": (datetime.utcnow() - customer.signup_date).days,
            }

            health = self._assess_health(signals)

            if health["status"] == "at_risk":
                await self._escalate(customer, health["reasons"])
            elif health["status"] == "engaged":
                await self._log_positive_signal(customer, health["reasons"])
```

### Step 4: Scaling Discussion

**Automation vs. Human Touch:**
- Self-service customers (80% of volume): Fully automated onboarding
- Mid-market (15%): Automated with SE check-ins at key milestones
- Enterprise (5%): SE-led with white-glove onboarding

**Personalization at Scale:**
- Segment customers by industry, use case, and technical maturity
- Auto-select relevant tutorials, sample code, and documentation
- Personalized email sequences based on onboarding stage and behavior

**Integration Points:**
- CRM (Salesforce): Customer data, SE assignments, deal tracking
- Support (Zendesk): Ticket creation, escalation workflows
- Billing (Stripe): Usage metering, plan upgrades
- Analytics (Mixpanel/Amplitude): Funnel tracking, drop-off analysis
- Communication (Slack/Email): Automated notifications, SE alerts

### Step 5: Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Fully automated vs SE-led onboarding | Scale vs personalization |
| Aggressive stall detection (24h) vs relaxed (7d) | Customer experience vs false alarms |
| Auto-assign SE at signup vs at first integration | Earlier relationship vs wasted SE time |
| Rich sandbox vs minimal sandbox | Better experience vs infrastructure cost |
| Proactive outreach vs wait for customer to ask | Customer appreciation vs annoyance |

**What makes this an SE-specific problem:**
The SE must understand the customer journey from a business perspective, not just
a technical one. The system must balance automation (for scale) with human touch
(for enterprise customers). The SE needs to explain to customers why certain
checkpoints exist and how the onboarding process is designed to get them to
production quickly and safely.
