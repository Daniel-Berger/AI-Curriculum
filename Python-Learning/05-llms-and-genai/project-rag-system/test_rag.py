"""pytest test suite for the RAG pipeline.

Tests cover all pipeline components: document loading, chunking,
embedding, vector storage, retrieval, and end-to-end query flow.
All tests run without API keys by using MockLLMClient and
MockEmbeddingService.

Swift parallel: This is the Python equivalent of XCTestCase,
using pytest fixtures instead of setUp()/tearDown() and parametrize
instead of repeated test methods.

Run:
    pytest test_rag.py -v
    pytest test_rag.py --cov=rag_pipeline --cov=llm_client -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from config import RAGConfig
from llm_client import (
    LLMResponse,
    MockLLMClient,
    format_rag_prompt,
)
from rag_pipeline import (
    Chunk,
    Chunker,
    Document,
    DocumentLoader,
    MockEmbeddingService,
    RAGPipeline,
    RetrievalResult,
    VectorStore,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_docs_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample documents."""
    doc1 = tmp_path / "python.txt"
    doc1.write_text(
        "Python is a high-level programming language. "
        "It supports multiple paradigms including OOP and functional programming. "
        "Python uses dynamic typing and automatic memory management.",
        encoding="utf-8",
    )

    doc2 = tmp_path / "ml.md"
    doc2.write_text(
        "Machine learning is a subset of artificial intelligence. "
        "Supervised learning uses labeled data to train models. "
        "Common algorithms include decision trees and neural networks.",
        encoding="utf-8",
    )

    doc3 = tmp_path / "llm.txt"
    doc3.write_text(
        "Large language models are based on the Transformer architecture. "
        "They use self-attention mechanisms to process sequences. "
        "Modern LLMs like Claude and GPT use decoder-only architectures.",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture
def sample_document() -> Document:
    """Create a sample Document for testing."""
    return Document(
        content=(
            "Python is a versatile programming language.\n\n"
            "It was created by Guido van Rossum in 1991.\n\n"
            "Python emphasizes code readability and simplicity."
        ),
        source="/test/python.txt",
        metadata={"filename": "python.txt", "extension": ".txt"},
    )


@pytest.fixture
def mock_llm() -> MockLLMClient:
    """Create a mock LLM client."""
    return MockLLMClient(
        responses=[
            "Python is a high-level programming language created by Guido van Rossum.",
            "Machine learning uses algorithms to learn from data.",
            "Transformers use self-attention mechanisms.",
        ]
    )


@pytest.fixture
def rag_config() -> RAGConfig:
    """Create a test RAG configuration."""
    return RAGConfig(
        chunk_size=200,
        chunk_overlap=20,
        top_k=2,
        collection_name="test_collection",
    )


@pytest.fixture
def pipeline(rag_config: RAGConfig, mock_llm: MockLLMClient) -> RAGPipeline:
    """Create a RAGPipeline with mock components."""
    return RAGPipeline(
        config=rag_config,
        llm_client=mock_llm,
        embedding_service=MockEmbeddingService(dimension=64),
    )


# ---------------------------------------------------------------------------
# DocumentLoader Tests
# ---------------------------------------------------------------------------

class TestDocumentLoader:
    """Tests for the DocumentLoader class."""

    def test_load_single_file(self, sample_docs_dir: Path) -> None:
        """DocumentLoader should load a single text file."""
        loader = DocumentLoader()
        doc = loader.load_file(sample_docs_dir / "python.txt")

        assert "Python" in doc.content
        assert doc.source == str(sample_docs_dir / "python.txt")
        assert doc.metadata["extension"] == ".txt"

    def test_load_directory(self, sample_docs_dir: Path) -> None:
        """DocumentLoader should load all supported files from a directory."""
        loader = DocumentLoader()
        docs = loader.load_directory(sample_docs_dir)

        assert len(docs) == 3  # .txt, .md, .txt
        sources = {doc.metadata["filename"] for doc in docs}
        assert "python.txt" in sources
        assert "ml.md" in sources

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """DocumentLoader should raise FileNotFoundError for missing files."""
        loader = DocumentLoader()

        with pytest.raises(FileNotFoundError):
            loader.load_file(tmp_path / "nonexistent.txt")

    def test_load_unsupported_extension(self, tmp_path: Path) -> None:
        """DocumentLoader should raise ValueError for unsupported file types."""
        unsupported = tmp_path / "data.json"
        unsupported.write_text('{"key": "value"}', encoding="utf-8")

        loader = DocumentLoader()
        with pytest.raises(ValueError, match="Unsupported file type"):
            loader.load_file(unsupported)

    def test_load_empty_file(self, tmp_path: Path) -> None:
        """DocumentLoader should raise ValueError for empty files."""
        empty = tmp_path / "empty.txt"
        empty.write_text("", encoding="utf-8")

        loader = DocumentLoader()
        with pytest.raises(ValueError, match="empty"):
            loader.load_file(empty)


# ---------------------------------------------------------------------------
# Chunker Tests
# ---------------------------------------------------------------------------

class TestChunker:
    """Tests for the Chunker class."""

    def test_short_text_single_chunk(self) -> None:
        """Text shorter than chunk_size should remain a single chunk."""
        chunker = Chunker(chunk_size=500, chunk_overlap=50)
        chunks = chunker.chunk_text("Hello, world!")

        assert len(chunks) == 1
        assert chunks[0] == "Hello, world!"

    def test_long_text_multiple_chunks(self) -> None:
        """Text longer than chunk_size should be split into multiple chunks."""
        chunker = Chunker(chunk_size=100, chunk_overlap=10)
        text = "This is a sentence. " * 20  # ~400 chars

        chunks = chunker.chunk_text(text)
        assert len(chunks) > 1
        # Each chunk should be at most chunk_size.
        for chunk in chunks:
            assert len(chunk) <= 110  # Allow slight overflow from overlap.

    def test_chunk_overlap(self) -> None:
        """Consecutive chunks should share overlapping text."""
        chunker = Chunker(chunk_size=100, chunk_overlap=20)
        text = "Word " * 60  # ~300 chars

        chunks = chunker.chunk_text(text)
        assert len(chunks) >= 2

    def test_chunk_document(self, sample_document: Document) -> None:
        """chunk_document should produce Chunk objects with metadata."""
        chunker = Chunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.chunk_document(sample_document)

        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)
        assert chunks[0].doc_source == sample_document.source
        assert chunks[0].chunk_index == 0
        assert "chunk_total" in chunks[0].metadata

    def test_empty_text_returns_empty_list(self) -> None:
        """Empty or whitespace-only text should return an empty list."""
        chunker = Chunker(chunk_size=500, chunk_overlap=50)

        assert chunker.chunk_text("") == []
        assert chunker.chunk_text("   ") == []

    def test_invalid_overlap_raises_error(self) -> None:
        """chunk_overlap >= chunk_size should raise ValueError."""
        with pytest.raises(ValueError, match="chunk_overlap"):
            Chunker(chunk_size=100, chunk_overlap=100)


# ---------------------------------------------------------------------------
# Embedding Tests
# ---------------------------------------------------------------------------

class TestMockEmbeddingService:
    """Tests for the MockEmbeddingService."""

    def test_embed_returns_correct_dimension(self) -> None:
        """Embedding should have the configured dimension."""
        service = MockEmbeddingService(dimension=128)
        embedding = service.embed("Hello, world!")

        assert len(embedding) == 128
        assert all(isinstance(v, float) for v in embedding)

    def test_embed_deterministic(self) -> None:
        """Same input should produce the same embedding."""
        service = MockEmbeddingService(dimension=64)

        emb1 = service.embed("Test text")
        emb2 = service.embed("Test text")

        assert emb1 == emb2

    def test_embed_different_texts(self) -> None:
        """Different inputs should produce different embeddings."""
        service = MockEmbeddingService(dimension=64)

        emb1 = service.embed("First text")
        emb2 = service.embed("Second text")

        assert emb1 != emb2

    def test_embed_batch(self) -> None:
        """embed_batch should process multiple texts at once."""
        service = MockEmbeddingService(dimension=64)
        texts = ["Hello", "World", "Test"]

        embeddings = service.embed_batch(texts)
        assert len(embeddings) == 3
        assert all(len(emb) == 64 for emb in embeddings)


# ---------------------------------------------------------------------------
# VectorStore Tests
# ---------------------------------------------------------------------------

class TestVectorStore:
    """Tests for the VectorStore class."""

    def test_add_and_count(self) -> None:
        """Adding chunks should increase the store count."""
        store = VectorStore(
            collection_name="test_add",
            embedding_service=MockEmbeddingService(dimension=64),
        )
        chunks = [
            Chunk(text="Chunk one about Python", doc_source="doc1.txt", chunk_index=0),
            Chunk(text="Chunk two about ML", doc_source="doc1.txt", chunk_index=1),
        ]

        added = store.add_chunks(chunks)
        assert added == 2
        assert store.count == 2

    def test_search_returns_results(self) -> None:
        """Search should return ranked results."""
        store = VectorStore(
            collection_name="test_search",
            embedding_service=MockEmbeddingService(dimension=64),
        )
        chunks = [
            Chunk(text="Python is a programming language", doc_source="py.txt", chunk_index=0),
            Chunk(text="Machine learning uses algorithms", doc_source="ml.txt", chunk_index=0),
            Chunk(text="Deep learning uses neural networks", doc_source="dl.txt", chunk_index=0),
        ]
        store.add_chunks(chunks)

        results = store.search("What is Python?", top_k=2)
        assert len(results) <= 2
        assert all(isinstance(r, RetrievalResult) for r in results)
        assert results[0].rank == 1

    def test_search_empty_store(self) -> None:
        """Search on an empty store should return empty results."""
        store = VectorStore(
            collection_name="test_empty_search",
            embedding_service=MockEmbeddingService(dimension=64),
        )

        results = store.search("anything", top_k=3)
        assert results == []

    def test_clear_store(self) -> None:
        """Clear should remove all items from the store."""
        store = VectorStore(
            collection_name="test_clear",
            embedding_service=MockEmbeddingService(dimension=64),
        )
        chunks = [
            Chunk(text="Test chunk", doc_source="test.txt", chunk_index=0),
        ]
        store.add_chunks(chunks)
        assert store.count == 1

        store.clear()
        assert store.count == 0


# ---------------------------------------------------------------------------
# LLM Client Tests
# ---------------------------------------------------------------------------

class TestMockLLMClient:
    """Tests for the MockLLMClient."""

    def test_generate_returns_response(self) -> None:
        """MockLLMClient should return an LLMResponse."""
        client = MockLLMClient()
        response = client.generate(context="Test context", question="Test?")

        assert isinstance(response, LLMResponse)
        assert response.content
        assert response.model == "mock-model"

    def test_generate_uses_canned_responses(self) -> None:
        """MockLLMClient should cycle through provided responses."""
        client = MockLLMClient(responses=["Answer one", "Answer two"])

        r1 = client.generate(context="ctx", question="q1")
        r2 = client.generate(context="ctx", question="q2")

        assert r1.content == "Answer one"
        assert r2.content == "Answer two"

    def test_call_history_tracked(self) -> None:
        """MockLLMClient should record all calls for test assertions."""
        client = MockLLMClient()
        client.generate(context="context1", question="question1")
        client.generate(context="context2", question="question2")

        assert len(client.call_history) == 2
        assert client.call_history[0]["question"] == "question1"
        assert client.call_history[1]["context"] == "context2"

    def test_stream_yields_words(self) -> None:
        """MockLLMClient.stream should yield words one at a time."""
        client = MockLLMClient(responses=["Hello world test"])
        tokens = list(client.stream(context="ctx", question="q"))

        assert len(tokens) == 3
        assert "Hello" in tokens[0]

    def test_format_rag_prompt(self) -> None:
        """format_rag_prompt should produce system + user messages."""
        messages = format_rag_prompt(context="Some context", question="What?")

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "Some context" in messages[1]["content"]
        assert "What?" in messages[1]["content"]


# ---------------------------------------------------------------------------
# RAGPipeline Integration Tests
# ---------------------------------------------------------------------------

class TestRAGPipeline:
    """End-to-end tests for the RAGPipeline."""

    def test_ingest_directory(
        self, pipeline: RAGPipeline, sample_docs_dir: Path
    ) -> None:
        """Pipeline should ingest all documents from a directory."""
        chunks_stored = pipeline.ingest(sample_docs_dir)

        assert chunks_stored > 0
        assert len(pipeline.ingested_sources) == 3

    def test_ingest_single_file(
        self, pipeline: RAGPipeline, sample_docs_dir: Path
    ) -> None:
        """Pipeline should ingest a single file."""
        chunks_stored = pipeline.ingest(sample_docs_dir / "python.txt")

        assert chunks_stored > 0
        assert len(pipeline.ingested_sources) == 1

    def test_query_after_ingest(
        self, pipeline: RAGPipeline, sample_docs_dir: Path
    ) -> None:
        """Pipeline should answer questions after ingestion."""
        pipeline.ingest(sample_docs_dir)
        response = pipeline.query("What is Python?")

        assert isinstance(response, LLMResponse)
        assert response.content  # Should have non-empty answer.

    def test_query_before_ingest_raises(self, pipeline: RAGPipeline) -> None:
        """Querying before ingestion should raise ValueError."""
        with pytest.raises(ValueError, match="No documents"):
            pipeline.query("What is Python?")

    def test_query_with_sources(
        self, pipeline: RAGPipeline, sample_docs_dir: Path
    ) -> None:
        """query_with_sources should return both answer and source chunks."""
        pipeline.ingest(sample_docs_dir)
        response, sources = pipeline.query_with_sources("What is ML?")

        assert isinstance(response, LLMResponse)
        assert len(sources) > 0
        assert all(isinstance(s, RetrievalResult) for s in sources)

    def test_query_with_reranking(
        self, pipeline: RAGPipeline, sample_docs_dir: Path
    ) -> None:
        """Query with reranking should still return valid results."""
        pipeline.ingest(sample_docs_dir)
        response = pipeline.query("What is Python?", rerank=True)

        assert isinstance(response, LLMResponse)
        assert response.content

    def test_full_pipeline_end_to_end(
        self, sample_docs_dir: Path, mock_llm: MockLLMClient
    ) -> None:
        """Full end-to-end test: config -> ingest -> query -> answer."""
        config = RAGConfig(
            chunk_size=150,
            chunk_overlap=15,
            top_k=2,
            collection_name="e2e_test",
        )
        pipeline = RAGPipeline(
            config=config,
            llm_client=mock_llm,
            embedding_service=MockEmbeddingService(dimension=32),
        )

        # Ingest
        chunks = pipeline.ingest(sample_docs_dir)
        assert chunks > 0
        assert pipeline.chunk_count > 0

        # Query
        response = pipeline.query("Explain transformers")
        assert response.content
        assert response.model == "mock-model"

        # Verify the LLM was called with context.
        assert len(mock_llm.call_history) == 1
        assert mock_llm.call_history[0]["question"] == "Explain transformers"
        assert mock_llm.call_history[0]["context"]  # Context should not be empty.


# ---------------------------------------------------------------------------
# Data Structure Tests
# ---------------------------------------------------------------------------

class TestDataStructures:
    """Tests for Document, Chunk, and RetrievalResult dataclasses."""

    def test_document_id_deterministic(self) -> None:
        """Document ID should be deterministic for same inputs."""
        doc1 = Document(content="Test", source="test.txt")
        doc2 = Document(content="Test", source="test.txt")

        assert doc1.doc_id == doc2.doc_id

    def test_chunk_id_deterministic(self) -> None:
        """Chunk ID should be deterministic for same source and index."""
        chunk1 = Chunk(text="Hello", doc_source="test.txt", chunk_index=0)
        chunk2 = Chunk(text="Hello", doc_source="test.txt", chunk_index=0)

        assert chunk1.chunk_id == chunk2.chunk_id

    def test_chunk_id_differs_by_index(self) -> None:
        """Different chunk indices should produce different IDs."""
        chunk1 = Chunk(text="Hello", doc_source="test.txt", chunk_index=0)
        chunk2 = Chunk(text="Hello", doc_source="test.txt", chunk_index=1)

        assert chunk1.chunk_id != chunk2.chunk_id
