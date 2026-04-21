"""
Module 03: Data Structures - Solutions
=======================================
Complete solutions with Pythonic alternatives and complexity notes.
"""
from collections import Counter, defaultdict, deque, namedtuple
from typing import NamedTuple


# =============================================================================
# Exercise 1: List Manipulation
# =============================================================================
def list_operations(items: list[int]) -> dict[str, object]:
    result = items.copy()  # Don't modify original — like Swift value semantics
    result.append(99)
    result.insert(0, 0)
    result.sort(reverse=True)
    return {
        "result": result,
        "length": len(result),
        "first": result[0],
        "last": result[-1],
        "sum": sum(result),
    }


# =============================================================================
# Exercise 2: Slice Master
# =============================================================================
def slice_operations(items: list[int]) -> dict[str, list[int]]:
    return {
        "first_three": items[:3],
        "last_three": items[-3:],
        "reversed": items[::-1],
        "every_other": items[::2],
        "middle": items[1:-1],
    }


# =============================================================================
# Exercise 3: Tuple Unpacking
# =============================================================================
def unpack_coordinates(points: list[tuple[float, float]]) -> dict[str, float]:
    xs, ys = zip(*points)  # Pythonic: unzip with zip(*iterable)
    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "avg_x": sum(xs) / len(xs),
        "avg_y": sum(ys) / len(ys),
    }


# =============================================================================
# Exercise 4: Word Frequency Counter
# =============================================================================
def word_frequency(text: str) -> list[tuple[str, int]]:
    counts = Counter(text.lower().split())
    # Filter words appearing more than once, sort by count desc then alpha
    return sorted(
        [(word, count) for word, count in counts.items() if count > 1],
        key=lambda x: (-x[1], x[0]),
    )


# =============================================================================
# Exercise 5: Set Operations
# =============================================================================
def analyze_enrollment(
    math_students: set[str],
    science_students: set[str],
    english_students: set[str],
) -> dict[str, set[str]]:
    all_students = math_students | science_students | english_students
    all_three = math_students & science_students & english_students

    math_only = math_students - science_students - english_students
    math_and_science = math_students & science_students

    # Exactly two: in at least two but not all three
    in_two_or_more = (
        (math_students & science_students)
        | (math_students & english_students)
        | (science_students & english_students)
    )
    exactly_two = in_two_or_more - all_three

    return {
        "all_students": all_students,
        "all_three": all_three,
        "math_only": math_only,
        "math_and_science": math_and_science,
        "exactly_two": exactly_two,
    }


# =============================================================================
# Exercise 6: Dict Merge and Transform
# =============================================================================
def merge_configs(*configs: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {}
    for config in configs:
        for key, value in config.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = merge_configs(result[key], value)  # type: ignore[arg-type]
            elif (
                key in result
                and isinstance(result[key], list)
                and isinstance(value, list)
            ):
                result[key] = result[key] + value  # type: ignore[operator]
            else:
                result[key] = value
    return result


# =============================================================================
# Exercise 7: Grouping with defaultdict
# =============================================================================
def group_by_length(words: list[str]) -> dict[int, list[str]]:
    groups: dict[int, list[str]] = defaultdict(list)
    for word in words:
        groups[len(word)].append(word)
    # Sort within each group and convert to regular dict
    return {k: sorted(v) for k, v in groups.items()}


# =============================================================================
# Exercise 8: Counter Arithmetic
# =============================================================================
def inventory_check(
    stock: dict[str, int],
    orders: list[dict[str, int]],
) -> dict[str, object]:
    total_ordered = Counter()
    for order in orders:
        total_ordered += Counter(order)

    stock_counter = Counter(stock)
    diff = stock_counter - total_ordered  # Only keeps positive values
    shortage_counter = total_ordered - stock_counter

    remaining = {item: max(0, stock.get(item, 0) - total_ordered.get(item, 0))
                 for item in stock}
    shortage = {item: count for item, count in shortage_counter.items() if count > 0}

    return {
        "total_ordered": total_ordered,
        "remaining": remaining,
        "can_fulfill": len(shortage) == 0,
        "shortage": shortage,
    }


# =============================================================================
# Exercise 9: Named Tuple Records
# =============================================================================
class Student(NamedTuple):
    name: str
    grade: int
    gpa: float


def process_students(data: list[tuple[str, int, float]]) -> dict[str, object]:
    students = sorted(
        [Student(*row) for row in data],
        key=lambda s: -s.gpa,
    )
    honor_roll = [s.name for s in students if s.gpa >= 3.5]

    by_grade: dict[int, list[str]] = defaultdict(list)
    for s in students:
        by_grade[s.grade].append(s.name)
    by_grade = {k: sorted(v) for k, v in by_grade.items()}

    return {
        "students": students,
        "honor_roll": honor_roll,
        "by_grade": by_grade,
        "top_student": students[0].name,
    }


# =============================================================================
# Exercise 10: Deque as Sliding Window
# Complexity: O(n) using monotonic deque
# =============================================================================
def sliding_window_max(numbers: list[int], window_size: int) -> list[int]:
    result = []
    dq: deque[int] = deque()  # Stores indices

    for i, num in enumerate(numbers):
        # Remove indices outside the window
        while dq and dq[0] < i - window_size + 1:
            dq.popleft()
        # Remove smaller elements (maintain decreasing order)
        while dq and numbers[dq[-1]] <= num:
            dq.pop()
        dq.append(i)
        # Start recording once we have a full window
        if i >= window_size - 1:
            result.append(numbers[dq[0]])

    return result


# =============================================================================
# Exercise 11: Deep Flatten
# =============================================================================
def deep_flatten(nested: list) -> list:
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(deep_flatten(item))
        else:
            result.append(item)
    return result

    # Pythonic alternative using generators:
    # def _flatten(lst):
    #     for item in lst:
    #         if isinstance(item, list):
    #             yield from _flatten(item)
    #         else:
    #             yield item
    # return list(_flatten(nested))


# =============================================================================
# Exercise 12: Matrix Operations with Lists
# =============================================================================
def matrix_ops(matrix: list[list[int]]) -> dict[str, object]:
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0

    transposed = [[matrix[r][c] for r in range(rows)] for c in range(cols)]
    # Pythonic alternative: list(map(list, zip(*matrix)))

    flattened = [val for row in matrix for val in row]
    row_sums = [sum(row) for row in matrix]
    col_sums = [sum(matrix[r][c] for r in range(rows)) for c in range(cols)]
    diagonal = [matrix[i][i] for i in range(rows)] if rows == cols else []

    return {
        "transposed": transposed,
        "flattened": flattened,
        "row_sums": row_sums,
        "col_sums": col_sums,
        "diagonal": diagonal,
    }


# =============================================================================
# Exercise 13: Stack
# =============================================================================
class Stack:
    def __init__(self) -> None:
        self._items: list = []

    def push(self, item: object) -> None:
        self._items.append(item)

    def pop(self) -> object | None:
        return self._items.pop() if self._items else None

    @property
    def peek(self) -> object | None:
        return self._items[-1] if self._items else None

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return len(self._items) > 0


# =============================================================================
# Exercise 14: Frequency Analysis Pipeline
# =============================================================================
def frequency_analysis(text: str) -> dict[str, object]:
    words = text.lower().split()
    letters_only = [c for c in text.lower() if c.isalpha()]

    char_freq = Counter(letters_only)
    word_freq = Counter(words)
    unique_words = set(words)

    char_to_words: dict[str, set[str]] = defaultdict(set)
    for word in words:
        for char in set(word):
            if char.isalpha():
                char_to_words[char].add(word)

    return {
        "char_freq": char_freq,
        "word_freq": word_freq,
        "unique_words": unique_words,
        "most_common_char": char_freq.most_common(1)[0][0],
        "most_common_word": word_freq.most_common(1)[0][0],
        "char_to_words": char_to_words,
    }


# =============================================================================
# Exercise 15: Data Pipeline with Unpacking
# =============================================================================
def process_transactions(
    transactions: list[tuple[str, str, float]],
) -> dict[str, object]:
    total = round(sum(amount for _, _, amount in transactions), 2)

    by_category: dict[str, float] = defaultdict(float)
    by_date: dict[str, list[tuple[str, float]]] = defaultdict(list)
    daily_totals: dict[str, float] = defaultdict(float)

    largest_txn = max(transactions, key=lambda t: t[2])

    for date, category, amount in transactions:
        by_category[category] = round(by_category[category] + amount, 2)
        by_date[date].append((category, amount))
        daily_totals[date] = round(daily_totals[date] + amount, 2)

    return {
        "total": total,
        "by_category": dict(by_category),
        "by_date": dict(by_date),
        "largest": {
            "date": largest_txn[0],
            "category": largest_txn[1],
            "amount": largest_txn[2],
        },
        "categories": sorted(by_category.keys()),
        "daily_totals": dict(sorted(daily_totals.items())),
    }
