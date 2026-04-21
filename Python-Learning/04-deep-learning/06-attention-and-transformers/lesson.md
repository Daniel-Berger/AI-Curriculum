# Module 06: Attention and Transformers

## Introduction for Swift Developers

If you've used Apple's Translation framework, on-device Siri, or any text generation
in iOS 18+, you've been using transformers. The transformer is the architecture behind
GPT, BERT, LLaMA, and virtually every modern AI system. Understanding it is arguably
the single most important concept in modern machine learning.

This module builds the transformer from scratch. We start with the attention mechanism
(the key innovation), then assemble the full architecture piece by piece. By the end,
you'll understand every component of the models powering ChatGPT.

```
Swift analogy: Think of attention as a sophisticated Dictionary lookup
where instead of exact key matching, you compute a similarity score
against ALL keys and return a weighted blend of the values.
```

---

## 1. The Problem: Fixed-Size Bottleneck

### Why RNN Seq2Seq Falls Short

In Module 05, we built a seq2seq model where the encoder compresses the entire
input into a single fixed-size vector (the context vector). This is a bottleneck:

```
Encoder: "The cat sat on the mat" --> [0.23, -0.41, 0.87, ...]  (single vector!)
Decoder: [0.23, -0.41, 0.87, ...] --> "Le chat etait assis sur le tapis"
```

Problems:
- Long inputs get crushed into the same size vector as short inputs
- Information from early tokens is particularly degraded
- The decoder can't "look back" at specific parts of the input

### The Attention Solution

Instead of compressing everything into one vector, let the decoder **attend** to
all encoder outputs at each decoding step:

```
"What part of the input should I focus on to generate the next output word?"
```

---

## 2. Attention Mechanism from Scratch

### Query, Key, Value

Attention uses three concepts borrowed from information retrieval:

| Concept | Analogy | Role |
|---------|---------|------|
| **Query** (Q) | Your search query | "What am I looking for?" |
| **Key** (K) | Index entries in a database | "What information is available?" |
| **Value** (V) | The actual stored data | "What do I return?" |

The process:
1. Compute a **score** between the query and each key (how relevant is each key?)
2. Normalize scores with **softmax** (convert to probabilities)
3. Use the probabilities to create a **weighted sum** of values

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


def simple_attention(
    query: torch.Tensor,   # (batch, d_model)
    keys: torch.Tensor,    # (batch, seq_len, d_model)
    values: torch.Tensor,  # (batch, seq_len, d_model)
) -> torch.Tensor:
    """Basic dot-product attention.

    Swift analogy: Like Dictionary.subscript but returning
    a weighted blend of ALL values instead of a single match.
    """
    # Step 1: Compute attention scores (dot product of query with each key)
    # query: (batch, 1, d_model)  <-- unsqueeze for broadcasting
    # keys:  (batch, seq_len, d_model)
    scores = torch.bmm(query.unsqueeze(1), keys.transpose(1, 2))
    # scores: (batch, 1, seq_len) -- one score per key

    # Step 2: Normalize with softmax (scores become probabilities)
    weights = F.softmax(scores, dim=-1)
    # weights: (batch, 1, seq_len) -- sums to 1.0

    # Step 3: Weighted sum of values
    context = torch.bmm(weights, values)
    # context: (batch, 1, d_model)

    return context.squeeze(1)  # (batch, d_model)


# Example
batch, seq_len, d_model = 2, 5, 8
query = torch.randn(batch, d_model)
keys = torch.randn(batch, seq_len, d_model)
values = torch.randn(batch, seq_len, d_model)

context = simple_attention(query, keys, values)
print(f"Context vector: {context.shape}")  # (2, 8)
```

### Scaled Dot-Product Attention

The full version used in transformers adds **scaling** to prevent dot products
from getting too large (which would make softmax saturate):

```python
def scaled_dot_product_attention(
    Q: torch.Tensor,  # (batch, num_queries, d_k)
    K: torch.Tensor,  # (batch, num_keys, d_k)
    V: torch.Tensor,  # (batch, num_keys, d_v)
    mask: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Scaled dot-product attention (the core of transformers).

    Formula: Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V

    Args:
        Q: Queries
        K: Keys
        V: Values
        mask: Optional mask (True = position to MASK/ignore)

    Returns:
        output: Weighted sum of values, shape (batch, num_queries, d_v)
        weights: Attention weights, shape (batch, num_queries, num_keys)
    """
    d_k = Q.shape[-1]

    # Step 1: Compute scaled scores
    # Q @ K^T: (batch, num_queries, d_k) @ (batch, d_k, num_keys)
    #        = (batch, num_queries, num_keys)
    scores = torch.bmm(Q, K.transpose(-2, -1)) / math.sqrt(d_k)

    # Why scale by sqrt(d_k)?
    # If Q and K have elements with mean 0, variance 1, then their dot
    # product has variance d_k. Dividing by sqrt(d_k) normalizes this
    # back to variance 1, keeping softmax in a useful gradient range.

    # Step 2: Apply mask (if provided)
    if mask is not None:
        scores = scores.masked_fill(mask, float('-inf'))
        # Positions with -inf will get softmax weight ≈ 0

    # Step 3: Softmax over key dimension
    weights = F.softmax(scores, dim=-1)

    # Step 4: Weighted sum of values
    output = torch.bmm(weights, V)

    return output, weights


# Example
Q = torch.randn(2, 3, 64)  # 2 batches, 3 queries, d_k=64
K = torch.randn(2, 5, 64)  # 2 batches, 5 keys, d_k=64
V = torch.randn(2, 5, 64)  # 2 batches, 5 values, d_v=64

output, weights = scaled_dot_product_attention(Q, K, V)
print(f"Output: {output.shape}")    # (2, 3, 64) -- one output per query
print(f"Weights: {weights.shape}")  # (2, 3, 5) -- each query attends to 5 keys
print(f"Weights sum: {weights.sum(dim=-1)}")  # All 1.0 (probability distribution)
```

---

## 3. Multi-Head Attention

### Why Multiple Heads?

A single attention mechanism can only focus on one type of relationship at a time.
Multi-head attention runs several attention operations **in parallel**, each learning
different aspects:

```
Head 1 might learn: syntactic relationships (subject-verb agreement)
Head 2 might learn: semantic relationships (word similarity)
Head 3 might learn: positional relationships (nearby words)
Head 4 might learn: coreference (pronouns to nouns)
```

### Implementation

```python
class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism.

    Instead of one big attention, we split into h smaller "heads"
    that each attend independently, then concatenate their outputs.

    Swift analogy: Like running multiple Dictionary lookups with
    different similarity functions, then combining the results.
    """

    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads  # Dimension per head

        # Linear projections for Q, K, V (applied before splitting into heads)
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)

        # Output projection (applied after concatenating heads)
        self.W_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        query: torch.Tensor,  # (batch, seq_q, d_model)
        key: torch.Tensor,    # (batch, seq_k, d_model)
        value: torch.Tensor,  # (batch, seq_k, d_model)
        mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        batch_size = query.shape[0]

        # 1. Linear projections
        Q = self.W_q(query)  # (batch, seq_q, d_model)
        K = self.W_k(key)    # (batch, seq_k, d_model)
        V = self.W_v(value)  # (batch, seq_k, d_model)

        # 2. Split into heads: reshape d_model -> (num_heads, d_k)
        # (batch, seq, d_model) -> (batch, seq, num_heads, d_k)
        #                       -> (batch, num_heads, seq, d_k)
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # 3. Scaled dot-product attention for all heads simultaneously
        # Scores: (batch, heads, seq_q, d_k) @ (batch, heads, d_k, seq_k)
        #       = (batch, heads, seq_q, seq_k)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask.unsqueeze(1), float('-inf'))

        weights = F.softmax(scores, dim=-1)
        weights = self.dropout(weights)

        # Weighted sum: (batch, heads, seq_q, seq_k) @ (batch, heads, seq_k, d_k)
        #             = (batch, heads, seq_q, d_k)
        attn_output = torch.matmul(weights, V)

        # 4. Concatenate heads
        # (batch, heads, seq_q, d_k) -> (batch, seq_q, heads, d_k)
        #                             -> (batch, seq_q, d_model)
        attn_output = (
            attn_output.transpose(1, 2)
            .contiguous()
            .view(batch_size, -1, self.d_model)
        )

        # 5. Final linear projection
        output = self.W_o(attn_output)  # (batch, seq_q, d_model)
        return output


# Example
mha = MultiHeadAttention(d_model=512, num_heads=8)
x = torch.randn(2, 10, 512)  # 2 batches, 10 tokens, 512 dims

# Self-attention: Q=K=V=x (attend to yourself)
output = mha(x, x, x)
print(f"Multi-head output: {output.shape}")  # (2, 10, 512)
```

---

## 4. Positional Encoding

### The Problem: Transformers Have No Sense of Order

Unlike RNNs which process tokens sequentially (so position is implicit),
transformers process all tokens **in parallel**. Without positional information,
"The cat sat on the mat" and "mat the on sat cat The" look identical.

### Sinusoidal Positional Encoding

The original transformer uses sine and cosine functions of different frequencies:

```python
class PositionalEncoding(nn.Module):
    """Add positional information to token embeddings.

    Uses sin/cos functions at different frequencies so each position
    gets a unique encoding. Nearby positions have similar encodings.

    Formula:
        PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
        PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        # position: (max_len, 1)

        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        # div_term: (d_model/2,) -- the frequency for each dimension pair

        pe[:, 0::2] = torch.sin(position * div_term)  # Even dimensions: sin
        pe[:, 1::2] = torch.cos(position * div_term)  # Odd dimensions: cos

        # Register as buffer (not a parameter, but saved with model)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input embeddings.

        Args:
            x: Token embeddings, shape (batch, seq_len, d_model)
        """
        x = x + self.pe[:, :x.shape[1], :]
        return self.dropout(x)


# Example
pe = PositionalEncoding(d_model=512)
embeddings = torch.randn(2, 10, 512)
encoded = pe(embeddings)
print(f"With positions: {encoded.shape}")  # (2, 10, 512) -- same shape!
```

**Why sin/cos?**
- Each position gets a unique vector
- Relative positions can be computed as linear transformations
- Generalizes to sequences longer than those seen during training

### Learned Positional Encoding (Alternative)

```python
class LearnedPositionalEncoding(nn.Module):
    """Positional encoding as learnable parameters (used in BERT, GPT)."""

    def __init__(self, d_model: int, max_len: int = 512):
        super().__init__()
        self.pos_embedding = nn.Embedding(max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        positions = torch.arange(x.shape[1], device=x.device)
        return x + self.pos_embedding(positions)

# This is simpler but can't generalize beyond max_len.
# GPT-2 uses this; the original transformer uses sinusoidal.
```

---

## 5. The Transformer Encoder Block

### Components

Each encoder block has two sub-layers:
1. **Multi-Head Self-Attention** (attend to all positions in the sequence)
2. **Position-wise Feed-Forward Network** (two linear layers with ReLU)

Both sub-layers have:
- **Residual connections** (add the input back to the output)
- **Layer normalization** (normalize the result)

```python
class TransformerEncoderBlock(nn.Module):
    """One block of the transformer encoder.

    Structure:
        x -> [Self-Attention] -> Add & LayerNorm -> [FFN] -> Add & LayerNorm -> output
             ^--- residual ---^                      ^--- residual ---^
    """

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int,
        dropout: float = 0.1,
    ):
        super().__init__()
        # Sub-layer 1: Multi-head self-attention
        self.self_attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)

        # Sub-layer 2: Position-wise feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),       # Expand
            nn.ReLU(),                       # Non-linearity
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),        # Contract back
        )
        self.norm2 = nn.LayerNorm(d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(
        self, x: torch.Tensor, mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        # Sub-layer 1: Self-attention with residual + norm
        attn_out = self.self_attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))  # Residual + LayerNorm

        # Sub-layer 2: FFN with residual + norm
        ffn_out = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_out))    # Residual + LayerNorm

        return x


# Example
encoder_block = TransformerEncoderBlock(d_model=512, num_heads=8, d_ff=2048)
x = torch.randn(2, 10, 512)  # (batch, seq_len, d_model)
output = encoder_block(x)
print(f"Encoder block output: {output.shape}")  # (2, 10, 512) -- same shape!
```

### Why These Design Choices?

```
Residual connections:
    - Allow gradients to flow directly through the network
    - Like Swift's ?? operator for gradients -- provides a "default path"
    - Without them, deep transformers (12+ layers) can't train

Layer normalization:
    - Stabilizes training by normalizing activations
    - Applied per-token (normalize across d_model dimension)
    - Different from batch norm: works with any batch size

Feed-forward network:
    - Expands to d_ff (usually 4x d_model), then contracts back
    - Adds non-linear processing capacity at each position
    - Each position is processed independently (no cross-token interaction)
```

---

## 6. The Transformer Decoder Block

### Additional Component: Masked Self-Attention

The decoder has three sub-layers:
1. **Masked Self-Attention** -- attend to previous positions only (can't peek ahead)
2. **Cross-Attention** -- attend to encoder outputs (where to look in the source)
3. **Feed-Forward Network** -- same as encoder

```python
class TransformerDecoderBlock(nn.Module):
    """One block of the transformer decoder.

    Structure:
        x -> [Masked Self-Attn] -> Add & Norm
          -> [Cross-Attn with encoder] -> Add & Norm
          -> [FFN] -> Add & Norm -> output
    """

    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int,
        dropout: float = 0.1,
    ):
        super().__init__()
        # Sub-layer 1: Masked self-attention
        self.masked_self_attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)

        # Sub-layer 2: Cross-attention (decoder attends to encoder output)
        self.cross_attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.norm2 = nn.LayerNorm(d_model)

        # Sub-layer 3: Feed-forward
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )
        self.norm3 = nn.LayerNorm(d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,            # Decoder input
        encoder_output: torch.Tensor, # From encoder
        src_mask: torch.Tensor | None = None,
        tgt_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        # 1. Masked self-attention (can't look at future tokens)
        self_attn = self.masked_self_attention(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(self_attn))

        # 2. Cross-attention (attend to encoder outputs)
        # Query comes from decoder, Key and Value come from encoder
        cross_attn = self.cross_attention(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout(cross_attn))

        # 3. Feed-forward
        ffn_out = self.ffn(x)
        x = self.norm3(x + self.dropout(ffn_out))

        return x


def generate_causal_mask(seq_len: int) -> torch.Tensor:
    """Create a causal (look-ahead) mask for the decoder.

    Returns a boolean mask where True means "DO NOT attend."
    Position i can attend to positions 0..i but not i+1..n.

    Example for seq_len=4:
        [[False,  True,  True,  True],   -- pos 0 sees only pos 0
         [False, False,  True,  True],   -- pos 1 sees pos 0-1
         [False, False, False,  True],   -- pos 2 sees pos 0-2
         [False, False, False, False]]   -- pos 3 sees pos 0-3
    """
    mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
    return mask


# Example
mask = generate_causal_mask(4)
print(mask)
# tensor([[False,  True,  True,  True],
#         [False, False,  True,  True],
#         [False, False, False,  True],
#         [False, False, False, False]])
```

---

## 7. The Full Transformer

### Putting It All Together

```python
class MiniTransformer(nn.Module):
    """A complete (small) transformer for sequence-to-sequence tasks.

    Architecture:
        Source tokens -> Embedding + PosEnc -> N x EncoderBlock
        Target tokens -> Embedding + PosEnc -> N x DecoderBlock -> Linear -> Logits

    This is the architecture from "Attention Is All You Need" (2017).
    """

    def __init__(
        self,
        src_vocab_size: int,
        tgt_vocab_size: int,
        d_model: int = 256,
        num_heads: int = 4,
        num_layers: int = 3,
        d_ff: int = 512,
        max_len: int = 512,
        dropout: float = 0.1,
    ):
        super().__init__()

        # Embeddings
        self.src_embedding = nn.Embedding(src_vocab_size, d_model)
        self.tgt_embedding = nn.Embedding(tgt_vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)

        # Scale embeddings (as in the original paper)
        self.d_model = d_model
        self.scale = math.sqrt(d_model)

        # Encoder stack
        self.encoder_layers = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        # Decoder stack
        self.decoder_layers = nn.ModuleList([
            TransformerDecoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        # Output projection
        self.output_proj = nn.Linear(d_model, tgt_vocab_size)

    def encode(
        self, src: torch.Tensor, src_mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        """Encode source sequence."""
        x = self.pos_encoding(self.src_embedding(src) * self.scale)
        for layer in self.encoder_layers:
            x = layer(x, src_mask)
        return x

    def decode(
        self,
        tgt: torch.Tensor,
        encoder_output: torch.Tensor,
        src_mask: torch.Tensor | None = None,
        tgt_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Decode target sequence given encoder output."""
        x = self.pos_encoding(self.tgt_embedding(tgt) * self.scale)
        for layer in self.decoder_layers:
            x = layer(x, encoder_output, src_mask, tgt_mask)
        return x

    def forward(
        self,
        src: torch.Tensor,  # (batch, src_len)
        tgt: torch.Tensor,  # (batch, tgt_len)
    ) -> torch.Tensor:
        # Create causal mask for decoder
        tgt_mask = generate_causal_mask(tgt.shape[1]).to(tgt.device)

        # Encode
        encoder_output = self.encode(src)

        # Decode
        decoder_output = self.decode(tgt, encoder_output, tgt_mask=tgt_mask)

        # Project to vocabulary
        logits = self.output_proj(decoder_output)
        return logits  # (batch, tgt_len, tgt_vocab_size)


# Example
transformer = MiniTransformer(
    src_vocab_size=1000,
    tgt_vocab_size=800,
    d_model=256,
    num_heads=4,
    num_layers=3,
)

src = torch.randint(0, 1000, (2, 10))  # Source sentences
tgt = torch.randint(0, 800, (2, 15))   # Target sentences
logits = transformer(src, tgt)
print(f"Transformer output: {logits.shape}")  # (2, 15, 800)

# Count parameters
total_params = sum(p.numel() for p in transformer.parameters())
print(f"Total parameters: {total_params:,}")
```

---

## 8. Self-Attention vs Cross-Attention

### The Three Types of Attention in a Transformer

```
1. ENCODER SELF-ATTENTION
   Q, K, V all come from the encoder input
   Each source token attends to ALL other source tokens
   "How does each word in the input relate to every other word?"

2. DECODER SELF-ATTENTION (MASKED)
   Q, K, V all come from the decoder input
   Each target token attends to PREVIOUS target tokens only
   "Given what I've generated so far, what should I focus on?"
   Causal mask prevents cheating (looking at future tokens)

3. CROSS-ATTENTION (ENCODER-DECODER ATTENTION)
   Q comes from the decoder
   K, V come from the encoder output
   "Which parts of the SOURCE should I look at for the NEXT output?"
   This is what connects encoder and decoder
```

```python
# Visualizing self-attention vs cross-attention
# In self-attention:
x = torch.randn(1, 5, 256)  # 5 tokens
self_attn = MultiHeadAttention(256, 4)
out = self_attn(query=x, key=x, value=x)  # Q=K=V=x

# In cross-attention:
decoder_state = torch.randn(1, 3, 256)   # 3 decoder tokens
encoder_output = torch.randn(1, 10, 256)  # 10 encoder tokens
cross_attn = MultiHeadAttention(256, 4)
out = cross_attn(
    query=decoder_state,      # Q from decoder
    key=encoder_output,       # K from encoder
    value=encoder_output,     # V from encoder
)  # Each decoder token attends to all 10 encoder tokens
```

---

## 9. Why Transformers Work

### Key Innovations

**1. Parallelization**
```
RNN:  Must process tokens sequentially: t1 -> t2 -> t3 -> t4
      Training time: O(sequence_length)

Transformer: Processes ALL tokens simultaneously via matrix multiply
             Training time: O(1) with enough parallelism
             This is why GPUs love transformers
```

**2. Long-Range Dependencies**
```
RNN: Token 1 reaches Token 100 after 99 sequential steps
     Gradient must flow through 99 operations (vanishing gradient)

Transformer: Token 1 directly attends to Token 100 in ONE step
             Gradient path length is O(1) regardless of distance
```

**3. Attention as Soft Dictionary Lookup**
```python
# Each head learns a different "lookup function"
# Head 1: "Find the subject of this verb"
# Head 2: "Find the adjective modifying this noun"
# Head 3: "Find tokens with similar meaning"
# Head 4: "Find nearby tokens for local context"

# The network learns WHAT to look up (Q, K projections)
# and WHAT to return (V projection) -- all through gradient descent.
```

**4. The Scaling Secret**
```
Original Transformer (2017): 65M parameters, 6 layers
GPT-2 (2019): 1.5B parameters, 48 layers
GPT-3 (2020): 175B parameters, 96 layers
GPT-4 (2023): Estimated >1T parameters

The architecture scales remarkably well:
- More data + more parameters = better performance (scaling laws)
- No fundamental architecture change needed -- just make it bigger
```

---

## 10. Encoder-Only vs Decoder-Only vs Encoder-Decoder

### Three Flavors of Transformers

| Type | Examples | Self-Attention | Use Case |
|------|----------|---------------|----------|
| **Encoder-only** | BERT, RoBERTa | Bidirectional (see all tokens) | Classification, NER, embeddings |
| **Decoder-only** | GPT, LLaMA | Causal (see only past tokens) | Text generation, chat |
| **Encoder-decoder** | T5, BART, original transformer | Both | Translation, summarization |

```python
# Encoder-only: for understanding tasks
# Every token can attend to every other token
# Output: contextual representations of each token

class TransformerEncoder(nn.Module):
    """Encoder-only transformer (like BERT)."""

    def __init__(self, vocab_size, d_model, num_heads, num_layers, d_ff):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_enc = PositionalEncoding(d_model)
        self.layers = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff)
            for _ in range(num_layers)
        ])

    def forward(self, x):
        x = self.pos_enc(self.embedding(x) * math.sqrt(self.embedding.embedding_dim))
        for layer in self.layers:
            x = layer(x)
        return x  # (batch, seq_len, d_model) -- rich representation of each token


# Decoder-only: for generation tasks
# Each token can only attend to itself and previous tokens
# Output: next-token prediction at each position

class TransformerDecoder(nn.Module):
    """Decoder-only transformer (like GPT)."""

    def __init__(self, vocab_size, d_model, num_heads, num_layers, d_ff):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_enc = PositionalEncoding(d_model)
        self.layers = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff)
            for _ in range(num_layers)
        ])
        # Note: Uses encoder blocks but with causal mask
        self.output = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        mask = generate_causal_mask(x.shape[1]).to(x.device)
        x = self.pos_enc(self.embedding(x) * math.sqrt(self.embedding.embedding_dim))
        for layer in self.layers:
            x = layer(x, mask)
        return self.output(x)  # (batch, seq_len, vocab_size)
```

---

## 11. Summary

### The Transformer Architecture at a Glance

```
INPUT TOKENS
    |
    v
[Token Embedding + Positional Encoding]
    |
    v
=== ENCODER (N layers) ===
    |
    [Multi-Head Self-Attention] ----+
    |                               | (residual)
    [Add & LayerNorm] <-------------+
    |
    [Feed-Forward Network] ---------+
    |                               | (residual)
    [Add & LayerNorm] <-------------+
    |
=== END ENCODER ===
    |
    | (encoder output used as K, V for cross-attention)
    v
=== DECODER (N layers) ===
    |
    [Masked Self-Attention] --------+
    |                               | (residual)
    [Add & LayerNorm] <-------------+
    |
    [Cross-Attention (Q=decoder, K=V=encoder)] ---+
    |                                              | (residual)
    [Add & LayerNorm] <----------------------------+
    |
    [Feed-Forward Network] --------+
    |                               | (residual)
    [Add & LayerNorm] <-------------+
    |
=== END DECODER ===
    |
    v
[Linear + Softmax] --> OUTPUT PROBABILITIES
```

### Key Takeaways

1. **Attention** replaces recurrence -- no more sequential processing bottleneck
2. **Scaled dot-product** attention is just: `softmax(Q @ K^T / sqrt(d_k)) @ V`
3. **Multi-head** attention runs multiple attention functions in parallel to capture different relationships
4. **Positional encoding** injects order information since attention is permutation-invariant
5. **Residual connections + LayerNorm** enable training very deep transformers
6. **Causal masking** in the decoder prevents looking at future tokens during generation
7. The same architecture scales from 65M (original) to 1T+ (GPT-4) parameters

---

## Swift/iOS Connection

| Python/PyTorch | Swift/iOS Equivalent |
|---------------|---------------------|
| `MultiHeadAttention` | Built into Core ML transformer layers |
| Transformer encoder | `NLModel` / `NLEmbedding` backends |
| Token embeddings | `NLEmbedding` word vectors |
| Causal mask | Implicit in generative Core ML models |
| Full transformer | Core ML `.mlpackage` converted from PyTorch |
| Positional encoding | Handled internally by Core ML |

You can convert your PyTorch transformer to Core ML using `coremltools`:
```python
import coremltools as ct

# After training your transformer in PyTorch:
traced = torch.jit.trace(model, example_input)
ml_model = ct.convert(traced, inputs=[ct.TensorType(shape=example_input.shape)])
ml_model.save("MyTransformer.mlpackage")
```
