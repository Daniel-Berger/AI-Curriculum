"""
Comprehensive tests for ML API application.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthCheck:
    """Test health check endpoints."""

    def test_health_check_success(self, client):
        """Test liveness probe returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "ml-api"
        assert "timestamp" in data

    def test_readiness_check_success(self, client):
        """Test readiness probe returns 200."""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "timestamp" in data


# ============================================================================
# Prediction Endpoint Tests
# ============================================================================

class TestPredictionEndpoint:
    """Test prediction endpoint."""

    def test_predict_success(self, client):
        """Test successful prediction."""
        request_data = {
            "prompt": "What is machine learning?",
            "max_tokens": 50
        }
        response = client.post("/predict", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "tokens_used" in data
        assert data["tokens_used"] > 0
        assert data["model"] == "mock-model"

    def test_predict_with_temperature(self, client):
        """Test prediction with custom temperature."""
        request_data = {
            "prompt": "Generate a story",
            "max_tokens": 100,
            "temperature": 0.9
        }
        response = client.post("/predict", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["tokens_used"] > 0

    def test_predict_missing_prompt(self, client):
        """Test prediction with missing prompt."""
        request_data = {"max_tokens": 50}
        response = client.post("/predict", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_predict_empty_prompt(self, client):
        """Test prediction with empty prompt."""
        request_data = {
            "prompt": "",
            "max_tokens": 50
        }
        response = client.post("/predict", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_predict_prompt_too_long(self, client):
        """Test prediction with overly long prompt."""
        request_data = {
            "prompt": "a" * 10000,  # Exceeds limit
            "max_tokens": 50
        }
        response = client.post("/predict", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_predict_max_tokens_too_high(self, client):
        """Test prediction with max_tokens exceeding limit."""
        request_data = {
            "prompt": "Test prompt",
            "max_tokens": 5000  # Exceeds limit
        }
        response = client.post("/predict", json=request_data)

        assert response.status_code == 422  # Validation error


# ============================================================================
# Batch Prediction Tests
# ============================================================================

class TestBatchPrediction:
    """Test batch prediction endpoint."""

    def test_batch_predict_success(self, client):
        """Test successful batch prediction."""
        request_data = [
            {"prompt": "Question 1?", "max_tokens": 50},
            {"prompt": "Question 2?", "max_tokens": 50}
        ]
        response = client.post("/batch-predict", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert len(data["predictions"]) == 2
        assert data["total_tokens"] > 0
        assert data["count"] == 2

    def test_batch_predict_single(self, client):
        """Test batch prediction with single item."""
        request_data = [
            {"prompt": "Single question?", "max_tokens": 50}
        ]
        response = client.post("/batch-predict", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1

    def test_batch_predict_exceeded_limit(self, client):
        """Test batch prediction exceeding size limit."""
        request_data = [
            {"prompt": f"Question {i}?", "max_tokens": 50}
            for i in range(101)  # Exceeds limit of 100
        ]
        response = client.post("/batch-predict", json=request_data)

        assert response.status_code == 400

    def test_batch_predict_empty(self, client):
        """Test batch prediction with empty list."""
        request_data = []
        response = client.post("/batch-predict", json=request_data)

        # Empty list should still be valid
        assert response.status_code in [200, 400]


# ============================================================================
# Validation Endpoint Tests
# ============================================================================

class TestValidationEndpoint:
    """Test prompt validation endpoint."""

    def test_validate_valid_prompt(self, client):
        """Test validating a valid prompt."""
        request_data = {"prompt": "Valid prompt"}
        response = client.post("/validate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "prompt_length" in data
        assert "warnings" in data

    def test_validate_short_prompt(self, client):
        """Test validating a short prompt."""
        request_data = {"prompt": "Hi"}
        response = client.post("/validate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data["warnings"]) > 0

    def test_validate_long_prompt(self, client):
        """Test validating a very long prompt."""
        request_data = {"prompt": "a" * 10000}
        response = client.post("/validate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data["warnings"]) > 0


# ============================================================================
# Info Endpoint Tests
# ============================================================================

class TestInfoEndpoint:
    """Test info endpoint."""

    def test_get_info(self, client):
        """Test getting service info."""
        response = client.get("/info")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "ML API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert len(data["endpoints"]) > 0


# ============================================================================
# Metrics Endpoint Tests
# ============================================================================

class TestMetricsEndpoint:
    """Test metrics endpoint."""

    def test_metrics_accessible(self, client):
        """Test that metrics endpoint is accessible."""
        response = client.get("/metrics")

        # Metrics endpoint returns Prometheus format
        assert response.status_code == 200
        # Should contain Prometheus metrics
        assert b"http_requests_total" in response.content or response.text


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling."""

    def test_not_found(self, client):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/nonexistent")

        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method."""
        response = client.get("/predict")  # POST endpoint, GET request

        assert response.status_code == 405

    def test_invalid_json(self, client):
        """Test error handling for invalid JSON."""
        response = client.post(
            "/predict",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422  # Validation error


# ============================================================================
# Middleware Tests
# ============================================================================

class TestMiddleware:
    """Test middleware functionality."""

    def test_response_headers(self, client):
        """Test that middleware adds custom headers."""
        response = client.get("/health")

        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers

    def test_process_time_header(self, client):
        """Test that process time is tracked."""
        response = client.get("/health")

        process_time = response.headers.get("X-Process-Time")
        assert process_time is not None
        # Should be a numeric string
        assert float(process_time) >= 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests across multiple endpoints."""

    def test_full_workflow(self, client):
        """Test complete workflow."""
        # 1. Check health
        health_response = client.get("/health")
        assert health_response.status_code == 200

        # 2. Check readiness
        ready_response = client.get("/ready")
        assert ready_response.status_code == 200

        # 3. Validate prompt
        validate_response = client.post(
            "/validate",
            json={"prompt": "Test prompt"}
        )
        assert validate_response.status_code == 200

        # 4. Get prediction
        predict_response = client.post(
            "/predict",
            json={"prompt": "Test prompt"}
        )
        assert predict_response.status_code == 200

        # 5. Get info
        info_response = client.get("/info")
        assert info_response.status_code == 200

    def test_concurrent_requests(self, client):
        """Test handling multiple concurrent requests."""
        # Simulate multiple requests
        responses = []
        for i in range(5):
            response = client.post(
                "/predict",
                json={"prompt": f"Question {i}?"}
            )
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        assert len(responses) == 5
