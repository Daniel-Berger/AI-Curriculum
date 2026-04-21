# Module 08: Advanced RAG Techniques

## Why This Module Matters

Basic RAG works, but production systems need refinement. Advanced techniques include:
- **HyDE**: Hypothetical Document Embeddings for better semantic matching
- **Multi-Query**: Multiple reformulations for robustness
- **Re-ranking**: Two-stage retrieval for precision
- **GraphRAG**: Structured knowledge for complex queries
- **RAGAS**: Evaluation framework for RAG systems

These improve quality and are frequently discussed in senior-level interviews.

---

## Hypothetical Document Embeddings (HyDE)

### The Problem

Query: "What is the capital of France?"
Naive embeddings might not match documents well because the query is a question, not a statement.

### The Solution

Generate hypothetical relevant documents, embed those, then use for retrieval.

```python
def hyde_retrieval(query):
    # Step 1: Generate hypothetical document
    hypothesis = llm.generate(f"""
    Generate a short hypothetical document that would answer this query:
    {query}
    """)

    # Step 2: Embed the hypothesis (not the original query)
    hypothesis_embedding = embed_model.encode(hypothesis)

    # Step 3: Retrieve documents similar to the hypothesis
    results = vector_db.search(hypothesis_embedding, top_k=5)

    return results
```

### Why It Works

- Hypothesis is in "document language" not "question language"
- Better semantic alignment with actual documents
- Improves retrieval especially for factual questions

---

## Multi-Query Retrieval

### The Problem

Single retrieval misses documents using different terminology.

Query: "machine learning"
Might not retrieve: "deep neural networks", "statistical learning", "AI"

### The Solution

Generate multiple paraphrases and retrieve from all, then combine results.

```python
def multi_query_retrieval(query, num_queries=3):
    # Generate paraphrases
    paraphrases = llm.generate(f"""
    Generate {num_queries} different ways to ask this question:
    {query}

    Return as a list, one per line.
    """).split('\n')

    # Retrieve for each paraphrase
    all_results = []
    for paraphrase in paraphrases:
        results = retrieve(paraphrase, top_k=3)
        all_results.extend(results)

    # Deduplicate and rerank by frequency
    unique_docs = {}
    for doc in all_results:
        doc_id = doc['id']
        if doc_id not in unique_docs:
            unique_docs[doc_id] = doc
        else:
            unique_docs[doc_id]['score'] += doc['score']

    # Sort by combined score
    return sorted(unique_docs.values(), key=lambda x: x['score'], reverse=True)
```

---

## Re-Ranking

### Two-Stage Retrieval

```
Stage 1: Candidate Retrieval (Fast, Broad)
  - Vector similarity
  - BM25
  - Result: Top-50 candidates

Stage 2: Re-Ranking (Slow, Precise)
  - Cross-encoder for relevance
  - LLM evaluation
  - Result: Top-5 reranked
```

### Cross-Encoder Re-Ranking

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

def rerank_results(query, candidates, top_k=5):
    # Score all candidates
    scores = reranker.predict([(query, doc['text']) for doc in candidates])

    # Sort by score
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

    return [doc for doc, score in ranked[:top_k]]
```

### LLM-based Re-Ranking

```python
def llm_rerank(query, candidates, top_k=5):
    ranking_prompt = f"""
    Rank these documents by relevance to the query:
    Query: {query}

    Documents:
    {'\n'.join([f"{i+1}. {doc['text'][:200]}" for i, doc in enumerate(candidates)])}

    Respond with a comma-separated list of document numbers, most relevant first.
    """

    ranking_str = llm.generate(ranking_prompt)
    ranking = [int(x.strip()) - 1 for x in ranking_str.split(',')]

    return [candidates[i] for i in ranking[:top_k] if i < len(candidates)]
```

---

## GraphRAG

### Concept

Instead of flat document retrieval, structure knowledge as a graph:
- **Nodes**: Entities (people, places, concepts)
- **Edges**: Relationships
- **Reasoning**: Multi-hop queries across connected entities

### Example

```
Query: "Who did Alice collaborate with?"

Graph:
  Alice --collaborated_with--> Bob
  Bob --managed_project--> ProjectX
  Alice --wrote_paper_for--> ProjectX

Multi-hop reasoning:
  1. Find Alice's collaborators: Bob
  2. Find Bob's projects: ProjectX
  3. Result: Alice collaborated with Bob on ProjectX
```

### Implementation Pattern

```python
class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}  # entity_id -> {name, type, properties}
        self.edges = {}  # (source, target) -> {relation_type, weight}

    def add_entity(self, entity_id, name, entity_type):
        self.nodes[entity_id] = {'name': name, 'type': entity_type}

    def add_relationship(self, source, target, relation, weight=1.0):
        self.edges[(source, target)] = {'relation': relation, 'weight': weight}

    def find_multi_hop_paths(self, start, hops=2):
        # BFS to find connected entities within hop distance
        paths = []
        visited = {start}
        queue = [(start, [])]

        for _ in range(hops):
            next_queue = []
            for node, path in queue:
                for (s, t), edge in self.edges.items():
                    if s == node and t not in visited:
                        next_queue.append((t, path + [edge['relation']]))
                        visited.add(t)
            queue = next_queue

        return queue
```

---

## RAGAS Evaluation

### Metrics

**Faithfulness**: Does the answer only use retrieved context? (Avoid hallucination)

```
Prompt LLM: "Is this statement supported by the context?
Context: {context}
Statement: {answer}"

Score: 0-1, higher = more faithful
```

**Answer Relevance**: Does the answer address the question?

```
Score LLM: "How relevant is this answer to the question?
Question: {question}
Answer: {answer}"

Score: 0-1
```

**Context Relevance**: Are retrieved documents relevant to the question?

```
Score LLM: "How relevant is this context to the question?
Question: {question}
Context: {context}"

Score: 0-1
```

**Context Utilization**: Does the answer actually use the context?

```
If answer matches context verbatim: low score (plagiarism)
If answer ignores context: low score (not using retrieval)
If answer synthesizes context: high score
```

### Implementation

```python
def evaluate_rag_system(question, retrieved_docs, answer):
    metrics = {}

    # 1. Faithfulness
    faithfulness_prompt = f"""
    Is this answer grounded in the provided context?
    Context: {' '.join(retrieved_docs)}
    Answer: {answer}

    Rate 0-1:"""
    metrics['faithfulness'] = score_llm(faithfulness_prompt)

    # 2. Relevance of retrieved docs
    relevance_prompt = f"""
    How relevant are these documents to the question?
    Question: {question}
    Docs: {' '.join(retrieved_docs)}

    Rate 0-1:"""
    metrics['context_relevance'] = score_llm(relevance_prompt)

    # 3. Answer quality
    quality_prompt = f"""
    How well does this answer address the question?
    Question: {question}
    Answer: {answer}

    Rate 0-1:"""
    metrics['answer_relevance'] = score_llm(quality_prompt)

    return metrics
```

---

## Adaptive Retrieval

### When to Retrieve More?

```python
def adaptive_retrieval(query, initial_k=3):
    results = retrieve(query, top_k=initial_k)

    # Check if top result is confident
    top_score = results[0]['score']

    if top_score < 0.7:  # Low confidence threshold
        # Retrieve more documents
        more_results = retrieve(query, top_k=10)
        results = more_results
    elif len(results) > 0 and results[-1]['score'] > 0.5:
        # Previous results were confident, could retrieve fewer
        results = results[:initial_k // 2]

    return results
```

### Recursive Refinement

```python
def recursive_rag(query, depth=0, max_depth=2):
    if depth >= max_depth:
        return llm.generate(f"Answer: {query}")

    # Retrieve and answer
    docs = retrieve(query, top_k=3)
    answer = llm.generate(f"Based on:\n{docs}\n\nAnswer: {query}")

    # Check if we need to refine
    followup_prompt = f"""
    Is this answer complete or do we need more information?
    {answer}

    If incomplete, what additional information is needed?
    """
    refinement = llm.generate(followup_prompt)

    if "more information" in refinement.lower():
        # Recursive call with refined query
        return recursive_rag(refinement, depth=depth+1, max_depth=max_depth)
    else:
        return answer
```

---

## Production Considerations

### Caching

Cache embeddings and results to reduce costs:

```python
cache = {}

def cached_retrieve(query, top_k=5):
    cache_key = (query, top_k)
    if cache_key in cache:
        return cache[cache_key]

    results = retrieve(query, top_k=top_k)
    cache[cache_key] = results
    return results
```

### Monitoring

Track metrics continuously:

```python
def log_rag_metrics(query, results, answer, user_satisfaction):
    metrics = {
        'query': query,
        'num_results': len(results),
        'top_score': results[0]['score'] if results else 0,
        'answer_length': len(answer),
        'user_satisfaction': user_satisfaction,
        'timestamp': datetime.now(),
    }
    log_to_monitoring(metrics)
```

---

## Summary

- **HyDE**: Generate hypothetical documents for better semantic matching
- **Multi-Query**: Paraphrase queries to retrieve with different terminology
- **Re-Ranking**: Two-stage retrieval for higher precision
- **GraphRAG**: Structured knowledge for complex reasoning
- **RAGAS**: Comprehensive evaluation of RAG systems
- **Adaptive**: Adjust retrieval based on confidence and needs
