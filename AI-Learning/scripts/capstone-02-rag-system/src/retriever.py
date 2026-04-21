"""
Hybrid Retriever Module
=======================

Implements a hybrid retrieval strategy combining:
1. **Dense retrieval**: Semantic similarity via vector embeddings
2. **Sparse retrieval**: Keyword matching via BM25
3. **Reranking**: Cross-encoder reranking of combined results

The hybrid approach balances semantic understanding with keyword precision,
and the reranking stage further refines the ranking using a more powerful
model for the final top-k selection.

Reciprocal Rank Fusion (RRF) is used to merge dense and sparse result lists
before reranking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .embeddings import EmbeddingService


@dataclass
class RetrievalResult:
    """A single retrieval result with content and scoring details.

    Attributes
    ----------
    content : str
        The retrieved chunk text.
    metadata : dict
        Source information and chunk metadata.
    score : float
        Final relevance score after fusion/reranking.
    dense_score : float or None
        Score from dense retrieval.
    sparse_score : float or None
        Score from sparse retrieval.
    rerank_score : float or None
        Score from cross-encoder reranking.
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    dense_score: Optional[float] = None
    sparse_score: Optional[float] = None
    rerank_score: Optional[float] = None


class HybridRetriever:
    """Hybrid retrieval combining dense, sparse, and reranking stages.

    Parameters
    ----------
    embedding_service : EmbeddingService
        Service for dense embedding-based retrieval.
    sparse_top_k : int
        Number of candidates from sparse (BM25) retrieval.
    dense_top_k : int
        Number of candidates from dense (vector) retrieval.
    final_top_k : int
        Number of final results after reranking.
    reranker_model : str, optional
        Cross-encoder model name for reranking (e.g.,
        'cross-encoder/ms-marco-MiniLM-L-6-v2').
    rrf_k : int
        Reciprocal Rank Fusion parameter (default 60).
    enable_reranking : bool
        Whether to apply cross-encoder reranking.

    Examples
    --------
    >>> retriever = HybridRetriever(
    ...     embedding_service=embedding_svc,
    ...     final_top_k=5,
    ...     enable_reranking=True,
    ... )
    >>> results = retriever.retrieve("What is RAG?")
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        sparse_top_k: int = 20,
        dense_top_k: int = 20,
        final_top_k: int = 5,
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        rrf_k: int = 60,
        enable_reranking: bool = True,
    ) -> None:
        self.embedding_service = embedding_service
        self.sparse_top_k = sparse_top_k
        self.dense_top_k = dense_top_k
        self.final_top_k = final_top_k
        self.reranker_model = reranker_model
        self.rrf_k = rrf_k
        self.enable_reranking = enable_reranking
        self._bm25_index: Optional[Any] = None
        self._reranker: Optional[Any] = None
        self._corpus: List[str] = []

    def initialize(self, corpus: List[str]) -> None:
        """Build the BM25 index and load the reranker model.

        Parameters
        ----------
        corpus : list of str
            All document chunks for BM25 indexing.
        """
        raise NotImplementedError

    def retrieve(self, query: str) -> List[RetrievalResult]:
        """Run the full hybrid retrieval pipeline.

        Performs dense retrieval, sparse retrieval, fuses results via RRF,
        and optionally reranks with a cross-encoder.

        Parameters
        ----------
        query : str
            The user's search query.

        Returns
        -------
        list of RetrievalResult
            Top-k results ranked by relevance.
        """
        raise NotImplementedError

    def dense_search(self, query: str) -> List[RetrievalResult]:
        """Perform dense vector similarity search.

        Parameters
        ----------
        query : str
            Search query.

        Returns
        -------
        list of RetrievalResult
            Dense retrieval results.
        """
        raise NotImplementedError

    def sparse_search(self, query: str) -> List[RetrievalResult]:
        """Perform sparse BM25 keyword search.

        Parameters
        ----------
        query : str
            Search query.

        Returns
        -------
        list of RetrievalResult
            Sparse retrieval results.
        """
        raise NotImplementedError

    def reciprocal_rank_fusion(
        self,
        dense_results: List[RetrievalResult],
        sparse_results: List[RetrievalResult],
    ) -> List[RetrievalResult]:
        """Merge dense and sparse result lists using Reciprocal Rank Fusion.

        Parameters
        ----------
        dense_results : list of RetrievalResult
            Results from dense retrieval.
        sparse_results : list of RetrievalResult
            Results from sparse retrieval.

        Returns
        -------
        list of RetrievalResult
            Fused and sorted results.
        """
        raise NotImplementedError

    def rerank(
        self, query: str, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """Rerank results using a cross-encoder model.

        Parameters
        ----------
        query : str
            Original query for cross-encoder scoring.
        results : list of RetrievalResult
            Candidate results to rerank.

        Returns
        -------
        list of RetrievalResult
            Reranked results with updated scores.
        """
        raise NotImplementedError
