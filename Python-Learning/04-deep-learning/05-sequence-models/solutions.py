"""
Module 05: Sequence Models (RNNs, LSTMs, GRUs) - Solutions
============================================================
Complete solutions for all exercises with explanations.

Run this file to verify all solutions pass: `python solutions.py`
"""

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


# =============================================================================
# PART 1: RNN Fundamentals
# =============================================================================

# Exercise 1: Manual RNN Step
# Difficulty: Easy
def rnn_step(
    x_t: torch.Tensor,
    h_prev: torch.Tensor,
    W_xh: torch.Tensor,
    W_hh: torch.Tensor,
    b: torch.Tensor,
) -> torch.Tensor:
    """Compute a single RNN step: h_t = tanh(x_t @ W_xh + h_prev @ W_hh + b)."""
    # This is the fundamental RNN equation.
    # x_t @ W_xh transforms the input into hidden space.
    # h_prev @ W_hh transforms the previous state.
    # Adding them + bias, then tanh squashes to [-1, 1].
    return torch.tanh(x_t @ W_xh + h_prev @ W_hh + b)

    # Note: PyTorch's nn.RNN does essentially this, but with optimized
    # CUDA kernels and support for multiple layers / bidirectional.


# Exercise 2: Unrolled RNN
# Difficulty: Easy
def rnn_forward(
    x: torch.Tensor,
    h_0: torch.Tensor,
    W_xh: torch.Tensor,
    W_hh: torch.Tensor,
    b: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Process an entire sequence by looping over time steps."""
    batch, seq_len, _ = x.shape
    h = h_0
    outputs = []

    for t in range(seq_len):
        # Apply rnn_step at each time step
        h = rnn_step(x[:, t, :], h, W_xh, W_hh, b)
        outputs.append(h)

    # Stack list of (batch, hidden) into (batch, seq_len, hidden)
    outputs = torch.stack(outputs, dim=1)
    return outputs, h

    # Note: This is exactly what PyTorch does internally for nn.RNN.
    # The "unrolled" loop through time is why these are called
    # "recurrent" -- the same weights are applied recurrently.


# Exercise 3: RNN Classifier Module
# Difficulty: Medium
class RNNClassifier(nn.Module):
    """Classify sequences using a vanilla RNN."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        hidden_dim: int,
        num_classes: int,
    ):
        super().__init__()
        # Embedding turns token IDs into dense vectors
        # padding_idx=0 means token 0 always maps to zero vector
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len) of token IDs
        embedded = self.embedding(x)       # (batch, seq_len, embed_dim)
        _, h_n = self.rnn(embedded)        # h_n: (1, batch, hidden_dim)
        h_n = h_n.squeeze(0)              # (batch, hidden_dim)
        logits = self.fc(h_n)             # (batch, num_classes)
        return logits

        # Why use h_n (final hidden state) instead of all outputs?
        # For classification, we want a single vector summarizing
        # the entire sequence. h_n is the RNN's "summary."
        # This is like using the last element of a reduce() in Swift.


# =============================================================================
# PART 2: LSTM Implementation
# =============================================================================

# Exercise 4: LSTM Gates
# Difficulty: Medium
def lstm_step(
    x_t: torch.Tensor,
    h_prev: torch.Tensor,
    c_prev: torch.Tensor,
    W: torch.Tensor,
    b: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Compute one LSTM step."""
    # 1. Concatenate input and hidden state
    combined = torch.cat([x_t, h_prev], dim=1)  # (batch, input+hidden)

    # 2. Single matrix multiply for all gates (efficiency trick)
    gates = combined @ W + b  # (batch, 4 * hidden_size)

    # 3. Split into four equal chunks
    hidden_size = h_prev.shape[1]
    i, f, g, o = gates.split(hidden_size, dim=1)

    # 4. Apply activations
    i = torch.sigmoid(i)  # Input gate: what to write
    f = torch.sigmoid(f)  # Forget gate: what to erase
    g = torch.tanh(g)     # Candidate values: what to write
    o = torch.sigmoid(o)  # Output gate: what to reveal

    # 5. Update cell state
    # f * c_prev: selectively forget old information
    # i * g: selectively add new information
    c_t = f * c_prev + i * g

    # 6. Compute hidden state
    # o * tanh(c_t): selectively output from cell state
    h_t = o * torch.tanh(c_t)

    return h_t, c_t

    # Key insight: c_t only involves element-wise operations on c_prev
    # (multiply by f, add i*g). No weight matrix multiply on c_prev!
    # This is the "gradient highway" that prevents vanishing gradients.


# Exercise 5: LSTM Sequence Processor
# Difficulty: Medium
class LSTMProcessor(nn.Module):
    """Process sequences with LSTM and return different outputs."""

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int = 1,
        bidirectional: bool = False,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
        )
        self.bidirectional = bidirectional
        self.hidden_size = hidden_size

    def forward(
        self, x: torch.Tensor, output_type: str = "last"
    ) -> torch.Tensor:
        outputs, (h_n, c_n) = self.lstm(x)
        # outputs: (batch, seq_len, hidden * num_directions)
        # h_n: (num_layers * num_directions, batch, hidden)

        if output_type == "all":
            return outputs

        elif output_type == "mean":
            # Average all time steps
            return outputs.mean(dim=1)

        elif output_type == "last":
            # Get final hidden state from last layer
            if self.bidirectional:
                # Concatenate forward and backward final hidden states
                h_forward = h_n[-2]   # Last layer, forward direction
                h_backward = h_n[-1]  # Last layer, backward direction
                return torch.cat([h_forward, h_backward], dim=1)
            else:
                return h_n[-1]  # Last layer hidden state

        else:
            raise ValueError(f"Unknown output_type: {output_type}")

        # Which output_type to use?
        # - "last": Most common for classification (final summary)
        # - "all": For sequence labeling (need output at every position)
        # - "mean": Robust alternative to "last" (less sensitive to final token)


# Exercise 6: Sentiment Classifier with LSTM
# Difficulty: Medium
class SentimentLSTM(nn.Module):
    """Bidirectional LSTM for binary sentiment classification."""

    def __init__(self, vocab_size: int, embed_dim: int, hidden_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=0.3,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(hidden_dim * 2, 1)  # *2 for bidirectional

    def forward(
        self, x: torch.Tensor, lengths: torch.Tensor
    ) -> torch.Tensor:
        # 1. Embed tokens
        embedded = self.embedding(x)  # (batch, seq_len, embed_dim)

        # 2. Pack sequences to handle variable lengths efficiently
        packed = pack_padded_sequence(
            embedded, lengths.cpu(),
            batch_first=True,
            enforce_sorted=False,  # Don't require pre-sorted input
        )

        # 3. LSTM forward pass
        _, (h_n, _) = self.lstm(packed)
        # h_n: (num_layers * 2, batch, hidden_dim)
        # We want the last layer's forward and backward states

        # 4. Concatenate final hidden states from both directions
        # h_n[-2] = last layer forward, h_n[-1] = last layer backward
        h_forward = h_n[-2]   # (batch, hidden_dim)
        h_backward = h_n[-1]  # (batch, hidden_dim)
        hidden = torch.cat([h_forward, h_backward], dim=1)  # (batch, hidden*2)

        # 5. Dropout + classification
        hidden = self.dropout(hidden)
        logits = self.fc(hidden)  # (batch, 1)
        return logits

        # For training: use nn.BCEWithLogitsLoss (includes sigmoid)
        # For inference: apply torch.sigmoid(logits) > 0.5


# =============================================================================
# PART 3: GRU and Comparisons
# =============================================================================

# Exercise 7: GRU Step from Scratch
# Difficulty: Medium
def gru_step(
    x_t: torch.Tensor,
    h_prev: torch.Tensor,
    W_z: nn.Linear,
    W_r: nn.Linear,
    W_h: nn.Linear,
) -> torch.Tensor:
    """Compute one GRU step."""
    # Concatenate input and previous hidden state
    combined = torch.cat([x_t, h_prev], dim=1)

    # Update gate: how much of the new state to use
    z = torch.sigmoid(W_z(combined))

    # Reset gate: how much of the old state to consider when computing candidate
    r = torch.sigmoid(W_r(combined))

    # Candidate hidden state: computed using reset-gated previous state
    combined_reset = torch.cat([x_t, r * h_prev], dim=1)
    h_candidate = torch.tanh(W_h(combined_reset))

    # Final hidden state: interpolation between old and candidate
    # z=1 -> completely new, z=0 -> completely old
    h_t = (1 - z) * h_prev + z * h_candidate

    return h_t

    # GRU vs LSTM comparison:
    # GRU: 2 gates (update, reset), no cell state
    # LSTM: 3 gates (input, forget, output), separate cell state
    # GRU typically performs similarly with fewer parameters.


# Exercise 8: Compare RNN Architectures
# Difficulty: Easy
def compare_architectures(
    input_size: int, hidden_size: int
) -> dict[str, int]:
    """Count trainable parameters for RNN, LSTM, and GRU."""
    rnn = nn.RNN(input_size, hidden_size, batch_first=True)
    lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
    gru = nn.GRU(input_size, hidden_size, batch_first=True)

    def count_params(model: nn.Module) -> int:
        return sum(p.numel() for p in model.parameters() if p.requires_grad)

    return {
        "rnn": count_params(rnn),
        "lstm": count_params(lstm),
        "gru": count_params(gru),
    }

    # Expected ratio: LSTM ~4x RNN, GRU ~3x RNN
    # RNN has 1 gate, LSTM has 4 gates, GRU has 3 gates
    # Each "gate" requires weights for input and hidden state + bias


# =============================================================================
# PART 4: Practical Applications
# =============================================================================

# Exercise 9: Packed Sequence Processing
# Difficulty: Hard
def process_packed_sequences(
    sequences: list[torch.Tensor],
    lstm: nn.LSTM,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Process variable-length sequences with proper packing."""
    # 1. Find max length
    max_len = max(seq.shape[0] for seq in sequences)
    input_size = sequences[0].shape[1]
    batch_size = len(sequences)

    # 2. Pad sequences and record lengths
    padded = torch.zeros(batch_size, max_len, input_size)
    lengths = []
    for i, seq in enumerate(sequences):
        seq_len = seq.shape[0]
        padded[i, :seq_len, :] = seq
        lengths.append(seq_len)
    lengths = torch.tensor(lengths)

    # 3. Pack padded sequences
    packed = pack_padded_sequence(
        padded, lengths,
        batch_first=True,
        enforce_sorted=False,  # Handles arbitrary ordering
    )

    # 4. Process through LSTM
    packed_output, (h_n, c_n) = lstm(packed)

    # 5. Unpack
    output, _ = pad_packed_sequence(packed_output, batch_first=True)

    return output, h_n

    # Why pack/unpack?
    # Without packing, the LSTM processes padding tokens as real input,
    # which wastes computation and can hurt performance.
    # Packing tells the LSTM exactly which positions are real data.


# Exercise 10: Sequence Generator (Character-Level RNN)
# Difficulty: Hard
class CharRNN(nn.Module):
    """Character-level language model using LSTM."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        hidden_dim: int,
        num_layers: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.fc = nn.Linear(hidden_dim, vocab_size)
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

    def forward(
        self,
        x: torch.Tensor,
        state: tuple[torch.Tensor, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        embedded = self.embedding(x)              # (batch, seq_len, embed_dim)
        output, state = self.lstm(embedded, state) # (batch, seq_len, hidden_dim)
        logits = self.fc(output)                   # (batch, seq_len, vocab_size)
        return logits, state

        # The model predicts the next token at each position.
        # During training: input = [a, b, c, d], target = [b, c, d, e]
        # The loss is computed between logits and shifted targets.

    def generate(
        self,
        start_token: int,
        max_len: int = 100,
        temperature: float = 1.0,
    ) -> list[int]:
        """Generate a sequence autoregressively."""
        self.eval()
        generated = [start_token]
        state = None

        with torch.no_grad():
            # Start with the initial token
            x = torch.tensor([[start_token]])  # (1, 1)

            for _ in range(max_len - 1):
                logits, state = self.forward(x, state)
                # logits: (1, 1, vocab_size)

                # Apply temperature: higher = more random, lower = more greedy
                logits = logits[:, -1, :] / temperature  # (1, vocab_size)

                # Sample from the distribution
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)  # (1, 1)

                generated.append(next_token.item())
                x = next_token  # Feed back as next input

        self.train()
        return generated

        # Temperature explained:
        # temp = 1.0: standard sampling from learned distribution
        # temp < 1.0: sharper distribution (more deterministic)
        # temp > 1.0: flatter distribution (more random/creative)
        # temp -> 0: equivalent to argmax (greedy decoding)


# Exercise 11: Seq2Seq Encoder-Decoder
# Difficulty: Hard
class Seq2SeqModel(nn.Module):
    """Sequence-to-sequence model with LSTM encoder and decoder."""

    def __init__(
        self,
        src_vocab_size: int,
        tgt_vocab_size: int,
        embed_dim: int,
        hidden_dim: int,
    ):
        super().__init__()
        # Encoder components
        self.encoder_embed = nn.Embedding(src_vocab_size, embed_dim)
        self.encoder = nn.LSTM(embed_dim, hidden_dim, batch_first=True)

        # Decoder components
        self.decoder_embed = nn.Embedding(tgt_vocab_size, embed_dim)
        self.decoder = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.output_proj = nn.Linear(hidden_dim, tgt_vocab_size)

    def forward(
        self, src: torch.Tensor, tgt: torch.Tensor
    ) -> torch.Tensor:
        # Encode source sequence
        src_embedded = self.encoder_embed(src)        # (batch, src_len, embed)
        _, (h_n, c_n) = self.encoder(src_embedded)     # h_n: (1, batch, hidden)

        # The encoder's final hidden state becomes the decoder's initial state.
        # This is the "context vector" -- entire source compressed into h_n, c_n.

        # Decode target sequence
        tgt_embedded = self.decoder_embed(tgt)        # (batch, tgt_len, embed)
        decoder_output, _ = self.decoder(tgt_embedded, (h_n, c_n))

        # Project to target vocabulary
        logits = self.output_proj(decoder_output)     # (batch, tgt_len, tgt_vocab)
        return logits

        # Limitation: The context vector is a bottleneck.
        # For long source sequences, important information gets lost.
        # Attention (Module 06) fixes this by allowing the decoder
        # to "look back" at all encoder states, not just the final one.


# Exercise 12: Training Loop for Sequence Model
# Difficulty: Hard
def train_sequence_model(
    model: nn.Module,
    data: list[tuple[torch.Tensor, torch.Tensor]],
    num_epochs: int = 5,
    learning_rate: float = 0.001,
    clip_grad_norm: float = 1.0,
) -> list[float]:
    """Train a sequence classification model with gradient clipping."""
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()
    epoch_losses = []

    model.train()

    for epoch in range(num_epochs):
        total_loss = 0.0
        num_batches = 0

        for input_tokens, labels in data:
            # 1. Zero gradients
            optimizer.zero_grad()

            # 2. Forward pass
            logits = model(input_tokens)  # (batch, num_classes)

            # 3. Compute loss
            loss = criterion(logits, labels)

            # 4. Backward pass
            loss.backward()

            # 5. Gradient clipping -- ESSENTIAL for RNNs
            # Without this, exploding gradients can make training diverge.
            torch.nn.utils.clip_grad_norm_(model.parameters(), clip_grad_norm)

            # 6. Update parameters
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / num_batches
        epoch_losses.append(avg_loss)

    return epoch_losses

    # Key points about RNN training:
    # 1. Gradient clipping is NOT optional -- exploding gradients are common
    # 2. Adam is usually better than SGD for RNNs
    # 3. Learning rate ~1e-3 is a good starting point
    # 4. Monitor both loss AND gradient norms during training


# =============================================================================
# TESTS (same as exercises.py)
# =============================================================================

def test_exercise_1():
    torch.manual_seed(42)
    x = torch.randn(2, 4)
    h = torch.zeros(2, 3)
    W_xh = torch.randn(4, 3)
    W_hh = torch.randn(3, 3)
    b = torch.zeros(3)
    result = rnn_step(x, h, W_xh, W_hh, b)
    assert result.shape == (2, 3)
    assert result.abs().max() <= 1.0
    print("Exercise 1 passed!")


def test_exercise_2():
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
    assert torch.allclose(outputs[:, -1, :], h_n)
    print("Exercise 2 passed!")


def test_exercise_3():
    model = RNNClassifier(vocab_size=100, embed_dim=16, hidden_dim=32, num_classes=5)
    x = torch.randint(0, 100, (4, 10))
    logits = model(x)
    assert logits.shape == (4, 5)
    print("Exercise 3 passed!")


def test_exercise_4():
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
    assert h_t.abs().max() <= 1.0
    print("Exercise 4 passed!")


def test_exercise_5():
    model = LSTMProcessor(input_size=10, hidden_size=32, num_layers=2)
    x = torch.randn(4, 20, 10)
    last = model(x, output_type="last")
    assert last.shape == (4, 32)
    all_out = model(x, output_type="all")
    assert all_out.shape == (4, 20, 32)
    mean_out = model(x, output_type="mean")
    assert mean_out.shape == (4, 32)
    model_bi = LSTMProcessor(input_size=10, hidden_size=32, bidirectional=True)
    last_bi = model_bi(x, output_type="last")
    assert last_bi.shape == (4, 64)
    print("Exercise 5 passed!")


def test_exercise_6():
    model = SentimentLSTM(vocab_size=1000, embed_dim=64, hidden_dim=128)
    x = torch.randint(1, 1000, (8, 30))
    lengths = torch.randint(10, 30, (8,))
    logits = model(x, lengths)
    assert logits.shape == (8, 1)
    print("Exercise 6 passed!")


def test_exercise_7():
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
    counts = compare_architectures(10, 32)
    assert counts["lstm"] > counts["gru"] > counts["rnn"]
    print(f"Exercise 8 passed! Params: {counts}")


def test_exercise_9():
    torch.manual_seed(42)
    sequences = [
        torch.randn(5, 10),
        torch.randn(3, 10),
        torch.randn(8, 10),
    ]
    lstm = nn.LSTM(input_size=10, hidden_size=16, batch_first=True)
    output, h_n = process_packed_sequences(sequences, lstm)
    assert output.shape == (3, 8, 16)
    print("Exercise 9 passed!")


def test_exercise_10():
    model = CharRNN(vocab_size=50, embed_dim=32, hidden_dim=64, num_layers=2)
    x = torch.randint(0, 50, (4, 20))
    logits, state = model(x)
    assert logits.shape == (4, 20, 50)
    assert len(state) == 2
    generated = model.generate(start_token=0, max_len=10)
    assert len(generated) == 10
    assert generated[0] == 0
    print("Exercise 10 passed!")


def test_exercise_11():
    model = Seq2SeqModel(
        src_vocab_size=100, tgt_vocab_size=80,
        embed_dim=32, hidden_dim=64,
    )
    src = torch.randint(0, 100, (4, 10))
    tgt = torch.randint(0, 80, (4, 15))
    logits = model(src, tgt)
    assert logits.shape == (4, 15, 80)
    print("Exercise 11 passed!")


def test_exercise_12():
    model = RNNClassifier(vocab_size=50, embed_dim=16, hidden_dim=32, num_classes=3)
    data = [
        (torch.randint(1, 50, (8, 10)), torch.randint(0, 3, (8,)))
        for _ in range(5)
    ]
    losses = train_sequence_model(model, data, num_epochs=3)
    assert len(losses) == 3
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
