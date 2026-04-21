"""
Module 06: Attention and Transformers - Exercises
==================================================
Target audience: Swift developers learning Python and deep learning.

Instructions:
- Fill in each function/class body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.

Prerequisites:
    pip install torch

Difficulty levels:
  Easy   - Direct application of lesson concepts
  Medium - Requires combining multiple concepts
  Hard   - Requires building complete components from scratch
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# =============================================================================
# PART 1: Attention Fundamentals
# =============================================================================

# Exercise 1: Dot-Product Attention Scores
# Difficulty: Easy
# Compute raw attention scores between queries and keys.
def compute_attention_scores(
    Q: torch.Tensor,  # (batch, num_queries, d_k)
    K: torch.Tensor,  # (batch, num_keys, d_k)
) -> torch.Tensor:
    """Compute scaled dot-product attention scores.

    Formula: scores = Q @ K^T / sqrt(d_k)

    Returns:
        scores: (batch, num_queries, num_keys)

    >>> Q = torch.ones(1, 2, 4)
    >>> K = torch.ones(1, 3, 4)
    >>> scores = compute_attention_scores(Q, K)
    >>> scores.shape
    torch.Size([1, 2, 3])
    """
    pass


# Exercise 2: Attention Weights from Scores
# Difficulty: Easy
# Convert attention scores to weights using softmax, with optional masking.
def attention_weights(
    scores: torch.Tensor,               # (batch, num_queries, num_keys)
    mask: torch.Tensor | None = None,   # (batch, num_queries, num_keys) bool
) -> torch.Tensor:
    """Convert scores to attention weights via softmax.

    If mask is provided, fill masked positions (True values) with -inf
    BEFORE applying softmax, so they receive ~0 weight.

    Returns:
        weights: (batch, num_queries, num_keys) -- each row sums to 1.0

    >>> scores = torch.tensor([[[1.0, 2.0, 3.0]]])
    >>> w = attention_weights(scores)
    >>> w.sum(dim=-1).item()  # Should be ~1.0
    1.0
    """
    pass


# Exercise 3: Scaled Dot-Product Attention
# Difficulty: Medium
# Implement complete scaled dot-product attention.
def scaled_dot_product_attention(
    Q: torch.Tensor,  # (batch, num_queries, d_k)
    K: torch.Tensor,  # (batch, num_keys, d_k)
    V: torch.Tensor,  # (batch, num_keys, d_v)
    mask: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Complete scaled dot-product attention.

    Steps:
        1. Compute scores = Q @ K^T / sqrt(d_k)
        2. Apply mask (if provided): scores[mask] = -inf
        3. weights = softmax(scores, dim=-1)
        4. output = weights @ V

    Returns:
        output: (batch, num_queries, d_v)
        weights: (batch, num_queries, num_keys)
    """
    pass


# Exercise 4: Causal (Look-Ahead) Mask
# Difficulty: Easy
# Generate a causal mask for autoregressive decoding.
def create_causal_mask(seq_len: int) -> torch.Tensor:
    """Create a causal mask where future positions are masked.

    Returns a boolean tensor where True means "DO NOT attend."
    Position i can only attend to positions 0, 1, ..., i.

    Args:
        seq_len: Length of the sequence

    Returns:
        mask: (seq_len, seq_len) boolean tensor

    >>> mask = create_causal_mask(3)
    >>> mask
    tensor([[False,  True,  True],
            [False, False,  True],
            [False, False, False]])
    """
    pass


# =============================================================================
# PART 2: Multi-Head Attention
# =============================================================================

# Exercise 5: Split into Heads
# Difficulty: Medium
# Reshape a tensor from (batch, seq, d_model) to (batch, heads, seq, d_k).
def split_heads(
    x: torch.Tensor,  # (batch, seq_len, d_model)
    num_heads: int,
) -> torch.Tensor:
    """Split the last dimension into (num_heads, d_k).

    d_k = d_model // num_heads

    Steps:
        1. Reshape: (batch, seq, d_model) -> (batch, seq, num_heads, d_k)
        2. Transpose: (batch, seq, num_heads, d_k) -> (batch, num_heads, seq, d_k)

    Returns:
        (batch, num_heads, seq_len, d_k)

    >>> x = torch.randn(2, 10, 512)
    >>> split_heads(x, 8).shape
    torch.Size([2, 8, 10, 64])
    """
    pass


# Exercise 6: Merge Heads
# Difficulty: Medium
# Reverse of split_heads: (batch, heads, seq, d_k) -> (batch, seq, d_model).
def merge_heads(x: torch.Tensor) -> torch.Tensor:
    """Merge the head dimension back into d_model.

    Steps:
        1. Transpose: (batch, heads, seq, d_k) -> (batch, seq, heads, d_k)
        2. Reshape: (batch, seq, heads, d_k) -> (batch, seq, heads * d_k)

    Returns:
        (batch, seq_len, d_model)

    >>> x = torch.randn(2, 8, 10, 64)
    >>> merge_heads(x).shape
    torch.Size([2, 10, 512])
    """
    pass


# Exercise 7: Multi-Head Attention Module
# Difficulty: Hard
# Implement the full multi-head attention as an nn.Module.
class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism.

    Architecture:
        1. Project Q, K, V with separate nn.Linear(d_model, d_model)
        2. Split into num_heads using split_heads()
        3. Apply scaled_dot_product_attention() per head
        4. Merge heads using merge_heads()
        5. Final projection with nn.Linear(d_model, d_model)

    Attributes to create in __init__:
        - self.W_q: nn.Linear(d_model, d_model)
        - self.W_k: nn.Linear(d_model, d_model)
        - self.W_v: nn.Linear(d_model, d_model)
        - self.W_o: nn.Linear(d_model, d_model)
        - self.num_heads: int
        - self.d_k: int = d_model // num_heads
    """

    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        # TODO: Initialize projections
        pass

    def forward(
        self,
        query: torch.Tensor,   # (batch, seq_q, d_model)
        key: torch.Tensor,     # (batch, seq_k, d_model)
        value: torch.Tensor,   # (batch, seq_k, d_model)
        mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Returns:
            output: (batch, seq_q, d_model)
        """
        pass


# =============================================================================
# PART 3: Transformer Components
# =============================================================================

# Exercise 8: Positional Encoding
# Difficulty: Medium
# Implement sinusoidal positional encoding.
class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding.

    Formula:
        PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
        PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

    Steps in __init__:
        1. Create a (max_len, d_model) tensor of zeros
        2. Create position indices: (max_len, 1)
        3. Create div_term = exp(arange(0, d_model, 2) * -log(10000) / d_model)
        4. Fill even columns with sin(position * div_term)
        5. Fill odd columns with cos(position * div_term)
        6. Add batch dimension and register as buffer

    Forward: Add positional encoding to input, then apply dropout.
    """

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        # TODO: Create and register positional encoding buffer
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to x and apply dropout.

        Args:
            x: (batch, seq_len, d_model)
        Returns:
            (batch, seq_len, d_model) with positions added
        """
        pass


# Exercise 9: Transformer Encoder Block
# Difficulty: Hard
# Implement a single transformer encoder block.
class TransformerEncoderBlock(nn.Module):
    """One encoder block: Self-Attention -> Add&Norm -> FFN -> Add&Norm.

    Architecture:
        1. self.self_attention = MultiHeadAttention(d_model, num_heads)
        2. self.norm1 = nn.LayerNorm(d_model)
        3. self.ffn = nn.Sequential(
               nn.Linear(d_model, d_ff),
               nn.ReLU(),
               nn.Dropout(dropout),
               nn.Linear(d_ff, d_model),
           )
        4. self.norm2 = nn.LayerNorm(d_model)
        5. self.dropout = nn.Dropout(dropout)

    Forward:
        attn_out = self_attention(x, x, x, mask)
        x = norm1(x + dropout(attn_out))
        ffn_out = ffn(x)
        x = norm2(x + dropout(ffn_out))
        return x
    """

    def __init__(
        self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1
    ):
        super().__init__()
        # TODO: Initialize layers
        pass

    def forward(
        self, x: torch.Tensor, mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, d_model)
            mask: Optional attention mask
        Returns:
            (batch, seq_len, d_model)
        """
        pass


# Exercise 10: Transformer Decoder Block
# Difficulty: Hard
# Implement a single transformer decoder block.
class TransformerDecoderBlock(nn.Module):
    """One decoder block: Masked Self-Attn -> Cross-Attn -> FFN.

    Architecture:
        1. self.masked_self_attention = MultiHeadAttention(d_model, num_heads)
        2. self.norm1 = nn.LayerNorm(d_model)
        3. self.cross_attention = MultiHeadAttention(d_model, num_heads)
        4. self.norm2 = nn.LayerNorm(d_model)
        5. self.ffn = nn.Sequential(
               nn.Linear(d_model, d_ff),
               nn.ReLU(),
               nn.Dropout(dropout),
               nn.Linear(d_ff, d_model),
           )
        6. self.norm3 = nn.LayerNorm(d_model)
        7. self.dropout = nn.Dropout(dropout)

    Forward:
        # Masked self-attention
        self_attn = masked_self_attention(x, x, x, tgt_mask)
        x = norm1(x + dropout(self_attn))
        # Cross-attention
        cross_attn = cross_attention(x, encoder_output, encoder_output, src_mask)
        x = norm2(x + dropout(cross_attn))
        # FFN
        ffn_out = ffn(x)
        x = norm3(x + dropout(ffn_out))
    """

    def __init__(
        self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1
    ):
        super().__init__()
        # TODO: Initialize layers
        pass

    def forward(
        self,
        x: torch.Tensor,
        encoder_output: torch.Tensor,
        src_mask: torch.Tensor | None = None,
        tgt_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Args:
            x: Decoder input (batch, tgt_len, d_model)
            encoder_output: Encoder output (batch, src_len, d_model)
            src_mask: Mask for encoder output
            tgt_mask: Causal mask for decoder self-attention
        Returns:
            (batch, tgt_len, d_model)
        """
        pass


# =============================================================================
# PART 4: Full Mini-Transformer
# =============================================================================

# Exercise 11: Mini Transformer
# Difficulty: Hard
# Assemble a complete transformer for sequence-to-sequence tasks.
class MiniTransformer(nn.Module):
    """Complete transformer model.

    Architecture:
        - src_embedding: nn.Embedding(src_vocab_size, d_model)
        - tgt_embedding: nn.Embedding(tgt_vocab_size, d_model)
        - pos_encoding: PositionalEncoding(d_model, max_len, dropout)
        - encoder_layers: nn.ModuleList of TransformerEncoderBlock
        - decoder_layers: nn.ModuleList of TransformerDecoderBlock
        - output_proj: nn.Linear(d_model, tgt_vocab_size)
        - self.scale = math.sqrt(d_model)

    Forward:
        1. Embed + positional encode source: pos_enc(src_embed(src) * scale)
        2. Pass through all encoder layers
        3. Create causal mask for target
        4. Embed + positional encode target: pos_enc(tgt_embed(tgt) * scale)
        5. Pass through all decoder layers (with encoder output and masks)
        6. Project to vocabulary with output_proj
    """

    def __init__(
        self,
        src_vocab_size: int,
        tgt_vocab_size: int,
        d_model: int = 256,
        num_heads: int = 4,
        num_layers: int = 2,
        d_ff: int = 512,
        max_len: int = 512,
        dropout: float = 0.1,
    ):
        super().__init__()
        # TODO: Initialize all components
        pass

    def forward(
        self, src: torch.Tensor, tgt: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            src: Source token IDs (batch, src_len)
            tgt: Target token IDs (batch, tgt_len)
        Returns:
            logits: (batch, tgt_len, tgt_vocab_size)
        """
        pass


# Exercise 12: Encoder-Only Transformer Classifier
# Difficulty: Medium
# Build a BERT-style classifier using only the encoder.
class TransformerClassifier(nn.Module):
    """Encoder-only transformer for sequence classification.

    Architecture:
        - embedding: nn.Embedding(vocab_size, d_model, padding_idx=0)
        - pos_encoding: PositionalEncoding(d_model, max_len, dropout)
        - encoder_layers: nn.ModuleList of TransformerEncoderBlock
        - classifier: nn.Linear(d_model, num_classes)
        - self.scale = math.sqrt(d_model)

    Forward:
        1. Embed + positional encode input
        2. Pass through all encoder layers
        3. Pool: take the mean of all token representations (dim=1)
        4. Classify with the linear layer
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        num_heads: int,
        num_layers: int,
        d_ff: int,
        num_classes: int,
        max_len: int = 512,
        dropout: float = 0.1,
    ):
        super().__init__()
        # TODO: Initialize components
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Token IDs (batch, seq_len)
        Returns:
            logits: (batch, num_classes)
        """
        pass


# =============================================================================
# TESTS
# =============================================================================

def test_exercise_1():
    """Test attention scores computation."""
    Q = torch.ones(1, 2, 4)
    K = torch.ones(1, 3, 4)
    scores = compute_attention_scores(Q, K)
    assert scores.shape == (1, 2, 3), f"Expected (1, 2, 3), got {scores.shape}"
    # With all-ones, Q@K^T = d_k for each entry, scaled = d_k/sqrt(d_k) = sqrt(d_k)
    expected_val = math.sqrt(4.0)
    assert torch.allclose(scores, torch.full_like(scores, expected_val), atol=1e-5), \
        f"Expected all values to be {expected_val}"
    print("Exercise 1 passed!")


def test_exercise_2():
    """Test attention weights."""
    scores = torch.tensor([[[1.0, 2.0, 3.0]]])
    w = attention_weights(scores)
    assert w.shape == (1, 1, 3)
    assert torch.allclose(w.sum(dim=-1), torch.ones(1, 1), atol=1e-5)

    # Test with mask
    mask = torch.tensor([[[False, False, True]]])
    w_masked = attention_weights(scores, mask)
    assert w_masked[0, 0, 2].item() < 1e-6, "Masked position should have ~0 weight"
    assert torch.allclose(w_masked.sum(dim=-1), torch.ones(1, 1), atol=1e-5)
    print("Exercise 2 passed!")


def test_exercise_3():
    """Test scaled dot-product attention."""
    torch.manual_seed(42)
    Q = torch.randn(2, 3, 64)
    K = torch.randn(2, 5, 64)
    V = torch.randn(2, 5, 64)
    output, weights = scaled_dot_product_attention(Q, K, V)
    assert output.shape == (2, 3, 64), f"Expected (2, 3, 64), got {output.shape}"
    assert weights.shape == (2, 3, 5), f"Expected (2, 3, 5), got {weights.shape}"
    assert torch.allclose(weights.sum(dim=-1), torch.ones(2, 3), atol=1e-5)
    print("Exercise 3 passed!")


def test_exercise_4():
    """Test causal mask generation."""
    mask = create_causal_mask(4)
    assert mask.shape == (4, 4)
    assert mask.dtype == torch.bool
    # Diagonal and below should be False (allowed)
    assert not mask[0, 0].item()
    assert not mask[2, 1].item()
    assert not mask[3, 3].item()
    # Above diagonal should be True (masked)
    assert mask[0, 1].item()
    assert mask[1, 3].item()
    print("Exercise 4 passed!")


def test_exercise_5():
    """Test split_heads."""
    x = torch.randn(2, 10, 512)
    out = split_heads(x, 8)
    assert out.shape == (2, 8, 10, 64), f"Expected (2, 8, 10, 64), got {out.shape}"
    print("Exercise 5 passed!")


def test_exercise_6():
    """Test merge_heads."""
    x = torch.randn(2, 8, 10, 64)
    out = merge_heads(x)
    assert out.shape == (2, 10, 512), f"Expected (2, 10, 512), got {out.shape}"

    # Round-trip test
    original = torch.randn(2, 10, 512)
    assert torch.allclose(merge_heads(split_heads(original, 8)), original)
    print("Exercise 6 passed!")


def test_exercise_7():
    """Test multi-head attention."""
    mha = MultiHeadAttention(d_model=256, num_heads=4)
    x = torch.randn(2, 10, 256)
    output = mha(x, x, x)  # Self-attention
    assert output.shape == (2, 10, 256), f"Expected (2, 10, 256), got {output.shape}"

    # Cross-attention
    q = torch.randn(2, 5, 256)
    kv = torch.randn(2, 8, 256)
    output = mha(q, kv, kv)
    assert output.shape == (2, 5, 256)
    print("Exercise 7 passed!")


def test_exercise_8():
    """Test positional encoding."""
    pe = PositionalEncoding(d_model=512, max_len=100)
    x = torch.zeros(2, 10, 512)
    encoded = pe(x)
    assert encoded.shape == (2, 10, 512)
    # If input is zeros, output should be just the positional encoding
    # (plus dropout, so we test in eval mode)
    pe.eval()
    encoded = pe(torch.zeros(1, 10, 512))
    # Different positions should have different encodings
    assert not torch.allclose(encoded[0, 0], encoded[0, 1], atol=1e-5), \
        "Different positions should have different encodings"
    print("Exercise 8 passed!")


def test_exercise_9():
    """Test transformer encoder block."""
    block = TransformerEncoderBlock(d_model=256, num_heads=4, d_ff=512)
    x = torch.randn(2, 10, 256)
    output = block(x)
    assert output.shape == (2, 10, 256), f"Expected (2, 10, 256), got {output.shape}"
    print("Exercise 9 passed!")


def test_exercise_10():
    """Test transformer decoder block."""
    block = TransformerDecoderBlock(d_model=256, num_heads=4, d_ff=512)
    x = torch.randn(2, 8, 256)
    enc_out = torch.randn(2, 12, 256)
    tgt_mask = create_causal_mask(8)
    output = block(x, enc_out, tgt_mask=tgt_mask)
    assert output.shape == (2, 8, 256), f"Expected (2, 8, 256), got {output.shape}"
    print("Exercise 10 passed!")


def test_exercise_11():
    """Test mini transformer."""
    model = MiniTransformer(
        src_vocab_size=100, tgt_vocab_size=80,
        d_model=64, num_heads=4, num_layers=2, d_ff=128,
    )
    src = torch.randint(0, 100, (2, 10))
    tgt = torch.randint(0, 80, (2, 8))
    logits = model(src, tgt)
    assert logits.shape == (2, 8, 80), f"Expected (2, 8, 80), got {logits.shape}"

    # Verify parameter count is reasonable
    params = sum(p.numel() for p in model.parameters())
    assert params > 0, "Model should have parameters"
    print(f"Exercise 11 passed! ({params:,} parameters)")


def test_exercise_12():
    """Test transformer classifier."""
    model = TransformerClassifier(
        vocab_size=500, d_model=128, num_heads=4,
        num_layers=2, d_ff=256, num_classes=5,
    )
    x = torch.randint(1, 500, (4, 20))
    logits = model(x)
    assert logits.shape == (4, 5), f"Expected (4, 5), got {logits.shape}"
    print("Exercise 12 passed!")


if __name__ == "__main__":
    tests = [
        test_exercise_1, test_exercise_2, test_exercise_3,
        test_exercise_4, test_exercise_5, test_exercise_6,
        test_exercise_7, test_exercise_8, test_exercise_9,
        test_exercise_10, test_exercise_11, test_exercise_12,
    ]

    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAILED: {test.__name__}: {e}")

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(tests)} exercises passed")
