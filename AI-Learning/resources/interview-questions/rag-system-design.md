# RAG System Design Interview Questions

10 system design questions focused on Retrieval-Augmented Generation. Each answer follows a structured format: Requirements Gathering, Architecture, Component Design, Tradeoffs, Evaluation, and Scaling.

---

## 1. Design a RAG system for legal document search

### Requirements Gathering

- How many documents? (thousands of contracts vs. millions of case filings)
- What types? (contracts, case law, statutes, regulations)
- Who are the users? (lawyers, paralegals, clients)
- Latency requirements? (interactive search vs. batch analysis)
- Accuracy requirements? (legal domain demands very high precision)
- Must responses cite specific sections/clauses?
- Multi-jurisdictional requirements?

### Architecture

```
+------------------+     +------------------+     +------------------+
|   Document       |     |   Ingestion      |     |   Vector Store   |
|   Sources        |---->|   Pipeline       |---->|   (Pinecone/     |
|   (S3/SharePoint)|     |                  |     |    Weaviate)     |
+------------------+     +--------+---------+     +--------+---------+
                                  |                         |
                         +--------v---------+               |
                         |   Metadata Store |               |
                         |   (PostgreSQL)   |               |
                         +--------+---------+               |
                                  |                         |
+------------------+     +--------v---------+     +---------v--------+
|   User Query     |---->|   Query Engine   |<----|   Retriever      |
|   Interface      |     |                  |     |   (Hybrid)       |
+------------------+     +--------+---------+     +------------------+
                                  |
                         +--------v---------+
                         |   LLM + Citation |
                         |   Generator      |
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   Response with  |
                         |   Citations      |
                         +------------------+
```

### Component Design

- **Document Processing**: PDF/DOCX parsing with layout-aware extraction (Unstructured.io). Preserve section headers, clause numbers, and page references.
- **Chunking**: Hierarchical chunking - split by section/clause boundaries, not arbitrary token windows. Maintain parent-child relationships (document > section > clause).
- **Embedding**: Legal-domain fine-tuned embeddings (e.g., fine-tune E5 or BGE on legal corpus). Store embeddings alongside metadata (doc type, jurisdiction, date, parties).
- **Retrieval**: Hybrid search combining dense (semantic) + sparse (BM25 for exact legal terms). Include metadata filtering (jurisdiction, document type, date range).
- **Generation**: LLM generates answers with mandatory inline citations (section, page, clause number). System prompt enforces "only answer from provided context" behavior.

### Tradeoffs

| Decision | Option A | Option B |
|----------|----------|----------|
| Chunking | Fixed-size (simple, uniform) | Section-based (preserves context, variable size) |
| Retrieval | Dense only (semantic) | Hybrid (catches exact legal terms) |
| LLM | Smaller/faster (GPT-3.5) | Larger/accurate (GPT-4/Claude) |
| Accuracy vs. Speed | Top-20 retrieval + reranking | Top-5 retrieval, faster response |

### Evaluation Strategy

- **Retrieval Metrics**: Recall@k, MRR, NDCG against lawyer-annotated relevance judgments
- **Generation Metrics**: Citation accuracy (does citation match source?), faithfulness (no hallucinated legal claims), answer completeness
- **Human Evaluation**: Lawyer review of answer quality on a 1-5 scale; track "acceptable for client use" rate
- **Regression Testing**: Golden set of 200+ query-answer pairs, run on every pipeline change

### Scaling Considerations

- Shard vector store by jurisdiction or document type
- Cache frequent queries (common contract clause lookups)
- Pre-compute embeddings for new documents asynchronously
- Consider tiered storage: hot (recent, frequently accessed) vs. cold (archived)

---

## 2. Design a RAG system for a customer support chatbot

### Requirements Gathering

- Number of knowledge base articles / FAQ entries?
- Expected query volume (QPS)?
- Support for multiple products/categories?
- Conversation history needed? (multi-turn?)
- Escalation path to human agents?
- Languages supported?
- Response time SLA?

### Architecture

```
+------------------+     +------------------+     +------------------+
|   Knowledge Base |     |   Ingestion      |     |   Vector Store   |
|   (Zendesk/      |---->|   Pipeline       |---->|   + BM25 Index   |
|    Confluence)   |     |   (scheduled)    |     |                  |
+------------------+     +------------------+     +--------+---------+
                                                           |
+------------------+     +------------------+     +--------v---------+
|   Customer Chat  |---->|   Query Router   |---->|   Retriever      |
|   Widget         |     |   + Classifier   |     |   (Hybrid)       |
+------------------+     +--------+---------+     +------------------+
                                  |
                         +--------v---------+
                         |  Conversation    |
                         |  Memory (Redis)  |
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   LLM Response   |
                         |   Generator      |
                         +--------+---------+
                                  |
                    +-------------+-------------+
                    |                           |
           +--------v---------+       +--------v---------+
           |   Confident      |       |   Low Confidence |
           |   Response       |       |   -> Escalate    |
           +------------------+       +------------------+
```

### Component Design

- **Knowledge Ingestion**: Sync from Zendesk/Confluence on a schedule (hourly). Parse articles, FAQ pairs, troubleshooting guides. Maintain source URL for "Learn more" links.
- **Query Router**: Classify intent (billing, technical, account, general). Route to specialized sub-indexes or apply metadata filters.
- **Conversation Memory**: Store last N turns in Redis with session ID. Inject recent turns into retrieval query for context-aware search.
- **Confidence Scoring**: If retrieval scores are below threshold or LLM confidence is low, escalate to human agent with conversation summary.
- **Response Generation**: Friendly, concise tone. Include "Was this helpful?" feedback mechanism for RLHF-style improvement.

### Tradeoffs

| Decision | Option A | Option B |
|----------|----------|----------|
| Memory | Stateless (simpler) | Multi-turn (better UX) |
| Routing | Single index | Per-category sub-indexes |
| Escalation | Always answer | Escalate on low confidence |
| Freshness | Real-time sync | Scheduled batch sync |

### Evaluation Strategy

- **Automated**: Answer relevance (RAGAS), retrieval precision, response latency P95
- **User Feedback**: Thumbs up/down on responses, track deflection rate (issues resolved without human)
- **Business Metrics**: Ticket volume reduction, average resolution time, CSAT score
- **A/B Testing**: Compare RAG chatbot vs. traditional FAQ search vs. human-only support

### Scaling Considerations

- Horizontal scaling of retrieval service behind load balancer
- Rate limiting per customer/session to prevent abuse
- Edge caching for common queries (top 100 questions cover 60%+ of traffic)
- Multi-region deployment for global customers

---

## 3. Design a RAG system that scales to 10M documents

### Requirements Gathering

- Document size distribution? (average tokens per doc)
- Query volume (QPS)?
- Latency SLA? (P50, P99)
- Update frequency? (static corpus vs. daily additions)
- Query complexity? (simple keyword vs. complex multi-hop)
- Budget constraints?
- Data residency requirements?

### Architecture

```
+------------------+     +------------------+     +------------------+
|   Document       |     |   Distributed    |     |   Sharded Vector |
|   Lake (S3)      |---->|   Ingestion      |---->|   Store          |
|   10M+ docs      |     |   (Spark/Ray)    |     |   (Milvus/       |
+------------------+     +--------+---------+     |    Qdrant)       |
                                  |               +--------+---------+
                         +--------v---------+              |
                         |   Metadata DB    |              |
                         |   (PostgreSQL +  |              |
                         |    partitioning) |              |
                         +--------+---------+              |
                                  |                        |
+------------------+     +--------v---------+     +--------v---------+
|   Query          |---->|   Query Planner  |---->|   Distributed    |
|                  |     |   + Router       |     |   Retrieval      |
+------------------+     +--------+---------+     +--------+---------+
                                                           |
                                                  +--------v---------+
                                                  |   Reranker       |
                                                  |   (Cross-encoder)|
                                                  +--------+---------+
                                                           |
                                                  +--------v---------+
                                                  |   LLM Generator  |
                                                  +------------------+
```

### Component Design

- **Distributed Ingestion**: Use Spark or Ray to parallelize document processing across a cluster. Chunk, embed, and index in parallel. Target throughput: 10K docs/hour.
- **Sharded Vector Store**: Partition by document category, date range, or hash. Use Milvus or Qdrant with multiple shards. Each shard holds ~1-2M vectors.
- **Two-Stage Retrieval**: Stage 1 - fast ANN retrieval (top-100 from vector store). Stage 2 - cross-encoder reranking (top-100 -> top-10). This balances speed with accuracy.
- **Query Planning**: For complex queries, decompose into sub-queries, retrieve independently, merge results.
- **Caching Layer**: Redis cache for frequent queries. LRU cache for embedding computations. Result cache with TTL.

### Tradeoffs

| Decision | Option A | Option B |
|----------|----------|----------|
| Vector DB | Managed (Pinecone) - simpler ops | Self-hosted (Milvus) - more control |
| Sharding | By category (query routing) | By hash (even distribution) |
| Reranking | Cross-encoder (accurate, slow) | ColBERT (fast, less accurate) |
| Embedding | Single model (simple) | Domain-specific per shard |

### Evaluation Strategy

- **Load Testing**: Simulate 1000 QPS with realistic query distribution
- **Retrieval Quality**: Sample 1000 queries, measure Recall@10, Recall@100 against human labels
- **Latency Profiling**: Break down P50/P95/P99 by stage (embedding, retrieval, reranking, generation)
- **Index Quality**: Monitor embedding drift, measure index fragmentation over time

### Scaling Considerations

- Vector store: horizontal sharding with consistent hashing for even distribution
- Ingestion: auto-scaling worker pool based on queue depth
- Read replicas for vector store during peak traffic
- Incremental indexing (don't rebuild entire index for new documents)
- Consider approximate methods (HNSW with tuned ef/M parameters) for latency
- Budget: at 10M docs with 1536-dim embeddings, expect ~60GB vector storage

---

## 4. How would you handle document updates in a RAG system?

### Requirements Gathering

- Update frequency? (real-time, hourly, daily)
- Update types? (full document replacement, partial edits, deletions)
- Consistency requirements? (eventual vs. strong)
- Can users see stale results temporarily?
- Document versioning needed?
- Audit trail requirements?

### Architecture

```
+------------------+     +------------------+
|   Document       |     |   Change         |
|   Source          |---->|   Detection      |
|                  |     |   (CDC / Webhook)|
+------------------+     +--------+---------+
                                  |
                    +-------------+-------------+
                    |                           |
           +--------v---------+       +--------v---------+
           |   Create/Update  |       |   Delete         |
           |   Pipeline       |       |   Pipeline       |
           +--------+---------+       +--------+---------+
                    |                           |
           +--------v---------+       +--------v---------+
           |   Re-chunk &     |       |   Remove vectors |
           |   Re-embed       |       |   + metadata     |
           +--------+---------+       +--------+---------+
                    |                           |
                    +-------------+-------------+
                                  |
                         +--------v---------+
                         |   Vector Store   |
                         |   (Upsert)       |
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   Invalidate     |
                         |   Cache          |
                         +------------------+
```

### Component Design

- **Change Detection**: CDC (Change Data Capture) from source DB, or webhooks from CMS. Track document hash to detect content changes. Maintain a change log table.
- **Document Versioning**: Store version ID with each chunk. On update, create new version chunks and tombstone old ones. Support "as-of" queries for compliance.
- **Chunk Mapping**: Maintain a mapping table: `document_id -> [chunk_ids]`. On document update, delete all old chunks and re-chunk/re-embed the entire document (simpler than diff-based updates).
- **Cache Invalidation**: Invalidate cached query results that referenced the updated document. Use document-to-query mapping or TTL-based expiration.
- **Consistency**: Use a "double-write" pattern: write new chunks, verify searchable, then delete old chunks. Prevents missing results during update window.

### Tradeoffs

| Decision | Option A | Option B |
|----------|----------|----------|
| Update granularity | Full re-chunk (simple, consistent) | Diff-based (efficient, complex) |
| Consistency | Strong (lock during update) | Eventual (faster, brief staleness) |
| Versioning | Keep all versions (audit) | Latest only (simpler, less storage) |
| Detection | Polling (simple) | CDC/Webhooks (real-time, complex) |

### Evaluation Strategy

- **Freshness Metrics**: Time from source update to searchable in vector store (target < 5 min)
- **Consistency Tests**: Query immediately after update, verify new content is returned
- **Regression Tests**: Verify updates don't degrade retrieval quality on unchanged documents
- **Orphan Detection**: Periodic audit for chunks without valid parent documents

### Scaling Considerations

- Batch updates during off-peak hours for large corpus refreshes
- Prioritize updates by document importance/query frequency
- Use message queue (Kafka/SQS) to decouple detection from processing
- Monitor update queue depth; alert on growing backlog
- For high-frequency updates, consider streaming architecture

---

## 5. Design a multi-modal RAG system (text + images)

### Requirements Gathering

- What modalities? (text, images, tables, diagrams, charts)
- Are images standalone or embedded in documents?
- Should the system answer questions about image content?
- Output modality? (text only, or text + relevant images?)
- Document types? (PDFs with figures, web pages, slide decks)
- Latency requirements?

### Architecture

```
+------------------+     +------------------+     +------------------+
|   Documents with |     |   Multi-modal    |     |   Text Embedding |
|   Text + Images  |---->|   Parser         |---->|   Store          |
|                  |     |                  |     +------------------+
+------------------+     +--------+---------+
                                  |               +------------------+
                                  +-------------->|   Image Embedding|
                                  |               |   Store (CLIP)   |
                                  |               +------------------+
                                  |
                                  |               +------------------+
                                  +-------------->|   Image Caption  |
                                                  |   Store          |
                                                  +------------------+

+------------------+     +------------------+     +------------------+
|   User Query     |---->|   Query          |---->|   Multi-index    |
|   (text/image)   |     |   Encoder        |     |   Retriever      |
+------------------+     +------------------+     +--------+---------+
                                                           |
                                                  +--------v---------+
                                                  |   Result Fusion  |
                                                  |   + Reranking    |
                                                  +--------+---------+
                                                           |
                                                  +--------v---------+
                                                  |   Multi-modal LLM|
                                                  |   (GPT-4V/Claude)|
                                                  +------------------+
```

### Component Design

- **Document Parsing**: Use layout-aware parsers (Unstructured, DocTR) to extract text and images separately while preserving spatial relationships. Extract tables as structured data.
- **Image Processing Pipeline**: (1) Generate captions using a vision-language model (BLIP-2, LLaVA). (2) Create CLIP embeddings for visual similarity search. (3) OCR for text in images. Store all three representations.
- **Dual Embedding Space**: Text chunks get text embeddings (E5/BGE). Images get CLIP embeddings. Captions bridge the two spaces (text embedding of image description).
- **Cross-Modal Retrieval**: Text query retrieves from both text index and caption index. Image query retrieves from CLIP index. Fuse results using reciprocal rank fusion (RRF).
- **Generation**: Pass retrieved text chunks AND relevant images directly to a multi-modal LLM (GPT-4V, Claude) for answer generation.

### Tradeoffs

| Decision | Option A | Option B |
|----------|----------|----------|
| Image representation | CLIP only (visual) | CLIP + captions (richer text search) |
| Fusion | Early fusion (single index) | Late fusion (separate indexes, merge) |
| LLM | Text-only (cheaper) | Multi-modal (can reason about images) |
| Storage | Store images inline | Store image references + thumbnails |

### Evaluation Strategy

- **Cross-Modal Retrieval**: Can text queries find relevant images? Can image queries find relevant text?
- **Caption Quality**: Human evaluation of generated captions (accuracy, completeness)
- **End-to-End**: Answer quality on questions requiring both text and image understanding
- **Benchmark**: Use datasets like DocVQA, ChartQA, or custom domain-specific test sets

### Scaling Considerations

- Image storage and embedding computation are expensive; pre-compute and cache
- CLIP embeddings are 512-dim (smaller than text embeddings), but image storage is large
- Consider CDN for serving images in responses
- Batch image processing with GPU workers
- Progressive enhancement: start with caption-based retrieval, add visual retrieval later

---

## 6. How would you debug a RAG system with low relevancy scores?

### Requirements Gathering

- What metric is low? (retrieval recall, answer relevance, faithfulness?)
- Is it across all queries or specific query types?
- When did it start? (recent regression or always low?)
- What's the baseline? (how did you measure before?)
- Do you have labeled data for evaluation?
- What does the current pipeline look like?

### Architecture (Debugging Pipeline)

```
+------------------+
|   Identify the   |
|   Failure Mode   |
+--------+---------+
         |
+--------v---------+     +------------------+
|   Is retrieval   |---->|   YES: Debug     |
|   finding the    |     |   Generation     |
|   right chunks?  |     |   (prompt, LLM)  |
+--------+---------+     +------------------+
         | NO
+--------v---------+
|   Retrieval      |
|   Debug Pipeline |
+--------+---------+
         |
+--------v----------------------------+-----------------------------+
|                                     |                             |
+--------v---------+     +------------v-------+     +---------------v--+
|   Chunking       |     |   Embedding        |     |   Index/Search   |
|   Analysis       |     |   Analysis         |     |   Analysis       |
+------------------+     +--------------------+     +------------------+

For each query:
+------------------+     +------------------+     +------------------+
|   1. Log query   |---->|   2. Log top-k   |---->|   3. Log LLM    |
|   + embedding    |     |   chunks + scores|     |   input/output  |
+------------------+     +------------------+     +------------------+
```

### Component Design (Debugging Steps)

1. **Isolate the Problem**: Separate retrieval quality from generation quality. Manually check if retrieved chunks contain the answer. If chunks are good but answer is bad -> generation problem. If chunks are bad -> retrieval problem.

2. **Chunking Analysis**:
   - View actual chunks for failing queries. Are they too small (missing context)? Too large (diluted relevance)?
   - Check for splitting errors (chunk boundary in the middle of a key paragraph)
   - Verify metadata is correct (wrong category, missing fields)

3. **Embedding Analysis**:
   - Compute cosine similarity between query embedding and expected chunk embedding
   - Visualize embeddings with UMAP/t-SNE to find clustering issues
   - Test if a different embedding model scores better on your domain

4. **Query Analysis**:
   - Are queries too vague? Try query expansion or HyDE (hypothetical document embeddings)
   - Are queries using different vocabulary than documents? Check for domain terminology gaps
   - Try query rewriting with an LLM before retrieval

5. **Index Configuration**:
   - Check ANN parameters (HNSW ef_search too low = missing results)
   - Verify correct distance metric (cosine vs. L2 vs. dot product)
   - Check if index needs rebuilding after large batch inserts

### Tradeoffs

| Fix | Effort | Impact |
|-----|--------|--------|
| Adjust chunk size | Low | Medium |
| Add query rewriting | Low | High |
| Change embedding model | Medium | High |
| Add reranker | Medium | High |
| Fine-tune embeddings | High | Very High |
| Restructure chunking | High | High |

### Evaluation Strategy

- **Build a test set**: 100+ query-expected_chunk pairs for automated regression
- **Per-stage metrics**: Retrieval Recall@k, Reranker NDCG, Answer Faithfulness, Answer Relevance
- **Logging**: Log every stage (query -> retrieved chunks -> reranked chunks -> LLM input -> LLM output) for debugging
- **A/B comparisons**: Test changes on the same query set before deploying

### Scaling Considerations

- Automated evaluation pipeline that runs on every change (CI/CD for RAG)
- Dashboard showing retrieval quality metrics over time
- Alert on metric degradation (e.g., average relevance score drops 10%)
- Periodic human evaluation cadence (weekly review of 50 random queries)

---

## 7. Design a RAG system with multi-step reasoning

### Requirements Gathering

- What types of multi-step questions? (comparison, aggregation, temporal reasoning)
- How many "hops" typically needed? (2-hop, 3-hop, open-ended)
- Acceptable latency? (multi-step = multiple LLM calls)
- Should the user see intermediate reasoning steps?
- Cost constraints? (more steps = more LLM calls)

### Architecture

```
+------------------+     +------------------+
|   Complex Query  |---->|   Query          |
|                  |     |   Decomposer     |
+------------------+     +--------+---------+
                                  |
                         +--------v---------+
                         |   Sub-question 1 |----> Retrieve -> Answer
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   Sub-question 2 |----> Retrieve -> Answer
                         |   (informed by   |      (may use answer 1
                         |    answer 1)     |       as context)
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   Sub-question N |----> Retrieve -> Answer
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   Synthesizer    |
                         |   (combine all   |
                         |    sub-answers)  |
                         +--------+---------+
                                  |
                         +--------v---------+
                         |   Verification   |
                         |   Step           |
                         +------------------+
```

### Component Design

- **Query Decomposer**: LLM breaks complex query into ordered sub-questions. Example: "How did company X's revenue compare to company Y's in Q3 vs Q4?" becomes: (1) "What was company X's Q3 revenue?" (2) "What was company X's Q4 revenue?" (3) "What was company Y's Q3 revenue?" (4) "What was company Y's Q4 revenue?"
- **Iterative Retriever**: Each sub-question triggers its own retrieval. Later sub-questions can incorporate earlier answers into the retrieval query for better targeting.
- **Reasoning Chain**: Use chain-of-thought prompting at each step. Maintain a "scratchpad" of accumulated facts.
- **Synthesizer**: Final LLM call combines all sub-answers into a coherent response. Handles comparison, aggregation, and reasoning across sub-answers.
- **Verification**: Optional step where LLM checks if the final answer is consistent with the retrieved evidence. Flag low-confidence answers.

### Tradeoffs

| Decision | Option A | Option B |
|----------|----------|----------|
| Decomposition | LLM-based (flexible) | Template-based (faster, limited) |
| Execution | Sequential (uses prior answers) | Parallel (faster, independent) |
| Verification | Always verify (slower, safer) | Skip verification (faster) |
| Transparency | Show reasoning chain | Show final answer only |

### Evaluation Strategy

- **Sub-question quality**: Are decomposed questions correct and sufficient?
- **Per-hop accuracy**: Is each intermediate answer correct?
- **End-to-end accuracy**: Is the final synthesized answer correct?
- **Benchmark**: Use multi-hop QA datasets (HotpotQA, MuSiQue, 2WikiMultiHopQA)
- **Cost tracking**: Average number of LLM calls per query

### Scaling Considerations

- Parallelize independent sub-questions to reduce latency
- Cache sub-question answers (same sub-question may recur across different queries)
- Set maximum hop count (3-5) to prevent runaway chains
- Streaming: show intermediate results as each step completes
- Cost budgeting: more complex queries cost more; implement per-query cost limits

---

## 8. Compare chunking strategies for technical documentation

### Requirements Gathering

- Document type? (API docs, tutorials, reference manuals, RFCs)
- Document format? (Markdown, HTML, PDF, RST)
- Average document length?
- Query types? (concept lookup, code example search, troubleshooting)
- Embedding model and its max token limit?

### Architecture (Chunking Strategy Comparison)

```
Same documents -> 5 chunking strategies -> same queries -> compare metrics

Strategy 1: Fixed-size          [====][====][====][====]
Strategy 2: Sentence-based      [sent1 sent2][sent3 sent4 sent5][sent6]
Strategy 3: Recursive/Markdown  [# Section 1...][## Sub 1.1...][## Sub 1.2...]
Strategy 4: Semantic             [topic A sentences][topic B sentences]
Strategy 5: Hierarchical        [Parent: Section][Child: Paragraph][Child: Paragraph]

                    +------------------+
                    |   Evaluation     |
                    |   on test set    |
                    +------------------+
```

### Component Design (Strategy Details)

**Strategy 1: Fixed-Size with Overlap**
- Split every N tokens with M token overlap
- Pros: Simple, predictable chunk size, works with any content
- Cons: Splits mid-sentence/paragraph, loses structural context
- Best for: Homogeneous text without clear structure

**Strategy 2: Sentence-Based**
- Group sentences up to a token limit, split on sentence boundaries
- Pros: Never splits mid-sentence, readable chunks
- Cons: Ignores document structure, variable chunk sizes
- Best for: Narrative text, blog posts

**Strategy 3: Recursive / Structure-Aware (Markdown/HTML)**
- Split on headers (H1 > H2 > H3), then paragraphs, then sentences
- Pros: Preserves document hierarchy, chunks are topically coherent
- Cons: Very uneven chunk sizes (some sections are huge, some tiny)
- Best for: Technical documentation with clear heading structure

**Strategy 4: Semantic Chunking**
- Compute sentence embeddings, split where similarity drops (breakpoint detection)
- Pros: Chunks are topically coherent regardless of document structure
- Cons: Expensive (requires embedding every sentence), harder to debug
- Best for: Long-form content without clear structure

**Strategy 5: Hierarchical (Parent-Child)**
- Create multiple chunk levels: large parent chunks (for context) and small child chunks (for precision). Retrieve child, return parent for context.
- Pros: Best of both worlds (precision + context)
- Cons: Complex indexing, more storage, harder to maintain
- Best for: Large-scale production systems where quality matters

### Tradeoffs

| Strategy | Retrieval Precision | Context Quality | Implementation | Storage |
|----------|-------------------|-----------------|----------------|---------|
| Fixed-size | Medium | Low | Trivial | 1x |
| Sentence | Medium-High | Medium | Simple | 1x |
| Recursive | High | High | Medium | 1x |
| Semantic | High | High | Complex | 1x |
| Hierarchical | Very High | Very High | Complex | 2-3x |

### Evaluation Strategy

- **A/B test on real queries**: Same 200 queries across all strategies, measure Recall@5, MRR
- **Chunk quality audit**: Manually review 50 chunks per strategy for coherence
- **End-to-end answer quality**: Does better chunking lead to better final answers?
- **Edge cases**: Test on very short docs, very long docs, code-heavy docs, table-heavy docs

### Scaling Considerations

- Fixed-size and sentence-based are cheapest to compute and maintain
- Semantic chunking requires GPU for sentence embeddings at scale
- Hierarchical requires 2-3x vector storage
- Recommendation: Start with recursive/structure-aware, upgrade to hierarchical if quality demands justify the complexity

---

## 9. Design a hybrid retrieval system (dense + sparse + reranking)

### Requirements Gathering

- Corpus characteristics? (technical jargon, acronyms, mixed languages)
- Query characteristics? (keyword-heavy vs. natural language)
- Latency budget? (total time for retrieval + reranking)
- Accuracy requirements?
- Infrastructure constraints? (managed services vs. self-hosted)

### Architecture

```
+------------------+
|   User Query     |
+--------+---------+
         |
         +---------------------------+
         |                           |
+--------v---------+     +-----------v------+
|   Dense Retrieval|     |   Sparse Retrieval|
|   (Embedding +   |     |   (BM25 /        |
|    ANN Search)   |     |    Elasticsearch) |
+--------+---------+     +-----------+------+
         |                           |
         |   Top-100 each            |   Top-100 each
         |                           |
+--------v---------------------------v------+
|              Result Fusion                |
|   (Reciprocal Rank Fusion / Weighted)     |
+---------------------+--------------------+
                      |
                      |   Top-100 fused
                      |
              +-------v--------+
              |   Cross-Encoder|
              |   Reranker     |
              |   (top-100 ->  |
              |    top-10)     |
              +-------+--------+
                      |
              +-------v--------+
              |   Final top-k  |
              |   to LLM       |
              +----------------+
```

### Component Design

- **Dense Retrieval**: Encode query with embedding model (E5-large, BGE-large). ANN search in vector store (HNSW index). Good at semantic similarity, paraphrasing, and conceptual matching.
- **Sparse Retrieval**: BM25 via Elasticsearch or Lucene. Good at exact keyword matching, acronyms, proper nouns, and rare terms that embedding models may not capture.
- **Result Fusion**: Reciprocal Rank Fusion (RRF): `score = sum(1 / (k + rank_i))` across retrieval methods. Alternative: weighted linear combination of normalized scores. RRF is parameter-free and robust.
- **Cross-Encoder Reranker**: Pass (query, document) pairs through a cross-encoder model (ms-marco-MiniLM, BGE-reranker). Much more accurate than bi-encoders but expensive (can't be pre-computed). Only feasible on top-100 candidates.
- **Score Calibration**: Normalize scores from different retrievers before fusion. Dense scores are cosine similarities [0,1]; BM25 scores are unbounded.

### Tradeoffs

| Decision | Option A | Option B |
|----------|----------|----------|
| Fusion method | RRF (parameter-free) | Weighted (tunable but needs optimization) |
| Reranker model | Small (MiniLM - fast) | Large (BGE-large - accurate) |
| Candidate pool | Top-50 (faster reranking) | Top-200 (better recall, slower) |
| Sparse engine | BM25 only | BM25 + SPLADE (learned sparse) |

### Evaluation Strategy

- **Ablation Study**: Measure each component independently: dense only, sparse only, dense+sparse, dense+sparse+reranker
- **Metrics**: Recall@100 (retrieval stage), NDCG@10 (after reranking), MRR
- **Latency Breakdown**: Measure time per stage under load
- **Per-Query Analysis**: Identify query types where sparse wins vs. dense wins

### Scaling Considerations

- Dense + sparse retrieval can run in parallel (latency = max, not sum)
- Reranking is the bottleneck; batch GPU inference helps
- Consider ColBERT as a middle ground (token-level late interaction, faster than cross-encoder)
- Cache reranker results for frequent queries
- SPLADE (learned sparse) can replace BM25 for better quality at similar cost

---

## 10. How would you evaluate a RAG system in production?

### Requirements Gathering

- What does "good" look like? (accuracy, latency, user satisfaction)
- Do you have labeled evaluation data?
- Evaluation cadence? (real-time monitoring vs. periodic batch eval)
- Budget for human evaluation?
- Regulatory requirements? (auditability, explainability)

### Architecture

```
+------------------+     +------------------+     +------------------+
|   Production     |---->|   Logging &      |---->|   Evaluation     |
|   RAG System     |     |   Telemetry      |     |   Pipeline       |
+------------------+     +------------------+     +--------+---------+
                                                           |
                    +--------------------------------------+
                    |                |                      |
           +--------v------+  +-----v--------+  +---------v--------+
           |  Automated    |  |  LLM-as-     |  |  Human          |
           |  Metrics      |  |  Judge       |  |  Evaluation     |
           +---------+-----+  +------+-------+  +--------+--------+
                     |               |                    |
                     +---------------+--------------------+
                                     |
                            +--------v---------+
                            |   Dashboard &    |
                            |   Alerting       |
                            +------------------+
```

### Component Design

**Tier 1: Automated Metrics (Real-time)**
- Retrieval: Average similarity score, number of chunks retrieved, empty result rate
- Generation: Response length, latency (P50/P95/P99), token usage, error rate
- System: Throughput (QPS), cache hit rate, index freshness

**Tier 2: LLM-as-Judge (Daily/Weekly Batch)**
- Faithfulness: Does the answer only use information from retrieved context? (use RAGAS)
- Relevance: Does the answer address the user's question?
- Completeness: Does the answer cover all aspects of the question?
- Harmfulness: Does the answer contain harmful or inappropriate content?
- Run on a sample of 500-1000 queries per evaluation cycle

**Tier 3: Human Evaluation (Weekly/Monthly)**
- Expert review of 50-100 queries per week on a 1-5 scale
- Focus on edge cases and LLM-judge disagreements
- Build golden dataset iteratively from human evaluations
- Inter-annotator agreement tracking

**User Feedback Signals**
- Explicit: thumbs up/down, "was this helpful?", report buttons
- Implicit: query reformulation (indicates bad first answer), click-through on citations, session length, escalation to human

### Tradeoffs

| Method | Coverage | Cost | Latency | Reliability |
|--------|----------|------|---------|-------------|
| Automated metrics | 100% | Very Low | Real-time | Low (proxies) |
| LLM-as-Judge | Sampled | Medium | Hours | Medium |
| Human eval | Sampled | High | Days | High |
| User feedback | Self-selected | Low | Real-time | Medium (biased) |

### Evaluation Strategy

- **Offline Eval**: Golden test set of 500+ query-answer pairs. Run before every deployment. Gate deployments on metric regression.
- **Online Eval**: A/B test new pipeline versions. Use interleaved retrieval (show results from both versions, measure preference).
- **Continuous Monitoring**: Dashboard with key metrics. Alert on: relevance score drop > 10%, empty retrieval rate > 5%, latency P99 > 3s, error rate > 1%.
- **Evaluation of Evaluation**: Measure correlation between LLM-judge scores and human scores. Recalibrate judge prompts quarterly.

### Scaling Considerations

- Logging at scale: structured logs to data warehouse (BigQuery/Snowflake), not just application logs
- Sampling strategy: random + stratified (ensure coverage of rare query types)
- Cost management: LLM-as-judge costs scale with sample size; budget accordingly
- Feedback loops: route low-scoring queries back to knowledge base team for content improvement
- Versioning: track evaluation results by pipeline version for historical comparison
