# Module 07: RAG Fundamentals

## Why This Module Matters for Interviews

Retrieval-Augmented Generation (RAG) is essential for production LLM systems. Interviewers ask:
- "How would you build a system that answers questions about company documents?"
- "How do you handle large documents that exceed context length?"
- "What's the difference between chunking strategies?"
- "How do you evaluate RAG system quality?"

RAG solves the core problem: **LLMs have a knowledge cutoff and limited context**. RAG adds real-time information retrieval.

---

## What Is RAG?

RAG = Retrieval-Augmented Generation

```
User Question
    ↓
Retrieve relevant documents from knowledge base
    ↓
Combine with user question into prompt
    ↓
Generate answer from LLM (grounded in retrieved docs)
```

**Key insight**: Instead of asking the LLM from scratch, you give it relevant context, making answers more accurate and up-to-date.

---

## RAG Architecture

### Components

```
┌─────────────────────────────────────────────┐
│           RAG Pipeline                      │
├─────────────────────────────────────────────┤
│  User Query                                 │
│      ↓                                      │
│  Query Embedding                            │
│  (same model as documents)                  │
│      ↓                                      │
│  Vector Database                            │
│  (search for similar documents)             │
│      ↓                                      │
│  Retrieved Documents (Top-K)                │
│      ↓                                      │
│  Prompt Construction                        │
│  "Answer based on: {retrieved_docs}"        │
│      ↓                                      │
│  LLM Generation                             │
│      ↓                                      │
│  Final Answer                               │
└─────────────────────────────────────────────┘
```

### Typical Flow

```python
# 1. Preprocessing: Once, during setup
documents = load_documents("company_docs/")
chunks = chunk_documents(documents)
embeddings = embed_chunks(chunks)
vector_db.index(embeddings, chunks)

# 2. Runtime: On every user query
query_embedding = embed_query(user_query)
relevant_chunks = vector_db.search(query_embedding, top_k=5)
context = "\n".join(relevant_chunks)

prompt = f"""Answer based on these documents:
{context}

Question: {user_query}"""

answer = llm.generate(prompt)
```

---

## Document Loading

### Common Sources

- **PDFs**: PyPDF2, pdfplumber, pymupdf
- **Markdown/Text**: Plain file reading
- **Web**: BeautifulSoup, Selenium
- **Databases**: SQL queries
- **APIs**: REST endpoints

### Example: Load PDFs

```python
from PyPDF2 import PdfReader

def load_pdfs(directory):
    documents = []
    for pdf_file in os.listdir(directory):
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        documents.append({
            "source": pdf_file,
            "content": text
        })
    return documents
```

---

## Document Chunking Strategies

### Why Chunk?

- Documents exceed context window
- Embeddings work better on smaller units
- Improves retrieval precision
- Reduces noise in retrieved context

### Strategy 1: Fixed Size

```python
def chunk_fixed(text, chunk_size=512, overlap=50):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks
```

**Pros**: Simple, predictable
**Cons**: Breaks sentences, poor semantic boundaries

### Strategy 2: Recursive (Semantic)

```python
def chunk_recursive(text, chunk_size=512, overlap=50):
    """Split by sentences first, then combine until chunk_size."""
    sentences = text.split('. ')
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) < chunk_size:
            current += sentence + ". "
        else:
            chunks.append(current)
            current = sentence + ". "
    return chunks
```

**Pros**: Preserves sentence structure
**Cons**: Slightly more complex

### Strategy 3: Token-Based

```python
def chunk_by_tokens(text, max_tokens=512, tokenizer=None):
    """Split text respecting token limits."""
    tokens = tokenizer.encode(text)
    chunks = []
    chunk_tokens = []
    for token in tokens:
        chunk_tokens.append(token)
        if len(chunk_tokens) >= max_tokens:
            chunks.append(tokenizer.decode(chunk_tokens))
            chunk_tokens = []
    return chunks
```

**Pros**: Precise token control, prevents API overages
**Cons**: Needs tokenizer

### Comparison

| Strategy | Semantic Awareness | Speed | Flexibility |
|----------|-------------------|-------|-------------|
| Fixed size | Low | Fast | Limited |
| Recursive | Medium | Medium | Better |
| Token-based | Medium | Medium | Best |
| Language-aware | High | Slow | Good |

---

## Embedding and Indexing

### Embedding Models

Common models for RAG:

| Model | Dimension | Strengths |
|-------|-----------|-----------|
| text-embedding-3-small | 1536 | Fast, good quality |
| text-embedding-3-large | 3072 | Best quality |
| all-MiniLM-L6-v2 | 384 | Efficient, open-source |
| bge-large-en-v1.5 | 1024 | Strong, open-source |

### Indexing

**FAISS** (Facebook AI Similarity Search):
```python
import faiss
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)  # Add embeddings
distances, indices = index.search(query_embedding, k=5)
```

**Chroma** (simple, managed):
```python
collection = chroma_client.create_collection("documents")
collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=texts
)
results = collection.query(query_embedding, n_results=5)
```

---

## Retrieval Strategies

### Simple: Top-K Retrieval

```python
def retrieve(query, top_k=5):
    query_embedding = embeddings_model.encode(query)
    scores, indices = vector_db.search(query_embedding, top_k)
    return [documents[i] for i in indices]
```

**When**: Simple questions, general knowledge

### BM25 (Keyword-Based)

Combines vector similarity with keyword matching:

```python
from rank_bm25 import BM25Okapi

corpus = [chunk.split() for chunk in chunks]
bm25 = BM25Okapi(corpus)
scores = bm25.get_scores(query.split())
top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
```

**When**: Technical docs with specific keywords

### Hybrid Retrieval

Combine vector + keyword:

```python
def hybrid_retrieve(query, top_k=5):
    # Vector search
    vector_results = vector_db.search(query, k=top_k)

    # Keyword search (BM25)
    keyword_results = bm25_search(query, k=top_k)

    # Merge and deduplicate
    merged = {}
    for score, idx in vector_results:
        merged[idx] = merged.get(idx, 0) + score
    for score, idx in keyword_results:
        merged[idx] = merged.get(idx, 0) + score

    # Return top-k by merged score
    sorted_results = sorted(merged.items(), key=lambda x: x[1], reverse=True)
    return [documents[idx] for idx, _ in sorted_results[:top_k]]
```

**When**: Need both semantic and keyword relevance

---

## Context Formatting

### Naive: Just Concatenate

```python
context = "\n".join(retrieved_docs)
prompt = f"Based on:\n{context}\n\nQuestion: {query}"
```

**Problem**: Model doesn't know which doc is most relevant

### Better: Ranked with Scores

```python
context = ""
for i, (doc, score) in enumerate(sorted(retrieved, key=lambda x: x[1], reverse=True)):
    context += f"[Document {i+1} - Relevance: {score:.2f}]\n{doc}\n\n"
```

### Best: Structured with Metadata

```python
context = ""
for doc in retrieved:
    context += f"""
---
Source: {doc['source']}
Section: {doc['section']}
---
{doc['content']}
"""
```

---

## Evaluation Metrics

### Retrieval Quality

**Recall@K**: Did the relevant document appear in top-K?
```
Recall@5 = (# relevant docs in top-5) / (# total relevant docs)
```

**Precision@K**: How many of top-K are relevant?
```
Precision@5 = (# relevant docs in top-5) / 5
```

**MRR (Mean Reciprocal Rank)**:
```
Rank of first relevant result. Higher = better.
MRR = 1 / avg(rank_of_first_relevant)
```

### Generation Quality

**BLEU**, **ROUGE**: Measure answer similarity to reference
**F1 Score**: For factoid questions with clear answers

### End-to-End

**Human Evaluation**: Does the answer help the user?
**Cost**: Tokens used × price
**Latency**: Time to response

---

## Common Pitfalls

1. **Bad chunking**: Chunks too small → missing context, or too large → noise
2. **Embedding mismatch**: Query embedded with different model than documents
3. **Retrieval over-confidence**: Top result isn't always correct
4. **Lost in the middle**: Model ignores middle documents (prefer first/last)
5. **Token overflow**: Retrieved context + answer exceeds model context window

---

## Summary

- **RAG**: Retrieve documents → Embed in prompt → Generate answer
- **Chunking**: Balance semantic coherence with size
- **Retrieval**: Vector search + optionally keyword search
- **Formatting**: Make source and relevance clear
- **Evaluation**: Measure retrieval quality (Recall, Precision, MRR) and generation quality
- **Production**: Monitor latency, cost, and answer quality continuously
