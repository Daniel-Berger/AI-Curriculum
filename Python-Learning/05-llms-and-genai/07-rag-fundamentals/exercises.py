"""
Module 07: RAG Fundamentals — Exercises
========================================

15 exercises on RAG architecture, chunking, retrieval, and evaluation.

Run this file directly to check your solutions:
    python exercises.py
"""


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

    Args:
        text: Input text
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks

    Returns:
        List of chunks
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Sentence-Based Chunking
# ---------------------------------------------------------------------------
def chunk_by_sentences(
    text: str,
    sentences_per_chunk: int = 3,
) -> list[str]:
    """
    Split text into chunks based on sentence boundaries.

    Split on '. ' and group sentences_per_chunk sentences together.

    Args:
        text: Input text
        sentences_per_chunk: How many sentences per chunk

    Returns:
        List of chunks (each is sentences_per_chunk sentences)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Vocabulary Extraction
# ---------------------------------------------------------------------------
def extract_keywords(
    text: str,
    top_k: int = 10,
) -> list[str]:
    """
    Extract top-k most frequent words (keywords) from text.

    Filter out common stop words: a, the, is, and, or, but, in, on, at, to, for, of, etc.

    Args:
        text: Input text
        top_k: Number of top keywords to return

    Returns:
        List of top-k keywords (lowercase)
    """
    pass


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

    Args:
        content: Chunk text
        source: Source document name
        page_num: Page number (if applicable)
        chunk_id: Chunk index

    Returns:
        Dict with keys: 'content', 'source', 'page', 'id', 'length'
        'length' should be character count of content
    """
    pass


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

    Pricing (per 1M tokens):
    - text-embedding-3-small: $0.02
    - text-embedding-3-large: $0.13
    - open-source (free): $0

    Speed: ~10k chunks per minute typically

    Args:
        num_chunks: Total chunks to embed
        avg_chunk_tokens: Average tokens per chunk
        model: Model name

    Returns:
        Dict with 'cost' (dollars), 'tokens' (int), 'time_minutes' (float)
    """
    pass


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
    Simple BM25 scoring (without IDF for this exercise).

    BM25 formula (simplified): score = sum of term frequencies adjusted by saturation

    For each query term in doc: score += (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_doc_len)))

    For this exercise, use avg_doc_len = len(doc_terms).

    Args:
        query_terms: List of query terms
        doc_terms: List of document terms
        k1: Saturation parameter (default 1.5)
        b: Length normalization (default 0.75)

    Returns:
        BM25 score (float)
    """
    pass


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

    Recall@K = (# relevant docs in top-k) / (# total relevant docs)

    Args:
        retrieved_doc_ids: Ranked list of retrieved document IDs
        relevant_doc_ids: Set of all relevant document IDs
        k: Top-K to consider

    Returns:
        Recall@K as float (0-1)
    """
    pass


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

    Precision@K = (# relevant docs in top-k) / k

    Args:
        retrieved_doc_ids: Ranked list of retrieved document IDs
        relevant_doc_ids: Set of all relevant document IDs
        k: Top-K to consider

    Returns:
        Precision@K as float (0-1)
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Mean Reciprocal Rank
# ---------------------------------------------------------------------------
def calculate_mrr(
    retrieved_doc_ids: list[int],
    relevant_doc_ids: list[int],
) -> float:
    """
    Calculate Mean Reciprocal Rank.

    MRR = 1 / (position of first relevant doc)

    Args:
        retrieved_doc_ids: Ranked list of retrieved document IDs
        relevant_doc_ids: Set of all relevant document IDs

    Returns:
        MRR as float (0-1), or 0 if no relevant doc found
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: Context Window Check
# ---------------------------------------------------------------------------
def check_context_fit(
    prompt_tokens: int,
    response_tokens: int,
    context_window: int = 4096,
) -> bool:
    """
    Check if prompt + response fits within context window.

    Need headroom: reserve 10% of context for safety.

    Args:
        prompt_tokens: Tokens in prompt (including retrieved context)
        response_tokens: Estimated max output tokens
        context_window: Model's context window size

    Returns:
        True if fits, False otherwise
    """
    pass


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

    Weighted average: vector_weight * vector_score + keyword_weight * keyword_score

    Args:
        vector_score: Cosine similarity (0-1)
        keyword_score: BM25 score (typically 0-10, normalize first)
        vector_weight: Weight for vector score
        keyword_weight: Weight for keyword score

    Returns:
        Fused score (float)
    """
    pass


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

    Format:
    {system_prompt}

    Context:
    {chunk1}
    ---
    {chunk2}
    ...

    Question: {question}
    Answer:

    Args:
        question: User question
        retrieved_chunks: List of retrieved document chunks
        system_prompt: System instruction

    Returns:
        Formatted prompt string
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 13: Duplicate Chunk Detection
# ---------------------------------------------------------------------------
def detect_duplicate_chunks(
    chunks: list[str],
    similarity_threshold: float = 0.95,
) -> list[tuple[int, int]]:
    """
    Detect duplicate or near-duplicate chunks.

    Use simple similarity: if two chunks share >similarity_threshold of terms, they're duplicates.

    Args:
        chunks: List of text chunks
        similarity_threshold: Similarity threshold (0-1)

    Returns:
        List of (index1, index2) tuples for duplicate pairs
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 14: Chunk Relevance Filtering
# ---------------------------------------------------------------------------
def filter_by_relevance(
    query: str,
    chunks: list[str],
    threshold: float = 0.3,
) -> list[str]:
    """
    Filter chunks by relevance to query (keyword overlap).

    Relevance = (# query terms in chunk) / (# query terms)

    Args:
        query: User query string
        chunks: List of chunks
        threshold: Minimum relevance (0-1)

    Returns:
        List of chunks that meet threshold
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 15: Retrieval Result Ranking
# ---------------------------------------------------------------------------
def rank_results(
    chunks: list[dict],
    ranking_method: str = 'relevance',
) -> list[dict]:
    """
    Rank retrieval results by various methods.

    Methods:
    - 'relevance': By score (highest first)
    - 'length': By length (longest first - more context)
    - 'recency': By timestamp (newest first, if available)

    Args:
        chunks: List of chunk dicts with 'score' and optionally 'length', 'timestamp'
        ranking_method: How to rank

    Returns:
        Sorted list of chunks
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    chunks = chunk_fixed_size("Hello world. This is a test.", chunk_size=10)
    assert isinstance(chunks, list) and len(chunks) > 0

    # Test Exercise 2
    chunks = chunk_by_sentences("Hello. World. Test.", sentences_per_chunk=2)
    assert len(chunks) > 0

    # Test Exercise 3
    keywords = extract_keywords("the quick brown fox jumps over the lazy dog")
    assert isinstance(keywords, list)

    # Test Exercise 4
    doc = create_document_chunk("Test content", "test.pdf", page_num=1)
    assert 'content' in doc and 'source' in doc

    # Test Exercise 5
    cost = calculate_embedding_cost(100, 256)
    assert 'cost' in cost and 'tokens' in cost

    # Test Exercise 6
    score = calculate_bm25_score(['test'], ['test', 'document'])
    assert isinstance(score, float)

    # Test Exercise 7
    recall = calculate_recall_at_k([1, 2, 3], [2, 3, 4], k=3)
    assert 0 <= recall <= 1

    # Test Exercise 8
    precision = calculate_precision_at_k([1, 2, 3], [2, 3, 4], k=3)
    assert 0 <= precision <= 1

    # Test Exercise 9
    mrr = calculate_mrr([1, 2, 3], [2, 3, 4])
    assert 0 <= mrr <= 1

    # Test Exercise 10
    fits = check_context_fit(1000, 200, context_window=2048)
    assert isinstance(fits, bool)

    # Test Exercise 11
    fused = fuse_relevance_scores(0.8, 5.0)
    assert isinstance(fused, float)

    # Test Exercise 12
    prompt = construct_rag_prompt("Q?", ["chunk1", "chunk2"])
    assert "Q?" in prompt

    # Test Exercise 13
    dups = detect_duplicate_chunks(["test doc", "test doc", "other"])
    assert isinstance(dups, list)

    # Test Exercise 14
    filtered = filter_by_relevance("test", ["test chunk", "other chunk"])
    assert isinstance(filtered, list)

    # Test Exercise 15
    ranked = rank_results([
        {'text': 'a', 'score': 0.5},
        {'text': 'b', 'score': 0.9}
    ])
    assert ranked[0]['score'] >= ranked[-1]['score']

    print('All tests passed!')
