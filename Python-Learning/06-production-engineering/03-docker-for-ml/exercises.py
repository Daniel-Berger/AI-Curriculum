"""
Docker for ML - Exercises

10 exercises covering:
- Basic Dockerfile creation
- Multi-stage builds
- .dockerignore configuration
- Docker Compose orchestration
- GPU support
- Best practices
"""

from typing import Dict, List


# ============================================================================
# Exercise 1-2: Basic Dockerfile
# ============================================================================

def exercise_1_python_app_dockerfile() -> str:
    """
    Exercise 1: Create a Dockerfile for a Python FastAPI application.

    Requirements:
    - Base image: python:3.11-slim
    - Working directory: /app
    - Copy requirements.txt and install dependencies
    - Copy application code
    - Expose port 8000
    - CMD to run with uvicorn

    Returns:
        Complete Dockerfile content as string
    """
    pass


def exercise_2_ml_inference_dockerfile() -> str:
    """
    Exercise 2: Create a Dockerfile for ML model inference service.

    Requirements:
    - Base image: python:3.11-slim
    - Install system dependencies: build-essential (cleanup after)
    - Copy requirements.txt and install pip packages
    - Copy pre-trained model file from ./models directory
    - Create non-root user 'mluser'
    - Expose port 5000
    - Health check endpoint at /health

    Returns:
        Complete Dockerfile content as string
    """
    pass


# ============================================================================
# Exercise 3-4: Multi-Stage Builds
# ============================================================================

def exercise_3_multi_stage_build() -> str:
    """
    Exercise 3: Create multi-stage Dockerfile for reduced image size.

    Requirements:
    Stage 1 (builder):
    - Use python:3.11-slim
    - Install dependencies with pip install --user
    - Create wheels for caching

    Stage 2 (runtime):
    - Use python:3.11-slim
    - Copy only necessary artifacts from builder
    - Copy application code
    - Run as non-root user
    - Expose port 8000

    Returns:
        Complete multi-stage Dockerfile content as string
    """
    pass


def exercise_4_gpu_multi_stage_build() -> str:
    """
    Exercise 4: Create multi-stage Dockerfile for GPU-accelerated ML service.

    Requirements:
    Stage 1 (build):
    - Use nvidia/cuda:12.2.0-devel-ubuntu22.04
    - Compile C extensions
    - Install PyTorch with CUDA support

    Stage 2 (runtime):
    - Use nvidia/cuda:12.2.0-runtime-ubuntu22.04
    - Copy compiled wheels from builder
    - Install only runtime dependencies
    - Expose port 8000 for model serving

    Returns:
        Complete GPU multi-stage Dockerfile content as string
    """
    pass


# ============================================================================
# Exercise 5: .dockerignore
# ============================================================================

def exercise_5_dockerignore_file() -> str:
    """
    Exercise 5: Create .dockerignore file for ML project.

    Requirements:
    - Exclude git files and directories
    - Exclude Python cache (__pycache__, *.pyc)
    - Exclude test directories and coverage reports
    - Exclude virtual environments
    - Exclude documentation
    - Exclude temporary files (*.log, *.tmp)
    - Exclude large model files (if stored locally for testing)
    - Exclude development tools

    Returns:
        Complete .dockerignore content as string
    """
    pass


# ============================================================================
# Exercise 6-7: Docker Compose
# ============================================================================

def exercise_6_docker_compose_basic() -> str:
    """
    Exercise 6: Create docker-compose.yml for FastAPI + PostgreSQL.

    Requirements:
    - Version 3.8
    - API service:
      * Build from current directory
      * Port 8000:8000
      * Depends on db
      * Environment: DATABASE_URL, DEBUG=true
    - PostgreSQL service:
      * Image: postgres:15-alpine
      * Port 5432:5432
      * Environment: POSTGRES_PASSWORD, POSTGRES_DB
      * Volume for data persistence
    - Network to connect services

    Returns:
        Complete docker-compose.yml content as string
    """
    pass


def exercise_7_docker_compose_ml_stack() -> str:
    """
    Exercise 7: Create docker-compose.yml for ML monitoring stack.

    Requirements:
    - ML API service:
      * Build from ./app
      * Port 8000:8000
      * Volume mount for models
      * Resource limits: 2 CPUs, 2GB RAM
    - Redis cache:
      * Image: redis:7-alpine
      * Port 6379:6379
      * Volume for persistence
    - Prometheus monitoring:
      * Image: prom/prometheus:latest
      * Port 9090:9090
      * Volume for config
    - Networks and depends_on for proper startup order

    Returns:
        Complete docker-compose.yml content as string
    """
    pass


# ============================================================================
# Exercise 8: GPU Support Configuration
# ============================================================================

def exercise_8_docker_compose_gpu() -> str:
    """
    Exercise 8: Create docker-compose.yml with GPU support.

    Requirements:
    - GPU service:
      * Build from ./ml-service
      * Runtime: nvidia
      * Environment: NVIDIA_VISIBLE_DEVICES=all
      * Volume mount for models: ./models:/app/models
      * Port 8000:8000
    - Include resource deployment limits
    - Include environment variables for GPU settings

    Returns:
        Complete docker-compose.yml content as string
    """
    pass


# ============================================================================
# Exercise 9-10: Best Practices and Configuration
# ============================================================================

def exercise_9_optimized_dockerfile() -> str:
    """
    Exercise 9: Create optimized Dockerfile following all best practices.

    Requirements:
    - Use minimal base image (python:3.11-slim)
    - Combine RUN commands to reduce layers
    - Install and cleanup in same RUN command
    - Copy requirements before code (cache efficiency)
    - Create non-root user
    - Add HEALTHCHECK
    - Use specific versions in requirements.txt (implied by comment)
    - Add LABEL for metadata

    Returns:
        Complete optimized Dockerfile content as string
    """
    pass


def exercise_10_docker_compose_production() -> str:
    """
    Exercise 10: Create production-ready docker-compose.yml.

    Requirements:
    - API service with:
      * Image: myregistry/ml-api:1.0.0 (not build)
      * Restart policy: always
      * Resource limits (CPU, memory)
      * Health check
      * Logging configuration
      * Environment file reference
    - Database with:
      * Persistent volume
      * Backup volume
      * Resource limits
    - Logging and monitoring services
    - Networks isolated by tier (frontend, backend, database)

    Returns:
        Complete production docker-compose.yml content as string
    """
    pass
