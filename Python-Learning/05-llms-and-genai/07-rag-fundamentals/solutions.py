"""
Module 07: RAG Fundamentals — Solutions
========================================

Complete solutions for all 15 exercises.
"""

import re
from collections import Counter
from typing import Optional


# ---------------------------------------------------------------------------
# Exercise 1: Text Chunking (Fixed Size)
# ---------------------------------------------------------------------------
def chunk_fixed_size(
    text: str,
    chunk_size: int = 256,
    overlap: int = 32,
) -> list[str]:
    """
    Split text into fixed-size chunks with overlap.
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk:
            chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------------------
# Exercise 2: Sentence-Based Chunking
# ---------------------------------------------------------------------------
def chunk_by_sentences(
    text: str,
    sentences_per_chunk: int = 3,
) -> list[str]:
    """
    Split text into chunks based on sentence boundaries.
    """
    sentences = text.split('. ')
    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence)
        if len(current_chunk) >= sentences_per_chunk:
            chunks.append('. '.join(current_chunk) + '.')
            current_chunk = []

    if current_chunk:
        chunks.append('. '.join(current_chunk) + ('.' if not current_chunk[-1].endswith('.') else ''))

    return [c for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# Exercise 3: Vocabulary Extraction
# ---------------------------------------------------------------------------
def extract_keywords(
    text: str,
    top_k: int = 10,
) -> list[str]:
    """
    Extract top-k most frequent words (keywords) from text.
    """
    stop_words = {
        'a', 'the', 'is', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'be', 'have', 'has', 'had', 'do',
        'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
        'it', 'we', 'they', 'what', 'which', 'who', 'where', 'when', 'why', 'how'
    }

    words = text.lower().split()
    words = [w.strip('.,!?;:') for w in words]
    words = [w for w in words if w and w not in stop_words and len(w) > 2]

    counter = Counter(words)
    top_keywords = counter.most_common(top_k)

    return [word for word, _ in top_keywords]


# ---------------------------------------------------------------------------
# Exercise 4: Document Metadata Structure
# ---------------------------------------------------------------------------
def create_document_chunk(
    content: str,
    source: str,
    page_num: int = 1,
    chunk_id: int = 1,
) -> dict:
    """
    Create a structured document chunk with metadata.
    """
    return {
        'content': content,
        'source': source,
        'page': page_num,
        'id': chunk_id,
        'length': len(content),
    }


# ---------------------------------------------------------------------------
# Exercise 5: Embedding Cost Calculator
# ---------------------------------------------------------------------------
def calculate_embedding_cost(
    num_chunks: int,
    avg_chunk_tokens: int,
    model: str = 'text-embedding-3-small',
) -> dict:
    """
    Calculate cost and time to embed all chunks.
    """
    pricing = {
        'text-embedding-3-small': 0.02,
        'text-embedding-3-large': 0.13,
        'open-source': 0.0,
    }

    total_tokens = num_chunks * avg_chunk_tokens
    price_per_million = pricing.get(model, 0.02)

    cost = (total_tokens / 1_000_000) * price_per_million

    # Rough estimate: 10k chunks per minute
    time_minutes = num_chunks / 10_000

    return {
        'cost': round(cost, 4),
        'tokens': total_tokens,
        'time_minutes': round(time_minutes, 2),
    }


# ---------------------------------------------------------------------------
# Exercise 6: BM25 Score Calculation
# ---------------------------------------------------------------------------
def calculate_bm25_score(
    query_terms: list[str],
    doc_terms: list[str],
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    """
    Simple BM25 scoring.
    """
    score = 0.0
    doc_len = len(doc_terms)
    avg_doc_len = doc_len

    doc_term_counts = Counter(doc_terms)

    for term in query_terms:
        if term in doc_term_counts:
            tf = doc_term_counts[term]
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / avg_doc_len))
            score += numerator / denominator

    return score


# ---------------------------------------------------------------------------
# Exercise 7: Retrieval Recall@K
# ---------------------------------------------------------------------------
def calculate_recall_at_k(
    retrieved_doc_ids: list[int],
    relevant_doc_ids: list[int],
    k: int = 5,
) -> float:
    """
    Calculate Recall@K metric.
    """
    if not relevant_doc_ids:
        return 0.0

    top_k_retrieved = set(retrieved_doc_ids[:k])
    relevant_set = set(relevant_doc_ids)

    num_relevant_in_k = len(top_k_retrieved & relevant_set)
    total_relevant = len(relevant_set)

    return num_relevant_in_k / total_relevant


# ---------------------------------------------------------------------------
# Exercise 8: Retrieval Precision@K
# ---------------------------------------------------------------------------
def calculate_precision_at_k(
    retrieved_doc_ids: list[int],
    relevant_doc_ids: list[int],
    k: int = 5,
) -> float:
    """
    Calculate Precision@K metric.
    """
    top_k_retrieved = set(retrieved_doc_ids[:k])
    relevant_set = set(relevant_doc_ids)

    num_relevant_in_k = len(top_k_retrieved & relevant_set)

    return num_relevant_in_k / k


# ---------------------------------------------------------------------------
# Exercise 9: Mean Reciprocal Rank
# ---------------------------------------------------------------------------
def calculate_mrr(
    retrieved_doc_ids: list[int],
    relevant_doc_ids: list[int],
) -> float:
    """
    Calculate Mean Reciprocal Rank.
    """
    relevant_set = set(relevant_doc_ids)

    for rank, doc_id in enumerate(retrieved_doc_ids, 1):
        if doc_id in relevant_set:
            return 1.0 / rank

    return 0.0


# ---------------------------------------------------------------------------
# Exercise 10: Context Window Check
# ---------------------------------------------------------------------------
def check_context_fit(
    prompt_tokens: int,
    response_tokens: int,
    context_window: int = 4096,
) -> bool:
    """
    Check if prompt + response fits within context window with headroom.
    """
    headroom = context_window * 0.1
    available = context_window - headroom

    return prompt_tokens + response_tokens <= available


# ---------------------------------------------------------------------------
# Exercise 11: Relevance Score Fusion
# ---------------------------------------------------------------------------
def fuse_relevance_scores(
    vector_score: float,
    keyword_score: float,
    vector_weight: float = 0.6,
    keyword_weight: float = 0.4,
) -> float:
    """
    Fuse vector and keyword retrieval scores.
    """
    # Normalize keyword score to 0-1 range (assume max BM25 is ~10)
    normalized_keyword = min(keyword_score / 10.0, 1.0)

    fused = (vector_weight * vector_score) + (keyword_weight * normalized_keyword)

    return min(fused, 1.0)


# ---------------------------------------------------------------------------
# Exercise 12: Prompt Construction
# ---------------------------------------------------------------------------
def construct_rag_prompt(
    question: str,
    retrieved_chunks: list[str],
    system_prompt: str = "Answer based on the provided context.",
) -> str:
    """
    Construct a RAG prompt with question and context.
    """
    prompt = f"{system_prompt}\n\nContext:\n"

    for i, chunk in enumerate(retrieved_chunks):
        prompt += f"{chunk}\n"
        if i < len(retrieved_chunks) - 1:
            prompt += "---\n"

    prompt += f"\nQuestion: {question}\nAnswer:"

    return prompt


# ---------------------------------------------------------------------------
# Exercise 13: Duplicate Chunk Detection
# ---------------------------------------------------------------------------
def detect_duplicate_chunks(
    chunks: list[str],
    similarity_threshold: float = 0.95,
) -> list[tuple[int, int]]:
    """
    Detect duplicate or near-duplicate chunks.
    """
    duplicates = []

    for i in range(len(chunks)):
        for j in range(i + 1, len(chunks)):
            # Extract terms
            terms_i = set(chunks[i].lower().split())
            terms_j = set(chunks[j].lower().split())

            # Calculate Jaccard similarity
            if terms_i and terms_j:
                intersection = len(terms_i & terms_j)
                union = len(terms_i | terms_j)
                similarity = intersection / union
            else:
                similarity = 0.0

            if similarity >= similarity_threshold:
                duplicates.append((i, j))

    return duplicates


# ---------------------------------------------------------------------------
# Exercise 14: Chunk Relevance Filtering
# ---------------------------------------------------------------------------
def filter_by_relevance(
    query: str,
    chunks: list[str],
    threshold: float = 0.3,
) -> list[str]:
    """
    Filter chunks by relevance to query.
    """
    query_terms = set(query.lower().split())
    filtered = []

    for chunk in chunks:
        chunk_terms = set(chunk.lower().split())
        matching_terms = len(query_terms & chunk_terms)
        relevance = matching_terms / len(query_terms) if query_terms else 0

        if relevance >= threshold:
            filtered.append(chunk)

    return filtered


# ---------------------------------------------------------------------------
# Exercise 15: Retrieval Result Ranking
# ---------------------------------------------------------------------------
def rank_results(
    chunks: list[dict],
    ranking_method: str = 'relevance',
) -> list[dict]:
    """
    Rank retrieval results by various methods.
    """
    if ranking_method == 'relevance':
        return sorted(chunks, key=lambda x: x.get('score', 0), reverse=True)
    elif ranking_method == 'length':
        return sorted(chunks, key=lambda x: x.get('length', 0), reverse=True)
    elif ranking_method == 'recency':
        return sorted(chunks, key=lambda x: x.get('timestamp', 0), reverse=True)
    else:
        return chunks


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    chunks = chunk_fixed_size("Hello world. This is a test.", chunk_size=10)
    assert len(chunks) > 0

    # Test Exercise 2
    chunks = chunk_by_sentences("Hello. World. Test.", sentences_per_chunk=2)
    assert len(chunks) > 0

    # Test Exercise 3
    keywords = extract_keywords("the quick brown fox jumps over the lazy dog")
    assert len(keywords) > 0

    # Test Exercise 4
    doc = create_document_chunk("Test content", "test.pdf", page_num=1)
    assert doc['length'] == 12

    # Test Exercise 5
    cost = calculate_embedding_cost(100, 256)
    assert cost['tokens'] == 25600

    # Test Exercise 6
    score = calculate_bm25_score(['test'], ['test', 'document'])
    assert score > 0

    # Test Exercise 7
    recall = calculate_recall_at_k([1, 2, 3], [2, 3, 4], k=3)
    assert recall == 2/3

    # Test Exercise 8
    precision = calculate_precision_at_k([1, 2, 3], [2, 3, 4], k=3)
    assert precision == 2/3

    # Test Exercise 9
    mrr = calculate_mrr([1, 2, 3], [2])
    assert mrr == 0.5

    # Test Exercise 10
    fits = check_context_fit(3000, 500, context_window=4096)
    assert fits is True

    # Test Exercise 11
    fused = fuse_relevance_scores(0.8, 5.0)
    assert 0 <= fused <= 1

    # Test Exercise 12
    prompt = construct_rag_prompt("Q?", ["chunk1"])
    assert "Q?" in prompt and "chunk1" in prompt

    # Test Exercise 13
    dups = detect_duplicate_chunks(["test test", "test test", "other"])
    assert len(dups) == 1

    # Test Exercise 14
    filtered = filter_by_relevance("test", ["test chunk", "other chunk"])
    assert len(filtered) == 1

    # Test Exercise 15
    ranked = rank_results([
        {'text': 'b', 'score': 0.9},
        {'text': 'a', 'score': 0.5}
    ])
    assert ranked[0]['score'] == 0.9

    print('All tests passed!')
