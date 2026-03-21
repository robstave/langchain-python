# Python Data Structures

## Lists

A list is a mutable, ordered sequence of elements. Lists are one of the most commonly
used data structures in Python.

### Creating Lists

```python
empty = []
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]
nested = [[1, 2], [3, 4]]
```

### Common Operations

- `append(x)` — adds an element to the end. O(1) amortized.
- `insert(i, x)` — inserts at index i. O(n) because elements shift.
- `pop()` — removes and returns the last element. O(1).
- `pop(i)` — removes at index i. O(n).
- `remove(x)` — removes the first occurrence of x. O(n).
- `sort()` — sorts in place. O(n log n) using Timsort.
- `reverse()` — reverses in place. O(n).

### List Comprehensions

List comprehensions provide a concise way to create lists:

```python
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
pairs = [(x, y) for x in range(3) for y in range(3)]
```

## Tuples

Tuples are immutable ordered sequences. They are hashable (if all elements are hashable)
and can be used as dictionary keys.

```python
point = (3, 4)
single = (42,)      # note the trailing comma
x, y = point        # tuple unpacking
```

Tuples are faster than lists for iteration and use less memory because they are
fixed-size and immutable.

## Dictionaries

Dictionaries store key-value pairs with O(1) average lookup time. Since Python 3.7,
dictionaries maintain insertion order.

### Creating Dictionaries

```python
empty = {}
person = {"name": "Alice", "age": 30}
from_pairs = dict([("a", 1), ("b", 2)])
comprehension = {x: x**2 for x in range(5)}
```

### Common Operations

- `d[key]` — get value, raises KeyError if missing
- `d.get(key, default)` — get value with a default fallback
- `d[key] = value` — set a value
- `del d[key]` — delete a key
- `key in d` — membership check, O(1)
- `d.keys()`, `d.values()`, `d.items()` — views
- `d.update(other)` — merge another dict

### defaultdict and Counter

The `collections` module provides specialized dict subclasses:

```python
from collections import defaultdict, Counter

# defaultdict auto-creates missing keys
word_count = defaultdict(int)
for word in words:
    word_count[word] += 1

# Counter counts hashable objects
counter = Counter(["apple", "banana", "apple", "cherry"])
counter.most_common(2)  # [('apple', 2), ('banana', 1)]
```

## Sets

Sets are unordered collections of unique hashable elements. They support mathematical
set operations.

```python
a = {1, 2, 3}
b = {2, 3, 4}

a | b    # union: {1, 2, 3, 4}
a & b    # intersection: {2, 3}
a - b    # difference: {1}
a ^ b    # symmetric difference: {1, 4}
```

Sets have O(1) average-case membership testing, making them ideal for deduplication
and fast lookups when ordering doesn't matter.

## Deques

A deque (double-ended queue) from `collections` is optimized for appending and
popping from both ends in O(1):

```python
from collections import deque

q = deque([1, 2, 3])
q.appendleft(0)   # [0, 1, 2, 3]
q.pop()            # returns 3
q.popleft()        # returns 0
q.rotate(1)        # rotate right by 1
```

Use deques instead of lists when you need a queue or need frequent operations
on both ends of the sequence.

## NamedTuples

Named tuples create tuple subclasses with named fields:

```python
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(3, 4)
print(p.x, p.y)   # 3 4

# Modern approach using typing
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float
    z: float = 0.0  # default value
```

Named tuples are immutable and memory-efficient, making them ideal for representing
simple data records.
