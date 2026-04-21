# Phase 5: LLMs & Generative AI — Comprehensive Quiz

35 questions covering all modules. Answers at the bottom.

---

## EASY (10 questions)

**1. What is a transformer?**
   - a) A type of neural network architecture based on self-attention
   - b) A data preprocessing tool
   - c) A software library by Google
   - d) A device for electrical power conversion

**2. What does "tokenization" mean in NLP?**
   - a) Converting tokens to embeddings
   - b) Breaking text into smaller units (tokens) for processing
   - c) Adding random noise to text
   - d) Translating text to another language

**3. What is BPE (Byte-Pair Encoding)?**
   - a) A method for compressing binary files
   - b) A subword tokenization algorithm
   - c) A neural network layer
   - d) A text classification technique

**4. What is a context window?**
   - a) A GUI component
   - b) The maximum amount of text an LLM can process at once
   - c) A caching mechanism
   - d) A training technique

**5. What does RLHF stand for?**
   - a) Reinforcement Learning from Human Feedback
   - b) Recurrent Layer Hyperparameter Framework
   - c) Regression Learning for Hidden Features
   - d) Real-time Language Handling Framework

**6. What is RAG?**
   - a) A type of loss function
   - b) Retrieval-Augmented Generation
   - c) Rapid API Growth
   - d) A model architecture

**7. What is an embedding?**
   - a) Including text within another text
   - b) A vector representation of text in semantic space
   - c) A type of database
   - d) An API endpoint

**8. What is DPO?**
   - a) Direct Policy Optimization
   - b) Data Preprocessing Operation
   - c) Direct Preference Optimization
   - d) Distributed Processing Operation

**9. What are "scaling laws" in LLMs?**
   - a) Rules for resizing models
   - b) Predictable power-law relationships between compute/data and performance
   - c) Methods for distributed training
   - d) Formulas for model efficiency

**10. What is the Chinchilla ratio?**
   - a) 1:1 ratio of parameters to layers
   - b) Approximately 20 tokens per parameter for optimal training
   - c) A metric for model compression
   - d) A technique for data augmentation

---

## MEDIUM (15 questions)

**11. In the Claude API, how are system prompts provided?**
   - a) As a separate parameter only
   - b) As a message with role='system'
   - c) Via environment variable
   - d) Both A and B

**12. What's the key difference between few-shot and zero-shot prompting?**
   - a) Few-shot uses more parameters
   - b) Few-shot provides examples; zero-shot does not
   - c) Zero-shot is faster
   - d) They're the same thing

**13. What does chain-of-thought prompting improve?**
   - a) Model speed
   - b) Accuracy on multi-step reasoning tasks
   - c) Token efficiency
   - d) Training speed

**14. In HyDE (Hypothetical Document Embeddings), what's the key insight?**
   - a) Generate hypothetical answers and embed those instead of the question
   - b) Use multiple hypotheses to improve search
   - c) Hypothetical documents train the model better
   - d) It's just a faster embedding method

**15. What is the purpose of re-ranking in RAG?**
   - a) Organize documents alphabetically
   - b) Two-stage retrieval: first retrieve broadly, then rank precisely
   - c) Prevent duplicate documents
   - d) Speed up vector search

**16. How does cosine similarity differ from Euclidean distance?**
   - a) Cosine is faster
   - b) Euclidean measures absolute distance; cosine measures angle
   - c) Cosine only works for normalized vectors
   - d) They measure the same thing

**17. What is LoRA in the context of fine-tuning?**
   - a) A type of activation function
   - b) Low-Rank Adaptation: efficient parameter updates using small rank matrices
   - c) Loss Optimization for Rapid Adaptation
   - d) A new model architecture

**18. In tool use/function calling, what does the model actually output?**
   - a) Natural language describing which tool to use
   - b) A structured request for a tool with specific parameters
   - c) Python code to execute tools
   - d) A confidence score

**19. What's the ReAct pattern?**
   - a) Response-Action pattern for model outputs
   - b) Reason + Act: the model thinks, then decides on actions
   - c) Retrieve-Extract-Act pattern
   - d) Real-time Action pattern

**20. How should you validate tool inputs before execution?**
   - a) Trust the model always
   - b) Check against JSON schema to validate types and constraints
   - c) No validation needed
   - d) Only validate in production

**21. What's the "lost in the middle" problem?**
   - a) Models get confused by middle paragraphs
   - b) Models tend to focus on first and last documents, ignoring middle ones
   - c) Training data is incomplete
   - d) Token limits are exceeded

**22. What does RAGAS evaluate?**
   - a) The grammar of generated text
   - b) How good a RAG system is (faithfulness, relevance, etc.)
   - c) The speed of retrieval
   - d) User satisfaction only

**23. What's the purpose of input validation in tool execution?**
   - a) To slow down execution
   - b) To ensure tool inputs are correct type and within constraints
   - c) To comply with regulations
   - d) No real purpose

**24. In fine-tuning, what's a good rule of thumb for training data size?**
   - a) Minimum 10 examples
   - b) Minimum 100 examples, ideally 500+
   - c) No minimum required
   - d) Millions of examples always needed

**25. What's the key difference between RLHF and DPO?**
   - a) RLHF is faster
   - b) DPO uses preference pairs directly; RLHF trains a separate reward model
   - c) They're the same
   - d) DPO is only for classification

---

## HARD (10 questions)

**26. Given a 7B parameter model with d_model=4096 and 32 layers, approximately how many parameters are in the attention layer alone?**
   - a) ~4.2 billion
   - b) ~200 million
   - c) ~1.6 billion
   - d) ~2.5 billion

**27. You need to embed 1M documents with text-embedding-3-small at $0.02 per 1M tokens. Average 256 tokens per document. What's the approximate cost?**
   - a) $5.12
   - b) $512
   - c) $51.20
   - d) $0.51

**28. Your RAG system retrieves 5 documents but the model ignores the middle 3 and only references the first and last. What might be happening?**
   - a) Model is performing correctly
   - b) Lost-in-the-middle problem: format retrieved docs to highlight importance
   - c) Documents are too long
   - d) Random model behavior

**29. In LLM training, if you overtrain a 7B model to 286 tokens per parameter (vs. Chinchilla-optimal 20), what are you likely optimizing for?**
   - a) Training speed
   - b) Parameter count reduction
   - c) Inference efficiency (smaller model, more data, cheaper to deploy)
   - d) Model accuracy only

**30. Your fine-tuned model has train loss=0.3, val loss=0.5. What's happening?**
   - a) Model is underfitting
   - b) Model is overfitting
   - c) Perfect training
   - d) Training is complete

**31. In multi-query RAG, why generate multiple paraphrases of the query?**
   - a) To trick the system
   - b) To improve diversity and robustness by retrieving with different phrasings
   - c) To increase computational cost
   - d) No real benefit

**32. What's the relationship between model parameters, training tokens, and optimal compute (Chinchilla)?**
   - a) Compute = Parameters * Tokens / 6
   - b) Compute = 6 * Parameters * Tokens
   - c) They're unrelated
   - d) Tokens should be 1/20 of Parameters

**33. When should you use streaming vs. non-streaming API calls?**
   - a) Always streaming
   - b) Streaming for lower perceived latency; non-streaming for batch processing
   - c) Only in development
   - d) Never stream

**34. What's the core challenge RAG solves?**
   - a) Making models faster
   - b) Adding real-time, domain-specific information without retraining
   - c) Replacing all LLMs
   - d) Improving tokenization

**35. In GraphRAG, how is the knowledge structure different from simple document retrieval?**
   - a) It's the same, just called differently
   - b) Documents are nodes; relationships are edges; enables multi-hop reasoning
   - c) It uses graphs instead of vectors
   - d) No significant difference

---

## ANSWER KEY

### Easy
1. **a** - Transformers are neural networks based on self-attention
2. **b** - Tokenization breaks text into tokens
3. **b** - BPE is a subword tokenization algorithm
4. **b** - Context window is max text length
5. **a** - RLHF = Reinforcement Learning from Human Feedback
6. **b** - RAG = Retrieval-Augmented Generation
7. **b** - Embeddings are vector representations
8. **c** - DPO = Direct Preference Optimization
9. **b** - Scaling laws are predictable power-law relationships
10. **b** - Chinchilla ratio ≈ 20 tokens per parameter

### Medium
11. **d** - Both parameter and message formats work
12. **b** - Few-shot provides examples; zero-shot doesn't
13. **b** - Chain-of-thought improves reasoning accuracy
14. **a** - HyDE generates hypothetical answers to embed instead of questions
15. **b** - Re-ranking is two-stage retrieval
16. **b** - Euclidean = distance; Cosine = angle
17. **b** - LoRA = Low-Rank Adaptation
18. **b** - Structured request with parameters (not natural language)
19. **b** - Reason + Act pattern
20. **b** - Validate against JSON schema
21. **b** - Models focus on first/last, ignore middle
22. **b** - RAGAS evaluates RAG system quality
23. **b** - Ensure inputs are correct type/constraints
24. **b** - Minimum 100 examples, ideally 500+
25. **b** - DPO direct; RLHF uses separate reward model

### Hard
26. **c** - Attention per layer = 4 * d_model^2 = 4 * 4096^2 ≈ 67M; 32 layers ≈ 2.1B
27. **a** - 1M * 256 / 1M = 256k tokens at 1M; (256k / 1M) * $0.02 = $5.12
28. **b** - Lost-in-the-middle problem
29. **c** - Over-training yields smaller model with good quality (deployment efficiency)
30. **b** - Train loss much lower than val loss = overfitting
31. **b** - Robustness through diverse phrasings
32. **b** - Compute = 6 * N * D (standard formula)
33. **b** - Streaming for UX; non-streaming for batch
34. **b** - Adding real-time information without retraining
35. **b** - GraphRAG uses entities/relationships for multi-hop reasoning

---

## Scoring

- **28-35 correct**: Expert level. Ready for senior interviews.
- **21-27 correct**: Advanced. Strong foundation, review weak areas.
- **14-20 correct**: Intermediate. Study harder modules before interviews.
- **<14 correct**: Foundational. Review all modules before interviews.

---

## Study Tips

1. **Review weak areas**: If you scored <20%, focus on modules covering those questions.
2. **Understand the "why"**: Don't just memorize; understand concepts.
3. **Practice code**: Work through exercises in each module.
4. **Ask yourself**: "How would I explain this to someone else?"
5. **Interview prep**: Practice explaining these concepts out loud.
