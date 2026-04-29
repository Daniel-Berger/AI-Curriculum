# CI/CD and Testing: Automated Quality Assurance

## Overview

Continuous Integration/Continuous Deployment (CI/CD) automates testing, building, and deployment processes. Combined with comprehensive testing strategies, CI/CD ensures code quality and reliability.

## 1. Testing Pyramid

The testing pyramid defines the ideal distribution of tests by type:

```
        /\
       /  \
      / E2E \       Few, slow, expensive
     /______\
    /        \
   / Integration\  Many, moderate speed/cost
  /____________\
 /              \
/   Unit Tests  \  Many, fast, cheap
/________________\
```

**Unit Tests**: 70-80%
- Test individual functions/methods
- Fast (milliseconds)
- No external dependencies
- Isolate code with mocks/stubs

**Integration Tests**: 10-20%
- Test component interactions
- May use real database, cache
- Moderate speed (seconds)
- Verify system parts work together

**E2E Tests**: 5-10%
- Test full user workflows
- Slow (minutes)
- Expensive to maintain
- Use real services

## 2. GitHub Actions Basics

GitHub Actions automates workflows triggered by repository events.

**Key Components:**

```yaml
name: CI Pipeline
on: [push, pull_request]  # Trigger events

jobs:
  test:
    runs-on: ubuntu-latest  # Runner environment
    steps:
      - uses: actions/checkout@v3  # Check out code
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Run tests
        run: pytest
```

**Common Triggers:**
- `push`: On code push
- `pull_request`: On PR creation/update
- `schedule`: On cron schedule
- `workflow_dispatch`: Manual trigger

## 3. Testing Strategy for ML/LLM Services

### Unit Tests
Focus on individual functions:
- Input validation
- Error handling
- Utility functions

```python
def test_validate_input():
    assert validate_input("valid") == True
    assert validate_input("") == False
```

### Integration Tests
Test component interactions:
- API endpoints with mocks
- Database interactions
- Cache behavior

```python
def test_api_with_database(client, db):
    response = client.post("/data", json={"value": 42})
    assert response.status_code == 201
    assert db.query(Data).count() == 1
```

### Model Validation Gates

Quality checks before deployment:

```yaml
- name: Validate Model
  run: |
    python -c "
    from ml_service import load_model
    model = load_model()
    assert model.evaluate() > 0.8, 'Model accuracy too low'
    "
```

## 4. Pre-commit Hooks

Local checks run before committing code. Catch issues early.

**Common Checks:**
- Code formatting (Black, isort)
- Linting (Flake8, pylint)
- Type checking (mypy)
- Security scanning (bandit)
- Secret detection

**.pre-commit-config.yaml:**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [--skip, B101]
```

## 5. Secrets Management

Never commit sensitive data. Use environment variables and secret managers.

**GitHub Secrets:**
```yaml
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: ./deploy.sh
```

**Best Practices:**
1. Use GitHub Secrets for sensitive data
2. Rotate secrets regularly
3. Use separate secrets per environment
4. Never log secrets
5. Use external secret managers (AWS Secrets Manager, HashiCorp Vault)

## 6. Model Validation Gates

Before deploying model updates:

```yaml
- name: Validate Model Performance
  run: |
    python validate_model.py \
      --min-accuracy 0.92 \
      --min-f1 0.85 \
      --max-latency 100ms

- name: Check Model Size
  run: |
    if [ $(stat -f%z "model.pth") -gt 500M ]; then
      echo "Model too large" && exit 1
    fi

- name: Regression Test
  run: pytest tests/regression/ -v
```

## 7. Artifact Management

Store build artifacts for deployment and debugging.

```yaml
- name: Build Docker Image
  run: docker build -t ml-api:${{ github.sha }} .

- name: Save Docker Image
  run: docker save ml-api:${{ github.sha }} > image.tar

- name: Upload Artifact
  uses: actions/upload-artifact@v3
  with:
    name: docker-image
    path: image.tar
    retention-days: 7

- name: Download Artifact
  uses: actions/download-artifact@v3
  with:
    name: docker-image
```

## 8. Deployment Strategies

### Blue-Green Deployment
Run two identical environments. Switch traffic between them.

```yaml
- name: Deploy Green
  run: kubectl apply -f deploy-green.yaml

- name: Run Smoke Tests
  run: pytest tests/smoke/ -v

- name: Switch Traffic
  if: success()
  run: kubectl patch service ml-api -p '{"spec":{"selector":{"version":"green"}}}'
```

### Canary Deployment
Gradually roll out to percentage of users.

```yaml
- name: Deploy Canary (10%)
  run: kubectl set image deployment/api api=ml-api:${{ github.sha }} --record

- name: Monitor Metrics
  run: python monitor_canary.py --threshold 0.01
```

### Rolling Deployment
Update instances gradually.

```yaml
deploy:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

## 9. Common CI/CD Patterns

### Test Coverage Requirements
```yaml
- name: Check Coverage
  run: |
    pytest --cov=src tests/
    coverage report --fail-under=80
```

### Security Scanning
```yaml
- name: Security Scan
  run: |
    pip install bandit safety
    bandit -r src/
    safety check --json
```

### Performance Testing
```yaml
- name: Performance Benchmarks
  run: pytest tests/performance/ --benchmark-only

- name: Compare with Baseline
  run: python compare_benchmarks.py
```

### Docker Image Scanning
```yaml
- name: Scan Docker Image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ml-api:latest
    format: 'sarif'
    output: 'trivy-results.sarif'
```

## 10. Environment Management

Different configurations for dev, staging, production.

**Structure:**
```
config/
├── dev.yaml
├── staging.yaml
└── production.yaml
```

**In CI/CD:**
```yaml
- name: Deploy to Staging
  env:
    ENVIRONMENT: staging
    CONFIG_FILE: config/staging.yaml
  run: python deploy.py

- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  env:
    ENVIRONMENT: production
    CONFIG_FILE: config/production.yaml
  run: python deploy.py
```

## 11. Best Practices

1. **Test Early and Often**
   - Run tests on every push
   - Fail fast on critical errors
   - Provide quick feedback

2. **Keep Tests Independent**
   - No shared state between tests
   - Tests can run in any order
   - Parallel test execution

3. **Monitor CI/CD Health**
   - Track build times
   - Monitor flaky tests
   - Alert on failures

4. **Document Deployment Process**
   - Clear deployment procedures
   - Rollback strategies
   - Disaster recovery plans

5. **Automate Everything**
   - Infrastructure as code
   - Configuration management
   - Automated deployments

## Summary

Effective CI/CD combined with comprehensive testing ensures:
- Code quality through automated checks
- Fast feedback loops for developers
- Reduced deployment risk
- Reliable, repeatable deployments
- Easy rollback capabilities

Master CI/CD practices to build confidence in your ML services and ensure safe, frequent deployments.
