"""
Module 01 Solutions: System Design Components
==============================================

Complete implementations of all system design building blocks.
Each solution includes complexity analysis and design notes.
"""

import time
import hashlib
import bisect
import heapq
import json
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Callable
from enum import Enum


# ---------------------------------------------------------------------------
# Solution 1: LRU Cache with TTL
# ---------------------------------------------------------------------------
# Time Complexity: O(1) for get and put (OrderedDict is a hash map + doubly linked list)
# Space Complexity: O(capacity)
#
# Design notes:
# - OrderedDict gives us O(1) access + O(1) move-to-end for LRU tracking
# - Each entry stores (value, expiry_time) tuple
# - Lazy expiration: we check TTL on access, not with a background thread
# - In production, use Redis with EXPIRE command instead
# ---------------------------------------------------------------------------

class LRUCacheWithTTL:
    """LRU cache with per-key TTL (time-to-live)."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()

    def get(self, key: str) -> Any | None:
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        # Check TTL
        if time.time() > expiry:
            del self._cache[key]
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return value

    def put(self, key: str, value: Any, ttl_seconds: float = 60.0) -> None:
        expiry = time.time() + ttl_seconds

        if key in self._cache:
            # Update existing key
            self._cache[key] = (value, expiry)
            self._cache.move_to_end(key)
        else:
            # Evict if at capacity
            if len(self._cache) >= self.capacity:
                self._evict_expired()
                # If still at capacity after removing expired, evict LRU
                if len(self._cache) >= self.capacity:
                    self._cache.popitem(last=False)  # Remove first (LRU)

            self._cache[key] = (value, expiry)

    def _evict_expired(self) -> None:
        now = time.time()
        expired_keys = [
            k for k, (_, expiry) in self._cache.items() if now > expiry
        ]
        for k in expired_keys:
            del self._cache[k]

    def __len__(self) -> int:
        self._evict_expired()
        return len(self._cache)


# ---------------------------------------------------------------------------
# Solution 2: Token Bucket Rate Limiter
# ---------------------------------------------------------------------------
# Time Complexity: O(1) per request
# Space Complexity: O(1)
#
# Design notes:
# - Lazy refill: calculate tokens to add based on elapsed time
# - min(capacity, ...) prevents exceeding bucket capacity
# - In production, use Redis + Lua script for atomic distributed rate limiting
# ---------------------------------------------------------------------------

class TokenBucketRateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)  # Start full
        self.last_refill_time = time.time()

    def allow_request(self) -> bool:
        self._refill()

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill_time
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now


# ---------------------------------------------------------------------------
# Solution 3: Consistent Hashing Ring
# ---------------------------------------------------------------------------
# Time Complexity:
#   - add_node: O(V * log(N*V)) where V = virtual nodes, N = physical nodes
#   - remove_node: O(V * log(N*V))
#   - get_node: O(log(N*V)) using binary search
# Space Complexity: O(N * V)
#
# Design notes:
# - Virtual nodes ensure even distribution even with few physical nodes
# - MD5 hash provides good distribution (not cryptographically necessary here)
# - bisect module for O(log n) lookup on sorted ring
# - In production, use a library like uhashring or ketama
# ---------------------------------------------------------------------------

class ConsistentHashRing:
    """Consistent hashing ring with virtual nodes."""

    def __init__(self, num_virtual_nodes: int = 150):
        self.num_virtual_nodes = num_virtual_nodes
        self._ring: dict[int, str] = {}      # hash position -> node name
        self._sorted_keys: list[int] = []    # sorted hash positions
        self._nodes: set[str] = set()         # physical node names

    def add_node(self, node: str) -> None:
        self._nodes.add(node)
        for i in range(self.num_virtual_nodes):
            key = self._hash(f"{node}:{i}")
            self._ring[key] = node
            bisect.insort(self._sorted_keys, key)

    def remove_node(self, node: str) -> None:
        self._nodes.discard(node)
        for i in range(self.num_virtual_nodes):
            key = self._hash(f"{node}:{i}")
            if key in self._ring:
                del self._ring[key]
                self._sorted_keys.remove(key)

    def get_node(self, key: str) -> str | None:
        if not self._sorted_keys:
            return None

        hash_val = self._hash(key)
        # Find the first position >= hash_val
        idx = bisect.bisect_left(self._sorted_keys, hash_val)

        # Wrap around if past the end
        if idx >= len(self._sorted_keys):
            idx = 0

        return self._ring[self._sorted_keys[idx]]

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)


# ---------------------------------------------------------------------------
# Solution 4: Sliding Window Counter
# ---------------------------------------------------------------------------
# Time Complexity: O(num_buckets) for count, O(1) for record
# Space Complexity: O(num_buckets)
#
# Design notes:
# - Divides the window into fixed-size buckets for efficiency
# - Each bucket covers window_seconds / num_buckets seconds
# - Stale buckets are lazily cleared when accessed
# - Trade granularity (more buckets) for memory/compute
# - In production, use Redis sorted sets with ZRANGEBYSCORE
# ---------------------------------------------------------------------------

class SlidingWindowCounter:
    """Sliding window request counter using sub-buckets."""

    def __init__(self, window_seconds: int = 60, num_buckets: int = 60):
        self.window_seconds = window_seconds
        self.num_buckets = num_buckets
        self.bucket_size = window_seconds / num_buckets
        self._buckets: list[int] = [0] * num_buckets
        self._bucket_timestamps: list[float] = [0.0] * num_buckets

    def record(self, timestamp: float | None = None) -> None:
        timestamp = timestamp or time.time()
        idx = self._get_bucket_index(timestamp)

        # If bucket is stale (from a previous window rotation), reset it
        if (timestamp - self._bucket_timestamps[idx]) >= self.bucket_size:
            self._buckets[idx] = 0
            self._bucket_timestamps[idx] = timestamp

        self._buckets[idx] += 1

    def count(self, timestamp: float | None = None) -> int:
        timestamp = timestamp or time.time()
        cutoff = timestamp - self.window_seconds
        total = 0

        for i in range(self.num_buckets):
            if self._bucket_timestamps[i] >= cutoff:
                total += self._buckets[i]

        return total

    def _get_bucket_index(self, timestamp: float) -> int:
        return int(timestamp / self.bucket_size) % self.num_buckets


# ---------------------------------------------------------------------------
# Solution 5: Priority Queue for Human Review
# ---------------------------------------------------------------------------
# Time Complexity:
#   - enqueue: O(log n)
#   - claim_next: O(n) worst case (scanning for unclaimed)
#   - complete: O(1)
# Space Complexity: O(n)
#
# Design notes:
# - Uses a max-heap (negated priorities for Python's min-heap)
# - Claim/release pattern prevents two reviewers working same item
# - Timeout auto-releases abandoned claims
# - In production, use Redis sorted sets + distributed locks
# ---------------------------------------------------------------------------

@dataclass(order=True)
class ReviewItem:
    """An item in the human review queue."""
    priority: float = field(compare=True)
    content_id: str = field(compare=False)
    content_type: str = field(compare=False)
    violation_type: str = field(compare=False)
    confidence: float = field(compare=False)
    claimed_by: str | None = field(default=None, compare=False)
    claimed_at: float | None = field(default=None, compare=False)


class ReviewQueue:
    """Priority-based human review queue with claim/release."""

    def __init__(self, claim_timeout_seconds: float = 300.0):
        self.claim_timeout = claim_timeout_seconds
        self._items: dict[str, ReviewItem] = {}  # content_id -> item
        self._completed: set[str] = set()

    def enqueue(self, item: ReviewItem) -> None:
        self._items[item.content_id] = item

    def claim_next(self, reviewer_id: str) -> ReviewItem | None:
        self._release_timed_out()

        # Find highest-priority unclaimed item
        best: ReviewItem | None = None
        for item in self._items.values():
            if item.content_id in self._completed:
                continue
            if item.claimed_by is not None:
                continue
            if best is None or item.priority > best.priority:
                best = item

        if best is not None:
            best.claimed_by = reviewer_id
            best.claimed_at = time.time()

        return best

    def complete(self, content_id: str, decision: str,
                 reviewer_id: str) -> bool:
        item = self._items.get(content_id)
        if item is None or item.claimed_by != reviewer_id:
            return False

        self._completed.add(content_id)
        return True

    def release(self, content_id: str, reviewer_id: str) -> bool:
        item = self._items.get(content_id)
        if item is None or item.claimed_by != reviewer_id:
            return False

        item.claimed_by = None
        item.claimed_at = None
        return True

    def _release_timed_out(self) -> None:
        now = time.time()
        for item in self._items.values():
            if (item.claimed_by is not None
                    and item.claimed_at is not None
                    and (now - item.claimed_at) > self.claim_timeout):
                item.claimed_by = None
                item.claimed_at = None

    def pending_count(self) -> int:
        return sum(
            1 for item in self._items.values()
            if item.content_id not in self._completed
            and item.claimed_by is None
        )


# ---------------------------------------------------------------------------
# Solution 6: Feature Store (In-Memory)
# ---------------------------------------------------------------------------
# Time Complexity: O(1) for get/upsert, O(k) for batch_get (k = number of IDs)
# Space Complexity: O(n) where n = number of entities
#
# Design notes:
# - Two-level dict: entity_type -> entity_id -> FeatureSet
# - Auto-incrementing version per entity
# - Lazy TTL checking (like the LRU cache)
# - In production, use Feast, Tecton, or Redis with feature serialization
# ---------------------------------------------------------------------------

@dataclass
class FeatureSet:
    """A set of features for an entity."""
    entity_id: str
    entity_type: str
    features: dict[str, Any]
    version: int
    updated_at: float
    ttl_seconds: float = 3600.0


class InMemoryFeatureStore:
    """Simplified feature store for ML serving."""

    def __init__(self):
        self._store: dict[str, dict[str, FeatureSet]] = {}

    def upsert(self, entity_type: str, entity_id: str,
               features: dict[str, Any], ttl_seconds: float = 3600.0) -> int:
        if entity_type not in self._store:
            self._store[entity_type] = {}

        existing = self._store[entity_type].get(entity_id)
        new_version = (existing.version + 1) if existing else 1

        self._store[entity_type][entity_id] = FeatureSet(
            entity_id=entity_id,
            entity_type=entity_type,
            features=features,
            version=new_version,
            updated_at=time.time(),
            ttl_seconds=ttl_seconds,
        )
        return new_version

    def get(self, entity_type: str, entity_id: str) -> FeatureSet | None:
        type_store = self._store.get(entity_type, {})
        fs = type_store.get(entity_id)

        if fs is None:
            return None

        # Check TTL
        if time.time() > fs.updated_at + fs.ttl_seconds:
            del type_store[entity_id]
            return None

        return fs

    def batch_get(self, entity_type: str,
                  entity_ids: list[str]) -> dict[str, FeatureSet | None]:
        return {eid: self.get(entity_type, eid) for eid in entity_ids}

    def get_feature_value(self, entity_type: str, entity_id: str,
                          feature_name: str) -> Any | None:
        fs = self.get(entity_type, entity_id)
        if fs is None:
            return None
        return fs.features.get(feature_name)


# ---------------------------------------------------------------------------
# Solution 7: Circuit Breaker
# ---------------------------------------------------------------------------
# Time Complexity: O(1) for all operations
# Space Complexity: O(1)
#
# Design notes:
# - Three states: CLOSED (normal), OPEN (failing fast), HALF_OPEN (testing)
# - Transitions: CLOSED -> OPEN on failure_threshold consecutive failures
#                OPEN -> HALF_OPEN after recovery_timeout
#                HALF_OPEN -> CLOSED on success, HALF_OPEN -> OPEN on failure
# - In production, use tenacity or pybreaker library
# - Consider exponential backoff for recovery_timeout on repeated failures
# ---------------------------------------------------------------------------

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
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._half_open_calls = 0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN and self._last_failure_time:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
        return self._state

    def record_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            # Success in half-open -> close the circuit
            self._state = CircuitState.CLOSED

        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            # Failure in half-open -> reopen
            self._state = CircuitState.OPEN
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN

    def allow_request(self) -> bool:
        current_state = self.state  # Property may trigger transition

        if current_state == CircuitState.CLOSED:
            return True
        elif current_state == CircuitState.OPEN:
            return False
        else:  # HALF_OPEN
            if self._half_open_calls < self.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False


# ---------------------------------------------------------------------------
# Solution 8: Request Coalescer (Singleflight)
# ---------------------------------------------------------------------------
# Time Complexity: O(1) for execute and forget
# Space Complexity: O(k) where k = number of unique in-flight keys
#
# Design notes:
# - This synchronous version caches results until explicitly forgotten
# - In an async version, you'd use asyncio.Event or asyncio.Future so
#   multiple coroutines can await the same computation
# - In production, use cachetools or implement with asyncio locks
# - Go's sync.singleflight is the inspiration for this pattern
# ---------------------------------------------------------------------------

class RequestCoalescer:
    """Coalesce duplicate concurrent requests into a single execution."""

    def __init__(self):
        self._results: dict[str, Any] = {}

    def execute(self, key: str, fetch_fn: Callable[[], Any]) -> Any:
        if key in self._results:
            return self._results[key]

        result = fetch_fn()
        self._results[key] = result
        return result

    def forget(self, key: str) -> None:
        self._results.pop(key, None)

    def in_flight_count(self) -> int:
        return len(self._results)


# ---------------------------------------------------------------------------
# Tests (identical to exercises.py)
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

    # Capacity eviction
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
    cache3.put("temp", "value", ttl_seconds=0.01)
    time.sleep(0.02)
    assert cache3.get("temp") is None

    print("  LRU Cache: PASSED")


def test_rate_limiter():
    """Test token bucket rate limiter."""
    limiter = TokenBucketRateLimiter(rate=10.0, capacity=5)

    for _ in range(5):
        assert limiter.allow_request() is True

    assert limiter.allow_request() is False

    time.sleep(0.2)
    assert limiter.allow_request() is True
    assert limiter.allow_request() is True
    assert limiter.allow_request() is False

    print("  Rate Limiter: PASSED")


def test_consistent_hash():
    """Test consistent hashing ring."""
    ring = ConsistentHashRing(num_virtual_nodes=100)

    ring.add_node("server-1")
    ring.add_node("server-2")
    ring.add_node("server-3")

    assignments = {}
    for i in range(1000):
        node = ring.get_node(f"key-{i}")
        assert node is not None
        assignments[f"key-{i}"] = node

    from collections import Counter
    counts = Counter(assignments.values())
    assert len(counts) == 3
    min_count = min(counts.values())
    max_count = max(counts.values())
    assert max_count < min_count * 3, f"Uneven distribution: {counts}"

    ring.remove_node("server-2")
    remapped = 0
    for key, old_node in assignments.items():
        new_node = ring.get_node(key)
        if new_node != old_node:
            remapped += 1
    assert remapped < 500, f"Too many remapped: {remapped}/1000"

    print("  Consistent Hash: PASSED")


def test_sliding_window():
    """Test sliding window counter."""
    counter = SlidingWindowCounter(window_seconds=1, num_buckets=10)

    base_time = time.time()

    for i in range(5):
        counter.record(base_time + i * 0.05)

    assert counter.count(base_time + 0.3) == 5
    assert counter.count(base_time + 2.0) == 0

    print("  Sliding Window: PASSED")


def test_review_queue():
    """Test priority review queue."""
    queue = ReviewQueue(claim_timeout_seconds=1.0)

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

    item = queue.claim_next("reviewer-1")
    assert item is not None
    assert item.content_id == "high"

    assert queue.complete("high", "remove", "reviewer-1") is True

    item2 = queue.claim_next("reviewer-2")
    assert item2 is not None
    assert item2.content_id == "medium"

    time.sleep(1.1)
    item3 = queue.claim_next("reviewer-3")
    assert item3 is not None
    assert item3.content_id == "medium"

    print("  Review Queue: PASSED")


def test_feature_store():
    """Test in-memory feature store."""
    store = InMemoryFeatureStore()

    v1 = store.upsert("user", "u123", {"age": 25, "country": "US"})
    assert v1 == 1

    v2 = store.upsert("user", "u123", {"age": 26, "country": "US"})
    assert v2 == 2

    fs = store.get("user", "u123")
    assert fs is not None
    assert fs.features["age"] == 26
    assert fs.version == 2

    store.upsert("user", "u456", {"age": 30, "country": "UK"})
    results = store.batch_get("user", ["u123", "u456", "u999"])
    assert results["u123"] is not None
    assert results["u456"] is not None
    assert results["u999"] is None

    assert store.get_feature_value("user", "u123", "country") == "US"

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

    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True

    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False

    time.sleep(0.6)
    assert cb.state == CircuitState.HALF_OPEN

    assert cb.allow_request() is True
    cb.record_success()

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

    result1 = coalescer.execute("key1", expensive_fetch)
    assert result1 == "result-1"
    assert call_count == 1

    result2 = coalescer.execute("key1", expensive_fetch)
    assert result2 == "result-1"
    assert call_count == 1

    result3 = coalescer.execute("key2", expensive_fetch)
    assert result3 == "result-2"
    assert call_count == 2

    coalescer.forget("key1")
    result4 = coalescer.execute("key1", expensive_fetch)
    assert result4 == "result-3"
    assert call_count == 3

    print("  Request Coalescer: PASSED")


if __name__ == "__main__":
    print("Testing system design solutions...\n")
    test_lru_cache()
    test_rate_limiter()
    test_consistent_hash()
    test_sliding_window()
    test_review_queue()
    test_feature_store()
    test_circuit_breaker()
    test_request_coalescer()
    print("\nAll system design solutions passed!")
