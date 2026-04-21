# Module 06: Embeddings and Vector Databases

## Introduction for Swift Developers

If you've worked with Core ML's `NLEmbedding` or Natural Language framework in iOS,
you've already touched embeddings -- converting words or sentences into numerical
vectors. In the LLM world, embeddings are the foundation of semantic search, RAG
(retrieval-augmented generation), recommendation systems, and clustering.

Think of embeddings like this: instead of comparing strings with `==` (exact match),
you compare meaning. "The dog ran quickly" and "A canine sprinted fast" would be nearly
identical as embeddings despite sharing zero words. This module covers how to create
embeddings, measure similarity, and store/query them efficiently with vector databases.

---

## 1. What Are Embeddings?

### From Text to Numbers

An embedding model converts text (a word, sentence, or document) into a dense vector
of floating-point numbers -- typically 256 to 3072 dimensions.

```python
# Conceptual representation
text = "The quick brown fox"
embedding = [0.023, -0.041, 0.089, ..., -0.015]  # e.g., 1536 numbers
```

### Why Vectors?

Vectors enable mathematical operations on meaning:
- **Similarity**: How close are two concepts? (cosine similarity)
- **Clustering**: Group similar documents together
- **Search**: Find the most relevant documents for a query
- **Arithmetic**: king - man + woman ≈ queen

### Swift Analogy

```swift
// iOS Natural Language framework
import NaturalLanguage

let embedding = NLEmbedding.wordEmbedding(for: .english)!
let vector = embedding.vector(for: "swift")  // [Double]?
let distance = embedding.distance(between: "swift", and: "fast")
```

In Python, the concept is the same but you have access to far more powerful models
and the ecosystem around them.

---

## 2. Embedding Models

### Overview of Popular Models

| Model | Provider | Dimensions | Use Case |
|-------|----------|-----------|----------|
| text-embedding-3-small | OpenAI | 1536 | General purpose, cost-effective |
| text-embedding-3-large | OpenAI | 3072 | Higher quality, more dimensions |
| embed-english-v3.0 | Cohere | 1024 | English-focused, fast |
| all-MiniLM-L6-v2 | sentence-transformers | 384 | Free, local, fast |
| BAAI/bge-large-en-v1.5 | HuggingFace | 1024 | Free, high quality |

### Creating Embeddings with OpenAI

```python
from openai import OpenAI

client = OpenAI()  # uses OPENAI_API_KEY

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="The quick brown fox jumps over the lazy dog"
)

embedding = response.data[0].embedding
print(f"Dimensions: {len(embedding)}")  # 1536
print(f"First 5 values: {embedding[:5]}")
# [0.0123, -0.0456, 0.0789, ...]
```

### Batch Embeddings

```python
texts = [
    "Python is a programming language",
    "Swift is used for iOS development",
    "Machine learning uses neural networks",
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

embeddings = [item.embedding for item in response.data]
print(f"Generated {len(embeddings)} embeddings")
print(f"Each has {len(embeddings[0])} dimensions")
```

### Creating Embeddings with Sentence Transformers (Free, Local)

```python
from sentence_transformers import SentenceTransformer

# Download model on first run (~80MB for MiniLM)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Single text
embedding = model.encode("Hello world")
print(f"Shape: {embedding.shape}")  # (384,)

# Batch encoding
texts = ["First sentence", "Second sentence", "Third sentence"]
embeddings = model.encode(texts)
print(f"Shape: {embeddings.shape}")  # (3, 384)

# With normalization (important for cosine similarity)
embeddings = model.encode(texts, normalize_embeddings=True)
```

### Creating Embeddings with Anthropic (via Voyager)

As of 2025, Anthropic does not offer a standalone embedding API. For Claude-based
workflows, pair Claude with an embedding model from another provider (OpenAI,
Cohere, or sentence-transformers for local use).

---

## 3. Similarity Metrics

### Cosine Similarity

The most common similarity metric for embeddings. It measures the angle between
two vectors, ignoring magnitude. Values range from -1 (opposite) to 1 (identical).

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# Example
vec_a = np.array([1.0, 2.0, 3.0])
vec_b = np.array([1.0, 2.0, 3.5])
vec_c = np.array([-1.0, -2.0, -3.0])

print(cosine_similarity(vec_a, vec_b))  # ~0.998 (very similar)
print(cosine_similarity(vec_a, vec_c))  # -1.0 (opposite)
```

### Dot Product

For normalized vectors (unit length), dot product equals cosine similarity. It's
faster to compute and is used by many vector databases internally.

```python
def dot_product_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute dot product between two vectors."""
    return float(np.dot(a, b))

# With normalized vectors
a_norm = vec_a / np.linalg.norm(vec_a)
b_norm = vec_b / np.linalg.norm(vec_b)
print(dot_product_similarity(a_norm, b_norm))  # Same as cosine similarity
```

### Euclidean Distance

Measures the straight-line distance between two points. Smaller = more similar.

```python
def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Compute Euclidean distance between two vectors."""
    return float(np.linalg.norm(a - b))

print(euclidean_distance(vec_a, vec_b))  # ~0.5 (close)
print(euclidean_distance(vec_a, vec_c))  # ~7.48 (far)
```

### When to Use Which?

| Metric | Best For | Notes |
|--------|----------|-------|
| Cosine Similarity | Text similarity, recommendations | Direction matters, magnitude doesn't |
| Dot Product | Normalized embeddings | Fastest computation |
| Euclidean Distance | Clustering, spatial queries | Affected by vector magnitude |

**Rule of thumb**: Use cosine similarity for text embeddings. Most embedding models
are optimized for it.

---

## 4. ChromaDB -- Local Vector Database

ChromaDB is an open-source, embeddable vector database that runs locally. It's
the easiest way to get started -- no cloud account, no API key, no Docker.

### Setup and Basic Usage

```python
import chromadb

# Create a client (in-memory)
client = chromadb.Client()

# Create a collection (like a table)
collection = client.create_collection(
    name="my_documents",
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)
```

### Adding Documents

ChromaDB can generate embeddings automatically using its built-in model:

```python
# Add documents -- ChromaDB embeds them automatically
collection.add(
    documents=[
        "Python is a versatile programming language",
        "Swift is used for iOS and macOS development",
        "Machine learning requires large datasets",
        "Neural networks are inspired by the brain",
        "Data science involves statistical analysis",
    ],
    metadatas=[
        {"topic": "programming", "language": "python"},
        {"topic": "programming", "language": "swift"},
        {"topic": "ml", "subtopic": "general"},
        {"topic": "ml", "subtopic": "neural-nets"},
        {"topic": "data-science"},
    ],
    ids=["doc1", "doc2", "doc3", "doc4", "doc5"]
)
```

### Querying

```python
# Semantic search -- find documents similar to a query
results = collection.query(
    query_texts=["What programming language should I learn?"],
    n_results=3
)

print(results["documents"])
# [['Python is a versatile programming language',
#   'Swift is used for iOS and macOS development',
#   'Data science involves statistical analysis']]

print(results["distances"])
# [[0.234, 0.456, 0.678]]  # Lower = more similar for cosine

print(results["metadatas"])
# [[{'topic': 'programming', 'language': 'python'}, ...]]
```

### Metadata Filtering

```python
# Query with metadata filter
results = collection.query(
    query_texts=["programming best practices"],
    n_results=3,
    where={"topic": "programming"}  # Only search programming docs
)

# Complex filters
results = collection.query(
    query_texts=["advanced topics"],
    n_results=5,
    where={
        "$and": [
            {"topic": {"$eq": "ml"}},
            {"subtopic": {"$ne": "general"}}
        ]
    }
)

# Filter by document content
results = collection.query(
    query_texts=["learning"],
    n_results=3,
    where_document={"$contains": "programming"}
)
```

### Persistence

```python
# Persistent client -- data survives restarts
client = chromadb.PersistentClient(path="./chroma_db")

# Get or create a collection
collection = client.get_or_create_collection("my_docs")

# List existing collections
collections = client.list_collections()
print([c.name for c in collections])

# Delete a collection
client.delete_collection("my_docs")
```

### Using Custom Embeddings with ChromaDB

```python
import chromadb
import numpy as np

client = chromadb.Client()

# Create collection without auto-embedding
collection = client.create_collection(
    name="custom_embeddings",
    metadata={"hnsw:space": "cosine"}
)

# Add with pre-computed embeddings
collection.add(
    ids=["id1", "id2"],
    embeddings=[
        [0.1, 0.2, 0.3, 0.4],  # Your own embeddings
        [0.5, 0.6, 0.7, 0.8],
    ],
    documents=["First doc", "Second doc"],
    metadatas=[{"source": "manual"}, {"source": "manual"}]
)

# Query with pre-computed query embedding
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3, 0.35]],
    n_results=2
)
```

### Update and Delete

```python
# Update a document
collection.update(
    ids=["doc1"],
    documents=["Updated: Python is an amazing programming language"],
    metadatas=[{"topic": "programming", "language": "python", "updated": True}]
)

# Upsert (update if exists, insert if not)
collection.upsert(
    ids=["doc1", "doc6"],
    documents=["Updated doc 1", "Brand new doc 6"],
    metadatas=[{"source": "update"}, {"source": "new"}]
)

# Delete
collection.delete(ids=["doc5"])

# Delete with filter
collection.delete(where={"topic": "data-science"})

# Get count
print(collection.count())
```

---

## 5. Pinecone -- Cloud Vector Database

Pinecone is a managed cloud vector database. It handles scaling, replication, and
infrastructure for you.

### Setup

```python
from pinecone import Pinecone

# Initialize
pc = Pinecone(api_key="your-api-key")

# Create an index
pc.create_index(
    name="my-index",
    dimension=1536,  # Must match your embedding model
    metric="cosine",
    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
)

# Connect to the index
index = pc.Index("my-index")
```

### Upsert (Insert/Update)

```python
# Upsert vectors
index.upsert(vectors=[
    {
        "id": "doc1",
        "values": [0.1, 0.2, ...],  # 1536 dimensions
        "metadata": {"title": "Python Guide", "topic": "programming"}
    },
    {
        "id": "doc2",
        "values": [0.3, 0.4, ...],
        "metadata": {"title": "ML Basics", "topic": "ml"}
    }
])

# Batch upsert for large datasets
import itertools

def chunks(iterable, batch_size=100):
    it = iter(iterable)
    chunk = list(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = list(itertools.islice(it, batch_size))

for batch in chunks(all_vectors, batch_size=100):
    index.upsert(vectors=batch)
```

### Query

```python
# Query
results = index.query(
    vector=[0.1, 0.2, ...],  # Query embedding
    top_k=5,
    include_metadata=True
)

for match in results.matches:
    print(f"ID: {match.id}, Score: {match.score:.4f}")
    print(f"  Metadata: {match.metadata}")
```

### Namespaces

Namespaces partition your index -- useful for multi-tenant applications:

```python
# Upsert to a specific namespace
index.upsert(
    vectors=[{"id": "doc1", "values": [...]}],
    namespace="user-123"
)

# Query within a namespace
results = index.query(
    vector=[...],
    top_k=5,
    namespace="user-123"
)
```

---

## 6. FAISS -- Facebook AI Similarity Search

FAISS is a library for efficient similarity search, not a database. It's
extremely fast and supports GPU acceleration, but you manage storage yourself.

### Basic Index (Flat L2)

```python
import faiss
import numpy as np

# Create some random embeddings (128-dimensional, 1000 vectors)
dimension = 128
num_vectors = 1000
embeddings = np.random.random((num_vectors, dimension)).astype("float32")

# Create a flat (brute-force) index
index = faiss.IndexFlatL2(dimension)  # L2 = Euclidean distance
index.add(embeddings)

print(f"Index contains {index.ntotal} vectors")

# Search
query = np.random.random((1, dimension)).astype("float32")
distances, indices = index.search(query, k=5)

print(f"Nearest neighbors: {indices[0]}")
print(f"Distances: {distances[0]}")
```

### IVF Index (Faster for Large Datasets)

IVF (Inverted File) partitions the space into clusters for faster search:

```python
# Quantizer for the IVF index
nlist = 100  # Number of clusters
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# Must train before adding vectors
index.train(embeddings)
index.add(embeddings)

# Search (nprobe controls accuracy vs speed tradeoff)
index.nprobe = 10  # Search 10 nearest clusters
distances, indices = index.search(query, k=5)
```

### HNSW Index (Best Quality/Speed Tradeoff)

```python
# HNSW = Hierarchical Navigable Small World
# Great balance of speed and recall
index = faiss.IndexHNSWFlat(dimension, 32)  # 32 = number of links per node
index.add(embeddings)

distances, indices = index.search(query, k=5)
```

### Saving and Loading FAISS Indexes

```python
# Save
faiss.write_index(index, "my_index.faiss")

# Load
loaded_index = faiss.read_index("my_index.faiss")
```

### GPU Support

```python
# Move index to GPU (requires faiss-gpu package)
# gpu_index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, index)
# distances, indices = gpu_index.search(query, k=5)
```

---

## 7. Choosing a Vector Database

### Decision Matrix

| Feature | ChromaDB | Pinecone | FAISS |
|---------|----------|----------|-------|
| **Type** | Embedded DB | Managed Cloud | Library |
| **Setup** | `pip install` | API key + dashboard | `pip install` |
| **Scale** | Small-medium | Large | Any (manual) |
| **Persistence** | File-based | Cloud | Manual (save/load) |
| **Metadata** | Yes | Yes | No (manual) |
| **Filtering** | Rich filters | Rich filters | No |
| **Cost** | Free | Pay-per-use | Free |
| **Speed** | Good | Good | Fastest |
| **Best For** | Prototypes, local apps | Production, multi-tenant | Research, max performance |

### Recommendations by Stage

```
Prototyping / Learning → ChromaDB
    - Zero config, runs locally, great for this course

Small Production App → ChromaDB (persistent) or Pinecone (free tier)
    - ChromaDB if you want to self-host
    - Pinecone if you want managed infrastructure

Large Scale → Pinecone, Weaviate, or Qdrant
    - Need managed scaling, replication, monitoring

Research / Benchmarking → FAISS
    - When you need raw speed and control
```

---

## 8. Hybrid Search

Combining semantic search (embeddings) with keyword search (BM25/TF-IDF) often
produces better results than either alone.

### Why Hybrid?

- **Semantic search** finds conceptually similar content but can miss exact terms
- **Keyword search** finds exact matches but misses synonyms and concepts
- **Hybrid** combines both for best results

### Simple Hybrid Search Implementation

```python
import numpy as np
from collections import defaultdict

def keyword_search(query: str, documents: list[str], top_k: int = 5) -> list[tuple[int, float]]:
    """Simple keyword search using term frequency."""
    query_terms = set(query.lower().split())
    scores = []

    for i, doc in enumerate(documents):
        doc_terms = set(doc.lower().split())
        # Jaccard similarity
        intersection = query_terms & doc_terms
        union = query_terms | doc_terms
        score = len(intersection) / len(union) if union else 0
        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]

def hybrid_search(
    query: str,
    documents: list[str],
    embeddings: np.ndarray,
    query_embedding: np.ndarray,
    alpha: float = 0.5,  # Weight: 0 = all keyword, 1 = all semantic
    top_k: int = 5
) -> list[tuple[int, float]]:
    """Combine semantic and keyword search results."""

    # Semantic scores (cosine similarity)
    norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    semantic_scores = np.dot(embeddings, query_embedding) / np.where(norms == 0, 1, norms)

    # Keyword scores
    kw_results = keyword_search(query, documents, top_k=len(documents))
    kw_scores = np.zeros(len(documents))
    for idx, score in kw_results:
        kw_scores[idx] = score

    # Combine with weighted average
    combined = alpha * semantic_scores + (1 - alpha) * kw_scores

    # Sort and return top-k
    ranked = sorted(enumerate(combined), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
```

---

## 9. Embedding Dimensions and Tradeoffs

### Higher Dimensions vs. Lower Dimensions

| Aspect | Lower (256-384) | Higher (1536-3072) |
|--------|-----------------|-------------------|
| **Storage** | Less | More |
| **Speed** | Faster search | Slower search |
| **Quality** | Good for simple tasks | Better semantic nuance |
| **Cost** | Cheaper to store/query | More expensive |

### Dimensionality Reduction

Some models support Matryoshka (nested) embeddings -- you can truncate to fewer
dimensions with minimal quality loss:

```python
from openai import OpenAI

client = OpenAI()

# Generate with reduced dimensions
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world",
    dimensions=512  # Instead of default 1536
)

embedding = response.data[0].embedding
print(f"Dimensions: {len(embedding)}")  # 512
```

### Storage Calculation

```python
def estimate_storage(num_documents: int, dimensions: int, bytes_per_float: int = 4) -> str:
    """Estimate storage for a vector database."""
    total_bytes = num_documents * dimensions * bytes_per_float
    if total_bytes < 1024**2:
        return f"{total_bytes / 1024:.1f} KB"
    elif total_bytes < 1024**3:
        return f"{total_bytes / 1024**2:.1f} MB"
    else:
        return f"{total_bytes / 1024**3:.2f} GB"

print(estimate_storage(10_000, 1536))     # "58.6 MB"
print(estimate_storage(1_000_000, 1536))  # "5.72 GB"
print(estimate_storage(1_000_000, 384))   # "1.43 GB"
```

---

## 10. Practical Example: Building a Semantic Search Engine

Here's a complete example using ChromaDB:

```python
import chromadb

def build_search_engine():
    """Build a simple semantic search engine with ChromaDB."""

    # Initialize ChromaDB
    client = chromadb.Client()
    collection = client.create_collection("knowledge_base")

    # Add documents (ChromaDB auto-embeds with its default model)
    documents = [
        "Python list comprehensions provide a concise way to create lists",
        "Swift uses optionals to handle the absence of a value",
        "Machine learning models learn patterns from training data",
        "REST APIs use HTTP methods like GET, POST, PUT, DELETE",
        "Docker containers package applications with their dependencies",
        "Git branches allow parallel development workflows",
        "SQL joins combine rows from two or more tables",
        "CSS flexbox provides a flexible layout model",
        "React components are reusable pieces of UI",
        "Neural networks consist of layers of interconnected nodes",
    ]

    collection.add(
        documents=documents,
        ids=[f"doc_{i}" for i in range(len(documents))],
        metadatas=[{"index": i} for i in range(len(documents))]
    )

    # Search function
    def search(query: str, n_results: int = 3) -> list[dict]:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return [
            {
                "document": doc,
                "distance": dist,
                "id": id_
            }
            for doc, dist, id_ in zip(
                results["documents"][0],
                results["distances"][0],
                results["ids"][0]
            )
        ]

    return search

# Usage
search = build_search_engine()

print("Query: 'How do I handle null values in programming?'")
for result in search("How do I handle null values in programming?"):
    print(f"  [{result['distance']:.4f}] {result['document']}")

print("\nQuery: 'deep learning architecture'")
for result in search("deep learning architecture"):
    print(f"  [{result['distance']:.4f}] {result['document']}")
```

---

## 11. Working with Embeddings in NumPy

### Common Operations

```python
import numpy as np

# Normalize vectors (required for dot product similarity)
def normalize(vectors: np.ndarray) -> np.ndarray:
    """Normalize vectors to unit length."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.where(norms == 0, 1, norms)

# Batch cosine similarity (one query vs many documents)
def batch_cosine_similarity(query: np.ndarray, documents: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between a query and multiple documents."""
    query_norm = query / np.linalg.norm(query)
    doc_norms = normalize(documents)
    return np.dot(doc_norms, query_norm)

# Find top-k similar
def top_k_similar(query: np.ndarray, documents: np.ndarray, k: int = 5) -> list[tuple[int, float]]:
    """Return indices and scores of top-k most similar documents."""
    similarities = batch_cosine_similarity(query, documents)
    top_indices = np.argsort(similarities)[::-1][:k]
    return [(int(idx), float(similarities[idx])) for idx in top_indices]

# Example
query = np.random.random(384).astype("float32")
documents = np.random.random((100, 384)).astype("float32")
results = top_k_similar(query, documents, k=3)
for idx, score in results:
    print(f"Document {idx}: similarity = {score:.4f}")
```

### Centroid Calculation (for Clustering)

```python
def compute_centroid(embeddings: np.ndarray) -> np.ndarray:
    """Compute the centroid (average) of a set of embeddings."""
    return np.mean(embeddings, axis=0)

# Cluster documents by computing centroids
cluster_a = np.random.random((10, 384)).astype("float32")
cluster_b = np.random.random((10, 384)).astype("float32")

centroid_a = compute_centroid(cluster_a)
centroid_b = compute_centroid(cluster_b)

# How similar are the clusters?
sim = cosine_similarity(centroid_a, centroid_b)
print(f"Cluster similarity: {sim:.4f}")
```

---

## 12. Best Practices

### Embedding Best Practices

1. **Normalize your embeddings** before storing if using dot product similarity
2. **Batch your embedding calls** to reduce API latency and cost
3. **Cache embeddings** -- don't re-embed the same text
4. **Choose dimensions based on your use case** -- 384 for speed, 1536+ for quality

### Vector Database Best Practices

1. **Add meaningful metadata** -- you'll want to filter later
2. **Use namespaces/collections** to separate different data types
3. **Monitor index size** -- know your storage requirements
4. **Test with your actual queries** -- synthetic benchmarks can mislead

### Common Pitfalls

```python
# WRONG: Embedding queries and documents with different models
query_embedding = model_a.encode("search query")      # Model A
doc_embedding = model_b.encode("document text")        # Model B
similarity = cosine_similarity(query_embedding, doc_embedding)  # Meaningless!

# RIGHT: Use the same model for both
query_embedding = model.encode("search query")
doc_embedding = model.encode("document text")
similarity = cosine_similarity(query_embedding, doc_embedding)  # Valid comparison

# WRONG: Comparing embeddings of different dimensions
vec_384 = np.random.random(384)
vec_1536 = np.random.random(1536)
# cosine_similarity(vec_384, vec_1536)  # ERROR: dimension mismatch

# RIGHT: Use consistent dimensions throughout your pipeline
```

---

## Key Takeaways

1. **Embeddings convert text to vectors** that capture semantic meaning
2. **Cosine similarity** is the standard metric for comparing embeddings
3. **ChromaDB** is the best starting point -- local, free, zero-config
4. **Pinecone** is the go-to for production cloud deployments
5. **FAISS** offers raw performance when you need speed
6. **Always use the same embedding model** for queries and documents
7. **Hybrid search** (semantic + keyword) often outperforms either alone
8. **Higher dimensions = better quality but more storage and compute**

---

## Further Reading

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS Wiki](https://github.com/facebookresearch/faiss/wiki)
- [Pinecone Documentation](https://docs.pinecone.io/)
