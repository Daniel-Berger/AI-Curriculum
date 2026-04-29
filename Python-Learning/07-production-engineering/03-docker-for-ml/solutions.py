"""
Docker for ML - Solutions

Complete implementations for all 10 exercises.
"""


def solution_1_python_app_dockerfile() -> str:
    """
    Solution 1: Basic Dockerfile for Python FastAPI application.
    """
    return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""


def solution_2_ml_inference_dockerfile() -> str:
    """
    Solution 2: Dockerfile for ML model inference service.
    """
    return """FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \\
    apt-get install -y build-essential && \\
    apt-get clean && \\
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models/ ./models/
COPY . .

RUN useradd -m mluser && chown -R mluser:mluser /app
USER mluser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

CMD ["python", "inference_server.py"]
"""


def solution_3_multi_stage_build() -> str:
    """
    Solution 3: Multi-stage Dockerfile for reduced image size.
    """
    return """FROM python:3.11-slim as builder

WORKDIR /tmp
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""


def solution_4_gpu_multi_stage_build() -> str:
    """
    Solution 4: Multi-stage Dockerfile for GPU-accelerated ML service.
    """
    return """FROM nvidia/cuda:12.2.0-devel-ubuntu22.04 as builder

RUN apt-get update && apt-get install -y python3.11 python3-pip && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3.11 && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 8000

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

CMD ["python3", "model_server.py"]
"""


def solution_5_dockerignore_file() -> str:
    """
    Solution 5: .dockerignore file for ML project.
    """
    return """.git
.gitignore
.github
.gitlab-ci.yml

__pycache__
*.py[cod]
*$py.class
*.so
.Python
.pytest_cache
.coverage
htmlcov/

.venv
venv/
ENV/
env/

*.log
*.tmp
*.bak
*~

tests/
docs/
examples/

.DS_Store
Thumbs.db

.vscode/
.idea/

# Large files
*.pth
*.pkl
*.h5
*.onnx

README.md
LICENSE
"""


def solution_6_docker_compose_basic() -> str:
    """
    Solution 6: Docker Compose for FastAPI + PostgreSQL.
    """
    return """version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mldb
      - DEBUG=true
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mldb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
"""


def solution_7_docker_compose_ml_stack() -> str:
    """
    Solution 7: Docker Compose for ML monitoring stack.
    """
    return """version: '3.8'

services:
  api:
    build: ./app
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    networks:
      - ml-network
    depends_on:
      - redis
      - prometheus

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ml-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    networks:
      - ml-network

volumes:
  redis_data:
  prometheus_data:

networks:
  ml-network:
    driver: bridge
"""


def solution_8_docker_compose_gpu() -> str:
    """
    Solution 8: Docker Compose with GPU support.
    """
    return """version: '3.8'

services:
  ml-service:
    build: ./ml-service
    ports:
      - "8000:8000"
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./models:/app/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          cpus: '4'
          memory: 8G
    networks:
      - ml-network

networks:
  ml-network:
    driver: bridge
"""


def solution_9_optimized_dockerfile() -> str:
    """
    Solution 9: Optimized Dockerfile following best practices.
    """
    return """FROM python:3.11-slim

LABEL maintainer="ml-team@company.com"
LABEL version="1.0.0"
LABEL description="Production ML API Service"

WORKDIR /app

RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
    gcc && \\
    apt-get clean && \\
    rm -rf /var/lib/apt/lists/* && \\
    useradd -m -u 1000 appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""


def solution_10_docker_compose_production() -> str:
    """
    Solution 10: Production-ready docker-compose.yml.
    """
    return """version: '3.8'

services:
  api:
    image: myregistry/ml-api:1.0.0
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - frontend
      - backend
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - db_data:/var/lib/postgresql/data
      - db_backup:/backup
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  prometheus:
    image: prom/prometheus:latest
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - backend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  db_data:
  db_backup:
  prometheus_data:

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
"""


if __name__ == "__main__":
    print("Dockerfile Solutions:")
    print("=" * 60)
    print("\nSolution 1: Python App Dockerfile")
    print(solution_1_python_app_dockerfile()[:200] + "...")
    print("\nSolution 6: Docker Compose Basic")
    print(solution_6_docker_compose_basic()[:200] + "...")
    print("\nSolution 10: Production Compose")
    print(solution_10_docker_compose_production()[:200] + "...")
