"""
Chunking Module
===============

Implements multiple text chunking strategies for preparing documents for
embedding and retrieval. The choice of chunking strategy significantly
impacts retrieval quality.

Strategies:
- **Fixed-size**: Split text into chunks of N characters/tokens with overlap
- **Semantic**: Split at natural boundaries (paragraphs, sections) using NLP
- **Recursive**: LangChain-style recursive splitting by multiple separators

Each strategy preserves source metadata and adds chunk-level metadata
(chunk index, start/end positions, overlap info).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .ingestion import Document


class ChunkingMethod(Enum):
    """Available chunking methods."""

    FIXED = "fixed"
    SEMANTIC = "semantic"
    RECURSIVE = "recursive"


@dataclass
class Chunk:
    """A chunk of text derived from a document.

    Attributes
    ----------
    content : str
        The chunk text.
    metadata : dict
        Inherited document metadata plus chunk-specific info.
    chunk_index : int
        Position of this chunk within the source document.
    doc_id : str
        ID of the parent document.
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_index: int = 0
    doc_id: str = ""


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies.

    Parameters
    ----------
    chunk_size : int
        Target chunk size (in characters or tokens, depending on strategy).
    chunk_overlap : int
        Number of characters/tokens to overlap between consecutive chunks.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """Split a document into chunks.

        Parameters
        ----------
        document : Document
            The document to chunk.

        Returns
        -------
        list of Chunk
            The resulting chunks.
        """
        ...

    def chunk_batch(self, documents: List[Document]) -> List[Chunk]:
        """Chunk multiple documents.

        Parameters
        ----------
        documents : list of Document
            Documents to chunk.

        Returns
        -------
        list of Chunk
            All chunks from all documents.
        """
        chunks: List[Chunk] = []
        for doc in documents:
            chunks.extend(self.chunk(doc))
        return chunks


class FixedSizeChunker(ChunkingStrategy):
    """Split text into fixed-size chunks with configurable overlap.

    Simply splits text at character boundaries every `chunk_size` characters,
    with `chunk_overlap` characters shared between consecutive chunks.
    """

    def chunk(self, document: Document) -> List[Chunk]:
        """Split document into fixed-size character chunks.

        Parameters
        ----------
        document : Document
            Source document.

        Returns
        -------
        list of Chunk
            Fixed-size chunks.
        """
        raise NotImplementedError


class SemanticChunker(ChunkingStrategy):
    """Split text at semantic boundaries (paragraphs, sections, sentences).

    Uses NLP-based sentence boundary detection and groups sentences into
    chunks that respect natural text boundaries while staying within
    the size limit.
    """

    def chunk(self, document: Document) -> List[Chunk]:
        """Split document at semantic boundaries.

        Parameters
        ----------
        document : Document
            Source document.

        Returns
        -------
        list of Chunk
            Semantically coherent chunks.
        """
        raise NotImplementedError


class RecursiveChunker(ChunkingStrategy):
    """Recursively split text using a hierarchy of separators.

    Attempts to split on double newlines first, then single newlines,
    then sentences, then words -- preserving the largest possible
    coherent units within the size limit.

    Parameters
    ----------
    separators : list of str, optional
        Ordered list of separators to try. Defaults to
        ['\\n\\n', '\\n', '. ', ' '].
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
    ) -> None:
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.separators = separators or ["\n\n", "\n", ". ", " "]

    def chunk(self, document: Document) -> List[Chunk]:
        """Recursively split document using separator hierarchy.

        Parameters
        ----------
        document : Document
            Source document.

        Returns
        -------
        list of Chunk
            Chunks created via recursive splitting.
        """
        raise NotImplementedError


def create_chunker(
    method: ChunkingMethod,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    **kwargs: Any,
) -> ChunkingStrategy:
    """Factory function to create a chunking strategy.

    Parameters
    ----------
    method : ChunkingMethod
        Which chunking strategy to use.
    chunk_size : int
        Target chunk size.
    chunk_overlap : int
        Overlap between chunks.
    **kwargs
        Additional strategy-specific parameters.

    Returns
    -------
    ChunkingStrategy
        The configured chunker instance.
    """
    strategies = {
        ChunkingMethod.FIXED: FixedSizeChunker,
        ChunkingMethod.SEMANTIC: SemanticChunker,
        ChunkingMethod.RECURSIVE: RecursiveChunker,
    }
    strategy_cls = strategies.get(method)
    if strategy_cls is None:
        raise ValueError(f"Unknown chunking method: {method}")
    return strategy_cls(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)
