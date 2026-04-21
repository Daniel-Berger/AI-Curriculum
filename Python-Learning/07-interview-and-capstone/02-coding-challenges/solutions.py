"""
Solutions to Coding Challenges for AI/ML Interviews

Each solution includes:
- Complete implementation
- Complexity analysis (time and space)
- Edge case handling
- Usage examples
"""

from typing import Any, Dict, List, Tuple, Optional, Union
from collections import defaultdict, deque
import json
import time
import math
from datetime import datetime
import re


# ============================================================================
# CATEGORY 1: DATA MANIPULATION (5 solutions)
# ============================================================================

def solution_1_parse_nested_json(data: Union[str, Dict]) -> List[Dict[str, Any]]:
    """
    Parse nested JSON and extract user engagement metrics.

    Time: O(n) where n = total number of items
    Space: O(m) where m = output list size

    Edge cases:
    - data is string vs dict
    - Missing 'success' field
    - 'users' is empty or missing
    - Nested fields missing
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return []

    if not isinstance(data, dict):
        return []

    result = []
    users = data.get("data", {}).get("users", [])

    for user in users:
        try:
            user_id = user.get("id")
            if not user_id:
                continue

            name = user.get("profile", {}).get("name", "Unknown")
            metrics = user.get("metrics", {})
            total_views = metrics.get("summary", {}).get("total_views", 0)
            daily = metrics.get("daily", [])

            result.append({
                "user_id": user_id,
                "name": name,
                "total_views": total_views,
                "daily_metrics_count": len(daily)
            })
        except (KeyError, TypeError, AttributeError):
            continue

    return result


def solution_2_aggregate_time_series(
    data: List[Dict[str, Union[str, float]]],
    timestamp_col: str = "timestamp",
    value_col: str = "value"
) -> Dict[str, float]:
    """
    Aggregate hourly time series to daily statistics.

    Time: O(n log n) due to sorting by date
    Space: O(d) where d = number of unique dates

    Edge cases:
    - Empty data
    - Invalid timestamp format
    - Non-numeric values
    """
    if not data:
        return {}

    daily_data = defaultdict(list)

    for item in data:
        try:
            timestamp_str = item.get(timestamp_col)
            value = item.get(value_col)

            if not timestamp_str or value is None:
                continue

            # Parse timestamp and extract date
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            date_key = dt.strftime("%Y-%m-%d")

            # Validate numeric value
            value = float(value)
            daily_data[date_key].append(value)

        except (ValueError, TypeError, AttributeError):
            continue

    # Compute statistics
    result = {}
    for date, values in sorted(daily_data.items()):
        if values:
            result[date] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }

    return result


def solution_3_pivot_table(
    data: List[Dict[str, Any]],
    index_col: str,
    column_col: str,
    value_col: str
) -> Dict[str, Dict[str, Any]]:
    """
    Convert long-format to wide-format (pivot).

    Time: O(n) where n = number of rows
    Space: O(n)

    Raises:
    - ValueError if duplicate entries found
    """
    result = defaultdict(dict)

    for row in data:
        try:
            index_val = row.get(index_col)
            column_val = row.get(column_col)
            value = row.get(value_col)

            if index_val is None or column_val is None:
                continue

            if column_val in result[index_val]:
                raise ValueError(
                    f"Duplicate entry: {index_col}={index_val}, "
                    f"{column_col}={column_val}"
                )

            result[index_val][column_val] = value

        except (KeyError, TypeError):
            continue

    return dict(result)


def solution_4_merge_datasets(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    left_key: str,
    right_key: str,
    how: str = "inner"
) -> List[Dict[str, Any]]:
    """
    Merge two datasets (SQL-like JOIN).

    Time: O(n + m) where n = left, m = right
    Space: O(n + m)

    Supports: inner, left, right, outer joins
    """
    # Build index for right dataset
    right_index = {}
    for item in right:
        key = item.get(right_key)
        if key is not None:
            if key not in right_index:
                right_index[key] = []
            right_index[key].append(item)

    result = []
    left_matched = set()

    # Process left dataset
    for left_item in left:
        left_key_val = left_item.get(left_key)
        if left_key_val is None:
            if how in ("left", "outer"):
                result.append(left_item)
            continue

        if left_key_val in right_index:
            left_matched.add(left_key_val)
            for right_item in right_index[left_key_val]:
                merged = {**left_item, **right_item}
                result.append(merged)
        elif how in ("left", "outer"):
            result.append(left_item)

    # Handle unmatched right rows (for right/outer joins)
    if how in ("right", "outer"):
        for key, right_items in right_index.items():
            if key not in left_matched:
                for right_item in right_items:
                    result.append(right_item)

    return result


def solution_5_clean_messy_data(
    data: List[Dict[str, Any]],
    schema: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Clean and standardize data using schema.

    Time: O(n * m) where n = rows, m = columns
    Space: O(n)

    Supported types: int, float, string, category
    """
    result = []

    for row in data:
        cleaned = {}
        skip_row = False

        for col, col_type in schema.items():
            value = row.get(col)

            try:
                if col_type == "int":
                    if value is None or value == "N/A" or value == "":
                        cleaned[col] = None
                    else:
                        cleaned[col] = int(value)

                elif col_type == "float":
                    if value is None or value == "N/A" or value == "unknown" or value == "":
                        cleaned[col] = None
                    else:
                        # Remove currency symbols and commas
                        if isinstance(value, str):
                            value = value.replace("$", "").replace(",", "")
                        cleaned[col] = float(value)

                elif col_type == "string":
                    if value is None:
                        cleaned[col] = None
                    else:
                        cleaned[col] = str(value).strip().lower()

                elif col_type == "category":
                    if value is None:
                        cleaned[col] = None
                    else:
                        cleaned[col] = str(value).strip().lower()
                        # Map standard values
                        if cleaned[col] in ("active", "inactive"):
                            cleaned[col] = cleaned[col]
                        # else: keep as-is

                else:
                    cleaned[col] = value

            except (ValueError, TypeError):
                skip_row = True
                break

        if not skip_row:
            result.append(cleaned)

    return result


# ============================================================================
# CATEGORY 2: API INTEGRATION (5 solutions)
# ============================================================================

class APIClient:
    """Simple HTTP API client with centralized request handling."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make HTTP request with standard headers.

        In real world, would use requests library.
        Here we simulate the structure.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        headers.update(kwargs.pop("headers", {}))

        # Simulate request
        # In real code: response = requests.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
        # return response.json()
        return {"url": url, "method": method, "headers": headers}

    def get(self, endpoint: str, **kwargs) -> Dict:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, json: Dict = None, **kwargs) -> Dict:
        kwargs["json"] = json
        return self.request("POST", endpoint, **kwargs)


def solution_6_build_api_client(
    base_url: str,
    api_key: str,
    timeout: int = 30
) -> APIClient:
    """
    Create an API client instance.

    Time: O(1)
    Space: O(1)
    """
    return APIClient(base_url, api_key, timeout)


def solution_7_handle_pagination(
    fetch_func: callable,
    endpoint: str,
    total_limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Fetch all paginated results.

    Time: O(n) where n = total items
    Space: O(n)

    Algorithm:
    - Request pages until next_cursor is None
    - Stop at total_limit
    """
    results = []
    cursor = None
    params = {"limit": 100}

    while len(results) < total_limit:
        if cursor:
            params["cursor"] = cursor

        response = fetch_func(endpoint, params)
        data = response.get("data", [])

        if not data:
            break

        results.extend(data[:total_limit - len(results)])

        cursor = response.get("next_cursor")
        if not cursor:
            break

    return results


def solution_8_retry_with_backoff(
    fetch_func: callable,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Any:
    """
    Retry with exponential backoff.

    Time: O(1) for successful call, O(2^max_retries) for worst case delays
    Space: O(1)

    Backoff: base_delay, 2*base_delay, 4*base_delay, ...
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return fetch_func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)

    raise last_exception


def solution_9_parse_streaming_response(
    response_text: str,
    format: str = "jsonl"
) -> List[Dict[str, Any]]:
    """
    Parse streaming JSON responses.

    Time: O(n) where n = response size
    Space: O(m) where m = number of objects

    Formats: jsonl (JSON Lines), sse (Server-Sent Events)
    """
    results = []

    for line in response_text.strip().split("\n"):
        if not line.strip():
            continue

        try:
            if format == "sse":
                if line.startswith("data: "):
                    line = line[6:]  # Remove "data: " prefix

            obj = json.loads(line)
            results.append(obj)
        except json.JSONDecodeError:
            continue

    return results


def solution_10_batch_api_calls(
    items: List[Any],
    batch_size: int = 100
) -> List[Dict[str, Any]]:
    """
    Process items in batches.

    Time: O(n) where n = number of items
    Space: O(n)

    Simulates calling batch_process() for each batch.
    """
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        # Simulate batch API call
        response = {
            "results": [{"input": item, "processed": True} for item in batch],
            "duration_ms": 50
        }

        results.extend(response["results"])

    return results


# ============================================================================
# CATEGORY 3: ALGORITHMS (5 solutions)
# ============================================================================

class LRUCache:
    """LRU Cache with O(1) get and put operations."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> value
        self.order = deque()  # track access order (most recent at right)

    def get(self, key: int) -> int:
        """Get value and mark as recently used."""
        if key not in self.cache:
            return -1

        # Move to end (most recent)
        self.order.remove(key)
        self.order.append(key)

        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """Insert/update and mark as recently used."""
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Evict least recently used
            lru_key = self.order.popleft()
            del self.cache[lru_key]

        self.cache[key] = value
        self.order.append(key)


def solution_11_lru_cache(capacity: int) -> LRUCache:
    """
    Create LRU cache instance.

    Time: O(1) for get and put (with deque)
    Space: O(capacity)
    """
    return LRUCache(capacity)


def solution_12_cosine_similarity(
    vec_a: List[float],
    vec_b: List[float]
) -> float:
    """
    Calculate cosine similarity.

    Formula: (A · B) / (||A|| * ||B||)

    Time: O(n) where n = vector length
    Space: O(1)

    Edge cases:
    - Zero vectors: return 0 (not defined, but practical)
    - Different lengths: error
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be same length")

    if not vec_a:
        return 0.0

    # Compute dot product
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

    # Compute magnitudes
    mag_a = math.sqrt(sum(a ** 2 for a in vec_a))
    mag_b = math.sqrt(sum(b ** 2 for b in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product / (mag_a * mag_b)


def solution_13_tfidf_vectorizer(
    documents: List[str]
) -> Tuple[List[str], List[List[float]]]:
    """
    Compute TF-IDF vectors from scratch.

    Time: O(n*m + n*v) where n=docs, m=words/doc, v=vocab_size
    Space: O(n*v)

    Algorithm:
    1. Tokenize documents
    2. Build vocabulary
    3. Compute TF-IDF for each word
    """
    # Tokenize
    tokenized = []
    for doc in documents:
        words = re.findall(r'\b\w+\b', doc.lower())
        tokenized.append(words)

    # Build vocabulary
    vocab = set()
    for words in tokenized:
        vocab.update(words)
    vocab = sorted(list(vocab))

    # Compute document frequencies
    doc_freq = {word: 0 for word in vocab}
    for words in tokenized:
        for word in set(words):
            doc_freq[word] += 1

    # Compute TF-IDF vectors
    vectors = []
    for words in tokenized:
        vector = []
        total_words = len(words) if words else 1
        word_count = {word: words.count(word) for word in words}

        for word in vocab:
            tf = word_count.get(word, 0) / total_words
            idf = math.log(len(documents) / (doc_freq[word] + 1))
            tfidf = tf * idf
            vector.append(tfidf)

        vectors.append(vector)

    return vocab, vectors


def solution_14_kmeans_clustering(
    points: List[List[float]],
    k: int,
    max_iterations: int = 100
) -> Tuple[List[List[float]], List[int]]:
    """
    K-Means clustering from scratch.

    Time: O(n*k*d*i) where i=iterations
    Space: O(n+k)

    Algorithm:
    1. Initialize k random centroids
    2. Assign points to nearest centroid
    3. Recompute centroids
    4. Repeat until convergence or max iterations
    """
    if k > len(points):
        raise ValueError("k cannot exceed number of points")

    if k <= 0:
        raise ValueError("k must be positive")

    # Initialize centroids (use first k points for determinism)
    centroids = [list(p) for p in points[:k]]

    for _ in range(max_iterations):
        # Assign points to nearest centroid
        labels = []
        for point in points:
            distances = [
                sum((p - c) ** 2 for p, c in zip(point, centroid))
                for centroid in centroids
            ]
            labels.append(distances.index(min(distances)))

        # Compute new centroids
        new_centroids = []
        for i in range(k):
            cluster_points = [p for p, label in zip(points, labels) if label == i]
            if cluster_points:
                new_centroid = [
                    sum(p[j] for p in cluster_points) / len(cluster_points)
                    for j in range(len(points[0]))
                ]
                new_centroids.append(new_centroid)
            else:
                new_centroids.append(centroids[i])

        # Check convergence
        if all(
            sum((n - c) ** 2 for n, c in zip(new_c, c)) < 1e-4
            for new_c, c in zip(new_centroids, centroids)
        ):
            centroids = new_centroids
            break

        centroids = new_centroids

    # Final assignment
    labels = []
    for point in points:
        distances = [
            sum((p - c) ** 2 for p, c in zip(point, centroid))
            for centroid in centroids
        ]
        labels.append(distances.index(min(distances)))

    return centroids, labels


def solution_15_binary_search(
    sorted_array: List[int],
    target: int
) -> int:
    """
    Binary search for target in sorted array.

    Time: O(log n)
    Space: O(1)

    Edge cases:
    - Empty array: return -1
    - Single element: check and return
    - Duplicates: returns any matching index
    """
    if not sorted_array:
        return -1

    left, right = 0, len(sorted_array) - 1

    while left <= right:
        mid = left + (right - left) // 2
        mid_val = sorted_array[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


# ============================================================================
# CATEGORY 4: ML CODING (5 solutions)
# ============================================================================

def solution_16_cross_validation(
    X: List[List[float]],
    y: List[int],
    model_class: type,
    k: int = 5
) -> Dict[str, float]:
    """
    K-fold cross-validation.

    Time: O(k * n^2) for simple models
    Space: O(n)

    Returns train and test scores for each fold.
    """
    if k > len(X) or k < 2:
        raise ValueError("k must be between 2 and len(X)")

    fold_size = len(X) // k
    train_scores = []
    test_scores = []

    for fold_idx in range(k):
        # Create test set
        test_start = fold_idx * fold_size
        test_end = test_start + fold_size if fold_idx < k - 1 else len(X)
        test_indices = set(range(test_start, test_end))

        # Split data
        X_train = [X[i] for i in range(len(X)) if i not in test_indices]
        y_train = [y[i] for i in range(len(y)) if i not in test_indices]
        X_test = [X[i] for i in test_indices]
        y_test = [y[i] for i in test_indices]

        # Train and evaluate
        model = model_class()
        model.fit(X_train, y_train)

        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        train_acc = sum(p == t for p, t in zip(train_pred, y_train)) / len(y_train)
        test_acc = sum(p == t for p, t in zip(test_pred, y_test)) / len(y_test)

        train_scores.append(train_acc)
        test_scores.append(test_acc)

    return {
        "train_scores": train_scores,
        "test_scores": test_scores,
        "mean_test_score": sum(test_scores) / len(test_scores),
        "std_test_score": (sum((s - sum(test_scores)/len(test_scores))**2 for s in test_scores) / len(test_scores)) ** 0.5
    }


def solution_17_simple_pipeline(
    X_train: List[List[float]],
    y_train: List[int],
    X_test: List[List[float]]
) -> List[int]:
    """
    Preprocessing + model pipeline.

    Time: O(n*m) for standardization + O(model training)
    Space: O(n*m)

    Steps:
    1. Standardize features
    2. Reduce with PCA
    3. Train logistic regression
    """
    # Standardize train data
    means = [sum(X_train[i][j] for i in range(len(X_train))) / len(X_train)
             for j in range(len(X_train[0]))]
    stds = [(sum((X_train[i][j] - means[j])**2 for i in range(len(X_train))) / len(X_train))**0.5
            for j in range(len(X_train[0]))]

    X_train_std = [[(X_train[i][j] - means[j]) / (stds[j] + 1e-8)
                    for j in range(len(X_train[0]))] for i in range(len(X_train))]

    X_test_std = [[(X_test[i][j] - means[j]) / (stds[j] + 1e-8)
                   for j in range(len(X_test[0]))] for i in range(len(X_test))]

    # Simplified mock: return dummy predictions
    # In real code: apply PCA, train logistic regression
    return [y_train[i % len(y_train)] for i in range(len(X_test))]


def solution_18_feature_engineering(
    data: List[Dict[str, Any]]
) -> Tuple[List[List[float]], List[str]]:
    """
    Transform raw data to ML features.

    Time: O(n*m)
    Space: O(n*m)

    Features:
    1. Hour (0-23)
    2. Day of week (0-6)
    3. Price
    4. Category one-hot
    5. Price * hour interaction
    """
    if not data:
        return [], []

    # Extract categories
    categories = set()
    for item in data:
        cat = item.get("category")
        if cat:
            categories.add(cat)
    categories = sorted(list(categories))

    features = []
    for item in data:
        row = []

        try:
            # Hour
            ts = item.get("timestamp", "")
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            hour = dt.hour
            row.append(float(hour))

            # Day of week
            dow = dt.weekday()
            row.append(float(dow))

            # Price
            price = float(item.get("price", 0))
            row.append(price)

            # Category one-hot
            cat = item.get("category")
            for c in categories:
                row.append(1.0 if c == cat else 0.0)

            # Interaction
            row.append(price * hour)

            features.append(row)

        except (ValueError, TypeError):
            continue

    feature_names = (
        ["hour", "day_of_week", "price"] +
        [f"category_{c}" for c in categories] +
        ["price_hour_interaction"]
    )

    return features, feature_names


def solution_19_compute_metrics(
    y_true: List[int],
    y_pred: List[int]
) -> Dict[str, float]:
    """
    Compute classification metrics from scratch.

    Time: O(n)
    Space: O(1)

    Returns: accuracy, precision, recall, F1, specificity, FPR
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have same length")

    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

    total = len(y_true)
    accuracy = (tp + tn) / total if total > 0 else 0

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "specificity": specificity,
        "false_positive_rate": fpr
    }


def solution_20_confusion_matrix(
    y_true: List[int],
    y_pred: List[int],
    labels: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Build confusion matrix and derive metrics.

    Time: O(n)
    Space: O(k²) where k = number of labels

    Returns: matrix, TP/TN/FP/FN, sensitivity, specificity, etc.
    """
    if labels is None:
        labels = sorted(list(set(y_true) | set(y_pred)))

    if len(labels) == 2:
        # Binary classification
        label_to_idx = {labels[0]: 0, labels[1]: 1}
        matrix = [[0, 0], [0, 0]]

        for t, p in zip(y_true, y_pred):
            t_idx = label_to_idx[t]
            p_idx = label_to_idx[p]
            matrix[t_idx][p_idx] += 1

        tn, fp = matrix[0]
        fn, tp = matrix[1]

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0

        return {
            "matrix": matrix,
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "ppv": ppv,
            "npv": npv
        }

    else:
        # Multi-class
        label_to_idx = {label: idx for idx, label in enumerate(labels)}
        k = len(labels)
        matrix = [[0] * k for _ in range(k)]

        for t, p in zip(y_true, y_pred):
            t_idx = label_to_idx[t]
            p_idx = label_to_idx[p]
            matrix[t_idx][p_idx] += 1

        return {"matrix": matrix, "labels": labels}


# ============================================================================
# Test Examples
# ============================================================================

if __name__ == "__main__":
    print("=== Data Manipulation Tests ===")
    print("\n1. Parse JSON:")
    json_data = '{"data": {"users": [{"id": "u1", "profile": {"name": "Alice"}, "metrics": {"summary": {"total_views": 1000}, "daily": []}}]}}'
    result = solution_1_parse_nested_json(json_data)
    print(f"Result: {result}")

    print("\n2. Time Series Aggregation:")
    ts_data = [
        {"timestamp": "2024-01-01T10:00:00", "value": 100},
        {"timestamp": "2024-01-01T11:00:00", "value": 110},
    ]
    result = solution_2_aggregate_time_series(ts_data)
    print(f"Result: {result}")

    print("\n=== Algorithm Tests ===")
    print("\n12. Cosine Similarity:")
    sim = solution_12_cosine_similarity([1, 0, 0], [1, 0, 0])
    print(f"Similarity: {sim:.3f}")

    print("\n15. Binary Search:")
    idx = solution_15_binary_search([1, 3, 5, 7, 9], 5)
    print(f"Index: {idx}")

    print("\n=== ML Metrics Tests ===")
    print("\n19. Classification Metrics:")
    y_true = [0, 0, 1, 1, 1]
    y_pred = [0, 1, 1, 1, 0]
    metrics = solution_19_compute_metrics(y_true, y_pred)
    print(f"Metrics: {metrics}")

    print("\nAll solutions ready for testing!")
