"""
Solutions for Module 06: Attention and Transformers
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# =============================================================================
# PART 1: Attention Fundamentals
# =============================================================================

# Exercise 1: Dot-Product Attention Scores
def compute_attention_scores(
    Q: torch.Tensor,  # (batch, num_queries, d_k)
    K: torch.Tensor,  # (batch, num_keys, d_k)
) -> torch.Tensor:
    """Compute scaled dot-product attention scores.

    Formula: scores = Q @ K^T / sqrt(d_k)
    """
    d_k = Q.shape[-1]
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    return scores


# Exercise 2: Attention Weights from Scores
def attention_weights(
    scores: torch.Tensor,               # (batch, num_queries, num_keys)
    mask: torch.Tensor | None = None,   # (batch, num_queries, num_keys) bool
) -> torch.Tensor:
    """Convert scores to attention weights via softmax.

    If mask is provided, fill masked positions (True values) with -inf
    BEFORE applying softmax, so they receive ~0 weight.
    """
    if mask is not None:
        # Fill masked positions with large negative values
        scores = scores.masked_fill(mask, float('-inf'))

    weights = F.softmax(scores, dim=-1)

    # Handle NaN values from softmax of all -inf
    weights = torch.nan_to_num(weights, nan=0.0)

    return weights


# Exercise 3: Scaled Dot-Product Attention
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
    scores = compute_attention_scores(Q, K)
    weights = attention_weights(scores, mask)
    output = torch.matmul(weights, V)
    return output, weights


# Exercise 4: Causal (Look-Ahead) Mask
def create_causal_mask(seq_len: int) -> torch.Tensor:
    """Create a causal mask where future positions are masked.

    Returns a boolean tensor where True means "DO NOT attend."
    Position i can only attend to positions 0, 1, ..., i.
    """
    mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
    return mask


# =============================================================================
# PART 2: Multi-Head Attention
# =============================================================================

# Exercise 5: Split into Heads
def split_heads(
    x: torch.Tensor,  # (batch, seq_len, d_model)
    num_heads: int,
) -> torch.Tensor:
    """Split the last dimension into (num_heads, d_k).

    d_k = d_model // num_heads

    Steps:
        1. Reshape: (batch, seq, d_model) -> (batch, seq, num_heads, d_k)
        2. Transpose: (batch, seq, num_heads, d_k) -> (batch, num_heads, seq, d_k)
    """
    batch_size, seq_len, d_model = x.shape
    d_k = d_model // num_heads

    # Reshape: (batch, seq, d_model) -> (batch, seq, num_heads, d_k)
    x = x.reshape(batch_size, seq_len, num_heads, d_k)

    # Transpose: (batch, seq, num_heads, d_k) -> (batch, num_heads, seq, d_k)
    x = x.transpose(1, 2)

    return x


# Exercise 6: Merge Heads
def merge_heads(x: torch.Tensor) -> torch.Tensor:
    """Merge the head dimension back into d_model.

    Steps:
        1. Transpose: (batch, heads, seq, d_k) -> (batch, seq, heads, d_k)
        2. Reshape: (batch, seq, heads, d_k) -> (batch, seq, heads * d_k)
    """
    batch_size, num_heads, seq_len, d_k = x.shape

    # Transpose: (batch, heads, seq, d_k) -> (batch, seq, heads, d_k)
    x = x.transpose(1, 2)

    # Reshape: (batch, seq, heads, d_k) -> (batch, seq, d_model)
    d_model = num_heads * d_k
    x = x.reshape(batch_size, seq_len, d_model)

    return x


# Exercise 7: Multi-Head Attention Module
class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism."""

    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(
        self,
        query: torch.Tensor,   # (batch, seq_q, d_model)
        key: torch.Tensor,     # (batch, seq_k, d_model)
        value: torch.Tensor,   # (batch, seq_k, d_model)
        mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Multi-head attention forward pass.

        Returns:
            output: (batch, seq_q, d_model)
        """
        batch_size = query.shape[0]

        # Project and split into heads
        Q = split_heads(self.W_q(query), self.num_heads)  # (batch, heads, seq_q, d_k)
        K = split_heads(self.W_k(key), self.num_heads)    # (batch, heads, seq_k, d_k)
        V = split_heads(self.W_v(value), self.num_heads)  # (batch, heads, seq_k, d_k)

        # Apply scaled dot-product attention per head
        attn_output, _ = scaled_dot_product_attention(Q, K, V, mask)  # (batch, heads, seq_q, d_k)

        # Merge heads
        output = merge_heads(attn_output)  # (batch, seq_q, d_model)

        # Final projection
        output = self.W_o(output)

        return output


# =============================================================================
# PART 3: Transformer Components
# =============================================================================

# Exercise 8: Positional Encoding
class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding.

    Formula:
        PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
        PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """

    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Create positional encoding
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)

        # Compute the angles
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float)
            * -(math.log(10000.0) / d_model)
        )

        # Apply sin to even indices
        pe[:, 0::2] = torch.sin(position * div_term)

        # Apply cos to odd indices
        if d_model % 2 == 1:
            pe[:, 1::2] = torch.cos(position * div_term[:-1])
        else:
            pe[:, 1::2] = torch.cos(position * div_term)

        # Add batch dimension and register as buffer
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to x and apply dropout.

        Args:
            x: (batch, seq_len, d_model)
        Returns:
            (batch, seq_len, d_model) with positions added
        """
        seq_len = x.shape[1]
        x = x + self.pe[:, :seq_len, :]
        return self.dropout(x)


# Exercise 9: Transformer Encoder Block
class TransformerEncoderBlock(nn.Module):
    """One encoder block: Self-Attention -> Add&Norm -> FFN -> Add&Norm."""

    def __init__(
        self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1
    ):
        super().__init__()

        self.self_attention = MultiHeadAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)

        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )
        self.norm2 = nn.LayerNorm(d_model)

        self.dropout = nn.Dropout(dropout)

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
        # Self-attention with residual connection
        attn_out = self.self_attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))

        # FFN with residual connection
        ffn_out = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_out))

        return x


# Exercise 10: Transformer Decoder Block
class TransformerDecoderBlock(nn.Module):
    """One decoder block: Masked Self-Attn -> Cross-Attn -> FFN."""

    def __init__(
        self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1
    ):
        super().__init__()

        self.masked_self_attention = MultiHeadAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)

        self.cross_attention = MultiHeadAttention(d_model, num_heads)
        self.norm2 = nn.LayerNorm(d_model)

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
        # Masked self-attention
        self_attn = self.masked_self_attention(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(self_attn))

        # Cross-attention
        cross_attn = self.cross_attention(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout(cross_attn))

        # FFN
        ffn_out = self.ffn(x)
        x = self.norm3(x + self.dropout(ffn_out))

        return x


# =============================================================================
# PART 4: Full Mini-Transformer
# =============================================================================

# Exercise 11: Mini Transformer
class MiniTransformer(nn.Module):
    """Complete transformer model."""

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

        self.scale = math.sqrt(d_model)

        self.src_embedding = nn.Embedding(src_vocab_size, d_model)
        self.tgt_embedding = nn.Embedding(tgt_vocab_size, d_model)

        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)

        self.encoder_layers = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        self.decoder_layers = nn.ModuleList([
            TransformerDecoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        self.output_proj = nn.Linear(d_model, tgt_vocab_size)

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
        # Encode source
        src_embedded = self.src_embedding(src) * self.scale
        encoder_output = self.pos_encoding(src_embedded)

        for layer in self.encoder_layers:
            encoder_output = layer(encoder_output)

        # Decode target
        tgt_embedded = self.tgt_embedding(tgt) * self.scale
        decoder_output = self.pos_encoding(tgt_embedded)

        # Create causal mask for target
        tgt_len = tgt.shape[1]
        tgt_mask = create_causal_mask(tgt_len)
        if tgt.device != torch.device('cpu'):
            tgt_mask = tgt_mask.to(tgt.device)

        for layer in self.decoder_layers:
            decoder_output = layer(decoder_output, encoder_output, tgt_mask=tgt_mask)

        # Project to vocabulary
        logits = self.output_proj(decoder_output)

        return logits


# Exercise 12: Encoder-Only Transformer Classifier
class TransformerClassifier(nn.Module):
    """Encoder-only transformer for sequence classification."""

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

        self.scale = math.sqrt(d_model)

        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)

        self.encoder_layers = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        self.classifier = nn.Linear(d_model, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Token IDs (batch, seq_len)
        Returns:
            logits: (batch, num_classes)
        """
        # Embed and positionally encode
        embedded = self.embedding(x) * self.scale
        x = self.pos_encoding(embedded)

        # Pass through encoder layers
        for layer in self.encoder_layers:
            x = layer(x)

        # Global average pooling
        x = x.mean(dim=1)  # (batch, d_model)

        # Classify
        logits = self.classifier(x)

        return logits
