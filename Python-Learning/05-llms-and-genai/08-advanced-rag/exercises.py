"""
Module 08: Advanced RAG — Exercises
====================================

12 exercises on HyDE, multi-query retrieval, re-ranking, GraphRAG, and RAGAS.

Run this file directly to check your solutions:
    python exercises.py
"""


# ---------------------------------------------------------------------------
# Exercise 1: HyDE Generation Prompt
# ---------------------------------------------------------------------------
def create_hyde_prompt(query: str) -> str:
    """
    Create a prompt to generate a hypothetical document for HyDE.

    Args:
        query: User query

    Returns:
        Prompt for LLM to generate hypothetical document
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Query Paraphrasing
# ---------------------------------------------------------------------------
def paraphrase_query(query: str, num_variants: int = 3) -> list[str]:
    """
    Generate paraphrased versions of a query.

    For exercise purposes, return simple variations.
    Return: original + simple rewrites

    Args:
        query: Original query
        num_variants: Number of variants to generate

    Returns:
        List of paraphrased queries
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Result Deduplication
# ---------------------------------------------------------------------------
def deduplicate_results(
    results: list[dict],
    key: str = 'id',
) -> list[dict]:
    """
    Remove duplicate results from combined retrieval results.

    Keep first occurrence, sum scores for duplicates.

    Args:
        results: List of result dicts
        key: Key to use for deduplication

    Returns:
        Deduplicated list
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Score Aggregation
# ---------------------------------------------------------------------------
def aggregate_scores(
    result_groups: list[list[tuple[int, float]]],
) -> dict[int, float]:
    """
    Aggregate scores from multiple retrieval runs.

    Each group is list of (doc_id, score) tuples from one query.
    Sum scores for documents appearing in multiple groups.

    Args:
        result_groups: List of score lists from different queries

    Returns:
        Dict mapping doc_id to aggregated score
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Cross-Encoder Re-Ranking (Mock)
# ---------------------------------------------------------------------------
def mock_rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """
    Mock re-ranking based on simple string overlap.

    Score each candidate by fraction of query terms it contains.

    Args:
        query: Query string
        candidates: List of candidate dicts with 'text' key
        top_k: Number to return

    Returns:
        Top-k candidates sorted by relevance
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Graph Node Creation
# ---------------------------------------------------------------------------
def create_graph_node(
    entity_id: str,
    name: str,
    entity_type: str,
    properties: dict = None,
) -> dict:
    """
    Create a graph node structure.

    Args:
        entity_id: Unique identifier
        name: Entity name
        entity_type: Type (person, place, concept, etc.)
        properties: Optional properties dict

    Returns:
        Node dict with keys: id, name, type, properties
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Graph Edge Creation
# ---------------------------------------------------------------------------
def create_graph_edge(
    source_id: str,
    target_id: str,
    relation_type: str,
    weight: float = 1.0,
) -> dict:
    """
    Create a graph edge (relationship) structure.

    Args:
        source_id: Source node ID
        target_id: Target node ID
        relation_type: Type of relationship
        weight: Importance weight

    Returns:
        Edge dict with keys: source, target, relation, weight
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 8: Faithfulness Score (Mock)
# ---------------------------------------------------------------------------
def evaluate_faithfulness(
    context: str,
    answer: str,
) -> float:
    """
    Evaluate if answer is grounded in context (mock evaluation).

    Use term overlap as proxy: fraction of answer terms in context.

    Args:
        context: Retrieved document context
        answer: Generated answer

    Returns:
        Faithfulness score 0-1
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 9: Context Relevance Score (Mock)
# ---------------------------------------------------------------------------
def evaluate_context_relevance(
    query: str,
    context: str,
) -> float:
    """
    Evaluate if context is relevant to query (mock evaluation).

    Use term overlap: fraction of query terms in context.

    Args:
        query: Original query
        context: Retrieved context

    Returns:
        Relevance score 0-1
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 10: RAG Evaluation Report
# ---------------------------------------------------------------------------
def create_evaluation_report(
    query: str,
    context: str,
    answer: str,
) -> dict:
    """
    Create a comprehensive evaluation report for RAG system.

    Calculate faithfulness and relevance scores.

    Args:
        query: Original query
        context: Retrieved context
        answer: Generated answer

    Returns:
        Dict with keys: faithfulness, context_relevance, overall_score
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 11: Adaptive Retrieval Threshold
# ---------------------------------------------------------------------------
def should_retrieve_more(
    top_score: float,
    threshold: float = 0.7,
) -> bool:
    """
    Determine if should retrieve more documents based on confidence.

    Args:
        top_score: Highest score from initial retrieval
        threshold: Confidence threshold

    Returns:
        True if should retrieve more, False otherwise
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 12: Multi-Hop Path Finding (Mock)
# ---------------------------------------------------------------------------
def find_related_entities(
    graph: dict,
    start_entity: str,
    num_hops: int = 2,
) -> list[str]:
    """
    Find entities related to start entity within num_hops steps.

    Graph format: {'edges': [{'source': ..., 'target': ..., ...}, ...]}

    Args:
        graph: Graph dict with 'edges' key
        start_entity: Starting entity ID
        num_hops: Number of relationship hops to traverse

    Returns:
        List of reachable entity IDs
    """
    pass


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    prompt = create_hyde_prompt("What is AI?")
    assert isinstance(prompt, str) and len(prompt) > 0

    # Test Exercise 2
    variants = paraphrase_query("hello world", num_variants=2)
    assert len(variants) >= 2

    # Test Exercise 3
    results = [{'id': 1, 'score': 0.9}, {'id': 1, 'score': 0.8}]
    dedup = deduplicate_results(results)
    assert len(dedup) == 1

    # Test Exercise 4
    groups = [[(1, 0.8), (2, 0.7)], [(1, 0.6)]]
    agg = aggregate_scores(groups)
    assert agg[1] == 1.4

    # Test Exercise 5
    reranked = mock_rerank("test", [{'text': 'test doc'}])
    assert len(reranked) > 0

    # Test Exercise 6
    node = create_graph_node('e1', 'Alice', 'person')
    assert node['name'] == 'Alice'

    # Test Exercise 7
    edge = create_graph_edge('e1', 'e2', 'knows')
    assert edge['relation'] == 'knows'

    # Test Exercise 8
    faith = evaluate_faithfulness('test content', 'test')
    assert 0 <= faith <= 1

    # Test Exercise 9
    rel = evaluate_context_relevance('test query', 'test content')
    assert 0 <= rel <= 1

    # Test Exercise 10
    report = create_evaluation_report('Q', 'C', 'A')
    assert 'faithfulness' in report

    # Test Exercise 11
    should = should_retrieve_more(0.5, threshold=0.7)
    assert should is True

    # Test Exercise 12
    graph = {'edges': [{'source': 'a', 'target': 'b'}]}
    related = find_related_entities(graph, 'a', num_hops=1)
    assert 'b' in related

    print('All tests passed!')
