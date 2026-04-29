# Production ML API Service

Complete production-ready LLM API with FastAPI, Docker, monitoring, and CI/CD.

## Project Structure

```
project/
├── app/
│   ├── main.py           # FastAPI application
│   ├── models.py         # Pydantic data models
│   ├── services.py       # Business logic
│   └── middleware.py     # Custom middleware
├── tests/
│   └── test_app.py       # Application tests
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container setup
├── ci_workflow.yml       # GitHub Actions workflow
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Features

- **FastAPI**: Modern async web framework
- **Async/Await**: Non-blocking I/O
- **Pydantic**: Data validation and serialization
- **Middleware**: Request/response processing
- **Docker**: Containerized deployment
- **Docker Compose**: Local development environment
- **Monitoring**: Prometheus metrics and structured logging
- **Testing**: Comprehensive test coverage
- **CI/CD**: GitHub Actions workflows

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git

### Installation

1. Clone and navigate:
```bash
cd project
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run locally:
```bash
uvicorn app.main:app --reload --port 8000
```

5. Or use Docker:
```bash
docker-compose up
```

### API Endpoints

**Health Check**
```bash
curl http://localhost:8000/health
```

**Predict**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is machine learning?"}'
```

**Metrics**
```bash
curl http://localhost:8000/metrics
```

## Configuration

Environment variables in `.env`:
```
MODEL_NAME=gpt-4
API_KEY=your-api-key
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## Testing

Run tests:
```bash
pytest tests/ -v --cov=app
```

## Deployment

### Docker

Build and run:
```bash
docker build -t ml-api:latest .
docker run -p 8000:8000 ml-api:latest
```

### Docker Compose (Multi-container)

```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Cloud Deployment

See `07-cloud-deployment/lesson.md` for AWS SageMaker, GCP Vertex AI, and serverless options.

## Monitoring

### Prometheus Metrics

Access at `http://localhost:9090`

Key metrics:
- `http_requests_total`: Total API requests
- `http_request_duration_seconds`: Request latency
- `llm_tokens_total`: LLM tokens consumed
- `model_accuracy_score`: Current model accuracy

### Structured Logs

Logs are output in JSON format for easy parsing:
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "info",
  "service": "ml-api",
  "endpoint": "/predict",
  "duration_ms": 125,
  "status": 200
}
```

## CI/CD Pipeline

GitHub Actions workflow in `ci_workflow.yml`:

1. **Test**: Run unit and integration tests
2. **Build**: Create Docker image
3. **Scan**: Security scanning with Trivy
4. **Deploy**: Push to registry and deploy to staging
5. **Validate**: Run smoke tests
6. **Promote**: Deploy to production

## Performance Optimization

- **Async endpoints**: Non-blocking I/O for concurrency
- **Caching**: Redis for frequent predictions
- **Batch processing**: Process multiple requests together
- **Model quantization**: Reduced model size
- **Request validation**: Fast failure on invalid input

## Security

- **CORS**: Configured for frontend integration
- **Rate limiting**: Prevent abuse
- **Input validation**: Pydantic schemas
- **Error handling**: Safe error messages
- **Logging**: Audit trail of API usage

## Troubleshooting

**Port already in use**:
```bash
lsof -i :8000
kill -9 <PID>
```

**Docker network issues**:
```bash
docker network prune
docker-compose down -v
docker-compose up
```

**Model loading errors**:
- Check model path in environment
- Verify model format compatibility
- Check available disk space

## Contributing

1. Create feature branch
2. Make changes with tests
3. Run `pytest` and `black`
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions:
1. Check this README
2. Review logs: `docker-compose logs app`
3. Check tests: `pytest tests/ -v`
