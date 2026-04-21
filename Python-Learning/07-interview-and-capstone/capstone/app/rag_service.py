"""
RAG (Retrieval-Augmented Generation) Service.

Handles document loading, chunking, embedding, and retrieval.
"""

import logging
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval-Augmented Generation service.

    Responsibilities:
    - Load documents from various formats
    - Chunk documents into overlapping segments
    - Embed chunks using SentenceTransformers
    - Store in ChromaDB vector database
    - Retrieve relevant chunks for user queries
    - Manage document lifecycle
    """

    def __init__(
        self,
        chroma_host: str = "localhost",
        chroma_port: int = 8000,
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        """Initialize RAG service.

        Args:
            chroma_host: ChromaDB server host
            chroma_port: ChromaDB server port
            embedding_model: HuggingFace embedding model name
            chunk_size: Characters per chunk
            chunk_overlap: Overlap between chunks for context preservation
        """
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Mock ChromaDB client (in production, use chromadb.HttpClient)
        self.client = None
        self.collection = None
        self.documents = {}  # In-memory document store for mocking

        self._initialize_chroma()

    def _initialize_chroma(self):
        """Initialize ChromaDB connection."""
        try:
            # Mock: In production, use:
            # import chromadb
            # self.client = chromadb.HttpClient(
            #     host=self.chroma_host,
            #     port=self.chroma_port
            # )
            # self.collection = self.client.get_or_create_collection(
            #     name="documents",
            #     metadata={"hnsw:space": "cosine"}
            # )

            logger.info(f"ChromaDB initialized (mock mode)")
            self.client = {"mock": True}
            self.collection = {"mock": True}

        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            raise

    def load_and_index_document(
        self,
        document_name: str,
        content: str
    ) -> Dict[str, int]:
        """Load document and index chunks.

        Args:
            document_name: Name/identifier for document
            content: Document text content

        Returns:
            Metadata: document_id, chunks_created, tokens_used
        """
        try:
            logger.info(f"Indexing document: {document_name}")

            # Chunk the document
            chunks = self._chunk_document(content)
            logger.info(f"Created {len(chunks)} chunks")

            # Embed and store chunks
            doc_id = document_name.replace(" ", "_").replace(".", "_")
            stored = self._store_chunks(doc_id, document_name, chunks)

            # Update metadata
            self.documents[doc_id] = {
                "name": document_name,
                "chunks": len(chunks),
                "indexed_at": datetime.utcnow(),
                "content_length": len(content)
            }

            logger.info(f"Document {doc_id} indexed successfully")

            return {
                "document_id": doc_id,
                "chunks_created": len(chunks),
                "tokens_used": len(chunks) * 20  # Rough estimate
            }

        except Exception as e:
            logger.error(f"Document indexing failed: {e}")
            raise

    def _chunk_document(self, content: str) -> List[str]:
        """Split document into overlapping chunks.

        Args:
            content: Document text

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(content):
            end = min(start + self.chunk_size, len(content))
            chunk = content[start:end]

            # Don't split words
            if end < len(content):
                last_space = chunk.rfind(" ")
                if last_space > 0:
                    end = start + last_space
                    chunk = content[start:end]

            if chunk.strip():
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def _store_chunks(
        self,
        doc_id: str,
        doc_name: str,
        chunks: List[str]
    ) -> int:
        """Store chunks in vector database.

        Args:
            doc_id: Document identifier
            doc_name: Document name
            chunks: List of text chunks

        Returns:
            Number of chunks stored
        """
        try:
            # Mock storage (in production, would embed and store in ChromaDB)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"

                # Store in-memory
                if not hasattr(self, '_chunks'):
                    self._chunks = {}

                self._chunks[chunk_id] = {
                    "content": chunk,
                    "document_id": doc_id,
                    "document_name": doc_name,
                    "chunk_index": i,
                    "embedding": None  # Would be real embedding in production
                }

            logger.info(f"Stored {len(chunks)} chunks for {doc_id}")
            return len(chunks)

        except Exception as e:
            logger.error(f"Chunk storage failed: {e}")
            raise

    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 3,
        doc_filter: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Retrieve relevant document chunks for query.

        Args:
            query: User question/query
            top_k: Number of chunks to retrieve
            doc_filter: Optional document ID to filter by

        Returns:
            List of relevant chunks with metadata
        """
        try:
            logger.info(f"Retrieving chunks for query: {query[:50]}")

            # Mock retrieval (in production: vector similarity search)
            results = []

            # Simple keyword matching for mock
            query_words = query.lower().split()

            if hasattr(self, '_chunks'):
                for chunk_id, chunk_data in self._chunks.items():
                    if doc_filter and chunk_data["document_id"] != doc_filter:
                        continue

                    content = chunk_data["content"].lower()
                    matches = sum(1 for word in query_words if word in content)

                    if matches > 0:
                        results.append({
                            "content": chunk_data["content"][:200],  # Preview
                            "document_id": chunk_data["document_id"],
                            "document_name": chunk_data["document_name"],
                            "chunk_index": chunk_data["chunk_index"],
                            "score": matches / len(query_words)  # Relevance score
                        })

            # Sort by score and return top-k
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []

    def build_context(self, chunks: List[Dict[str, str]]) -> str:
        """Build context string from retrieved chunks.

        Args:
            chunks: Retrieved chunks

        Returns:
            Formatted context for LLM
        """
        if not chunks:
            return ""

        context_parts = ["Retrieved context:"]
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"\n[Document {i}: {chunk.get('document_name', 'Unknown')}]\n"
                f"{chunk['content']}"
            )

        return "\n".join(context_parts)

    def list_documents(self) -> List[Dict]:
        """List all indexed documents."""
        docs = []
        for doc_id, metadata in self.documents.items():
            docs.append({
                "id": doc_id,
                "name": metadata["name"],
                "chunks": metadata["chunks"],
                "indexed_at": metadata["indexed_at"].isoformat()
            })
        return docs

    def delete_document(self, doc_id: str) -> bool:
        """Delete document and its chunks.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            if doc_id not in self.documents:
                return False

            # Remove from metadata
            del self.documents[doc_id]

            # Remove chunks
            if hasattr(self, '_chunks'):
                to_delete = [
                    k for k, v in self._chunks.items()
                    if v["document_id"] == doc_id
                ]
                for k in to_delete:
                    del self._chunks[k]

            logger.info(f"Deleted document {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    def check_connection(self) -> bool:
        """Check ChromaDB connection."""
        try:
            # Mock check
            return self.client is not None
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False

    def close(self):
        """Close ChromaDB connection."""
        try:
            # Clean up resources
            self.client = None
            self.collection = None
            logger.info("ChromaDB connection closed")
        except Exception as e:
            logger.error(f"Close failed: {e}")
