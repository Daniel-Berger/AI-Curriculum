# Phase 6: Production Engineering - Quiz

25 questions testing knowledge of production ML systems.

---

## EASY (8 questions)

### 1. FastAPI Basics
What is the main advantage of FastAPI over Flask for building APIs?
- A) It's more popular
- B) It provides automatic API documentation and async support
- C) It's easier to learn
- D) It has a larger community

**Answer: B** - FastAPI automatically generates OpenAPI/Swagger docs and has built-in async/await support.

### 2. Docker Fundamentals
What is the primary purpose of a Dockerfile?
- A) Configure databases
- B) Define a Docker image's composition and how to build it
- C) Store credentials securely
- D) Monitor container performance

**Answer: B** - A Dockerfile contains instructions for building a Docker image.

### 3. Docker Compose
What does the `depends_on` directive do in docker-compose.yml?
- A) Limits CPU usage
- B) Controls service startup order and dependencies
- C) Sets environment variables
- D) Configures networking

**Answer: B** - `depends_on` specifies which services must start before others.

### 4. Prometheus Metrics
Which metric type is used for monotonically increasing values like request count?
- A) Gauge
- B) Histogram
- C) Counter
- D) Summary

**Answer: C** - Counter is for values that only increase (like total requests).

### 5. Health Checks
What is the difference between liveness and readiness probes?
- A) They are the same thing
- B) Liveness checks if service exists; readiness checks if it can handle requests
- C) Liveness is for containers; readiness is for databases
- D) There is no standard difference

**Answer: B** - Liveness = "is service running?"; Readiness = "can it handle traffic?".

### 6. GitHub Actions
What trigger event starts a GitHub Actions workflow on push?
- A) `on: push`
- B) `on: commit`
- C) `on: deploy`
- D) `on: pull_request`

**Answer: A** - `on: push` triggers on code push events.

### 7. Testing Pyramid
What is the recommended distribution of tests by type?
- A) 50% unit, 30% integration, 20% E2E
- B) 70% unit, 20% integration, 10% E2E
- C) 33% each
- D) 100% E2E only

**Answer: B** - Testing pyramid recommends mostly unit tests, fewer integration, fewest E2E.

### 8. Cloud Deployment
Which AWS service is recommended for real-time model inference?
- A) AWS Lambda
- B) SageMaker Endpoints
- C) SageMaker Batch Transform
- D) EC2 instances only

**Answer: B** - SageMaker Endpoints provide real-time inference with auto-scaling.

---

## MEDIUM (10 questions)

### 9. Async/Await in FastAPI
Why are async endpoints important in web frameworks?
- A) They are faster than sync
- B) They allow handling multiple requests concurrently without blocking
- C) They use less memory
- D) They are required for all APIs

**Answer: B** - Async/await enables non-blocking I/O and concurrent request handling.

### 10. Middleware
What is the correct order when a request goes through multiple middleware layers?
- A) Request → Middleware1 → Middleware2 → Handler → Middleware2 → Middleware1 → Response
- B) Request → Handler → Middleware1 → Middleware2 → Response
- C) All middleware process in parallel
- D) Order doesn't matter

**Answer: A** - Middleware wraps the handler like nested functions (LIFO for response).

### 11. Multi-Stage Docker Builds
What is the main benefit of multi-stage builds?
- A) Faster builds
- B) Reduces final image size by excluding build dependencies
- C) Enables parallel processing
- D) Improves security

**Answer: B** - Multi-stage builds separate build dependencies from runtime, reducing final image size.

### 12. Model Evaluation
Which metric is used to compare model-generated text with a reference translation?
- A) Accuracy
- B) BLEU Score
- C) Latency
- D) Throughput

**Answer: B** - BLEU compares generated and reference text using n-gram overlap.

### 13. Red-Teaming
What is the purpose of red-teaming an LLM?
- A) Improve model accuracy
- B) Systematically find vulnerabilities and failure modes
- C) Train the model faster
- D) Reduce latency

**Answer: B** - Red-teaming is adversarial testing to find jailbreaks, hallucinations, bias, etc.

### 14. A/B Testing
In A/B testing LLMs, how should user assignment be determined?
- A) Randomly on each request
- B) Deterministically based on user ID hash
- C) Alternating requests
- D) Based on time of day

**Answer: B** - Deterministic assignment (e.g., user_id hash) ensures consistency for each user.

### 15. Cost Optimization
Approximately how much cheaper is SageMaker Batch Transform compared to a real-time endpoint?
- A) 10% cheaper
- B) 50% cheaper
- C) 100x cheaper
- D) Same cost

**Answer: C** - Batch jobs can be 100x cheaper since they run only when needed.

### 16. CI/CD Pipeline Stages
What is the typical order of CI/CD stages?
- A) Deploy → Test → Build
- B) Test → Build → Deploy
- C) Build → Deploy → Test
- D) Deploy → Build → Test

**Answer: B** - Standard CI/CD: Test code → Build artifacts → Deploy to production.

### 17. Monitoring
What should you monitor for LLM-powered services that's different from traditional APIs?
- A) Token usage and cost
- B) Only request latency
- C) Only error rates
- D) Nothing different

**Answer: A** - LLM services need tracking of token consumption, API costs, and model accuracy.

### 18. Security in Docker
What is the best practice for running containers?
- A) Always run as root
- B) Create and run as non-root user
- C) It doesn't matter
- D) Use elevated privileges

**Answer: B** - Running as non-root user limits damage from container compromise.

---

## HARD (7 questions)

### 19. AsyncIO and Concurrency
What is the difference between `asyncio.gather()` and `asyncio.create_task()`?
- A) They are identical
- B) `gather()` waits for all tasks; `create_task()` returns immediately
- C) `create_task()` is faster
- D) `gather()` handles errors differently

**Answer: B** - `gather()` blocks until all complete; `create_task()` schedules without waiting.

### 20. Kubernetes Probes in Production
What happens if readiness probe fails but liveness probe succeeds?
- A) Container is restarted
- B) Container stays running but receives no traffic
- C) Service is deleted
- D) No action taken

**Answer: B** - Failed readiness probe removes from load balancer but container runs; failed liveness probe restarts.

### 21. Distributed Tracing
How does distributed tracing help debug latency in a microservices architecture?
- A) It doesn't; you need logs instead
- B) It shows each service's contribution to total latency across requests
- C) It only measures total time
- D) It's only for database queries

**Answer: B** - Traces show request flow through services with timing for each span.

### 22. Bias Testing at Scale
When testing LLMs for demographic bias across multiple attributes, what statistical measure ensures results are meaningful?
- A) Only use user ratings
- B) Test only majority populations
- C) Use consistent methodology and multiple raters with calculated inter-rater agreement
- D) Run tests only once

**Answer: C** - Use consistent testing methodology with multiple raters and metrics like Fleiss' Kappa for agreement.

### 23. Load Testing and Scaling
If your API has 100 users and takes 500ms per request, and you need to handle 1000 users with <100ms latency, what's the relationship between resources and concurrency?
- A) You need 10x resources
- B) You need more than 10x due to concurrency overhead
- C) Latency is independent of users
- D) You only need faster hardware

**Answer: B** - With 10x users and 5x latency reduction, you need >10x resources accounting for concurrency overhead.

### 24. Model Serving Optimization
What technique reduces model size by 4x-10x without retraining?
- A) Batch processing
- B) Quantization (converting float32 to int8)
- C) Adding more parameters
- D) Fine-tuning on more data

**Answer: B** - Quantization reduces precision (float32→int8) achieving 4-10x size reduction with minimal accuracy loss.

### 25. Production Observability
In a production LLM API, which metric combination would best indicate a problem?
- A) Only request count increasing
- B) Request latency increasing + token cost increasing + accuracy decreasing
- C) Only memory usage
- D) CPU at 50%

**Answer: B** - Multiple signals together (latency ↑, cost ↑, accuracy ↓) indicate model degradation/drift, not just noise.

---

## Answer Summary

| # | Answer | Difficulty |
|---|--------|-----------|
| 1 | B | Easy |
| 2 | B | Easy |
| 3 | B | Easy |
| 4 | C | Easy |
| 5 | B | Easy |
| 6 | A | Easy |
| 7 | B | Easy |
| 8 | B | Easy |
| 9 | B | Medium |
| 10 | A | Medium |
| 11 | B | Medium |
| 12 | B | Medium |
| 13 | B | Medium |
| 14 | B | Medium |
| 15 | C | Medium |
| 16 | B | Medium |
| 17 | A | Medium |
| 18 | B | Medium |
| 19 | B | Hard |
| 20 | B | Hard |
| 21 | B | Hard |
| 22 | C | Hard |
| 23 | B | Hard |
| 24 | B | Hard |
| 25 | B | Hard |

**Scoring Guide:**
- 20-25 correct: Excellent understanding of production engineering
- 15-19 correct: Good grasp of core concepts
- 10-14 correct: Solid foundation, review medium/hard concepts
- Below 10: Review fundamentals and core lessons
