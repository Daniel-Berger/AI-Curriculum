"""
Module 06: Embeddings and Vector Databases — Exercises
=======================================================

12 exercises on embeddings, similarity, vector databases, and retrieval.

Topics:
- Embedding representations
- Similarity metrics (cosine, Euclidean)
- Vector database operations
- ChromaDB
- Indexing strategies

Run this file directly to check your solutions:
    python exercises.py
"""

import math
from typing import Optional


# ---------------------------------------------------------------------------
# Exercise 1: Cosine Similarity
# ---------------------------------------------------------------------------
def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Cosine similarity = (A · B) / (||A|| * ||B||)
    where · is dot product, ||A|| is Euclidean norm.

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Cosine similarity as float between -1 and 1
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Euclidean Distance
# ---------------------------------------------------------------------------
def euclidean_distance(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Calculate Euclidean distance between two vectors.

    Distance = sqrt(sum((a_i - b_i)^2))

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Euclidean distance as float
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Vector Normalization
# ---------------------------------------------------------------------------
def normalize_vector(vec: list[float]) -> list[float]:
    """
    Normalize a vector to unit length (L2 normalization).

    Normalized vector = vec / ||vec||

    Args:
        vec: Input vector

    Returns:
        Normalized vector (length 1)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Batch Similarity Search
# ---------------------------------------------------------------------------
def find_similar_vectors(
    query_vec: list[float],
    corpus_vecs: list[list[float]],
    top_k: int = 3,
) -> list[int]:
    """
    Find indices of top-k most similar vectors using cosine similarity.

    Args:
        query_vec: Query vector
        corpus_vecs: List of candidate vectors
        top_k: Number of most similar vectors to return

    Returns:
        List of indices (in corpus_vecs) sorted by similarity (highest first)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Dimension Reduction Check
# ---------------------------------------------------------------------------
def compression_ratio(
    original_dim: int,
    reduced_dim: int,
) -> float:
    """
    Calculate compression ratio when reducing vector dimensions.

    Ratio = original_dim / reduced_dim

    Args:
        original_dim: Original embedding dimension
        reduced_dim: Reduced embedding dimension

    Returns:
        Compression ratio as float
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Embedding Storage Size Estimation
# ---------------------------------------------------------------------------
def estimate_storage_gb(
    num_vectors: int,
    dim: int,
    bytes_per_float: int = 4,
) -> float:
    """
    Estimate storage size for embeddings in gigabytes.

    Size = num_vectors * dim * bytes_per_float

    Args:
        num_vectors: Number of embeddings
        dim: Embedding dimension (e.g., 768 for sentence-transformers)
        bytes_per_float: Bytes per floating point (4 for float32, 2 for float16)

    Returns:
        Storage size in gigabytes, rounded to 2 decimal places
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Vector Quantization
# ---------------------------------------------------------------------------
def quantize_vector(vec: list[float], bits: int = 8) -> list[int]:
    """
    Quantize a floating-point vector to integers (reduces memory).

    Convert floats in [-1, 1] to integers in [-2^(bits-1), 2^(bits-1)-1].
    For 8-bit: [-128, 127]

    Args:
        vec: Floating-point vector
        bits: Number of bits for quantization (default 8)

    Returns:
        Quantized vector as list of integers
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Index Configuration
# ---------------------------------------------------------------------------
def create_index_config(
    embedding_dim: int,
    distance_metric: str = 'cosine',
    use_gpu: bool = False,
) -> dict:
    """
    Create a configuration dict for initializing a vector index.

    Args:
        embedding_dim: Dimension of embeddings
        distance_metric: 'cosine', 'euclidean', or 'dot'
        use_gpu: Whether to use GPU acceleration

    Returns:
        Configuration dictionary with keys:
        - 'dim': embedding dimension
        - 'metric': distance metric
        - 'gpu': GPU flag
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Batch Embedding Size
# ---------------------------------------------------------------------------
def batch_embedding_tokens(
    num_texts: int,
    avg_tokens_per_text: int,
) -> int:
    """
    Calculate total tokens needed to embed a batch of texts.

    Used for cost estimation: OpenAI charges per 1000 tokens.

    Args:
        num_texts: Number of texts to embed
        avg_tokens_per_text: Average tokens per text

    Returns:
        Total tokens
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Embedding Cost Estimation
# ---------------------------------------------------------------------------
def estimate_embedding_cost(
    num_texts: int,
    avg_tokens_per_text: int,
    model: str = 'text-embedding-3-small',
) -> float:
    """
    Estimate cost to embed texts using OpenAI API.

    Pricing (per 1M tokens):
    - text-embedding-3-small: $0.02
    - text-embedding-3-large: $0.13
    - text-embedding-ada-002: $0.10

    Args:
        num_texts: Number of texts
        avg_tokens_per_text: Average tokens per text
        model: Embedding model name

    Returns:
        Estimated cost in dollars
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Vector Store Metadata
# ---------------------------------------------------------------------------
def create_vector_store_entry(
    embedding: list[float],
    text: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Create a vector store entry with embedding and metadata.

    Args:
        embedding: Vector embedding
        text: Original text
        metadata: Optional metadata dict (e.g., {"source": "file.txt"})

    Returns:
        Dictionary with 'embedding', 'text', 'metadata' keys
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Similarity Score Interpretation
# ---------------------------------------------------------------------------
def interpret_similarity_score(
    score: float,
    metric: str = 'cosine',
) -> str:
    """
    Interpret a similarity score as human-readable text.

    For cosine similarity ([-1, 1]):
    - 0.9-1.0: Very similar
    - 0.7-0.9: Similar
    - 0.5-0.7: Moderately similar
    - 0.3-0.5: Somewhat similar
    - < 0.3: Dissimilar

    For euclidean distance (convert to similarity first: 1/(1+distance)):
    - Then use cosine interpretation

    Args:
        score: Similarity score
        metric: 'cosine' or 'euclidean'

    Returns:
        Human-readable interpretation string
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    sim = cosine_similarity([1, 0], [1, 0])
    assert abs(sim - 1.0) < 0.01

    # Test Exercise 2
    dist = euclidean_distance([0, 0], [3, 4])
    assert abs(dist - 5.0) < 0.01

    # Test Exercise 3
    normalized = normalize_vector([3, 4])
    assert abs(sum(x**2 for x in normalized) - 1.0) < 0.01

    # Test Exercise 4
    query = [1, 0]
    corpus = [[1, 0], [0, 1], [1, 1]]
    indices = find_similar_vectors(query, corpus, top_k=2)
    assert len(indices) <= 2

    # Test Exercise 5
    ratio = compression_ratio(768, 256)
    assert ratio == 3.0

    # Test Exercise 6
    storage = estimate_storage_gb(1000000, 768)
    assert storage > 0

    # Test Exercise 7
    quantized = quantize_vector([0.5, -0.5])
    assert isinstance(quantized, list)

    # Test Exercise 8
    config = create_index_config(768)
    assert config['dim'] == 768

    # Test Exercise 9
    tokens = batch_embedding_tokens(100, 50)
    assert tokens == 5000

    # Test Exercise 10
    cost = estimate_embedding_cost(100, 50)
    assert cost > 0

    # Test Exercise 11
    entry = create_vector_store_entry([0.1, 0.2], 'hello')
    assert 'embedding' in entry

    # Test Exercise 12
    interp = interpret_similarity_score(0.95)
    assert isinstance(interp, str)

    print('All tests passed!')
