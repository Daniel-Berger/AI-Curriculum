"""Production RAG (Retrieval-Augmented Generation) pipeline.

Orchestrates the full RAG workflow: load documents, chunk text, embed
chunks, store in a vector database, retrieve relevant chunks, and
generate answers using an LLM.

Architecture:
    Documents -> DocumentLoader -> Chunker -> EmbeddingService
        -> VectorStore -> Retriever -> LLM -> Answer

Swift parallel:
    - DocumentLoader  ~  FileManager + Data(contentsOf:)
    - Chunker         ~  String slicing with stride/overlap
    - VectorStore     ~  Core Data / GRDB with vector extensions
    - RAGPipeline     ~  A Coordinator pattern orchestrating services

Usage:
    from rag_pipeline import RAGPipeline
    from llm_client import MockLLMClient
    from config import RAGConfig

    config = RAGConfig()
    pipeline = RAGPipeline(config=config, llm_client=MockLLMClient())
    pipeline.ingest("./sample_docs")
    answer = pipeline.query("What is Python?")
    print(answer)
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Sequence

from config import RAGConfig
from llm_client import BaseLLMClient, LLMResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Document:
    """A loaded document with metadata.

    Attributes:
        content: The full text content of the document.
        source: The file path or URI where the document originated.
        metadata: Additional key-value metadata (e.g., file type, title).
    """

    content: str
    source: str
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def doc_id(self) -> str:
        """Deterministic ID based on source and content hash."""
        hash_input = f"{self.source}:{self.content[:200]}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


@dataclass(frozen=True)
class Chunk:
    """A text chunk extracted from a document.

    Attributes:
        text: The chunk text.
        doc_source: The source document's path/URI.
        chunk_index: Position of this chunk within its parent document.
        metadata: Inherited and chunk-specific metadata.
    """

    text: str
    doc_source: str
    chunk_index: int
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def chunk_id(self) -> str:
        """Deterministic ID based on source and chunk index."""
        hash_input = f"{self.doc_source}:chunk_{self.chunk_index}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


@dataclass
class RetrievalResult:
    """A retrieved chunk with its relevance score.

    Attributes:
        chunk: The retrieved text chunk.
        score: Similarity score (higher = more relevant).
        rank: Position in the retrieval ranking (1-based).
    """

    chunk: Chunk
    score: float
    rank: int


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------

class EmbeddingProvider(Protocol):
    """Protocol for embedding services.

    Any class that implements embed() and embed_batch() can be used
    as the embedding provider in the pipeline.

    Swift parallel:
        protocol EmbeddingProvider {
            func embed(_ text: String) -> [Float]
            func embedBatch(_ texts: [String]) -> [[Float]]
        }
    """

    def embed(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


# ---------------------------------------------------------------------------
# DocumentLoader
# ---------------------------------------------------------------------------

class DocumentLoader:
    """Loads documents from files on disk.

    Supports plain text (.txt), markdown (.md), and simple text-based
    formats. For a production system, you would add PDF, DOCX, and
    HTML loaders.

    Swift parallel: Similar to using FileManager.default.contentsOfDirectory
    to list files, then Data(contentsOf:) to read each one.
    """

    SUPPORTED_EXTENSIONS: set[str] = {".txt", ".md", ".text", ".markdown"}

    def load_file(self, file_path: Path) -> Document:
        """Load a single file into a Document.

        Args:
            file_path: Path to the file to load.

        Returns:
            A Document with the file's content and metadata.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is not supported.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {file_path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )

        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"File is empty: {file_path}")

        logger.info("Loaded document: %s (%d chars)", file_path.name, len(content))

        return Document(
            content=content,
            source=str(file_path),
            metadata={
                "filename": file_path.name,
                "extension": file_path.suffix,
                "size_chars": str(len(content)),
            },
        )

    def load_directory(self, dir_path: Path) -> list[Document]:
        """Load all supported files from a directory.

        Args:
            dir_path: Path to the directory to scan.

        Returns:
            A list of Document objects, one per file.

        Raises:
            FileNotFoundError: If the directory does not exist.
            ValueError: If no supported files are found.
        """
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")

        documents: list[Document] = []
        for ext in sorted(self.SUPPORTED_EXTENSIONS):
            for file_path in sorted(dir_path.glob(f"*{ext}")):
                try:
                    documents.append(self.load_file(file_path))
                except (ValueError, FileNotFoundError) as e:
                    logger.warning("Skipping file %s: %s", file_path, e)

        if not documents:
            raise ValueError(
                f"No supported files found in {dir_path}. "
                f"Supported extensions: {self.SUPPORTED_EXTENSIONS}"
            )

        logger.info("Loaded %d documents from %s", len(documents), dir_path)
        return documents


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------

class Chunker:
    """Splits documents into overlapping text chunks.

    Uses recursive text splitting: first tries to split on paragraph
    boundaries, then sentences, then falls back to character-level
    splitting. Overlap ensures context is preserved across chunk
    boundaries.

    Swift parallel: Similar to splitting a String by components
    (separatedBy:) with a sliding window for overlap.
    """

    # Separators ordered from most to least preferred.
    DEFAULT_SEPARATORS: list[str] = ["\n\n", "\n", ". ", " "]

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be less than "
                f"chunk_size ({chunk_size})"
            )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks.

        Args:
            text: The full text to split.

        Returns:
            A list of text chunks, each at most chunk_size characters.
        """
        if not text.strip():
            return []

        if len(text) <= self.chunk_size:
            return [text.strip()]

        return self._recursive_split(text, self.DEFAULT_SEPARATORS)

    def chunk_document(self, document: Document) -> list[Chunk]:
        """Split a Document into Chunk objects with metadata.

        Args:
            document: The document to chunk.

        Returns:
            A list of Chunk objects with inherited metadata.
        """
        raw_chunks = self.chunk_text(document.content)

        return [
            Chunk(
                text=text,
                doc_source=document.source,
                chunk_index=i,
                metadata={**document.metadata, "chunk_total": str(len(raw_chunks))},
            )
            for i, text in enumerate(raw_chunks)
        ]

    def _recursive_split(
        self, text: str, separators: list[str]
    ) -> list[str]:
        """Recursively split text using the preferred separator hierarchy.

        This is the core algorithm behind LangChain's
        RecursiveCharacterTextSplitter, implemented from scratch.
        """
        if not separators:
            # Base case: force-split by character count.
            return self._force_split(text)

        separator = separators[0]
        remaining_separators = separators[1:]

        # Split on the current separator.
        parts = text.split(separator)

        chunks: list[str] = []
        current_chunk = ""

        for part in parts:
            candidate = (
                current_chunk + separator + part if current_chunk else part
            )

            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
            else:
                # Current chunk is full -- save it.
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # If this part alone exceeds chunk_size, split it further.
                if len(part) > self.chunk_size:
                    sub_chunks = self._recursive_split(part, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part

        # Don't forget the last accumulated chunk.
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Apply overlap between consecutive chunks.
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)

        return chunks

    def _force_split(self, text: str) -> list[str]:
        """Split text by character count when no separator works."""
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - self.chunk_overlap if self.chunk_overlap else end
        return chunks

    def _apply_overlap(self, chunks: list[str]) -> list[str]:
        """Add overlap text from the end of each chunk to the start of the next."""
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            overlap_text = prev[-self.chunk_overlap :] if len(prev) > self.chunk_overlap else prev
            combined = overlap_text + " " + chunks[i]
            # Trim to chunk_size if overlap pushed us over.
            if len(combined) > self.chunk_size:
                combined = combined[: self.chunk_size]
            overlapped.append(combined.strip())
        return overlapped


# ---------------------------------------------------------------------------
# EmbeddingService
# ---------------------------------------------------------------------------

class MockEmbeddingService:
    """Mock embedding service for testing without model dependencies.

    Generates deterministic pseudo-embeddings based on text hashing.
    This allows the full pipeline to run in tests and development
    without downloading heavy ML models.

    In production, replace with SentenceTransformerEmbeddingService
    or an API-based embedding provider.
    """

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        """Generate a deterministic pseudo-embedding for a single text.

        Uses character-level hashing to produce a consistent vector
        for the same input text.
        """
        # Create a deterministic hash-based vector.
        hash_bytes = hashlib.sha256(text.encode()).digest()
        # Expand the hash to fill the dimension.
        values: list[float] = []
        for i in range(self.dimension):
            byte_val = hash_bytes[i % len(hash_bytes)]
            # Normalize to [-1, 1] range.
            values.append((byte_val / 127.5) - 1.0)
        return values

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate pseudo-embeddings for a batch of texts."""
        return [self.embed(text) for text in texts]


class SentenceTransformerEmbeddingService:
    """Embedding service using the sentence-transformers library.

    Wraps a SentenceTransformer model to produce real semantic
    embeddings. Requires the sentence-transformers package.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model_name)
            self.dimension = self._model.get_sentence_embedding_dimension()
        except ImportError:
            raise ImportError(
                "The 'sentence-transformers' package is required. "
                "Install it with: pip install sentence-transformers"
            )

    def embed(self, text: str) -> list[float]:
        """Generate an embedding for a single text."""
        embedding = self._model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        embeddings = self._model.encode(texts)
        return embeddings.tolist()


# ---------------------------------------------------------------------------
# VectorStore (wrapping ChromaDB)
# ---------------------------------------------------------------------------

class VectorStore:
    """Vector database wrapper using ChromaDB.

    Stores document chunks as embeddings and supports similarity
    search for retrieval. Falls back to an in-memory store when
    ChromaDB is not available.

    Swift parallel: Similar to Core Data with vector search
    extensions, or a custom index backed by vDSP distance calculations.
    """

    def __init__(
        self,
        collection_name: str = "rag_documents",
        persist_directory: str | None = None,
        embedding_service: MockEmbeddingService | SentenceTransformerEmbeddingService | None = None,
    ) -> None:
        self.collection_name = collection_name
        self._embedding_service = embedding_service or MockEmbeddingService()
        self._use_chromadb = True

        try:
            import chromadb

            if persist_directory:
                self._client = chromadb.PersistentClient(path=persist_directory)
            else:
                self._client = chromadb.Client()

            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "ChromaDB collection '%s' ready (%d items)",
                collection_name,
                self._collection.count(),
            )
        except ImportError:
            logger.warning(
                "ChromaDB not available. Using in-memory fallback. "
                "Install with: pip install chromadb"
            )
            self._use_chromadb = False
            self._memory_store: list[dict] = []

    def add_chunks(self, chunks: list[Chunk]) -> int:
        """Add chunks to the vector store.

        Args:
            chunks: List of Chunk objects to store.

        Returns:
            Number of chunks added.
        """
        if not chunks:
            return 0

        texts = [c.text for c in chunks]
        ids = [c.chunk_id for c in chunks]
        metadatas = [
            {"doc_source": c.doc_source, "chunk_index": c.chunk_index, **c.metadata}
            for c in chunks
        ]

        if self._use_chromadb:
            embeddings = self._embedding_service.embed_batch(texts)
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,  # type: ignore[arg-type]
            )
        else:
            # In-memory fallback.
            embeddings = self._embedding_service.embed_batch(texts)
            for i, chunk in enumerate(chunks):
                self._memory_store.append({
                    "id": ids[i],
                    "text": texts[i],
                    "embedding": embeddings[i],
                    "metadata": metadatas[i],
                })

        logger.info("Added %d chunks to vector store", len(chunks))
        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        """Search for the most relevant chunks given a query.

        Args:
            query: The search query text.
            top_k: Number of results to return.

        Returns:
            A list of RetrievalResult objects ranked by relevance.
        """
        if self._use_chromadb:
            query_embedding = self._embedding_service.embed(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, max(self._collection.count(), 1)),
            )

            retrieval_results: list[RetrievalResult] = []
            if results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                distances = results["distances"][0] if results["distances"] else [0.0] * len(documents)
                metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)

                for rank, (doc, dist, meta) in enumerate(
                    zip(documents, distances, metadatas), start=1
                ):
                    chunk = Chunk(
                        text=doc,
                        doc_source=meta.get("doc_source", "unknown"),
                        chunk_index=int(meta.get("chunk_index", 0)),
                    )
                    # ChromaDB returns distances; convert to similarity.
                    similarity = max(0.0, 1.0 - dist)
                    retrieval_results.append(
                        RetrievalResult(chunk=chunk, score=similarity, rank=rank)
                    )
        else:
            # In-memory cosine similarity search.
            retrieval_results = self._memory_search(query, top_k)

        logger.info(
            "Search for '%s' returned %d results",
            query[:50],
            len(retrieval_results),
        )
        return retrieval_results

    def _memory_search(self, query: str, top_k: int) -> list[RetrievalResult]:
        """In-memory cosine similarity search (fallback)."""
        if not self._memory_store:
            return []

        query_embedding = self._embedding_service.embed(query)

        scored: list[tuple[float, dict]] = []
        for item in self._memory_store:
            score = self._cosine_similarity(query_embedding, item["embedding"])
            scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)

        results: list[RetrievalResult] = []
        for rank, (score, item) in enumerate(scored[:top_k], start=1):
            chunk = Chunk(
                text=item["text"],
                doc_source=item["metadata"].get("doc_source", "unknown"),
                chunk_index=int(item["metadata"].get("chunk_index", 0)),
            )
            results.append(RetrievalResult(chunk=chunk, score=score, rank=rank))

        return results

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @property
    def count(self) -> int:
        """Number of items in the store."""
        if self._use_chromadb:
            return self._collection.count()
        return len(self._memory_store)

    def clear(self) -> None:
        """Remove all items from the store."""
        if self._use_chromadb:
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        else:
            self._memory_store.clear()
        logger.info("Cleared vector store")


# ---------------------------------------------------------------------------
# RAGPipeline -- the orchestrator
# ---------------------------------------------------------------------------

class RAGPipeline:
    """Orchestrates the full RAG workflow.

    This is the main entry point for using the RAG system. It wires
    together document loading, chunking, embedding, storage, retrieval,
    and generation into a cohesive pipeline.

    Swift parallel: This is a Coordinator/Service pattern -- similar to
    how you might build a NetworkService that composes URLSession,
    JSONDecoder, and caching into a single interface.

    Usage:
        config = RAGConfig()
        pipeline = RAGPipeline(config=config, llm_client=MockLLMClient())

        # Ingest documents
        pipeline.ingest("./sample_docs")

        # Query
        answer = pipeline.query("What is Python?")
        print(answer.content)
    """

    def __init__(
        self,
        config: RAGConfig,
        llm_client: BaseLLMClient,
        embedding_service: MockEmbeddingService | SentenceTransformerEmbeddingService | None = None,
    ) -> None:
        self.config = config
        self.llm_client = llm_client

        # Initialize components.
        self.loader = DocumentLoader()
        self.chunker = Chunker(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )
        self._embedding_service = embedding_service or MockEmbeddingService(
            dimension=config.embedding_dimension
        )
        self.vector_store = VectorStore(
            collection_name=config.collection_name,
            persist_directory=None,  # In-memory for development.
            embedding_service=self._embedding_service,
        )

        # Track ingested documents.
        self._ingested_sources: set[str] = set()

        logger.info("RAGPipeline initialized with config: %s", config)

    def ingest(self, source: str | Path) -> int:
        """Ingest documents from a file or directory.

        This runs the load -> chunk -> embed -> store pipeline.

        Args:
            source: Path to a file or directory to ingest.

        Returns:
            Number of chunks stored.
        """
        source_path = Path(source)

        # Load documents.
        if source_path.is_dir():
            documents = self.loader.load_directory(source_path)
        else:
            documents = [self.loader.load_file(source_path)]

        # Chunk all documents.
        all_chunks: list[Chunk] = []
        for doc in documents:
            chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)
            self._ingested_sources.add(doc.source)
            logger.info(
                "Document '%s' split into %d chunks",
                doc.metadata.get("filename", "unknown"),
                len(chunks),
            )

        # Store chunks (embedding happens inside vector_store.add_chunks).
        stored = self.vector_store.add_chunks(all_chunks)
        logger.info(
            "Ingestion complete: %d documents, %d chunks stored",
            len(documents),
            stored,
        )
        return stored

    def query(
        self,
        question: str,
        *,
        top_k: int | None = None,
        rerank: bool = False,
    ) -> LLMResponse:
        """Query the RAG system with a question.

        Retrieves relevant chunks and uses the LLM to generate an
        answer grounded in the retrieved context.

        Args:
            question: The user's question.
            top_k: Number of chunks to retrieve (overrides config).
            rerank: Whether to apply simple re-ranking to results.

        Returns:
            An LLMResponse with the generated answer.

        Raises:
            ValueError: If no documents have been ingested.
        """
        if self.vector_store.count == 0:
            raise ValueError(
                "No documents have been ingested. Call ingest() first."
            )

        k = top_k or self.config.top_k

        # Retrieve relevant chunks.
        results = self.vector_store.search(question, top_k=k)

        if not results:
            return LLMResponse(
                content="No relevant information found for your question.",
                model="none",
            )

        # Optional re-ranking (simple keyword overlap scoring).
        if rerank:
            results = self._rerank(question, results)

        # Build context from retrieved chunks.
        context = self._format_context(results)

        logger.info(
            "Generating answer for: '%s' (using %d chunks)",
            question[:80],
            len(results),
        )

        # Generate answer.
        response = self.llm_client.generate(
            context=context,
            question=question,
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens,
        )

        return response

    def query_with_sources(
        self,
        question: str,
        *,
        top_k: int | None = None,
    ) -> tuple[LLMResponse, list[RetrievalResult]]:
        """Query and return both the answer and the source chunks.

        This is useful when you want to display citations alongside
        the answer.

        Args:
            question: The user's question.
            top_k: Number of chunks to retrieve.

        Returns:
            A tuple of (LLMResponse, list of RetrievalResults).
        """
        k = top_k or self.config.top_k
        results = self.vector_store.search(question, top_k=k)
        context = self._format_context(results)

        response = self.llm_client.generate(
            context=context,
            question=question,
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens,
        )

        return response, results

    def _format_context(self, results: list[RetrievalResult]) -> str:
        """Format retrieved chunks into a context string for the LLM.

        Each chunk is labeled with its source and relevance score
        to help the LLM weigh information appropriately.
        """
        sections: list[str] = []
        for result in results:
            source = Path(result.chunk.doc_source).name
            sections.append(
                f"[Source: {source} | Relevance: {result.score:.2f}]\n"
                f"{result.chunk.text}"
            )
        return "\n\n---\n\n".join(sections)

    def _rerank(
        self, query: str, results: list[RetrievalResult]
    ) -> list[RetrievalResult]:
        """Simple keyword-based re-ranking.

        Boosts chunks that contain exact query terms. In production,
        you would use a cross-encoder model for re-ranking (e.g.,
        cross-encoder/ms-marco-MiniLM-L-6-v2).
        """
        query_terms = set(re.findall(r"\w+", query.lower()))

        reranked: list[tuple[float, RetrievalResult]] = []
        for result in results:
            chunk_terms = set(re.findall(r"\w+", result.chunk.text.lower()))
            # Keyword overlap as a simple relevance boost.
            overlap = len(query_terms & chunk_terms)
            boost = overlap / max(len(query_terms), 1) * 0.3
            combined_score = result.score + boost
            reranked.append((combined_score, result))

        reranked.sort(key=lambda x: x[0], reverse=True)

        return [
            RetrievalResult(
                chunk=r.chunk,
                score=score,
                rank=rank,
            )
            for rank, (score, r) in enumerate(reranked, start=1)
        ]

    @property
    def ingested_sources(self) -> set[str]:
        """Set of source paths that have been ingested."""
        return set(self._ingested_sources)

    @property
    def chunk_count(self) -> int:
        """Total number of chunks in the vector store."""
        return self.vector_store.count
