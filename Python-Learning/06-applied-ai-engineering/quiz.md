# Phase 6: Applied AI Engineering - Quiz

**30 questions** covering all 10 modules. Take under timed conditions (60 minutes).

**Scoring:**
- 27-30: Excellent - ready for SE interviews
- 22-26: Good - review weak areas
- 17-21: Solid foundation - more practice needed
- Below 17: Review the modules thoroughly

---

## Questions

### Module 01: Customer Integration Patterns

**1. (Easy)** A customer reports receiving `401 Unauthorized` errors intermittently. Their API key starts with `sk-ant-`. What is the most likely issue?

a) The key is expired
b) They're sending the key to the wrong provider (e.g., sending an Anthropic key to OpenAI)
c) Rate limiting
d) Network timeout

**2. (Medium)** When implementing a circuit breaker for LLM API calls, what are the three states and their transitions?

a) Open → Closed → Half-Open
b) Closed → Open → Half-Open → Closed
c) Active → Inactive → Recovery
d) Healthy → Degraded → Failed

**3. (Hard)** A customer's middleware pipeline processes requests in this order: Logging → Validation → PII Detection → Cost Tracking. They report that PII is appearing in their logs. What is the root cause and fix?

---

### Module 02: Cost & Performance Optimization

**4. (Easy)** For Claude 3.5 Sonnet, if input tokens cost $3/MTok and output tokens cost $15/MTok, what is the cost of a request with 1,000 input tokens and 500 output tokens?

a) $0.0105
b) $0.003
c) $0.0075
d) $0.0045

**5. (Medium)** A customer processes 10,000 customer support tickets daily. Each ticket averages 200 input tokens and 150 output tokens. They want to reduce costs by 60% without significant quality loss. Rank these strategies by likely impact:

a) Switch from Opus to Haiku for all requests
b) Implement prompt caching for the system prompt
c) Batch requests and process during off-peak hours
d) Route simple tickets to Haiku and complex ones to Sonnet

**6. (Hard)** Explain the tradeoff between prompt caching hit rate and prompt flexibility. How would you design a system that maximizes cache hits while still allowing per-customer customization?

---

### Module 03: Evaluation & Quality Assurance

**7. (Easy)** What is the primary advantage of LLM-as-judge evaluation over traditional metrics like BLEU or ROUGE?

a) It's faster to compute
b) It can evaluate semantic correctness and nuance, not just surface-level similarity
c) It's deterministic
d) It doesn't require reference answers

**8. (Medium)** When using an LLM as a judge, what is "position bias" and how do you mitigate it?

a) The judge prefers longer responses; mitigate by normalizing length
b) The judge prefers the response presented first/last in the prompt; mitigate by randomizing order and averaging
c) The judge prefers responses from the same provider; mitigate by anonymizing
d) The judge's scores drift over time; mitigate by re-calibrating

**9. (Hard)** Design an evaluation pipeline for a legal document summarization system. What metrics would you use, how would you build a golden dataset, and how would you handle the fact that multiple valid summaries exist for the same document?

---

### Module 04: Conversation & Application Design

**10. (Easy)** What is the purpose of a sliding window in multi-turn conversation management?

a) To improve response quality by providing more context
b) To keep conversation history within the model's context window by removing oldest messages
c) To encrypt conversation data
d) To rate limit user messages

**11. (Medium)** A customer reports that their chatbot "forgets" important information from early in the conversation. They're using a simple sliding window of the last 10 messages. What alternative strategy would you recommend?

a) Increase the window to 50 messages
b) Use a hybrid approach: summarize old messages + keep recent ones + pin key facts
c) Switch to a model with a larger context window
d) Store all messages in a database and retrieve them as needed

**12. (Hard)** Design a human-in-the-loop system for a financial services chatbot that must escalate when: (1) the user asks about specific investment advice, (2) the model's confidence is below a threshold, or (3) the user explicitly requests a human. How would you implement the confidence threshold without access to model logprobs?

---

### Module 05: Enterprise Security & Compliance

**13. (Easy)** Which of the following is NOT a common PII pattern that should be redacted before sending text to an LLM?

a) Social Security Numbers
b) Email addresses
c) Company names
d) Credit card numbers

**14. (Medium)** A healthcare customer asks: "Can we use your AI API and remain HIPAA compliant?" What are the three most important things you need to verify?

a) BAA (Business Associate Agreement), data encryption, audit logging
b) Model accuracy, response time, uptime SLA
c) Prompt caching, cost optimization, batch processing
d) Multi-provider support, failover, geographic routing

**15. (Hard)** A customer discovers that a prompt injection attack bypasses their content moderation by encoding malicious instructions in base64 within a user message. Design a defense-in-depth strategy that addresses this and similar encoding attacks.

---

### Module 06: Rapid Prototyping & Demos

**16. (Easy)** Which Python framework is better suited for building a quick interactive AI chat demo for a customer meeting?

a) Django
b) Flask
c) Streamlit
d) FastAPI

**17. (Medium)** You're preparing a live demo for an enterprise customer. The demo calls a live LLM API. What should you prepare in case the API is down or slow during the demo?

a) Cancel the demo and reschedule
b) Use a different provider as backup
c) Have pre-cached responses for key demo scenarios as a fallback
d) Both b and c

**18. (Hard)** A customer wants a POC built in 2 weeks that demonstrates: multi-provider support, PII redaction, evaluation metrics, and a chat interface. Describe how you would scope this POC, what you would include vs. defer, and how you would set success criteria with the customer.

---

### Module 07: Technical Communication

**19. (Easy)** When writing an API code sample for documentation, what is the most important quality?

a) It should demonstrate every feature of the API
b) It should be copy-paste runnable with minimal modification
c) It should use advanced language features to show expertise
d) It should be as short as possible

**20. (Medium)** A customer's VP of Engineering asks: "Why should we switch from OpenAI to Anthropic?" A customer's ML Engineer asks the same question. How should your answer differ?

a) Give the same technical answer to both
b) VP: focus on reliability, security, cost, and support; ML Engineer: focus on model quality, API features, and migration effort
c) VP: show benchmark results; ML Engineer: discuss pricing
d) Decline to answer and refer them to sales

---

### Module 08: Multi-Provider & Multi-Modal AI

**21. (Easy)** What is the primary benefit of using LiteLLM for multi-provider support?

a) It makes LLM calls faster
b) It provides a unified API interface across 100+ LLM providers
c) It reduces token costs
d) It improves response quality

**22. (Medium)** A customer needs to route requests to different providers based on data residency requirements (EU data stays in EU). Which routing strategy is most appropriate?

a) Cost-based routing
b) Latency-based routing
c) Geographic/compliance-based routing
d) Quality-based routing

**23. (Hard)** Design a model routing system that optimizes for cost while maintaining a quality SLA (95% of responses must score above 0.8 on your eval harness). How would you implement this, and how would you handle the cold-start problem when adding a new model?

---

### Module 09: Observability for LLM Apps

**24. (Easy)** Which metric is most important for detecting a sudden increase in LLM API costs?

a) p99 latency
b) Requests per second
c) Cost per request (rolling average)
d) Error rate

**25. (Medium)** A customer reports that their AI application's response quality has degraded over the past week, but no code changes were deployed. What observability data would you examine first?

a) Token usage trends, model version changes, prompt template diffs, quality score trends
b) CPU utilization, memory usage, disk I/O
c) User count, session duration, page views
d) Git commit history, deployment logs

**26. (Hard)** Design an observability pipeline for a multi-step RAG application (retrieve → rerank → generate → validate). What spans/traces would you create, what custom attributes would you log at each step, and how would you correlate a quality issue in the final output back to a specific step?

---

### Module 10: Customer Scenario Simulation

**27. (Easy)** When triaging a new customer request, which factor should have the HIGHEST priority in determining response urgency?

a) Customer company size
b) Whether it's a production outage vs. development question
c) How recently they signed the contract
d) The technical complexity of the issue

**28. (Medium)** A customer is evaluating your AI platform against a competitor. They want a POC completed in 3 weeks. After week 1, you discover their data has significant quality issues that will affect results. What do you do?

a) Continue the POC and explain results may be lower quality
b) Immediately flag the data quality issue, provide specific examples, suggest a revised timeline that includes data cleaning, and get stakeholder alignment
c) Clean the data yourself without telling the customer
d) Recommend they go with the competitor since their data isn't ready

**29. (Hard)** Walk through a complete incident response scenario: A customer's production AI system starts returning empty responses at 3am. You're the on-call SE. Describe your first 60 minutes — what do you check, who do you communicate with, and how do you balance speed of resolution with thoroughness of investigation?

---

### Cross-Module

**30. (Hard)** A Fortune 500 financial services company wants to deploy an AI-powered document analysis system. They have strict compliance requirements (SOC 2, data residency), need multi-provider redundancy, require full audit logging, and want to see a working POC in 2 weeks. Using concepts from across all 10 modules, outline your approach from first customer call to POC delivery.

---

## Answer Key

### Easy Questions

**1.** b) They're sending the key to the wrong provider. The `sk-ant-` prefix is Anthropic-specific; if sent to OpenAI's endpoint, it would fail.

**4.** a) $0.0105. Calculation: (1000 × $3/1M) + (500 × $15/1M) = $0.003 + $0.0075 = $0.0105

**7.** b) LLM-as-judge can evaluate semantic correctness and nuance that surface-level metrics miss.

**10.** b) Sliding windows keep conversation history manageable by removing oldest messages to stay within context limits.

**13.** c) Company names are generally not considered PII. SSNs, emails, and credit card numbers are classic PII.

**16.** c) Streamlit is purpose-built for rapid interactive data/AI app prototyping.

**19.** b) Code samples should be copy-paste runnable. Users want to get started quickly, not read a textbook.

**21.** b) LiteLLM provides a unified `completion()` interface across 100+ providers with the same calling convention.

**24.** c) Cost per request (rolling average) directly measures spending and will spike when costs increase.

**27.** b) Production outages always take priority over development questions, regardless of customer size or contract.

### Medium Questions

**2.** b) Closed (normal) → Open (failures exceed threshold, reject all) → Half-Open (allow test request) → back to Closed if test succeeds.

**5.** Best ranking: d (model routing by complexity) > b (prompt caching) > a (downgrade all to Haiku) > c (batch timing doesn't change cost). Model routing preserves quality for complex tickets while saving on simple ones.

**8.** b) Position bias means the judge prefers responses shown in certain positions. Mitigate by evaluating in both orders and averaging scores.

**11.** b) A hybrid approach (summarize + recent + pinned facts) preserves important context while staying within token limits.

**14.** a) BAA, encryption, and audit logging are the three pillars of HIPAA compliance for AI APIs.

**17.** d) Both a backup provider and pre-cached fallback responses ensure the demo succeeds regardless of API issues.

**20.** b) Tailor the message: business value for VP, technical depth for ML Engineer.

**22.** c) Geographic/compliance-based routing ensures data stays within required jurisdictions.

**25.** a) Quality degradation without code changes suggests model version changes, prompt drift, or data distribution shift — all visible in LLM-specific observability.

**28.** b) Transparency and proactive communication build trust. Flagging issues early with a revised plan is better than delivering poor results.

### Hard Questions (Sample Answers)

**3.** The Logging middleware runs before PII Detection, so it logs the raw request including PII. Fix: Move PII Detection before Logging, or implement PII-aware logging that redacts sensitive data.

**6.** Prompt caching requires identical prefix sequences. Design: Use a static, cacheable system prompt prefix shared across customers. Append customer-specific instructions after the cached prefix. This maximizes cache hits on the expensive system prompt while allowing customization.

**9.** Metrics: factual accuracy (claim extraction vs. source), completeness (key points coverage), conciseness ratio. Golden dataset: have 3+ lawyers independently summarize each document, use majority agreement. Multiple valid summaries: use semantic similarity against all reference summaries and take the max score; supplement with claim-level evaluation rather than text-level comparison.

**12.** Without logprobs, estimate confidence via: (1) self-consistency — ask the model to answer 3 times and measure agreement, (2) ask the model to rate its own confidence with structured output, (3) check if the response contains hedging language. Implement as a scoring pipeline after generation but before delivery.

**15.** Defense-in-depth: (1) Pre-processing: decode common encodings (base64, URL encoding, unicode escapes) before moderation, (2) Moderation: run decoded text through content filters, (3) Output validation: check response for policy violations, (4) Behavioral: use system prompts that instruct the model to ignore encoded instructions, (5) Monitoring: log and alert on encoded content in inputs.

**18.** Scope: Week 1 — chat UI (Streamlit), single provider, basic PII redaction. Week 2 — add second provider, cost tracking display, 5-case eval suite. Defer: production auth, deployment, comprehensive eval. Success criteria: functional chat with PII redaction demonstrated, cost tracking visible, eval scores above baseline on 5 agreed-upon test cases.

**23.** Start new models at low traffic (5%), run eval harness on every response, track quality scores. If quality stays above 0.8 threshold over N samples, gradually increase traffic. Use Thompson Sampling or epsilon-greedy to balance exploration vs. exploitation. Maintain a "known good" model that always stays in rotation as fallback.

**26.** Create parent span for full request. Child spans: `retrieve` (query, num_docs, latency), `rerank` (input_count, output_count, model), `generate` (prompt_tokens, completion_tokens, model, latency), `validate` (quality_score, hallucination_check). Log document IDs at each step. To trace quality issues: follow the trace ID from validation failure backward through spans to identify which step degraded (e.g., retrieval returned irrelevant docs, or reranker filtered too aggressively).

**29.** First 60 minutes: (0-5 min) Check provider status pages, ping customer API endpoint. (5-15 min) Check observability dashboard — error rates, latency, recent deployments. (15-20 min) Send customer initial acknowledgment with severity level. (20-40 min) Reproduce issue, check logs for error patterns (rate limits, auth failures, model errors). (40-50 min) Implement fix or workaround. (50-60 min) Update customer with root cause, fix, and prevention plan. Throughout: document everything in the incident channel.

**30.** Day 1-2: Discovery call — understand workflows, data types, compliance requirements, success criteria. Day 3-4: Architecture — choose providers with EU data centers, design PII redaction pipeline, set up audit logging. Day 5-7: Build core POC — document ingestion, analysis pipeline, Streamlit UI, mock security controls. Day 8-10: Add multi-provider failover, cost tracking, basic eval harness with 10 test documents. Day 11-12: Security review prep — compliance checklist, data flow diagram, encryption verification. Day 13-14: Polish, internal testing, prepare demo script and handoff documentation.

---

**End of Quiz**
