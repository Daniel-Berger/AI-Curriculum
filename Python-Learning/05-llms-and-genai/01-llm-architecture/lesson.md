# Module 01: LLM Architecture — From Transformers to Instruction-Tuned Models

## Why This Module Matters for Interviews

If you're applying for roles involving AI/ML -- whether as an iOS engineer integrating LLMs or a
full-stack ML engineer -- interviewers will probe your understanding of how language models are
built, trained, and aligned. You do not need to train one from scratch, but you must understand the
pipeline: pretraining, fine-tuning, alignment, and deployment. Think of it like understanding
UIKit's responder chain -- you rarely build it yourself, but you must know how it works.

This module is conceptual. There is no code to run (we will get hands-on starting in Module 02).
Focus on building a mental model you can articulate clearly in an interview.

---

## What Makes a Language Model "Large"

### Parameters: The Knobs of the Model

A neural network's "parameters" are its learnable weights and biases. Every matrix multiplication
in a transformer layer adds parameters. When we say a model has 7 billion parameters, we mean
there are 7 billion floating-point numbers that were tuned during training.

**Swift analogy:** Think of parameters as the configuration of a massively complex `struct`. If
you had a `struct` with 7 billion `Float` properties, each one tuned to produce the right output --
that is roughly what a 7B-parameter model looks like in memory.

### Scale Dimensions

Three things make a model "large":

| Dimension         | Description                                  | Example                        |
|-------------------|----------------------------------------------|--------------------------------|
| **Parameters**    | Number of learnable weights                  | GPT-3: 175B, Llama 3: 8B-405B |
| **Training data** | Amount of text consumed during pretraining   | Llama 2: ~2 trillion tokens    |
| **Compute**       | GPU-hours required for training              | GPT-4: estimated 10^25 FLOPs  |

### Parameter Counts by Model Component

For a standard transformer decoder (like GPT):

```
Parameters per layer:
  - Self-attention:  4 * d_model^2  (Q, K, V, Output projections)
  - Feed-forward:    2 * d_model * d_ff  (typically d_ff = 4 * d_model)
  - Layer norms:     2 * d_model (negligible)

Total per layer ≈ 4 * d_model^2 + 8 * d_model^2 = 12 * d_model^2

For a model with L layers:
  Total ≈ 12 * L * d_model^2 + V * d_model  (embedding layer)
```

**Example: Llama 2 7B**
- `d_model` = 4096, `L` = 32 layers, `V` = 32,000 vocabulary
- Per layer: 12 * 4096^2 = ~201M parameters
- All layers: 32 * 201M = ~6.4B
- Embeddings: 32,000 * 4096 = ~131M
- Total: ~6.5B (close to the reported 6.7B with extra components)

---

## The Transformer Architecture (Quick Review)

If you covered transformers in Phase 4, this is a recap. If not, here are the essentials.

### Core Components

```
Input text → Tokenizer → Token IDs → Embedding Layer → Positional Encoding
    → [Transformer Block × L] → Output Projection → Next Token Probabilities

Each Transformer Block:
    ┌──────────────────────┐
    │   Layer Norm         │
    │   Multi-Head Self-   │
    │   Attention          │
    │   + Residual         │
    ├──────────────────────┤
    │   Layer Norm         │
    │   Feed-Forward       │
    │   Network (FFN)      │
    │   + Residual         │
    └──────────────────────┘
```

### Self-Attention Mechanism

Self-attention lets each token "look at" every other token in the sequence to decide what
information is relevant.

```
Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V

Where:
  Q = input @ W_Q   (queries: "what am I looking for?")
  K = input @ W_K   (keys: "what do I contain?")
  V = input @ W_V   (values: "what information do I provide?")
  d_k = dimension of keys (for numerical stability)
```

**Multi-head attention** runs this computation in parallel across multiple "heads," each with
its own Q/K/V projections, allowing the model to attend to different types of relationships
simultaneously.

**Swift analogy:** Think of multi-head attention as having multiple `filter` closures running
on the same array, each looking for different patterns, then merging the results.

### Positional Encoding

Transformers have no inherent notion of position (unlike RNNs). Position information is injected
through positional encodings. Modern models use:

- **Rotary Position Embeddings (RoPE)**: Used in Llama, Mistral, Gemma. Encodes position as a
  rotation in the embedding space. Allows generalization to longer sequences than seen in training.
- **Absolute positional embeddings**: Original transformer / GPT-2 approach. Fixed or learned.
- **ALiBi (Attention with Linear Biases)**: Adds a linear bias to attention scores based on
  distance. Used in some BLOOM variants.

---

## Pretraining Objectives

### Causal Language Modeling (CLM) — Decoder-Only

The model predicts the next token given all previous tokens. This is the dominant paradigm for
modern LLMs (GPT, Claude, Llama, Mistral).

```
Input:   "The cat sat on the"
Target:  "cat sat on the mat"

The model can only see tokens to the LEFT (causal mask).
```

This is trained with **cross-entropy loss** between predicted and actual next tokens:

```
Loss = -sum(log P(token_t | token_1, ..., token_{t-1}))
```

**Key property:** The model learns a probability distribution over the entire vocabulary at each
position. Generation works by sampling from this distribution autoregressively.

### Masked Language Modeling (MLM) — Encoder-Only

Used by BERT and its variants. Random tokens are masked, and the model predicts them using
context from BOTH directions.

```
Input:   "The [MASK] sat on the [MASK]"
Target:  "cat", "mat"
```

MLM produces excellent representations for understanding tasks (classification, NER) but cannot
generate text autoregressively.

### Comparison

| Aspect               | Causal LM (GPT, Claude)        | Masked LM (BERT)              |
|----------------------|--------------------------------|-------------------------------|
| Direction            | Left-to-right only             | Bidirectional                 |
| Good at              | Text generation                | Text understanding            |
| Use case             | Chatbots, code gen, reasoning  | Classification, search, NER   |
| Modern prevalence    | Dominant for LLMs              | Used for embeddings/encoders  |

### Prefix LM and Encoder-Decoder

- **Prefix LM**: Bidirectional attention on a prefix, then causal attention on the rest. Used in
  some PaLM variants.
- **Encoder-Decoder**: Separate encoder (bidirectional) and decoder (causal) with cross-attention.
  Used in T5, BART, and the original transformer.

---

## The Pretraining Process

### Data

Modern LLMs are trained on massive, curated datasets:

| Dataset         | Size             | Content                                  |
|-----------------|------------------|------------------------------------------|
| The Pile        | ~800 GB text     | Books, GitHub, Wikipedia, ArXiv, etc.    |
| CommonCrawl     | Petabytes raw    | Web scrapes (heavily filtered)           |
| RefinedWeb      | ~5 trillion tokens | Deduplicated, filtered web data        |
| RedPajama       | ~1.2 trillion tokens | Open reproduction of LLaMA data      |

**Data pipeline:**
1. Collect raw text (web crawls, books, code repositories)
2. Filter low-quality content (deduplication, language detection, toxicity filtering)
3. Tokenize into subword tokens
4. Shuffle and batch

### Compute Requirements

Training a large model requires enormous compute:

```
Compute (FLOPs) ≈ 6 × N × D

Where:
  N = number of parameters
  D = number of training tokens

Example: Llama 2 70B
  N = 70 billion, D = 2 trillion tokens
  FLOPs ≈ 6 × 70 × 10^9 × 2 × 10^12 = 8.4 × 10^23
  On A100 GPUs (312 TFLOPS): ~31 days on 2,000 GPUs
```

### Training Dynamics

- **Learning rate schedule:** Warmup followed by cosine decay is standard.
- **Batch size:** Gradually increased during training. Final batch sizes can be millions of tokens.
- **Mixed precision:** FP16 or BF16 for forward/backward pass, FP32 for master weights.
- **Gradient accumulation:** Simulate larger batch sizes across multiple forward passes.
- **Model parallelism:** Split the model across GPUs (tensor parallelism, pipeline parallelism).
- **Data parallelism:** Each GPU processes different batches, gradients are synchronized.

### Training Loss Curves

```
Loss
  |
4 |\.
  |  '\.
3 |     '\.
  |        '---...__
2 |                  '---...___
  |                             '---...___
1 |                                        '------
  |_____________________________________________
  0    200B   400B   600B   800B   1T    1.5T   2T
                    Training Tokens
```

The loss decreases smoothly and predictably -- this is what makes scaling laws possible.

---

## Scaling Laws

### The Chinchilla Insight

In 2022, DeepMind published the "Chinchilla" paper, which showed that most LLMs were
**undertrained**. The key finding:

> For compute-optimal training, the number of training tokens should scale proportionally
> with the number of parameters.

**The Chinchilla ratio:** Approximately 20 tokens per parameter.

```
Optimal tokens ≈ 20 × N (number of parameters)

Chinchilla (70B params) was trained on 1.4 trillion tokens
  → 1.4T / 70B = 20 tokens per parameter ✓

GPT-3 (175B params) was trained on 300 billion tokens
  → 300B / 175B = 1.7 tokens per parameter ✗ (severely undertrained)
```

### Scaling Law Equations

The cross-entropy loss of a language model follows predictable power laws:

```
L(N) = (N_c / N)^α_N    (scaling with parameters)
L(D) = (D_c / D)^α_D    (scaling with data)
L(C) = (C_c / C)^α_C    (scaling with compute)

Where α values are empirically determined constants (~0.07-0.08)
```

**Why this matters:** You can predict model performance before training, enabling informed
decisions about resource allocation.

### Modern Post-Chinchilla Practice

In practice, many recent models over-train relative to Chinchilla-optimal because:
1. **Inference cost matters more than training cost.** A smaller model trained on more data
   is cheaper to deploy than a larger model.
2. Llama 2 7B was trained on 2T tokens (286 tokens/param) -- far beyond Chinchilla-optimal.
3. The trend is toward smaller, heavily-trained models for deployment efficiency.

---

## Emergent Abilities

Some capabilities appear suddenly as models scale, rather than improving gradually:

| Ability                  | Approximate threshold     |
|--------------------------|---------------------------|
| Few-shot learning        | ~1B parameters            |
| Chain-of-thought         | ~60B parameters           |
| Multi-step reasoning     | ~100B+ parameters         |
| Complex code generation  | ~30B+ parameters          |

**Caveat:** Recent research questions whether emergence is truly "sudden" or an artifact of
how we measure performance (discrete metrics vs. continuous ones). When measured with continuous
metrics (like log-probability), improvement is often gradual.

**Interview tip:** Be prepared to discuss emergence nuancedly. Don't just say "abilities appear
magically at scale." Mention the measurement artifact debate.

---

## Instruction Tuning (Supervised Fine-Tuning / SFT)

### The Problem with Base Models

A pretrained base model is an excellent next-token predictor, but it's not a helpful assistant.
Given the prompt "What is the capital of France?", a base model might continue with:

```
"What is the capital of France?\nWhat is the capital of Germany?\nWhat is the capital of Spain?"
```

It's completing a pattern of questions, not answering. Instruction tuning fixes this.

### What is SFT?

Supervised Fine-Tuning takes the base model and trains it on a dataset of (instruction, response)
pairs. The model learns to follow instructions rather than just predict text.

### Data Format

```json
{
  "instruction": "Explain quantum computing in simple terms.",
  "input": "",
  "output": "Quantum computing uses quantum bits (qubits) that can exist in multiple states simultaneously, unlike classical bits that are either 0 or 1. This property, called superposition, allows quantum computers to explore many solutions at once, making them potentially much faster for certain types of problems like cryptography, drug discovery, and optimization."
}
```

Or in the chat/messages format used by modern APIs:

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms."},
    {"role": "assistant", "content": "Quantum computing uses quantum bits (qubits)..."}
  ]
}
```

### Quality vs. Quantity

A crucial finding: **data quality matters far more than quantity** for SFT.

- **LIMA paper (2023):** Just 1,000 carefully curated examples produced a strong instruction-
  following model. The paper's title: "Less Is More for Alignment."
- **Alpaca:** 52,000 GPT-generated examples. Good but not great.
- Modern practice: 10,000-100,000 high-quality examples, often human-written and reviewed.

**Key quality signals:**
- Diverse task coverage (not just Q&A)
- Consistent formatting
- Accurate, helpful responses
- Appropriate refusals for harmful requests

---

## RLHF: Reinforcement Learning from Human Feedback

### Why SFT is Not Enough

SFT teaches the model to follow instructions, but it doesn't teach the model which responses
humans actually prefer. Two responses can both follow instructions but differ in helpfulness,
safety, or style. RLHF bridges this gap.

### The Three-Stage RLHF Pipeline

```
Stage 1: SFT Model (already done above)
    ↓
Stage 2: Train a Reward Model
    ↓
Stage 3: Optimize the SFT model using PPO against the Reward Model
```

### Stage 2: Reward Model Training

1. Generate multiple responses to the same prompt using the SFT model.
2. Have human annotators rank the responses (e.g., Response A > Response B).
3. Train a reward model (often a copy of the LLM with a scalar output head) to predict
   human preferences.

```
Reward Model:
  Input:  (prompt, response)
  Output: scalar score (higher = better)

Training objective (Bradley-Terry model):
  Loss = -log(sigmoid(r(preferred) - r(rejected)))
```

### Stage 3: PPO Optimization

Proximal Policy Optimization (PPO) is used to fine-tune the SFT model to maximize the reward
model's score while staying close to the original SFT model (to prevent reward hacking).

```
Objective = E[R(prompt, response)] - β × KL(π_RL || π_SFT)

Where:
  R = reward model score
  KL = KL divergence (penalty for diverging too far from SFT model)
  β = coefficient controlling the KL penalty
  π_RL = current RL policy (model being optimized)
  π_SFT = original SFT model (reference)
```

**Why KL divergence?** Without it, the model learns to exploit the reward model -- generating
bizarre outputs that score high on the reward model but are actually terrible. This is called
"reward hacking."

**Swift analogy:** Think of the reward model as a code review bot. PPO is like iteratively
improving your code to pass the review, but with a constraint that you can't stray too far from
your original architecture (the KL penalty).

---

## DPO: Direct Preference Optimization

### The Problem with RLHF

RLHF is complex: it requires training a separate reward model, then running PPO (which is
notoriously unstable and hyperparameter-sensitive). DPO simplifies this.

### How DPO Works

DPO skips the reward model entirely. Instead, it directly optimizes the language model using
preference pairs:

```
DPO Loss = -log sigmoid(β × (log π(y_w|x)/π_ref(y_w|x) - log π(y_l|x)/π_ref(y_l|x)))

Where:
  y_w = preferred (winning) response
  y_l = dispreferred (losing) response
  x = prompt
  π = model being trained
  π_ref = reference model (frozen SFT model)
  β = temperature parameter
```

**Key insight:** DPO shows that the optimal policy under the RLHF objective can be expressed
in closed form, eliminating the need for a separate reward model and RL training loop.

### RLHF vs. DPO Comparison

| Aspect             | RLHF                          | DPO                           |
|--------------------|------------------------------ |-------------------------------|
| Components         | SFT + Reward Model + PPO      | SFT + Direct Optimization    |
| Complexity         | High (3 models in memory)     | Low (2 models in memory)     |
| Stability          | PPO can be unstable           | Standard supervised training  |
| Data required      | Preference pairs              | Same preference pairs         |
| Performance        | Strong (proven at scale)      | Competitive (simpler)         |
| Used by            | OpenAI (GPT-4), Anthropic     | Llama, many open-source       |

**Interview tip:** Know that DPO exists as a simpler alternative. Many interviewers ask about
the tradeoffs. The answer: DPO is simpler and more stable, but RLHF can be more flexible
(e.g., online RLHF with continuously updated reward models).

---

## Model Families Overview

### GPT Series (OpenAI)

| Model    | Parameters | Context  | Key Innovation                          |
|----------|------------|----------|-----------------------------------------|
| GPT-2    | 1.5B       | 1024     | Showed language models can be general   |
| GPT-3    | 175B       | 2048     | Few-shot learning, in-context learning  |
| GPT-3.5  | ~175B      | 4K-16K   | ChatGPT, instruction-tuned with RLHF   |
| GPT-4    | ~1.8T MoE  | 8K-128K  | Multimodal, massive quality jump        |
| GPT-4o   | Unknown    | 128K     | Omni-modal (text, vision, audio)        |

**Architecture note:** GPT-4 is widely believed to be a Mixture of Experts (MoE) model --
multiple smaller "expert" networks with a router that selects which experts handle each token.
This allows a very large total parameter count while keeping per-token compute manageable.

### Claude (Anthropic)

| Model       | Context  | Key Features                              |
|-------------|----------|-------------------------------------------|
| Claude 1    | 9K       | Constitutional AI (CAI)                   |
| Claude 2    | 100K     | Long context pioneer                      |
| Claude 3    | 200K     | Haiku/Sonnet/Opus tiers                   |
| Claude 3.5  | 200K     | Sonnet: strong coding, fast               |
| Claude 4    | 200K     | Extended thinking, agentic capabilities   |

**Key differentiator:** Anthropic uses Constitutional AI (CAI), where the model critiques and
revises its own outputs based on a set of principles ("constitution"), reducing reliance on
human feedback.

### Llama (Meta)

| Model      | Sizes            | Key Innovation                           |
|------------|------------------|------------------------------------------|
| Llama 1    | 7B-65B           | Open weights, competitive quality        |
| Llama 2    | 7B-70B           | Open for commercial use, chat variants   |
| Llama 3    | 8B, 70B          | GQA, improved tokenizer, 15T tokens     |
| Llama 3.1  | 8B, 70B, 405B    | 128K context, tool use, multilingual     |

**Architecture details:**
- RoPE positional embeddings
- Grouped-Query Attention (GQA) -- shares key/value heads across query heads for efficiency
- SwiGLU activation function in FFN
- RMSNorm instead of LayerNorm

### Mistral

| Model        | Sizes    | Key Innovation                             |
|--------------|----------|--------------------------------------------|
| Mistral 7B   | 7B       | Sliding window attention, strong for size  |
| Mixtral 8x7B | 46.7B    | Open-source MoE, 12.9B active params      |
| Mistral Large | Unknown | Competitive with GPT-4                     |

**Key innovation:** Sliding Window Attention -- each token attends only to a local window of
tokens rather than the full sequence, reducing memory from O(n^2) to O(n * w).

### Gemma (Google)

| Model    | Sizes       | Key Features                               |
|----------|-------------|--------------------------------------------|
| Gemma    | 2B, 7B      | Open weights, based on Gemini architecture |
| Gemma 2  | 2B, 9B, 27B | Improved quality, knowledge distillation   |

### Architecture Comparison

| Feature               | GPT-4      | Claude 3  | Llama 3   | Mistral 7B  |
|-----------------------|------------|-----------|-----------|-------------|
| Attention             | MHA (MoE)  | Unknown   | GQA       | GQA + SWA   |
| Positional Encoding   | Unknown    | Unknown   | RoPE      | RoPE        |
| Activation (FFN)      | Unknown    | Unknown   | SwiGLU    | SwiGLU      |
| Normalization         | Unknown    | Unknown   | RMSNorm   | RMSNorm     |
| Open Weights          | No         | No        | Yes       | Yes         |

---

## Context Window Evolution

The context window determines how much text the model can process at once.

```
Timeline of context length growth:

2018  GPT-1:           512 tokens
2019  GPT-2:         1,024 tokens
2020  GPT-3:         2,048 tokens
2022  GPT-3.5:       4,096 tokens
2023  GPT-4:       128,000 tokens
2023  Claude 2:    100,000 tokens
2024  Claude 3:    200,000 tokens
2024  Gemini 1.5: 1,000,000 tokens
2025  Gemini 2.0: 2,000,000 tokens
```

**Techniques for extending context:**
- **RoPE scaling:** Interpolate or extrapolate rotary embeddings to longer sequences
- **ALiBi:** Attention with linear biases generalizes naturally
- **Ring Attention:** Distribute long sequences across GPUs
- **Sparse attention patterns:** Not all tokens need to attend to all others

**Why context length matters:**
- Longer context = more information available for each response
- Enables processing entire codebases, books, or long documents
- Reduces the need for retrieval-augmented generation (RAG) in some cases
- But longer context != perfect recall (models struggle with info in the middle -- the
  "lost in the middle" problem)

---

## Model Sizes and Their Capabilities

### Size Tiers

| Tier       | Parameters | Typical Use Cases                        | Example           |
|------------|------------|------------------------------------------|--------------------|
| Tiny       | <1B        | Edge devices, simple classification      | TinyLlama (1.1B)   |
| Small      | 1-3B       | Mobile, fast inference, simple tasks     | Gemma 2B, Phi-2    |
| Medium     | 7-13B      | Good general ability, runs on 1 GPU     | Llama 3 8B         |
| Large      | 30-70B     | Strong reasoning, coding, analysis       | Llama 3 70B        |
| Frontier   | 100B+      | State-of-the-art, multi-step reasoning   | GPT-4, Claude 3    |

### Memory Requirements

```
Memory ≈ Parameters × Bytes per Parameter

FP32 (full precision):     7B × 4 bytes = 28 GB
FP16 (half precision):     7B × 2 bytes = 14 GB
INT8 (8-bit quantization): 7B × 1 byte  = 7 GB
INT4 (4-bit quantization): 7B × 0.5 bytes = 3.5 GB

Plus overhead for KV cache, activations, etc.
```

### Quantization

Quantization reduces the precision of model weights to shrink memory usage and speed up
inference, with minimal quality loss.

| Method     | Bits | Quality Impact     | Use Case                   |
|------------|------|--------------------|----------------------------|
| FP16/BF16  | 16   | Negligible         | Standard GPU inference     |
| INT8       | 8    | Very small         | Single GPU deployment      |
| INT4 (GPTQ)| 4   | Small but notable  | Consumer GPUs, edge        |
| GGUF (llama.cpp) | 2-8 | Varies       | CPU inference, mobile      |

---

## The Full LLM Training Pipeline

Putting it all together:

```
Stage 0: Data Collection & Curation
    │  Collect text from web, books, code, etc.
    │  Filter, deduplicate, clean
    ▼
Stage 1: Pretraining (Causal LM)
    │  Train on trillions of tokens
    │  Learn language, world knowledge, reasoning
    │  Output: Base model
    ▼
Stage 2: Supervised Fine-Tuning (SFT)
    │  Train on instruction-response pairs
    │  Learn to follow instructions, be helpful
    │  Output: SFT model (chat-capable)
    ▼
Stage 3: Alignment (RLHF or DPO)
    │  Train on human preference data
    │  Learn what humans consider helpful, harmless, honest
    │  Output: Aligned model (deployed model)
    ▼
Stage 4: Deployment
    │  Quantization, serving infrastructure
    │  Safety filters, rate limiting
    │  Monitoring and feedback collection
```

---

## Key Concepts for Interviews

### Questions You Should Be Able to Answer

1. **"What is the difference between pretraining and fine-tuning?"**
   - Pretraining: learning general language patterns from massive unlabeled data
   - Fine-tuning: adapting the pretrained model for specific tasks with labeled data

2. **"What is RLHF and why is it needed?"**
   - Reinforcement Learning from Human Feedback aligns model behavior with human preferences
   - SFT teaches format; RLHF teaches quality and safety

3. **"What are scaling laws?"**
   - Performance (loss) follows predictable power-law relationships with compute, data, and parameters
   - Chinchilla showed optimal training uses ~20 tokens per parameter

4. **"Explain DPO vs RLHF."**
   - DPO directly optimizes from preference pairs without a reward model
   - Simpler, more stable, but potentially less flexible than RLHF

5. **"What is a Mixture of Experts model?"**
   - Multiple "expert" FFN layers with a learned router
   - Only a subset of experts process each token
   - Large total parameter count, but efficient per-token compute

6. **"How do models handle long context?"**
   - Techniques like RoPE scaling, sliding window attention, ring attention
   - Context length has grown from 512 to 1M+ tokens in ~6 years

### Common Misconceptions

| Misconception                              | Reality                                    |
|--------------------------------------------|--------------------------------------------|
| More parameters = always better            | Training data and quality matter equally   |
| Models "understand" language               | They learn statistical patterns            |
| RLHF makes models safe                    | It helps but doesn't guarantee safety      |
| Bigger context = better retrieval          | "Lost in the middle" problem exists        |
| Open-source models are far behind          | Gap has narrowed significantly             |

---

## Swift Developer's Mental Model

If you're coming from iOS/Swift, here is how LLM concepts map to familiar ideas:

| LLM Concept           | Swift/iOS Analogy                                    |
|------------------------|------------------------------------------------------|
| Pretrained base model  | UIKit framework -- general-purpose foundation        |
| SFT                    | Building your app on top of UIKit                    |
| RLHF / DPO            | User testing and iterating based on feedback         |
| Parameters             | Configuration values in a massive `struct`           |
| Context window         | Working memory -- like a `Data` buffer with a limit  |
| Tokenizer              | `String.UTF8View` -- converting text to numbers      |
| Inference              | Running your compiled app                            |
| Training               | Xcode compilation (but takes weeks and costs millions)|
| Quantization           | App thinning / bitcode optimization                  |
| MoE routing            | Dynamic dispatch / protocol witness tables           |

---

## Further Reading

- **"Attention Is All You Need" (2017)** — The original transformer paper
- **"Scaling Laws for Neural Language Models" (Kaplan et al., 2020)** — OpenAI's scaling laws
- **"Training Compute-Optimal Large Language Models" (Hoffmann et al., 2022)** — Chinchilla paper
- **"LLaMA: Open and Efficient Foundation Language Models" (Touvron et al., 2023)** — Llama 1
- **"Direct Preference Optimization" (Rafailov et al., 2023)** — DPO paper
- **"LIMA: Less Is More for Alignment" (Zhou et al., 2023)** — Quality over quantity for SFT
- **"Constitutional AI" (Bai et al., 2022)** — Anthropic's alignment approach

---

## Summary

| Topic                   | Key Takeaway                                              |
|--------------------------|-----------------------------------------------------------|
| Scale                    | Parameters, data, and compute all matter                 |
| Pretraining              | Causal LM on trillions of tokens = general intelligence  |
| SFT                      | Small, high-quality dataset → instruction following       |
| RLHF                     | Reward model + PPO → aligned with human preferences       |
| DPO                      | Simpler alternative to RLHF, directly uses preference data|
| Scaling laws             | Performance is predictable; Chinchilla ratio ≈ 20:1       |
| Model families           | GPT, Claude, Llama, Mistral, Gemma — each with tradeoffs |
| Context windows          | Growing rapidly; 200K+ tokens now standard               |
| Quantization             | Enables deployment on consumer hardware                   |

Next module: **Tokenization** — how text becomes the numbers that models actually process.
