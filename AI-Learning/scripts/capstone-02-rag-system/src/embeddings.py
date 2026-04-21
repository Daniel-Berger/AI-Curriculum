"""
Embedding Service Module
========================

Manages document embedding generation and vector store interactions.
Supports multiple embedding providers (OpenAI, sentence-transformers,
Cohere) and vector databases (ChromaDB, Qdrant).

Responsibilities:
- Generate embeddings for text chunks
- Batch embedding with rate limiting
- Store and retrieve embeddings from vector databases
- Manage vector store collections and indices
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np

from .chunking import Chunk


class EmbeddingProvider(Enum):
    """Supported embedding model providers."""

    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    COHERE = "cohere"


class VectorStoreType(Enum):
    """Supported vector database backends."""

    CHROMADB = "chromadb"
    QDRANT = "qdrant"


class EmbeddingService:
    """Generate and manage embeddings for document chunks.

    Parameters
    ----------
    provider : EmbeddingProvider
        Which embedding model provider to use.
    model_name : str
        Specific model name (e.g., 'text-embedding-3-small',
        'all-MiniLM-L6-v2').
    vector_store_type : VectorStoreType
        Which vector database to use for storage.
    collection_name : str
        Name of the vector store collection.
    vector_store_config : dict, optional
        Connection parameters for the vector database.

    Examples
    --------
    >>> service = EmbeddingService(
    ...     provider=EmbeddingProvider.OPENAI,
    ...     model_name="text-embedding-3-small",
    ...     vector_store_type=VectorStoreType.CHROMADB,
    ...     collection_name="documents",
    ... )
    >>> service.embed_and_store(chunks)
    """

    def __init__(
        self,
        provider: EmbeddingProvider = EmbeddingProvider.OPENAI,
        model_name: str = "text-embedding-3-small",
        vector_store_type: VectorStoreType = VectorStoreType.CHROMADB,
        collection_name: str = "documents",
        vector_store_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.provider = provider
        self.model_name = model_name
        self.vector_store_type = vector_store_type
        self.collection_name = collection_name
        self.vector_store_config = vector_store_config or {}
        self._client: Optional[Any] = None
        self._collection: Optional[Any] = None

    def initialize(self) -> None:
        """Initialize the embedding model and vector store connection.

        Raises
        ------
        ConnectionError
            If the vector store cannot be reached.
        """
        raise NotImplementedError

    def embed_text(self, text: str) -> np.ndarray:
        """Generate an embedding vector for a single text string.

        Parameters
        ----------
        text : str
            Input text to embed.

        Returns
        -------
        np.ndarray
            Embedding vector.
        """
        raise NotImplementedError

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a batch of texts.

        Handles rate limiting and batching automatically.

        Parameters
        ----------
        texts : list of str
            Texts to embed.

        Returns
        -------
        list of np.ndarray
            Embedding vectors.
        """
        raise NotImplementedError

    def embed_and_store(self, chunks: List[Chunk]) -> int:
        """Embed chunks and store them in the vector database.

        Parameters
        ----------
        chunks : list of Chunk
            Text chunks to embed and store.

        Returns
        -------
        int
            Number of chunks successfully stored.
        """
        raise NotImplementedError

    def similarity_search(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find the most similar chunks to a query string.

        Parameters
        ----------
        query : str
            The search query.
        top_k : int
            Number of results to return.

        Returns
        -------
        list of dict
            Each dict contains 'content', 'metadata', and 'score'.
        """
        raise NotImplementedError

    def delete_collection(self) -> None:
        """Delete the current vector store collection.

        Use with caution -- this removes all stored embeddings.
        """
        raise NotImplementedError

    def get_collection_stats(self) -> Dict[str, Any]:
        """Return statistics about the current collection.

        Returns
        -------
        dict
            Keys: 'total_documents', 'embedding_dimension', 'collection_name'.
        """
        raise NotImplementedError
