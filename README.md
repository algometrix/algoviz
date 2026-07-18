<div align="center">

# AlgoViz

**Data structures that draw themselves as your algorithm runs.**

[![CI](https://github.com/algometrix/algoviz/actions/workflows/ci.yml/badge.svg)](https://github.com/algometrix/algoviz/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/algoviz.svg?logo=pypi&logoColor=white)](https://pypi.org/project/algoviz/)
[![Python](https://img.shields.io/pypi/pyversions/algoviz.svg?logo=python&logoColor=white)](https://pypi.org/project/algoviz/)
[![Downloads](https://static.pepy.tech/badge/algoviz)](https://pepy.tech/project/algoviz)
[![Downloads/month](https://img.shields.io/pypi/dm/algoviz.svg)](https://pypi.org/project/algoviz/)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#development)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE.txt)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)

[Quick start](#quick-start) · [Structures](#the-structures) · [Demos](#demo-gallery) · [Configuration](#configuration) · [Upgrading](#upgrading-from-02x)

</div>

---

Wrap a data structure, run your algorithm **unchanged**, and watch every step
render in your terminal with the cells you touched highlighted. Reads light up
in one colour, writes in another, and each frame shows only what that step
touched.

No decorators. No callbacks. No rewriting your solution to fit a framework.

```python
from algoviz import VizList

dp = VizList([0] * 4, title_name='Coin Change')
dp[0] = 1
for coin in (1, 2):
    for value in range(coin, 4):
        dp[value] += dp[value - coin]
```

```text
Coin Change Init
┏━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃
┡━━━╇━━━╇━━━╇━━━┩
│ 0 │ 0 │ 0 │ 0 │
└───┴───┴───┴───┘
   Coin Change
┏━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃
┡━━━╇━━━╇━━━╇━━━┩
│ 1 │ 0 │ 0 │ 0 │
└───┴───┴───┴───┘
```

## Why

Reading a DP recurrence tells you what the code does. It does not tell you what
the table *looks like* three iterations in, which is where the bug usually is.
AlgoViz prints that table on every write, so the state is in front of you
instead of in your head.

It is built for the moment you are stuck on a problem, teaching someone who is,
or writing up a solution and want the intermediate states to show.

## Installation

```bash
pip install algoviz
```

```bash
uv add algoviz
```

Requires Python 3.10 or newer. The only dependency is
[rich](https://github.com/Textualize/rich).

## Quick start

Every structure takes the data you already have and hands back something that
behaves the same way:

```python
from algoviz import VizList, VizStack, VizHeap, VizGrid

VizList([0] * 5)              # 1D and 2D tables
VizStack()                    # LIFO, top always labelled
VizHeap([5, 3, 8], max_heap=True)
VizGrid(['110', '011'])       # terrain plus a visited/queued overlay
```

## The structures

| Class | Backed by | Reach for it when |
| :--- | :--- | :--- |
| `VizList` | `MutableSequence` | 1D and 2D DP tables, prefix sums, any array problem |
| `VizStack` | `list` | Valid parentheses, monotonic stack, next greater element |
| `VizQueue` | `deque` | BFS, level-order traversal, shortest path |
| `VizDeque` | `deque` | Sliding window maximum, monotonic deque |
| `VizHeap` | `heapq` | Top-K, merge K lists, task scheduler, running median |
| `VizDict` | `MutableMapping` | Index maps, memoisation, seen-value lookups |
| `VizCounter` | `MutableMapping` | Frequency maps, group anagrams, sliding windows |
| `VizSet` | `MutableSet` | Seen-sets, cycle detection, longest consecutive |
| `VizGrid` | `list[list]` | Islands, flood fill, word search, shortest path |
| `VizLinkedList` | `ListNode` | Reverse a list, cycle detection, two pointers |
| `VizTree` | `TreeNode` | Binary tree and BST traversals |
| `VizTrie` | prefix tree | Word search, autocomplete, word break |
| `VizUnionFind` | rank + path compression | Connected components, redundant connection |

`ListNode` and `TreeNode` use the same `.val` / `.next` / `.left` / `.right`
shape LeetCode uses, so existing solutions paste in unchanged.

### Implementing it yourself

When the structure *is* the exercise, the library gets out of the way. Each of
these hands you the real nodes so your own code does the walking, and a hook to
light up the step you are on:

| Structure | Nodes | Drive the animation with |
| :--- | :--- | :--- |
| `VizTree` | `root_node`, `TreeNode` | `visit(node)` |
| `VizTrie` | `root_node`, `TrieNode` | `visit(node, writing=...)` |
| `VizLinkedList` | `head`, `nodes()`, `ListNode` | `set_pointer(name, node)` |

```python
from algoviz import TrieNode, VizTrie

viz = VizTrie(title_name='Trie')
node = viz.root_node
for char in 'cat':               # your insert, not the library's
    node.children.setdefault(char, TrieNode())
    node = node.children[char]
    viz.visit(node, writing=True)
node.is_word = True
```

## Demo gallery

Twenty-six runnable solutions live in [`demo/`](demo/). Every one is executed
and checked against the correct answer in CI, so none of them can rot.

Each demo writes its own algorithm. Where the library offers a shortcut that
would *be* the answer, the demo deliberately does not call it: the level-order
demo drives its own queue, the top-K demo maintains its own bounded heap, and
the trie demo builds its own nodes.

```bash
python demo/num_islands.py
```

#### Arrays and dynamic programming

| Demo | Problem | Idea |
| :--- | :--- | :--- |
| [`climbing_stairs.py`](demo/climbing_stairs.py) | [70](https://leetcode.com/problems/climbing-stairs/) Climbing Stairs | The smallest interesting DP |
| [`coin_change.py`](demo/coin_change.py) | [518](https://leetcode.com/problems/coin-change-ii/) Coin Change II | Count the ways to make an amount |
| [`house_robber.py`](demo/house_robber.py) | [198](https://leetcode.com/problems/house-robber/) House Robber | Skip-or-take DP |
| [`jump.py`](demo/jump.py) | [45](https://leetcode.com/problems/jump-game-ii/) Jump Game II | Fewest jumps to the last index |
| [`count_palin.py`](demo/count_palin.py) | [647](https://leetcode.com/problems/palindromic-substrings/) Palindromic Substrings | Expand a 2D table |
| [`longest_common_subsequence.py`](demo/longest_common_subsequence.py) | [1143](https://leetcode.com/problems/longest-common-subsequence/) LCS | The canonical 2D table |

#### Stacks, queues, and deques

| Demo | Problem | Idea |
| :--- | :--- | :--- |
| [`valid_parentheses.py`](demo/valid_parentheses.py) | [20](https://leetcode.com/problems/valid-parentheses/) Valid Parentheses | The classic stack warm-up |
| [`daily_temperatures.py`](demo/daily_temperatures.py) | [739](https://leetcode.com/problems/daily-temperatures/) Daily Temperatures | A monotonic stack of indices |
| [`min_stack.py`](demo/min_stack.py) | [155](https://leetcode.com/problems/min-stack/) Min Stack | Constant-time minimum via a paired stack |
| [`sliding_window_max.py`](demo/sliding_window_max.py) | [239](https://leetcode.com/problems/sliding-window-maximum/) Sliding Window Maximum | The monotonic deque |
| [`rotting_oranges.py`](demo/rotting_oranges.py) | [994](https://leetcode.com/problems/rotting-oranges/) Rotting Oranges | BFS measured in levels |

#### Heaps, maps, and sets

| Demo | Problem | Idea |
| :--- | :--- | :--- |
| [`kth_largest.py`](demo/kth_largest.py) | [215](https://leetcode.com/problems/kth-largest-element-in-an-array/) Kth Largest | A bounded min-heap |
| [`top_k_frequent.py`](demo/top_k_frequent.py) | [347](https://leetcode.com/problems/top-k-frequent-elements/) Top K Frequent | A heap capped at k |
| [`two_sum.py`](demo/two_sum.py) | [1](https://leetcode.com/problems/two-sum/) Two Sum | The hash-map one-pass |
| [`group_anagrams.py`](demo/group_anagrams.py) | [49](https://leetcode.com/problems/group-anagrams/) Group Anagrams | Bucket by sorted letters |
| [`longest_consecutive.py`](demo/longest_consecutive.py) | [128](https://leetcode.com/problems/longest-consecutive-sequence/) Longest Consecutive | A set, not a sort |

#### Grids, lists, trees, and graphs

| Demo | Problem | Idea |
| :--- | :--- | :--- |
| [`num_islands.py`](demo/num_islands.py) | [200](https://leetcode.com/problems/number-of-islands/) Number of Islands | BFS over a grid overlay |
| [`flood_fill.py`](demo/flood_fill.py) | [733](https://leetcode.com/problems/flood-fill/) Flood Fill | Recolour a connected region |
| [`reverse_linked_list.py`](demo/reverse_linked_list.py) | [206](https://leetcode.com/problems/reverse-linked-list/) Reverse Linked List | Pointer surgery, one node at a time |
| [`linked_list_cycle.py`](demo/linked_list_cycle.py) | [141](https://leetcode.com/problems/linked-list-cycle/) Linked List Cycle | Floyd's tortoise and hare |
| [`binary_tree_level_order.py`](demo/binary_tree_level_order.py) | [102](https://leetcode.com/problems/binary-tree-level-order-traversal/) Level Order | Drive the BFS queue yourself |
| [`validate_bst.py`](demo/validate_bst.py) | [98](https://leetcode.com/problems/validate-binary-search-tree/) Validate BST | Bounds, not just parents |
| [`implement_trie.py`](demo/implement_trie.py) | [208](https://leetcode.com/problems/implement-trie-prefix-tree/) Implement Trie | Walk and build the nodes yourself |
| [`word_break.py`](demo/word_break.py) | [139](https://leetcode.com/problems/word-break/) Word Break | A trie plus a DP sweep |
| [`number_of_provinces.py`](demo/number_of_provinces.py) | [547](https://leetcode.com/problems/number-of-provinces/) Number of Provinces | Union-find over a matrix |
| [`redundant_connection.py`](demo/redundant_connection.py) | [684](https://leetcode.com/problems/redundant-connection/) Redundant Connection | The edge that closes a cycle |

## Highlights

### Stack

The top is always labelled, and a popped value stays visible for exactly one
frame so you can see what left.

```python
from algoviz import VizStack

stack = VizStack(title_name='Parens')
for char in '([])':
    stack.push(char) if char in '([' else stack.pop()
```

```text
       Parens
┏━━━━━━━━━━┳━━━━━━━┓
┃          ┃ value ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ ✗ popped │ [     │
│ ← top    │ (     │
└──────────┴───────┘
```

### Heap

Renders the backing array **and** the tree it represents, which is the part a
flat list never shows you.

```python
from algoviz import VizHeap

heap = VizHeap([5, 3, 8, 1], title_name='Min Heap')
heap.push(2)
```

```text
      Min Heap
┏━━━┳━━━┳━━━┳━━━┳━━━┓
┃ 0 ┃ 1 ┃ 2 ┃ 3 ┃ 4 ┃
┡━━━╇━━━╇━━━╇━━━╇━━━┩
│ 1 │ 2 │ 8 │ 5 │ 3 │
└───┴───┴───┴───┴───┘
Min Heap (tree)
1
├── 2
│   ├── 5
│   └── 3
└── 8
```

Ordering comes straight from the standard library's `heapq`, so what you see is
the real thing rather than a reimplementation. Pass `max_heap=True` for a
max-heap.

### Grid

Grid cells usually hold terrain. What matters is the **overlay**: which cells
are visited, queued, or on the current path.

```python
from algoviz import VizGrid

grid = VizGrid(['11000', '11000', '00100'], title_name='Islands')
grid.mark_start(0, 0)
for row, col in grid.neighbors(0, 0):
    grid.mark_queued(row, col)
```

`neighbors()` handles bounds for you, `diagonal=True` gives all eight, and
`grid.batch()` suspends redrawing so you get one frame per BFS level instead of
one per cell.

### Linked list

Named pointers make two-pointer and cycle problems legible, and a cyclic list
renders its back-edge instead of hanging.

```python
from algoviz import VizLinkedList

linked = VizLinkedList([1, 2, 3, 4, 5])
slow = fast = linked.head
while fast and fast.next:
    slow, fast = slow.next, fast.next.next
    linked.set_pointer('slow', slow)
    linked.set_pointer('fast', fast)
```

### Union-find

Path compression and union by rank are both implemented, and the render shows
each element's parent alongside the current components, so you can watch
compression flatten the tree.

```python
from algoviz import VizUnionFind

uf = VizUnionFind(5)
uf.union(0, 1)
uf.union(3, 4)
uf.component_count  # 3
```

## Configuration

Every structure accepts the same settings, as keyword overrides or a shared
`VizConfig`:

```python
from algoviz import VizConfig, VizList

VizList([1, 2, 3], get_color='green', set_color='magenta', sleep_time=0.3)

quiet = VizConfig(auto_print=False, show_init=False)
dp = VizList([0] * 5, config=quiet)
dp[2] = 7
dp.show()  # draw only when you ask
```

| Setting | Default | Meaning |
| :--- | :--- | :--- |
| `get_color` | `blue` | Colour for cells that were read |
| `set_color` | `red` | Colour for cells that were written |
| `sleep_time` | `0` | Seconds to pause after each frame |
| `auto_print` | `True` | Redraw automatically after every write |
| `show_init` | `True` | Draw the initial state on construction |
| `show_header` | `True` | Show the index header row |

Set `sleep_time` and let it run to get an animation. Set `auto_print=False` and
call `.show()` yourself to control exactly which frames appear.

## Development

This project uses [uv](https://github.com/astral-sh/uv).

```bash
uv sync             # create the environment
uv run pytest       # 547 tests
uv run pytest --cov # with coverage
uv run ruff check   # lint
uv run ruff format  # format
uv run mypy         # type check
uv build            # build sdist and wheel
```

CI runs the suite on Python 3.10 through 3.14 across Linux, macOS, and Windows,
plus lint, format, types, and a packaging check.

## Upgrading from 0.2.x

Version 0.3.0 rewrote the core. Three changes can affect existing code:

1. **`VizList` is a `MutableSequence`, not a `list` subclass.** It behaves like
   a list everywhere that matters, but `isinstance(dp, list)` is now `False`.
   The old inheritance was broken regardless: the real `list` storage was
   always empty, so anything reading it saw the wrong data. Use `dp.data` when
   you need a plain list.
2. **`a + b` no longer mutates `a`.** The old `__add__` called `extend`, so
   concatenation modified the left operand in place. It now returns a new list,
   as `+` should.
3. **`print(expr)` is sandboxed.** Expressions still use `#` for the underlying
   data, but they evaluate with no builtins and no access to internals.

Python 3.9 users can stay on 0.2.3.

## Contributing

Issues and pull requests are welcome. Please run `uv run pytest`,
`uv run ruff check`, and `uv run mypy` before opening one. New demos should
include their expected output in `tests/test_demos.py`, which is what keeps the
gallery honest.

## License

MIT. See [LICENSE.txt](LICENSE.txt).
