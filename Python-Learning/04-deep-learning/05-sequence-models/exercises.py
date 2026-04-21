"""
Module 05: Sequence Models (RNNs, LSTMs, GRUs) - Exercises
============================================================
Target audience: Swift developers learning Python and deep learning.

Instructions:
- Fill in each function body (replace `pass` with your solution).
- Run this file to check your work: `python exercises.py`
- All exercises use assert statements for self-checking.
- If no AssertionError is raised, your solution is correct.

Prerequisites:
    pip install torch

Difficulty levels:
  Easy   - Direct application of lesson concepts
  Medium - Requires combining multiple concepts
  Hard   - Requires deeper understanding and implementation skill
"""

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


# =============================================================================
# PART 1: RNN Fundamentals
# =============================================================================

# Exercise 1: Manual RNN Step
# Difficulty: Easy
# Implement a single RNN step: h_t = tanh(W_xh @ x_t + W_hh @ h_{t-1} + b)
def rnn_step(
    x_t: torch.Tensor,      # (batch, input_size)
    h_prev: torch.Tensor,   # (batch, hidden_size)
    W_xh: torch.Tensor,     # (input_size, hidden_size)
    W_hh: torch.Tensor,     # (hidden_size, hidden_size)
    b: torch.Tensor,        # (hidden_size,)
) -> torch.Tensor:
    """Compute a single RNN step and return the new hidden state h_t.

    The formula is: h_t = tanh(x_t @ W_xh + h_prev @ W_hh + b)

    >>> torch.manual_seed(42)
    <torch.._GeneratorImpl object at ...>
    >>> x = torch.randn(2, 4)
    >>> h = torch.zeros(2, 3)
    >>> W_xh = torch.randn(4, 3)
    >>> W_hh = torch.randn(3, 3)
    >>> b = torch.zeros(3)
    >>> result = rnn_step(x, h, W_xh, W_hh, b)
    >>> result.shape
    torch.Size([2, 3])
    """
    pass


# Exercise 2: Unrolled RNN
# Difficulty: Easy
# Process an entire sequence using rnn_step from Exercise 1.
def rnn_forward(
    x: torch.Tensor,        # (batch, seq_len, input_size)
    h_0: torch.Tensor,      # (batch, hidden_size)
    W_xh: torch.Tensor,     # (input_size, hidden_size)
    W_hh: torch.Tensor,     # (hidden_size, hidden_size)
    b: torch.Tensor,        # (hidden_size,)
) -> tuple[torch.Tensor, torch.Tensor]:
    """Process an entire sequence, returning all hidden states and the final one.

    Returns:
        outputs: All hidden states stacked, shape (batch, seq_len, hidden_size)
        h_n: Final hidden state, shape (batch, hidden_size)
    """
    pass


# Exercise 3: RNN Classifier Module
# Difficulty: Medium
# Build an nn.Module that uses nn.RNN for sequence classification.
class RNNClassifier(nn.Module):
    """Classify sequences using a vanilla RNN.

    Architecture:
        1. nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        2. nn.RNN(embed_dim, hidden_dim, batch_first=True)
        3. nn.Linear(hidden_dim, num_classes)

    Forward pass:
        - Embed input tokens
        - Pass through RNN
        - Use the LAST hidden state (h_n) for classification
        - Project to num_classes with the linear layer
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        hidden_dim: int,
        num_classes: int,
    ):
        super().__init__()
        # TODO: Initialize layers
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Token IDs, shape (batch, seq_len)

        Returns:
            logits: Shape (batch, num_classes)
        """
        pass


# =============================================================================
# PART 2: LSTM Implementation
# =============================================================================

# Exercise 4: LSTM Gates
# Difficulty: Medium
# Implement the LSTM gate computations for a single time step.
def lstm_step(
    x_t: torch.Tensor,     # (batch, input_size)
    h_prev: torch.Tensor,  # (batch, hidden_size)
    c_prev: torch.Tensor,  # (batch, hidden_size)
    W: torch.Tensor,       # (input_size + hidden_size, 4 * hidden_size)
    b: torch.Tensor,       # (4 * hidden_size,)
) -> tuple[torch.Tensor, torch.Tensor]:
    """Compute one LSTM step, returning new (h_t, c_t).

    Steps:
        1. Concatenate x_t and h_prev along dim=1
        2. Compute gates = combined @ W + b
        3. Split gates into 4 chunks: i, f, g, o
        4. Apply sigmoid to i, f, o and tanh to g
        5. c_t = f * c_prev + i * g
        6. h_t = o * tanh(c_t)

    Returns:
        h_t: New hidden state (batch, hidden_size)
        c_t: New cell state (batch, hidden_size)
    """
    pass


# Exercise 5: LSTM Sequence Processor
# Difficulty: Medium
# Build a complete LSTM module using nn.LSTM.
class LSTMProcessor(nn.Module):
    """Process sequences with LSTM and return different outputs.

    Architecture:
        - nn.LSTM with given parameters

    The forward method should support returning different outputs
    based on the output_type parameter.
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int = 1,
        bidirectional: bool = False,
    ):
        super().__init__()
        # TODO: Initialize nn.LSTM with batch_first=True
        pass

    def forward(
        self, x: torch.Tensor, output_type: str = "last"
    ) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, input_size)
            output_type: One of:
                - "last": Return final hidden state of last layer (batch, hidden_size * num_directions)
                - "all": Return all hidden states (batch, seq_len, hidden_size * num_directions)
                - "mean": Return mean of all hidden states (batch, hidden_size * num_directions)

        Returns:
            Tensor with shape depending on output_type
        """
        pass


# Exercise 6: Sentiment Classifier with LSTM
# Difficulty: Medium
# Build a complete sentiment analysis model.
class SentimentLSTM(nn.Module):
    """Bidirectional LSTM for binary sentiment classification.

    Architecture:
        1. nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        2. nn.LSTM(embed_dim, hidden_dim, num_layers=2, batch_first=True,
                   dropout=0.3, bidirectional=True)
        3. nn.Dropout(0.5)
        4. nn.Linear(hidden_dim * 2, 1)  -- *2 for bidirectional

    Forward pass:
        - Embed tokens
        - Pack padded sequences using provided lengths
        - Run through LSTM
        - Concatenate final forward and backward hidden states
        - Apply dropout
        - Project to single logit (for binary classification with BCEWithLogitsLoss)
    """

    def __init__(self, vocab_size: int, embed_dim: int, hidden_dim: int):
        super().__init__()
        # TODO: Initialize layers
        pass

    def forward(
        self, x: torch.Tensor, lengths: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            x: Token IDs (batch, max_seq_len)
            lengths: Actual sequence lengths (batch,)

        Returns:
            logits: (batch, 1) -- raw scores (apply sigmoid for probabilities)
        """
        pass


# =============================================================================
# PART 3: GRU and Comparisons
# =============================================================================

# Exercise 7: GRU Step from Scratch
# Difficulty: Medium
# Implement a single GRU step.
def gru_step(
    x_t: torch.Tensor,     # (batch, input_size)
    h_prev: torch.Tensor,  # (batch, hidden_size)
    W_z: nn.Linear,        # Update gate linear layer
    W_r: nn.Linear,        # Reset gate linear layer
    W_h: nn.Linear,        # Candidate hidden state linear layer
) -> torch.Tensor:
    """Compute one GRU step.

    Steps:
        1. combined = cat([x_t, h_prev], dim=1)
        2. z = sigmoid(W_z(combined))        -- update gate
        3. r = sigmoid(W_r(combined))        -- reset gate
        4. combined_reset = cat([x_t, r * h_prev], dim=1)
        5. h_candidate = tanh(W_h(combined_reset))
        6. h_t = (1 - z) * h_prev + z * h_candidate

    Returns:
        h_t: New hidden state (batch, hidden_size)
    """
    pass


# Exercise 8: Compare RNN Architectures
# Difficulty: Easy
# Create and compare parameter counts of RNN, LSTM, and GRU.
def compare_architectures(
    input_size: int, hidden_size: int
) -> dict[str, int]:
    """Count trainable parameters for RNN, LSTM, and GRU.

    Create each model with:
        - nn.RNN(input_size, hidden_size, batch_first=True)
        - nn.LSTM(input_size, hidden_size, batch_first=True)
        - nn.GRU(input_size, hidden_size, batch_first=True)

    Returns:
        Dictionary with keys "rnn", "lstm", "gru" and values as
        total parameter counts.

    >>> counts = compare_architectures(10, 32)
    >>> counts["lstm"] > counts["gru"] > counts["rnn"]
    True
    """
    pass


# =============================================================================
# PART 4: Practical Applications
# =============================================================================

# Exercise 9: Packed Sequence Processing
# Difficulty: Hard
# Process variable-length sequences properly using packing.
def process_packed_sequences(
    sequences: list[torch.Tensor],  # List of tensors with different seq_lens
    lstm: nn.LSTM,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Process variable-length sequences with proper packing.

    Steps:
        1. Determine max length and pad all sequences to that length
        2. Stack into a batch tensor
        3. Record the original lengths
        4. Pack the padded sequences (use enforce_sorted=False)
        5. Process through the LSTM
        6. Unpack and return

    Args:
        sequences: List of tensors, each shape (seq_len_i, input_size)
                   where seq_len_i varies per sequence
        lstm: An nn.LSTM module (batch_first=True)

    Returns:
        padded_output: (batch, max_seq_len, hidden_size) -- unpacked output
        h_n: Final hidden state from the LSTM
    """
    pass


# Exercise 10: Sequence Generator (Character-Level RNN)
# Difficulty: Hard
# Build a character-level sequence generator.
class CharRNN(nn.Module):
    """Character-level language model using LSTM.

    Architecture:
        1. nn.Embedding(vocab_size, embed_dim)
        2. nn.LSTM(embed_dim, hidden_dim, num_layers=num_layers,
                   batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        3. nn.Linear(hidden_dim, vocab_size)

    This model predicts the next character given the previous characters.
    """

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        hidden_dim: int,
        num_layers: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()
        # TODO: Initialize layers
        pass

    def forward(
        self,
        x: torch.Tensor,
        state: tuple[torch.Tensor, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        """
        Args:
            x: Token IDs (batch, seq_len)
            state: Optional (h_0, c_0) for continuing generation

        Returns:
            logits: (batch, seq_len, vocab_size)
            state: (h_n, c_n) for next call
        """
        pass

    def generate(
        self,
        start_token: int,
        max_len: int = 100,
        temperature: float = 1.0,
    ) -> list[int]:
        """Generate a sequence autoregressively.

        Steps:
            1. Start with start_token as input
            2. Get logits from forward pass
            3. Apply temperature scaling: logits / temperature
            4. Sample from softmax distribution
            5. Use sampled token as next input
            6. Repeat for max_len steps

        Args:
            start_token: Integer token ID to start generation
            max_len: Maximum number of tokens to generate
            temperature: Sampling temperature (lower = more deterministic)

        Returns:
            List of generated token IDs (including start_token)
        """
        pass


# Exercise 11: Seq2Seq Encoder-Decoder
# Difficulty: Hard
# Implement a basic sequence-to-sequence model.
class Seq2SeqModel(nn.Module):
    """Sequence-to-sequence model with LSTM encoder and decoder.

    Encoder:
        1. nn.Embedding(src_vocab_size, embed_dim)
        2. nn.LSTM(embed_dim, hidden_dim, batch_first=True)

    Decoder:
        1. nn.Embedding(tgt_vocab_size, embed_dim)
        2. nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        3. nn.Linear(hidden_dim, tgt_vocab_size)

    Forward pass:
        - Embed and encode source sequence
        - Use encoder's final (h, c) as decoder's initial state
        - Embed and decode target sequence
        - Project decoder outputs to target vocabulary
    """

    def __init__(
        self,
        src_vocab_size: int,
        tgt_vocab_size: int,
        embed_dim: int,
        hidden_dim: int,
    ):
        super().__init__()
        # TODO: Initialize encoder and decoder layers
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


# Exercise 12: Training Loop for Sequence Model
# Difficulty: Hard
# Write a training function with gradient clipping and teacher forcing.
def train_sequence_model(
    model: nn.Module,
    data: list[tuple[torch.Tensor, torch.Tensor]],
    num_epochs: int = 5,
    learning_rate: float = 0.001,
    clip_grad_norm: float = 1.0,
) -> list[float]:
    """Train a sequence classification model.

    The model should take token IDs (batch, seq_len) and return
    logits (batch, num_classes).

    Steps for each epoch:
        1. Iterate over data (each item is (input_tokens, label))
        2. Forward pass: logits = model(input_tokens)
        3. Compute cross-entropy loss
        4. Backward pass
        5. Clip gradients using torch.nn.utils.clip_grad_norm_
        6. Optimizer step (use Adam)
        7. Track average loss per epoch

    Args:
        model: A sequence classification model
        data: List of (input_tensor, label_tensor) pairs
              input_tensor: (batch, seq_len) of token IDs
              label_tensor: (batch,) of class indices
        num_epochs: Number of training epochs
        learning_rate: Learning rate for Adam optimizer
        clip_grad_norm: Maximum gradient norm

    Returns:
        List of average losses per epoch
    """
    pass


# =============================================================================
# TESTS
# =============================================================================

def test_exercise_1():
    """Test RNN step."""
    torch.manual_seed(42)
    x = torch.randn(2, 4)
    h = torch.zeros(2, 3)
    W_xh = torch.randn(4, 3)
    W_hh = torch.randn(3, 3)
    b = torch.zeros(3)
    result = rnn_step(x, h, W_xh, W_hh, b)
    assert result.shape == (2, 3), f"Expected shape (2, 3), got {result.shape}"
    # All values should be in [-1, 1] due to tanh
    assert result.abs().max() <= 1.0, "Values should be in [-1, 1] (tanh output)"
    print("Exercise 1 passed!")


def test_exercise_2():
    """Test unrolled RNN forward."""
    torch.manual_seed(42)
    batch, seq_len, input_size, hidden_size = 2, 5, 4, 3
    x = torch.randn(batch, seq_len, input_size)
    h_0 = torch.zeros(batch, hidden_size)
    W_xh = torch.randn(input_size, hidden_size)
    W_hh = torch.randn(hidden_size, hidden_size)
    b = torch.zeros(hidden_size)
    outputs, h_n = rnn_forward(x, h_0, W_xh, W_hh, b)
    assert outputs.shape == (batch, seq_len, hidden_size)
    assert h_n.shape == (batch, hidden_size)
    # Final hidden state should match last output
    assert torch.allclose(outputs[:, -1, :], h_n), "h_n should equal last output"
    print("Exercise 2 passed!")


def test_exercise_3():
    """Test RNN classifier."""
    model = RNNClassifier(vocab_size=100, embed_dim=16, hidden_dim=32, num_classes=5)
    x = torch.randint(0, 100, (4, 10))
    logits = model(x)
    assert logits.shape == (4, 5), f"Expected (4, 5), got {logits.shape}"
    print("Exercise 3 passed!")


def test_exercise_4():
    """Test LSTM step."""
    torch.manual_seed(42)
    batch, input_size, hidden_size = 2, 4, 3
    x_t = torch.randn(batch, input_size)
    h_prev = torch.zeros(batch, hidden_size)
    c_prev = torch.zeros(batch, hidden_size)
    W = torch.randn(input_size + hidden_size, 4 * hidden_size)
    b = torch.zeros(4 * hidden_size)
    h_t, c_t = lstm_step(x_t, h_prev, c_prev, W, b)
    assert h_t.shape == (batch, hidden_size)
    assert c_t.shape == (batch, hidden_size)
    assert h_t.abs().max() <= 1.0, "h_t should be bounded by tanh"
    print("Exercise 4 passed!")


def test_exercise_5():
    """Test LSTM processor."""
    model = LSTMProcessor(input_size=10, hidden_size=32, num_layers=2)
    x = torch.randn(4, 20, 10)

    last = model(x, output_type="last")
    assert last.shape == (4, 32), f"Expected (4, 32), got {last.shape}"

    all_out = model(x, output_type="all")
    assert all_out.shape == (4, 20, 32), f"Expected (4, 20, 32), got {all_out.shape}"

    mean_out = model(x, output_type="mean")
    assert mean_out.shape == (4, 32), f"Expected (4, 32), got {mean_out.shape}"

    # Test bidirectional
    model_bi = LSTMProcessor(input_size=10, hidden_size=32, bidirectional=True)
    last_bi = model_bi(x, output_type="last")
    assert last_bi.shape == (4, 64), f"Expected (4, 64), got {last_bi.shape}"

    print("Exercise 5 passed!")


def test_exercise_6():
    """Test sentiment LSTM."""
    model = SentimentLSTM(vocab_size=1000, embed_dim=64, hidden_dim=128)
    x = torch.randint(1, 1000, (8, 30))
    lengths = torch.randint(10, 30, (8,))
    logits = model(x, lengths)
    assert logits.shape == (8, 1), f"Expected (8, 1), got {logits.shape}"
    print("Exercise 6 passed!")


def test_exercise_7():
    """Test GRU step."""
    torch.manual_seed(42)
    input_size, hidden_size = 4, 3
    W_z = nn.Linear(input_size + hidden_size, hidden_size)
    W_r = nn.Linear(input_size + hidden_size, hidden_size)
    W_h = nn.Linear(input_size + hidden_size, hidden_size)
    x_t = torch.randn(2, input_size)
    h_prev = torch.zeros(2, hidden_size)
    h_t = gru_step(x_t, h_prev, W_z, W_r, W_h)
    assert h_t.shape == (2, hidden_size)
    print("Exercise 7 passed!")


def test_exercise_8():
    """Test architecture comparison."""
    counts = compare_architectures(10, 32)
    assert "rnn" in counts and "lstm" in counts and "gru" in counts
    assert counts["lstm"] > counts["gru"] > counts["rnn"], (
        f"Expected LSTM > GRU > RNN params, got {counts}"
    )
    print(f"Exercise 8 passed! Params: {counts}")


def test_exercise_9():
    """Test packed sequence processing."""
    torch.manual_seed(42)
    sequences = [
        torch.randn(5, 10),   # Length 5
        torch.randn(3, 10),   # Length 3
        torch.randn(8, 10),   # Length 8
    ]
    lstm = nn.LSTM(input_size=10, hidden_size=16, batch_first=True)
    output, h_n = process_packed_sequences(sequences, lstm)
    assert output.shape == (3, 8, 16), f"Expected (3, 8, 16), got {output.shape}"
    print("Exercise 9 passed!")


def test_exercise_10():
    """Test character RNN."""
    model = CharRNN(vocab_size=50, embed_dim=32, hidden_dim=64, num_layers=2)
    x = torch.randint(0, 50, (4, 20))
    logits, state = model(x)
    assert logits.shape == (4, 20, 50), f"Expected (4, 20, 50), got {logits.shape}"
    assert len(state) == 2  # (h_n, c_n)

    # Test generation
    generated = model.generate(start_token=0, max_len=10)
    assert len(generated) == 10, f"Expected 10 tokens, got {len(generated)}"
    assert generated[0] == 0, "First token should be start_token"
    print("Exercise 10 passed!")


def test_exercise_11():
    """Test seq2seq model."""
    model = Seq2SeqModel(
        src_vocab_size=100, tgt_vocab_size=80,
        embed_dim=32, hidden_dim=64,
    )
    src = torch.randint(0, 100, (4, 10))
    tgt = torch.randint(0, 80, (4, 15))
    logits = model(src, tgt)
    assert logits.shape == (4, 15, 80), f"Expected (4, 15, 80), got {logits.shape}"
    print("Exercise 11 passed!")


def test_exercise_12():
    """Test training loop."""
    model = RNNClassifier(vocab_size=50, embed_dim=16, hidden_dim=32, num_classes=3)
    data = [
        (torch.randint(1, 50, (8, 10)), torch.randint(0, 3, (8,)))
        for _ in range(5)
    ]
    losses = train_sequence_model(model, data, num_epochs=3)
    assert len(losses) == 3, f"Expected 3 loss values, got {len(losses)}"
    assert all(isinstance(l, float) for l in losses)
    print(f"Exercise 12 passed! Losses: {losses}")


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
