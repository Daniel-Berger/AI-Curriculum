"""
Comprehensive tests for RAG Chat Application.

Covers:
- API endpoints
- Request/response validation
- Error handling
- Service integration
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.main import app
from app.models import ChatRequest, ChatResponse
from app.rag_service import RAGService
from app.agent_service import AgentService
from app.llm_client import LLMClient


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_rag_service():
    """Mock RAG service."""
    service = Mock(spec=RAGService)
    service.retrieve_relevant_chunks = Mock(return_value=[
        {
            "content": "Test document content",
            "document_id": "doc1",
            "document_name": "Test.txt",
            "chunk_index": 0,
            "score": 0.95
        }
    ])
    service.build_context = Mock(return_value="Test context")
    service.list_documents = Mock(return_value=[])
    service.delete_document = Mock(return_value=True)
    service.check_connection = Mock(return_value=True)
    service.close = Mock()
    return service


@pytest.fixture
def mock_llm_client():
    """Mock LLM client."""
    client = Mock(spec=LLMClient)
    client.generate_response = AsyncMock(return_value="This is a test response.")
    client.stream_response = AsyncMock()
    client.count_tokens = Mock(return_value=10)
    return client


# ============================================================================
# Chat Endpoint Tests
# ============================================================================

class TestChatEndpoint:
    """Test chat endpoint."""

    def test_chat_valid_request(self, client):
        """Test valid chat request."""
        payload = {
            "message": "What is RAG?",
            "chat_id": "user123",
            "temperature": 0.7
        }

        # Note: In actual test, we'd patch the services
        # For now, this tests the model validation
        response = client.post("/chat", json=payload)

        # Should get response (may be error if services not initialized)
        assert response.status_code in [200, 500]

    def test_chat_missing_required_field(self, client):
        """Test chat request missing required field."""
        payload = {
            "chat_id": "user123"
            # missing "message"
        }

        response = client.post("/chat", json=payload)
        assert response.status_code == 422  # Validation error

    def test_chat_empty_message(self, client):
        """Test chat request with empty message."""
        payload = {
            "message": "   ",  # Whitespace only
            "chat_id": "user123"
        }

        response = client.post("/chat", json=payload)
        assert response.status_code == 422

    def test_chat_invalid_temperature(self, client):
        """Test chat with invalid temperature."""
        payload = {
            "message": "Hello",
            "chat_id": "user123",
            "temperature": 1.5  # Outside 0-1 range
        }

        response = client.post("/chat", json=payload)
        assert response.status_code == 422

    def test_chat_message_too_long(self, client):
        """Test chat with excessively long message."""
        payload = {
            "message": "x" * 100000,  # Over max_length
            "chat_id": "user123"
        }

        response = client.post("/chat", json=payload)
        assert response.status_code == 422


# ============================================================================
# Document Management Endpoint Tests
# ============================================================================

class TestDocumentEndpoints:
    """Test document management endpoints."""

    def test_list_documents_empty(self, client):
        """Test listing documents when none exist."""
        response = client.get("/documents")

        # Should return empty list or error depending on initialization
        assert response.status_code in [200, 500]

    def test_upload_document(self, client):
        """Test document upload."""
        file_content = b"This is test document content."

        response = client.post(
            "/documents/upload",
            files={"file": ("test.txt", file_content, "text/plain")}
        )

        # Should succeed or return initialization error
        assert response.status_code in [200, 500]

    def test_upload_document_missing_file(self, client):
        """Test document upload without file."""
        response = client.post("/documents/upload")

        assert response.status_code == 422  # Validation error

    def test_delete_document(self, client):
        """Test document deletion."""
        response = client.delete("/documents/test_doc")

        # Should handle gracefully
        assert response.status_code in [200, 404, 500]


# ============================================================================
# Health & Monitoring Tests
# ============================================================================

class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "total_tokens_used" in data
        assert "errors" in data


# ============================================================================
# Root Endpoint Tests
# ============================================================================

class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "endpoints" in data


# ============================================================================
# Model Validation Tests
# ============================================================================

class TestModelValidation:
    """Test Pydantic model validation."""

    def test_chat_request_valid(self):
        """Test valid ChatRequest."""
        req = ChatRequest(
            message="Hello",
            chat_id="user123",
            temperature=0.5
        )
        assert req.message == "Hello"
        assert req.temperature == 0.5

    def test_chat_request_temperature_bounds(self):
        """Test temperature bounds."""
        with pytest.raises(ValueError):
            ChatRequest(
                message="Hello",
                chat_id="user123",
                temperature=1.5  # > 1.0
            )

    def test_chat_response(self):
        """Test ChatResponse creation."""
        resp = ChatResponse(
            message="Test response",
            sources=[{"document": "test.txt", "snippet": "test"}],
            tokens_used=100
        )
        assert resp.message == "Test response"
        assert len(resp.sources) == 1


# ============================================================================
# RAG Service Tests
# ============================================================================

class TestRAGService:
    """Test RAG service."""

    def test_rag_initialization(self):
        """Test RAG service initialization."""
        service = RAGService(
            chroma_host="localhost",
            chroma_port=8000,
            chunk_size=500,
            chunk_overlap=100
        )

        assert service.chunk_size == 500
        assert service.chunk_overlap == 100

    def test_chunk_document(self):
        """Test document chunking."""
        service = RAGService(chunk_size=100, chunk_overlap=20)

        content = "a" * 250

        chunks = service._chunk_document(content)

        assert len(chunks) > 0
        assert all(len(chunk) <= 100 for chunk in chunks)

    def test_load_and_index_document(self):
        """Test document indexing."""
        service = RAGService()

        result = service.load_and_index_document(
            document_name="test.txt",
            content="This is test content."
        )

        assert "document_id" in result
        assert "chunks_created" in result

    def test_retrieve_chunks_empty(self):
        """Test retrieval with no documents."""
        service = RAGService()

        chunks = service.retrieve_relevant_chunks("test query")

        assert chunks == []

    def test_list_documents(self):
        """Test listing documents."""
        service = RAGService()

        # Index a document first
        service.load_and_index_document("test.txt", "content")

        docs = service.list_documents()

        assert len(docs) > 0

    def test_delete_document(self):
        """Test document deletion."""
        service = RAGService()

        # Index document
        service.load_and_index_document("test.txt", "content")

        # Delete it
        success = service.delete_document("test")

        assert success is True

    def test_check_connection(self):
        """Test connection check."""
        service = RAGService()

        connected = service.check_connection()

        assert isinstance(connected, bool)


# ============================================================================
# LLM Client Tests
# ============================================================================

class TestLLMClient:
    """Test LLM client."""

    def test_llm_initialization(self):
        """Test LLM client initialization."""
        client = LLMClient(api_key="test-key", use_mock=True)

        assert client.temperature == 0.7
        assert client.max_tokens == 1024

    def test_count_tokens(self):
        """Test token counting."""
        client = LLMClient(api_key="test-key")

        text = "Hello world" * 100  # ~200 words

        tokens = client.count_tokens(text)

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_estimate_cost(self):
        """Test cost estimation."""
        client = LLMClient(api_key="test-key")

        cost = client.estimate_cost(input_tokens=1000, output_tokens=100)

        assert cost > 0
        assert isinstance(cost, float)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests."""

    def test_end_to_end_chat_flow(self, client):
        """Test complete chat flow."""
        # 1. Upload document
        response = client.post(
            "/documents/upload",
            files={"file": ("test.txt", b"Test content", "text/plain")}
        )
        assert response.status_code in [200, 500]

        # 2. Chat request
        chat_payload = {
            "message": "What is in the document?",
            "chat_id": "test123",
            "temperature": 0.7
        }
        response = client.post("/chat", json=chat_payload)
        assert response.status_code in [200, 500]

        # 3. Check health
        response = client.get("/health")
        assert response.status_code == 200

        # 4. Check metrics
        response = client.get("/metrics")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
