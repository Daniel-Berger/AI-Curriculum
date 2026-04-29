# Docker for ML: Containerization and Deployment

## Overview

Docker provides containerization for ML applications, ensuring consistency across development, testing, and production environments. This lesson covers essential Docker concepts for ML services.

## 1. What is Docker?

Docker is a containerization platform that packages applications with all dependencies into isolated, portable units called containers.

**Key Benefits:**
- **Reproducibility**: Same environment across machines
- **Isolation**: Avoid dependency conflicts
- **Portability**: Run anywhere Docker is installed
- **Scalability**: Easy to replicate containers

## 2. Docker Fundamentals

### Images vs Containers

**Docker Image**: A template containing:
- OS (usually minimal Linux distribution)
- Application code
- Runtime (Python, Node.js, etc.)
- Dependencies and libraries

**Docker Container**: A running instance of an image.

```
Image → Template
Container → Instance of that template
```

### Basic Dockerfile Structure

```dockerfile
# 1. Base image (parent image)
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy files
COPY requirements.txt .

# 4. Install dependencies
RUN pip install -r requirements.txt

# 5. Copy application code
COPY . .

# 6. Expose port (documentation)
EXPOSE 8000

# 7. Set default command
CMD ["python", "main.py"]
```

## 3. Multi-Stage Builds

Multi-stage builds reduce image size by using multiple FROM statements.

**Benefits:**
- Separate build dependencies from runtime dependencies
- Reduce final image size significantly
- Improve security by excluding build tools

**Example Structure:**

```
Stage 1 (Builder):
- Large base image
- Compile/build dependencies
- Complex build steps

Stage 2 (Runtime):
- Minimal base image
- Copy only necessary artifacts from Stage 1
- Exclude build tools and temporary files
```

**Use Cases:**
- Compiling C extensions for Python
- Building machine learning models
- Creating optimized wheels from source packages

## 4. .dockerignore File

Similar to .gitignore, specifies files to exclude from build context.

**Purpose:**
- Reduce build context size (faster builds)
- Avoid copying unnecessary files
- Improve security

**Common Patterns:**

```
.git
.gitignore
*.log
__pycache__
*.pyc
.pytest_cache
.venv
node_modules
dist
build
*.md
```

## 5. Docker Compose

Docker Compose orchestrates multiple containers as a single application.

**Use Cases:**
- ML API + PostgreSQL database
- FastAPI service + Redis cache + Prometheus monitoring
- Development environments mimicking production

**Key Concepts:**

- **Services**: Individual containers (api, db, cache)
- **Networks**: Connect services together
- **Volumes**: Persistent storage across container restarts
- **Environment Variables**: Configuration management

**Basic Structure:**

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 6. GPU Support in Docker

For ML workloads requiring GPU acceleration:

### NVIDIA Docker Runtime

**Requirements:**
- NVIDIA GPU
- NVIDIA drivers installed
- NVIDIA Container Toolkit

**Dockerfile:**

```dockerfile
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip && \
    pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

**Docker Compose with GPU:**

```yaml
services:
  ml_service:
    build: .
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ./models:/app/models
```

## 7. Best Practices

### Image Size Optimization

1. **Use minimal base images**
   - `python:3.11-slim` instead of `python:3.11`
   - `ubuntu:22.04` instead of `ubuntu` (full)

2. **Combine RUN commands**
   ```dockerfile
   # Bad: Creates multiple layers
   RUN apt-get update
   RUN apt-get install -y python3
   RUN apt-get install -y pip

   # Good: Single layer
   RUN apt-get update && \
       apt-get install -y python3 pip && \
       apt-get clean
   ```

3. **Use .dockerignore**
   - Exclude unnecessary files from build context

### Security Best Practices

1. **Run as non-root user**
   ```dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

2. **Scan images for vulnerabilities**
   ```bash
   docker scan myimage:latest
   ```

3. **Use specific version tags**
   - `FROM python:3.11.0-slim` ✓ (specific)
   - `FROM python:3.11-slim` ~ (minor version)
   - `FROM python:3.11-slim` ✗ (latest)

### Performance Best Practices

1. **Cache-efficient layer ordering**
   - Stable dependencies (requirements.txt) before code
   - Frequently changing code last

   ```dockerfile
   # Good order
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   ```

2. **Health checks**
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=10s \
     CMD curl -f http://localhost:8000/health || exit 1
   ```

3. **Resource limits in Compose**
   ```yaml
   services:
     api:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

## 8. Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Large base images | Slow builds/deployment | Use `-slim` variants |
| Not using .dockerignore | Large context, slow builds | Add .dockerignore |
| Installing unnecessary packages | Large images, security risk | Use minimal images + apt-get clean |
| Running as root | Security vulnerability | Create non-root user |
| No health checks | Dead containers stay running | Add HEALTHCHECK directive |
| Secrets in Dockerfile | Exposed credentials | Use Docker secrets or environment variables |

## 9. Development Workflow

```bash
# Build image
docker build -t ml-api:1.0 .

# Run container
docker run -p 8000:8000 ml-api:1.0

# Run with volume mount (for development)
docker run -p 8000:8000 -v $(pwd):/app ml-api:1.0

# Use Docker Compose
docker-compose up

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## 10. Production Considerations

1. **Image versioning**: Use semantic versioning (1.0.0, not 'latest')
2. **Container registries**: Push to Docker Hub, ECR, GCR, or private registry
3. **Environment-specific configs**: Use docker-compose.prod.yml
4. **Resource limits**: Define CPU and memory constraints
5. **Log management**: Use structured logging, aggregation tools
6. **Network policies**: Restrict container communication
7. **Secrets management**: Use Docker secrets or external secret manager

## Summary

Docker is essential for ML applications because it:
- Ensures reproducible environments
- Simplifies deployment and scaling
- Isolates dependencies and prevents conflicts
- Enables easy testing in production-like environments
- Supports GPU acceleration for ML workloads
- Integrates with orchestration platforms (Kubernetes)

Master Docker fundamentals before moving to Kubernetes or serverless platforms.
