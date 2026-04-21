"""
Retriever Tests
===============

Unit tests for the hybrid retrieval system. Tests cover individual
retrieval methods (dense, sparse), fusion logic, and reranking.
Uses mocked embedding services and vector stores.
"""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chunking import Chunk
from src.embeddings import EmbeddingService, EmbeddingProvider, VectorStoreType
from src.retriever import HybridRetriever, RetrievalResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_embedding_service() -> MagicMock:
    """Create a mocked EmbeddingService."""
    service = MagicMock(spec=EmbeddingService)
    service.similarity_search.return_value = [
        {
            "content": "RAG combines retrieval with generation.",
            "metadata": {"source": "doc1.pdf", "page": 1},
            "score": 0.95,
        },
        {
            "content": "Vector databases store embeddings efficiently.",
            "metadata": {"source": "doc2.pdf", "page": 3},
            "score": 0.87,
        },
    ]
    return service


@pytest.fixture
def sample_corpus() -> List[str]:
    """Sample document corpus for BM25 indexing."""
    return [
        "Retrieval-Augmented Generation combines search with LLMs.",
        "Vector databases like ChromaDB store document embeddings.",
        "BM25 is a sparse retrieval algorithm based on term frequency.",
        "Cross-encoders provide more accurate relevance scoring.",
        "Chunking strategies affect retrieval quality significantly.",
    ]


@pytest.fixture
def retriever(mock_embedding_service: MagicMock) -> HybridRetriever:
    """Create a HybridRetriever with mocked dependencies."""
    return HybridRetriever(
        embedding_service=mock_embedding_service,
        sparse_top_k=10,
        dense_top_k=10,
        final_top_k=3,
        enable_reranking=False,
    )


# ---------------------------------------------------------------------------
# HybridRetriever Tests
# ---------------------------------------------------------------------------


class TestHybridRetriever:
    """Tests for the HybridRetriever class."""

    def test_init_default_params(self) -> None:
        """HybridRetriever should initialize with sensible defaults."""
        retriever = HybridRetriever()
        assert retriever.final_top_k == 5
        assert retriever.enable_reranking is True
        assert retriever.rrf_k == 60

    def test_init_custom_params(self, retriever: HybridRetriever) -> None:
        """HybridRetriever should store custom configuration."""
        assert retriever.final_top_k == 3
        assert retriever.enable_reranking is False

    def test_initialize_raises_not_implemented(
        self, retriever: HybridRetriever, sample_corpus: List[str]
    ) -> None:
        """initialize should raise NotImplementedError until implemented."""
        with pytest.raises(NotImplementedError):
            retriever.initialize(sample_corpus)

    def test_retrieve_raises_not_implemented(
        self, retriever: HybridRetriever
    ) -> None:
        """retrieve should raise NotImplementedError until implemented."""
        with pytest.raises(NotImplementedError):
            retriever.retrieve("What is RAG?")

    def test_dense_search_raises_not_implemented(
        self, retriever: HybridRetriever
    ) -> None:
        """dense_search should raise NotImplementedError until implemented."""
        with pytest.raises(NotImplementedError):
            retriever.dense_search("test query")

    def test_sparse_search_raises_not_implemented(
        self, retriever: HybridRetriever
    ) -> None:
        """sparse_search should raise NotImplementedError until implemented."""
        with pytest.raises(NotImplementedError):
            retriever.sparse_search("test query")

    def test_rrf_raises_not_implemented(
        self, retriever: HybridRetriever
    ) -> None:
        """reciprocal_rank_fusion should raise NotImplementedError until implemented."""
        dense = [RetrievalResult(content="a", score=0.9)]
        sparse = [RetrievalResult(content="b", score=0.8)]
        with pytest.raises(NotImplementedError):
            retriever.reciprocal_rank_fusion(dense, sparse)


class TestRetrievalResult:
    """Tests for the RetrievalResult dataclass."""

    def test_creation_with_defaults(self) -> None:
        """RetrievalResult should have sensible defaults."""
        result = RetrievalResult(content="test content")
        assert result.content == "test content"
        assert result.score == 0.0
        assert result.dense_score is None
        assert result.sparse_score is None
        assert result.rerank_score is None

    def test_creation_with_all_scores(self) -> None:
        """RetrievalResult should store all score types."""
        result = RetrievalResult(
            content="test",
            score=0.9,
            dense_score=0.85,
            sparse_score=0.7,
            rerank_score=0.95,
        )
        assert result.dense_score == 0.85
        assert result.sparse_score == 0.7
        assert result.rerank_score == 0.95
