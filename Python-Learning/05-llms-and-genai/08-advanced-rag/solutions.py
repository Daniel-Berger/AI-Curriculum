"""
Module 08: Advanced RAG — Solutions
====================================

Complete solutions for all 12 exercises.
"""

from collections import defaultdict


# ---------------------------------------------------------------------------
# Exercise 1: HyDE Generation Prompt
# ---------------------------------------------------------------------------
def create_hyde_prompt(query: str) -> str:
    """
    Create a prompt to generate a hypothetical document for HyDE.
    """
    return f"""Generate a hypothetical document that would answer this query.
The document should be realistic and relevant.

Query: {query}

Hypothetical document:"""


# ---------------------------------------------------------------------------
# Exercise 2: Query Paraphrasing
# ---------------------------------------------------------------------------
def paraphrase_query(query: str, num_variants: int = 3) -> list[str]:
    """
    Generate paraphrased versions of a query.
    """
    variants = [query]

    # Simple paraphrasing strategies
    if num_variants >= 2:
        variants.append(f"Find information about: {query}")
    if num_variants >= 3:
        variants.append(f"What is {query}?")
    if num_variants >= 4:
        variants.append(f"Explain {query}")
    if num_variants >= 5:
        variants.append(f"Details on {query}")

    return variants[:num_variants]


# ---------------------------------------------------------------------------
# Exercise 3: Result Deduplication
# ---------------------------------------------------------------------------
def deduplicate_results(
    results: list[dict],
    key: str = 'id',
) -> list[dict]:
    """
    Remove duplicate results, summing scores.
    """
    dedup_dict = {}

    for result in results:
        result_key = result.get(key)
        if result_key not in dedup_dict:
            dedup_dict[result_key] = result.copy()
        else:
            # Sum scores
            if 'score' in result and 'score' in dedup_dict[result_key]:
                dedup_dict[result_key]['score'] += result['score']

    return list(dedup_dict.values())


# ---------------------------------------------------------------------------
# Exercise 4: Score Aggregation
# ---------------------------------------------------------------------------
def aggregate_scores(
    result_groups: list[list[tuple[int, float]]],
) -> dict[int, float]:
    """
    Aggregate scores from multiple retrieval runs.
    """
    aggregated = defaultdict(float)

    for group in result_groups:
        for doc_id, score in group:
            aggregated[doc_id] += score

    return dict(aggregated)


# ---------------------------------------------------------------------------
# Exercise 5: Cross-Encoder Re-Ranking (Mock)
# ---------------------------------------------------------------------------
def mock_rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """
    Mock re-ranking based on string overlap.
    """
    query_terms = set(query.lower().split())

    scored = []
    for candidate in candidates:
        text = candidate.get('text', '').lower()
        text_terms = set(text.split())

        # Overlap score
        overlap = len(query_terms & text_terms)
        score = overlap / len(query_terms) if query_terms else 0

        scored.append((candidate, score))

    # Sort by score
    sorted_candidates = sorted(scored, key=lambda x: x[1], reverse=True)

    return [cand for cand, _ in sorted_candidates[:top_k]]


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
    """
    return {
        'id': entity_id,
        'name': name,
        'type': entity_type,
        'properties': properties or {},
    }


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
    Create a graph edge structure.
    """
    return {
        'source': source_id,
        'target': target_id,
        'relation': relation_type,
        'weight': weight,
    }


# ---------------------------------------------------------------------------
# Exercise 8: Faithfulness Score (Mock)
# ---------------------------------------------------------------------------
def evaluate_faithfulness(
    context: str,
    answer: str,
) -> float:
    """
    Evaluate if answer is grounded in context.
    """
    context_terms = set(context.lower().split())
    answer_terms = set(answer.lower().split())

    if not answer_terms:
        return 1.0

    # Fraction of answer terms in context
    overlap = len(answer_terms & context_terms)
    faithfulness = overlap / len(answer_terms)

    return min(faithfulness, 1.0)


# ---------------------------------------------------------------------------
# Exercise 9: Context Relevance Score (Mock)
# ---------------------------------------------------------------------------
def evaluate_context_relevance(
    query: str,
    context: str,
) -> float:
    """
    Evaluate if context is relevant to query.
    """
    query_terms = set(query.lower().split())
    context_terms = set(context.lower().split())

    if not query_terms:
        return 0.0

    # Fraction of query terms in context
    overlap = len(query_terms & context_terms)
    relevance = overlap / len(query_terms)

    return min(relevance, 1.0)


# ---------------------------------------------------------------------------
# Exercise 10: RAG Evaluation Report
# ---------------------------------------------------------------------------
def create_evaluation_report(
    query: str,
    context: str,
    answer: str,
) -> dict:
    """
    Create a comprehensive evaluation report.
    """
    faithfulness = evaluate_faithfulness(context, answer)
    context_relevance = evaluate_context_relevance(query, context)

    # Overall score is average
    overall_score = (faithfulness + context_relevance) / 2

    return {
        'faithfulness': round(faithfulness, 3),
        'context_relevance': round(context_relevance, 3),
        'overall_score': round(overall_score, 3),
    }


# ---------------------------------------------------------------------------
# Exercise 11: Adaptive Retrieval Threshold
# ---------------------------------------------------------------------------
def should_retrieve_more(
    top_score: float,
    threshold: float = 0.7,
) -> bool:
    """
    Determine if should retrieve more documents.
    """
    return top_score < threshold


# ---------------------------------------------------------------------------
# Exercise 12: Multi-Hop Path Finding (Mock)
# ---------------------------------------------------------------------------
def find_related_entities(
    graph: dict,
    start_entity: str,
    num_hops: int = 2,
) -> list[str]:
    """
    Find entities related within num_hops steps.
    """
    visited = {start_entity}
    current_level = {start_entity}

    edges = graph.get('edges', [])

    for _ in range(num_hops):
        next_level = set()

        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')

            # Forward edges
            if source in current_level and target not in visited:
                next_level.add(target)
                visited.add(target)

            # Backward edges
            if target in current_level and source not in visited:
                next_level.add(source)
                visited.add(source)

        current_level = next_level

    return list(visited - {start_entity})


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Test Exercise 1
    prompt = create_hyde_prompt("What is AI?")
    assert "hypothetical" in prompt.lower()

    # Test Exercise 2
    variants = paraphrase_query("hello", num_variants=2)
    assert len(variants) >= 2

    # Test Exercise 3
    results = [{'id': 1, 'score': 0.9}, {'id': 1, 'score': 0.8}]
    dedup = deduplicate_results(results)
    assert len(dedup) == 1
    assert dedup[0]['score'] == 1.7

    # Test Exercise 4
    groups = [[(1, 0.8), (2, 0.7)], [(1, 0.6)]]
    agg = aggregate_scores(groups)
    assert agg[1] == 1.4
    assert agg[2] == 0.7

    # Test Exercise 5
    reranked = mock_rerank("test", [{'text': 'test doc'}, {'text': 'other'}])
    assert reranked[0]['text'] == 'test doc'

    # Test Exercise 6
    node = create_graph_node('e1', 'Alice', 'person')
    assert node['name'] == 'Alice'
    assert node['type'] == 'person'

    # Test Exercise 7
    edge = create_graph_edge('e1', 'e2', 'knows', weight=0.8)
    assert edge['source'] == 'e1'
    assert edge['weight'] == 0.8

    # Test Exercise 8
    faith = evaluate_faithfulness('test content', 'test')
    assert faith > 0

    # Test Exercise 9
    rel = evaluate_context_relevance('test query', 'test content')
    assert rel > 0

    # Test Exercise 10
    report = create_evaluation_report('Q', 'Q test', 'Q')
    assert 'overall_score' in report

    # Test Exercise 11
    assert should_retrieve_more(0.5) is True
    assert should_retrieve_more(0.9) is False

    # Test Exercise 12
    graph = {'edges': [{'source': 'a', 'target': 'b'}, {'source': 'b', 'target': 'c'}]}
    related = find_related_entities(graph, 'a', num_hops=1)
    assert 'b' in related

    print('All tests passed!')
