"""
Module 06: Embeddings and Vector Databases — Solutions
=======================================================

Complete solutions for all 12 exercises.
"""

import math
from typing import Optional


# ---------------------------------------------------------------------------
# Exercise 1: Cosine Similarity
# ---------------------------------------------------------------------------
def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

    mag_a = math.sqrt(sum(a ** 2 for a in vec_a))
    mag_b = math.sqrt(sum(b ** 2 for b in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product / (mag_a * mag_b)


# ---------------------------------------------------------------------------
# Exercise 2: Euclidean Distance
# ---------------------------------------------------------------------------
def euclidean_distance(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Calculate Euclidean distance between two vectors.
    """
    sum_of_squares = sum((a - b) ** 2 for a, b in zip(vec_a, vec_b))
    return math.sqrt(sum_of_squares)


# ---------------------------------------------------------------------------
# Exercise 3: Vector Normalization
# ---------------------------------------------------------------------------
def normalize_vector(vec: list[float]) -> list[float]:
    """
    Normalize a vector to unit length.
    """
    magnitude = math.sqrt(sum(x ** 2 for x in vec))

    if magnitude == 0:
        return vec

    return [x / magnitude for x in vec]


# ---------------------------------------------------------------------------
# Exercise 4: Batch Similarity Search
# ---------------------------------------------------------------------------
def find_similar_vectors(
    query_vec: list[float],
    corpus_vecs: list[list[float]],
    top_k: int = 3,
) -> list[int]:
    """
    Find indices of top-k most similar vectors.
    """
    similarities = []

    for i, vec in enumerate(corpus_vecs):
        sim = cosine_similarity(query_vec, vec)
        similarities.append((i, sim))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top-k indices
    return [idx for idx, _ in similarities[:top_k]]


# ---------------------------------------------------------------------------
# Exercise 5: Dimension Reduction Check
# ---------------------------------------------------------------------------
def compression_ratio(
    original_dim: int,
    reduced_dim: int,
) -> float:
    """
    Calculate compression ratio.
    """
    return original_dim / reduced_dim


# ---------------------------------------------------------------------------
# Exercise 6: Embedding Storage Size Estimation
# ---------------------------------------------------------------------------
def estimate_storage_gb(
    num_vectors: int,
    dim: int,
    bytes_per_float: int = 4,
) -> float:
    """
    Estimate storage size for embeddings.
    """
    total_bytes = num_vectors * dim * bytes_per_float
    total_gb = total_bytes / (1024 ** 3)
    return round(total_gb, 2)


# ---------------------------------------------------------------------------
# Exercise 7: Vector Quantization
# ---------------------------------------------------------------------------
def quantize_vector(vec: list[float], bits: int = 8) -> list[int]:
    """
    Quantize a floating-point vector to integers.
    """
    max_val = 2 ** (bits - 1) - 1
    min_val = -(2 ** (bits - 1))

    quantized = []
    for val in vec:
        # Assume values are in [-1, 1]
        # Scale to [-max_val, max_val]
        scaled = int(val * max_val)
        # Clamp to range
        clamped = max(min_val, min(max_val, scaled))
        quantized.append(clamped)

    return quantized


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
    """
    return {
        'dim': embedding_dim,
        'metric': distance_metric,
        'gpu': use_gpu,
    }


# ---------------------------------------------------------------------------
# Exercise 9: Batch Embedding Size
# ---------------------------------------------------------------------------
def batch_embedding_tokens(
    num_texts: int,
    avg_tokens_per_text: int,
) -> int:
    """
    Calculate total tokens needed to embed a batch.
    """
    return num_texts * avg_tokens_per_text


# ---------------------------------------------------------------------------
# Exercise 10: Embedding Cost Estimation
# ---------------------------------------------------------------------------
def estimate_embedding_cost(
    num_texts: int,
    avg_tokens_per_text: int,
    model: str = 'text-embedding-3-small',
) -> float:
    """
    Estimate cost to embed texts.
    """
    pricing = {
        'text-embedding-3-small': 0.02,
        'text-embedding-3-large': 0.13,
        'text-embedding-ada-002': 0.10,
    }

    price_per_million = pricing.get(model, 0.02)

    total_tokens = batch_embedding_tokens(num_texts, avg_tokens_per_text)
    cost = (total_tokens / 1_000_000) * price_per_million

    return cost


# ---------------------------------------------------------------------------
# Exercise 11: Vector Store Metadata
# ---------------------------------------------------------------------------
def create_vector_store_entry(
    embedding: list[float],
    text: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Create a vector store entry.
    """
    return {
        'embedding': embedding,
        'text': text,
        'metadata': metadata or {},
    }


# ---------------------------------------------------------------------------
# Exercise 12: Similarity Score Interpretation
# ---------------------------------------------------------------------------
def interpret_similarity_score(
    score: float,
    metric: str = 'cosine',
) -> str:
    """
    Interpret a similarity score as human-readable text.
    """
    # For Euclidean distance, convert to similarity
    if metric == 'euclidean':
        score = 1.0 / (1.0 + score)

    # Now interpret cosine similarity
    if score >= 0.9:
        return "Very similar"
    elif score >= 0.7:
        return "Similar"
    elif score >= 0.5:
        return "Moderately similar"
    elif score >= 0.3:
        return "Somewhat similar"
    else:
        return "Dissimilar"


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
    magnitude = math.sqrt(sum(x**2 for x in normalized))
    assert abs(magnitude - 1.0) < 0.01

    # Test Exercise 4
    query = [1, 0]
    corpus = [[1, 0], [0, 1], [1, 1]]
    indices = find_similar_vectors(query, corpus, top_k=2)
    assert len(indices) == 2
    assert indices[0] == 0  # [1,0] is most similar

    # Test Exercise 5
    ratio = compression_ratio(768, 256)
    assert ratio == 3.0

    # Test Exercise 6
    storage = estimate_storage_gb(1000000, 768)
    assert storage > 0
    assert isinstance(storage, float)

    # Test Exercise 7
    quantized = quantize_vector([0.5, -0.5])
    assert isinstance(quantized, list)
    assert all(isinstance(x, int) for x in quantized)

    # Test Exercise 8
    config = create_index_config(768)
    assert config['dim'] == 768
    assert config['metric'] == 'cosine'

    # Test Exercise 9
    tokens = batch_embedding_tokens(100, 50)
    assert tokens == 5000

    # Test Exercise 10
    cost = estimate_embedding_cost(100, 50)
    assert cost > 0

    # Test Exercise 11
    entry = create_vector_store_entry([0.1, 0.2], 'hello')
    assert 'embedding' in entry
    assert entry['text'] == 'hello'

    # Test Exercise 12
    interp = interpret_similarity_score(0.95)
    assert 'similar' in interp.lower()

    print('All tests passed!')
