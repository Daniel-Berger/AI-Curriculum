"""
Module 01 Exercises: System Design Components
=============================================

These exercises implement key building blocks that appear in system design
interviews. Each one is a simplified version of a production component.

For Swift developers: think of these like implementing a custom URLSession
cache policy or a GCD-based rate limiter -- small, focused components that
fit into a larger architecture.
"""

import time
import hashlib
import json
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Exercise 1: LRU Cache with TTL
# ---------------------------------------------------------------------------
# Design and implement an LRU (Least Recently Used) cache with time-to-live.
# This is the fundamental building block of the caching layers we discussed
# in every system design problem.
#
# Requirements:
#   - get(key) returns value if present and not expired, else None
#   - put(key, value, ttl_seconds) stores with expiration
#   - Evicts least recently used item when capacity is exceeded
#   - Thread-safety is NOT required for this exercise
#
# Swift analogy: NSCache with expiration policy
# ---------------------------------------------------------------------------

class LRUCacheWithTTL:
    """LRU cache with per-key TTL (time-to-live)."""

    def __init__(self, capacity: int):
        """Initialize cache with given capacity.

        Args:
            capacity: Maximum number of items in cache.
        """
        self.capacity = capacity
        # TODO: Initialize your data structures
        pass

    def get(self, key: str) -> Any | None:
        """Get value by key. Returns None if not found or expired.

        Should mark the key as recently used.
        """
        # TODO: Implement
        pass

    def put(self, key: str, value: Any, ttl_seconds: float = 60.0) -> None:
        """Store key-value pair with TTL.

        If at capacity, evict least recently used item first.
        """
        # TODO: Implement
        pass

    def _evict_expired(self) -> None:
        """Remove all expired entries."""
        # TODO: Implement
        pass

    def __len__(self) -> int:
        """Return number of non-expired items."""
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 2: Token Bucket Rate Limiter
# ---------------------------------------------------------------------------
# Implement a token bucket rate limiter -- used in API gateways for every
# system we designed. The token bucket allows bursts up to bucket capacity
# while enforcing an average rate.
#
# How it works:
#   - Bucket holds up to `capacity` tokens
#   - Tokens are added at `rate` tokens per second
#   - Each request consumes 1 token
#   - If no tokens available, request is rejected
#
# Swift analogy: Like managing a DispatchSemaphore that refills over time
# ---------------------------------------------------------------------------

class TokenBucketRateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        """Initialize rate limiter.

        Args:
            rate: Tokens added per second.
            capacity: Maximum tokens in bucket (burst size).
        """
        self.rate = rate
        self.capacity = capacity
        # TODO: Initialize state
        pass

    def allow_request(self) -> bool:
        """Check if a request is allowed. Consumes a token if yes.

        Returns:
            True if request is allowed, False if rate limited.
        """
        # TODO: Implement
        pass

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 3: Consistent Hashing Ring
# ---------------------------------------------------------------------------
# Implement consistent hashing -- the algorithm used to distribute data across
# cache nodes or database shards. When a node is added/removed, only K/N keys
# need to be remapped (K = total keys, N = total nodes).
#
# Used in: Feature store sharding, distributed caching, load balancing.
#
# Swift analogy: Like distributing cells across UITableView sections, but the
# sections can be added/removed dynamically with minimal cell movement.
# ---------------------------------------------------------------------------

class ConsistentHashRing:
    """Consistent hashing ring with virtual nodes."""

    def __init__(self, num_virtual_nodes: int = 150):
        """Initialize hash ring.

        Args:
            num_virtual_nodes: Number of virtual nodes per physical node.
                More virtual nodes = better distribution.
        """
        self.num_virtual_nodes = num_virtual_nodes
        # TODO: Initialize data structures
        # Hint: You need a sorted structure of hash positions -> node names
        pass

    def add_node(self, node: str) -> None:
        """Add a node to the ring with its virtual nodes.

        Each virtual node is hashed at position: hash(f"{node}:{i}")
        """
        # TODO: Implement
        pass

    def remove_node(self, node: str) -> None:
        """Remove a node and all its virtual nodes from the ring."""
        # TODO: Implement
        pass

    def get_node(self, key: str) -> str | None:
        """Get the node responsible for the given key.

        Find the first node position >= hash(key) on the ring.
        If no such position exists, wrap around to the first node.
        """
        # TODO: Implement
        pass

    def _hash(self, key: str) -> int:
        """Hash a key to a position on the ring."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)


# ---------------------------------------------------------------------------
# Exercise 4: Sliding Window Counter
# ---------------------------------------------------------------------------
# Implement a sliding window counter for tracking request rates.
# Unlike the token bucket (which allows bursts), this strictly counts
# requests in a rolling time window.
#
# Used in: Rate limiting, anomaly detection, monitoring dashboards.
#
# Approach: Use sub-windows (buckets) for efficiency.
#   - Divide the window into N buckets (e.g., 60 one-second buckets for 1 min)
#   - Count requests per bucket
#   - Sum non-expired buckets for current count
# ---------------------------------------------------------------------------

class SlidingWindowCounter:
    """Sliding window request counter using sub-buckets."""

    def __init__(self, window_seconds: int = 60, num_buckets: int = 60):
        """Initialize sliding window counter.

        Args:
            window_seconds: Total window duration in seconds.
            num_buckets: Number of sub-buckets (granularity).
        """
        self.window_seconds = window_seconds
        self.num_buckets = num_buckets
        # TODO: Initialize data structures
        pass

    def record(self, timestamp: float | None = None) -> None:
        """Record a request at the given timestamp (or now)."""
        # TODO: Implement
        pass

    def count(self, timestamp: float | None = None) -> int:
        """Get the number of requests in the current window."""
        # TODO: Implement
        pass

    def _get_bucket_index(self, timestamp: float) -> int:
        """Map a timestamp to a bucket index."""
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 5: Priority Queue for Human Review
# ---------------------------------------------------------------------------
# Implement the priority-based review queue from the content moderation system.
# Items are scored by severity * uncertainty * reach and processed in priority
# order. Support for claim/release pattern (reviewer claims an item, must
# release or complete within a timeout).
#
# Swift analogy: Like a custom OperationQueue with priority scheduling.
# ---------------------------------------------------------------------------

@dataclass(order=True)
class ReviewItem:
    """An item in the human review queue."""
    priority: float = field(compare=True)       # Higher = more urgent
    content_id: str = field(compare=False)
    content_type: str = field(compare=False)     # "text", "image", "video"
    violation_type: str = field(compare=False)
    confidence: float = field(compare=False)
    claimed_by: str | None = field(default=None, compare=False)
    claimed_at: float | None = field(default=None, compare=False)


class ReviewQueue:
    """Priority-based human review queue with claim/release."""

    def __init__(self, claim_timeout_seconds: float = 300.0):
        """Initialize review queue.

        Args:
            claim_timeout_seconds: How long a reviewer can hold an item
                before it's automatically released.
        """
        self.claim_timeout = claim_timeout_seconds
        # TODO: Initialize data structures
        pass

    def enqueue(self, item: ReviewItem) -> None:
        """Add an item to the review queue."""
        # TODO: Implement
        pass

    def claim_next(self, reviewer_id: str) -> ReviewItem | None:
        """Claim the highest-priority unclaimed item.

        Returns None if no items available.
        Releases timed-out claims before checking.
        """
        # TODO: Implement
        pass

    def complete(self, content_id: str, decision: str,
                 reviewer_id: str) -> bool:
        """Mark a claimed item as reviewed.

        Returns True if successfully completed, False if item not found
        or not claimed by this reviewer.
        """
        # TODO: Implement
        pass

    def release(self, content_id: str, reviewer_id: str) -> bool:
        """Release a claimed item back to the queue."""
        # TODO: Implement
        pass

    def _release_timed_out(self) -> None:
        """Release items that have been claimed longer than the timeout."""
        # TODO: Implement
        pass

    def pending_count(self) -> int:
        """Return number of unclaimed items."""
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 6: Feature Store (In-Memory)
# ---------------------------------------------------------------------------
# Implement a simplified feature store that supports:
#   - Storing user and item features
#   - Batch retrieval (get features for multiple entities at once)
#   - Feature versioning (track which version of features are stored)
#   - TTL-based expiration
#
# Used in: Recommendation systems, real-time ML inference.
# ---------------------------------------------------------------------------

@dataclass
class FeatureSet:
    """A set of features for an entity."""
    entity_id: str
    entity_type: str          # "user" or "item"
    features: dict[str, Any]
    version: int
    updated_at: float
    ttl_seconds: float = 3600.0


class InMemoryFeatureStore:
    """Simplified feature store for ML serving."""

    def __init__(self):
        # TODO: Initialize data structures
        pass

    def upsert(self, entity_type: str, entity_id: str,
               features: dict[str, Any], ttl_seconds: float = 3600.0) -> int:
        """Insert or update features for an entity.

        Returns the new version number.
        Auto-increments version on each update.
        """
        # TODO: Implement
        pass

    def get(self, entity_type: str, entity_id: str) -> FeatureSet | None:
        """Get features for a single entity. Returns None if not found or expired."""
        # TODO: Implement
        pass

    def batch_get(self, entity_type: str,
                  entity_ids: list[str]) -> dict[str, FeatureSet | None]:
        """Get features for multiple entities at once.

        Returns dict mapping entity_id -> FeatureSet (or None if missing).
        """
        # TODO: Implement
        pass

    def get_feature_value(self, entity_type: str, entity_id: str,
                          feature_name: str) -> Any | None:
        """Get a single feature value for an entity."""
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 7: Circuit Breaker
# ---------------------------------------------------------------------------
# Implement the circuit breaker pattern for external service calls.
# When a service is failing, the circuit breaker "opens" to prevent
# cascading failures and allows the service time to recover.
#
# States:
#   CLOSED   -> normal operation, requests pass through
#   OPEN     -> service is down, requests fail immediately
#   HALF_OPEN -> testing if service recovered (allow limited requests)
#
# Used in: Every microservice architecture. Critical for LLM API calls
# (which can be slow/unreliable).
#
# Swift analogy: Like implementing a custom URLSession retry policy with
# backoff, but at the service level.
# ---------------------------------------------------------------------------

from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures to open circuit.
            recovery_timeout: Seconds to wait before trying half-open.
            half_open_max_calls: Max test calls in half-open state.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        # TODO: Initialize state
        pass

    @property
    def state(self) -> CircuitState:
        """Get current circuit state (may transition from OPEN to HALF_OPEN)."""
        # TODO: Implement
        pass

    def record_success(self) -> None:
        """Record a successful call."""
        # TODO: Implement
        pass

    def record_failure(self) -> None:
        """Record a failed call."""
        # TODO: Implement
        pass

    def allow_request(self) -> bool:
        """Check if a request should be allowed through.

        CLOSED: always allow
        OPEN: never allow (fail fast)
        HALF_OPEN: allow up to half_open_max_calls
        """
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Exercise 8: Request Coalescer (Singleflight)
# ---------------------------------------------------------------------------
# Implement request coalescing: when multiple clients request the same
# resource simultaneously, only one actual fetch happens. Others wait
# for and share the result.
#
# Used in: Preventing cache stampedes, reducing duplicate LLM calls,
# embedding batch optimization.
#
# Swift analogy: Like Task.value in structured concurrency -- multiple
# awaiters share a single computation.
#
# Note: This is a synchronous simulation. In production, you'd use
# asyncio or threading.
# ---------------------------------------------------------------------------

from dataclasses import dataclass
from typing import Callable


class RequestCoalescer:
    """Coalesce duplicate concurrent requests into a single execution."""

    def __init__(self):
        # TODO: Initialize data structures
        # Hint: Track in-flight requests and their results
        pass

    def execute(self, key: str, fetch_fn: Callable[[], Any]) -> Any:
        """Execute fetch_fn for the given key, coalescing duplicate calls.

        If a request for the same key is already in-flight, return its result.
        Otherwise, execute fetch_fn and cache the result for other waiters.

        For this synchronous version:
        - First call for a key: execute fetch_fn, store result
        - Subsequent calls for same key while result exists: return cached result
        - Call forget(key) to clear the cached result

        Args:
            key: Unique identifier for this request.
            fetch_fn: Function to call if no in-flight request exists.

        Returns:
            The result of fetch_fn.
        """
        # TODO: Implement
        pass

    def forget(self, key: str) -> None:
        """Remove cached result for a key, allowing fresh fetch next time."""
        # TODO: Implement
        pass

    def in_flight_count(self) -> int:
        """Return number of cached/in-flight results."""
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_lru_cache():
    """Test LRU cache with TTL."""
    cache = LRUCacheWithTTL(capacity=3)

    # Basic put/get
    cache.put("a", 1, ttl_seconds=10.0)
    cache.put("b", 2, ttl_seconds=10.0)
    cache.put("c", 3, ttl_seconds=10.0)
    assert cache.get("a") == 1
    assert cache.get("b") == 2
    assert cache.get("c") == 3

    # Capacity eviction (a was accessed most recently via get, so b is LRU)
    cache.put("d", 4, ttl_seconds=10.0)
    # After accessing a, b, c in order, then adding d, LRU should be b
    # Actually: put a, put b, put c, get a (a moves to recent), get b, get c
    # So order is: a, b, c (all accessed). Adding d evicts... the one
    # accessed earliest. After get(a), get(b), get(c): order is a, b, c
    # So 'a' accessed first after puts, is LRU. Let's simplify:
    cache2 = LRUCacheWithTTL(capacity=2)
    cache2.put("x", 10)
    cache2.put("y", 20)
    cache2.get("x")       # x is now most recently used
    cache2.put("z", 30)   # evicts y (LRU)
    assert cache2.get("x") == 10
    assert cache2.get("y") is None  # evicted
    assert cache2.get("z") == 30

    # TTL expiration
    cache3 = LRUCacheWithTTL(capacity=10)
    cache3.put("temp", "value", ttl_seconds=0.01)  # 10ms TTL
    time.sleep(0.02)  # Wait for expiration
    assert cache3.get("temp") is None  # Expired

    print("  LRU Cache: PASSED")


def test_rate_limiter():
    """Test token bucket rate limiter."""
    limiter = TokenBucketRateLimiter(rate=10.0, capacity=5)

    # Should allow burst up to capacity
    for _ in range(5):
        assert limiter.allow_request() is True

    # Should reject when bucket is empty
    assert limiter.allow_request() is False

    # After waiting, should refill
    time.sleep(0.2)  # 0.2s * 10 tokens/s = 2 tokens
    assert limiter.allow_request() is True
    assert limiter.allow_request() is True
    assert limiter.allow_request() is False  # Only 2 tokens refilled

    print("  Rate Limiter: PASSED")


def test_consistent_hash():
    """Test consistent hashing ring."""
    ring = ConsistentHashRing(num_virtual_nodes=100)

    ring.add_node("server-1")
    ring.add_node("server-2")
    ring.add_node("server-3")

    # All keys should map to a node
    assignments = {}
    for i in range(1000):
        node = ring.get_node(f"key-{i}")
        assert node is not None
        assignments[f"key-{i}"] = node

    # Distribution should be roughly even (within 2x)
    from collections import Counter
    counts = Counter(assignments.values())
    assert len(counts) == 3
    min_count = min(counts.values())
    max_count = max(counts.values())
    assert max_count < min_count * 3, f"Uneven distribution: {counts}"

    # Removing a node should only remap ~1/3 of keys
    ring.remove_node("server-2")
    remapped = 0
    for key, old_node in assignments.items():
        new_node = ring.get_node(key)
        if new_node != old_node:
            remapped += 1
    # Keys that were on server-2 must remap; others mostly shouldn't
    assert remapped < 500, f"Too many remapped: {remapped}/1000"

    print("  Consistent Hash: PASSED")


def test_sliding_window():
    """Test sliding window counter."""
    counter = SlidingWindowCounter(window_seconds=1, num_buckets=10)

    base_time = time.time()

    # Record 5 events
    for i in range(5):
        counter.record(base_time + i * 0.05)  # spread over 250ms

    # All should be in window
    assert counter.count(base_time + 0.3) == 5

    # After window expires, count should be 0
    assert counter.count(base_time + 2.0) == 0

    print("  Sliding Window: PASSED")


def test_review_queue():
    """Test priority review queue."""
    queue = ReviewQueue(claim_timeout_seconds=1.0)

    # Add items with different priorities
    queue.enqueue(ReviewItem(
        priority=5.0, content_id="low", content_type="text",
        violation_type="spam", confidence=0.9
    ))
    queue.enqueue(ReviewItem(
        priority=9.0, content_id="high", content_type="image",
        violation_type="violence", confidence=0.7
    ))
    queue.enqueue(ReviewItem(
        priority=7.0, content_id="medium", content_type="text",
        violation_type="hate_speech", confidence=0.8
    ))

    # Should claim highest priority first
    item = queue.claim_next("reviewer-1")
    assert item is not None
    assert item.content_id == "high"

    # Complete the review
    assert queue.complete("high", "remove", "reviewer-1") is True

    # Next should be medium priority
    item2 = queue.claim_next("reviewer-2")
    assert item2 is not None
    assert item2.content_id == "medium"

    # Test timeout: wait for claim to expire
    time.sleep(1.1)
    item3 = queue.claim_next("reviewer-3")
    assert item3 is not None
    assert item3.content_id == "medium"  # Released after timeout

    print("  Review Queue: PASSED")


def test_feature_store():
    """Test in-memory feature store."""
    store = InMemoryFeatureStore()

    # Store user features
    v1 = store.upsert("user", "u123", {"age": 25, "country": "US"})
    assert v1 == 1

    # Update bumps version
    v2 = store.upsert("user", "u123", {"age": 26, "country": "US"})
    assert v2 == 2

    # Retrieve
    fs = store.get("user", "u123")
    assert fs is not None
    assert fs.features["age"] == 26
    assert fs.version == 2

    # Batch get
    store.upsert("user", "u456", {"age": 30, "country": "UK"})
    results = store.batch_get("user", ["u123", "u456", "u999"])
    assert results["u123"] is not None
    assert results["u456"] is not None
    assert results["u999"] is None

    # Single feature value
    assert store.get_feature_value("user", "u123", "country") == "US"

    # TTL expiration
    store.upsert("user", "temp", {"x": 1}, ttl_seconds=0.01)
    time.sleep(0.02)
    assert store.get("user", "temp") is None

    print("  Feature Store: PASSED")


def test_circuit_breaker():
    """Test circuit breaker."""
    cb = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=0.5,
        half_open_max_calls=2,
    )

    # Should start closed
    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True

    # Record failures up to threshold
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED  # Not yet at threshold

    cb.record_failure()  # 3rd failure = threshold
    assert cb.state == CircuitState.OPEN

    # Should reject requests when open
    assert cb.allow_request() is False

    # Wait for recovery timeout
    time.sleep(0.6)
    assert cb.state == CircuitState.HALF_OPEN

    # Should allow limited requests in half-open
    assert cb.allow_request() is True
    cb.record_success()

    # After success in half-open, should close
    assert cb.state == CircuitState.CLOSED

    print("  Circuit Breaker: PASSED")


def test_request_coalescer():
    """Test request coalescer."""
    coalescer = RequestCoalescer()
    call_count = 0

    def expensive_fetch() -> str:
        nonlocal call_count
        call_count += 1
        return f"result-{call_count}"

    # First call executes the function
    result1 = coalescer.execute("key1", expensive_fetch)
    assert result1 == "result-1"
    assert call_count == 1

    # Second call with same key returns cached result
    result2 = coalescer.execute("key1", expensive_fetch)
    assert result2 == "result-1"  # Same result
    assert call_count == 1        # Function not called again

    # Different key executes function again
    result3 = coalescer.execute("key2", expensive_fetch)
    assert result3 == "result-2"
    assert call_count == 2

    # After forget, next call executes fresh
    coalescer.forget("key1")
    result4 = coalescer.execute("key1", expensive_fetch)
    assert result4 == "result-3"  # Fresh result
    assert call_count == 3

    print("  Request Coalescer: PASSED")


if __name__ == "__main__":
    print("Testing system design components...\n")
    test_lru_cache()
    test_rate_limiter()
    test_consistent_hash()
    test_sliding_window()
    test_review_queue()
    test_feature_store()
    test_circuit_breaker()
    test_request_coalescer()
    print("\nAll system design exercises passed!")
