# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `VizStack` bar column, opted into with `bar_of` and tuned with `bar_label`,
  `bar_min`, `bar_max`, and `bar_width`. Monotonic-stack algorithms order
  their elements by a magnitude and typically store indices into some other
  array, so the rendered column read `2, 3, 4` and the invariant the
  algorithm maintains was invisible. `bar_of` maps a stored element back to
  the magnitude it stands for and draws it as a bar, turning "temperatures
  decrease from the bottom of the stack up" into a visible staircase. Bars
  are measured against the magnitude range rather than against zero, since
  clustered values would otherwise all render as identical full bars; the
  magnitude is printed beside each bar to keep the truncated scale honest.
  Stacks with no `bar_of` render exactly as before.
- `demo/daily_temperatures.py` now shows the invariant being maintained: it
  announces each incoming day, then you watch every bar shorter than that
  day's temperature pop off, one frame each, until the staircase is restored.

## [0.4.0] - 2026-07-19

### Added

- `VizList.set_pointer(name, index)`, `clear_pointers()`, and a `pointers`
  property. Two-pointer problems are about where the pointers are, and until
  now only `VizLinkedList` could show one. Labels are drawn in a row under the
  values and stay put until the pointer moves, unlike a highlight, which
  clears every frame. Pointers take an index rather than a value, since that
  is what the algorithm already holds; an out-of-range index is remembered but
  not drawn, so loops that terminate by walking off the end need no guard.
- Four demos this unlocks: Sort Colors (the Dutch national flag partition),
  Container With Most Water, 3Sum, and Subarray Sum Equals K. That last one is
  deliberately not a two-pointer solution, since negative numbers break the
  sliding window, and it pairs `VizList` with `VizDict` to show the prefix-sum
  map filling up.

## [0.3.0] - 2026-07-18

A rewrite of the core plus ten new data structures.

### Added

- **New structures**: `VizStack`, `VizQueue`, `VizDeque`, `VizHeap`,
  `VizDict`, `VizCounter`, `VizSet`, `VizGrid`, `VizLinkedList`, `VizTree`,
  `VizTrie`, and `VizUnionFind`, covering the structures LeetCode problems
  actually use.
- `VizHeap` renders the backing array and the tree it represents side by side.
  Ordering is delegated to `heapq`, so it is the real algorithm.
- `VizGrid` separates cell values from an overlay (`visited`, `queued`, `path`,
  `start`, `target`) with a documented precedence, plus `neighbors()` and
  `in_bounds()` helpers and a `batch()` context manager for one frame per BFS
  level rather than per cell.
- `VizLinkedList` supports named pointers for two-pointer problems and renders
  a cycle as a back-edge instead of hanging. `head` is assignable and `nodes()`
  exposes the real nodes, so pointer-rewiring problems work directly.
- `VizTree` builds from the level-order list with `None` padding that problems
  are stated in, and exposes all four traversals.
- `TrieNode` is public and `VizTrie` exposes `root_node` and `visit()`, so a
  student can implement insert and search by hand and still see each step.
  This matches the hooks `VizTree` and `VizLinkedList` already had.
- `VizTree.find()` locates a value in a tree of any shape. `search()` assumes
  BST ordering and silently returns `None` for present values on an unordered
  tree, which is now documented on `search` itself.
- Top-level exports: everything is importable from `algoviz` directly.
- 560 tests, 95% coverage, and 26 runnable demos in `demo/` that are executed
  and checked against the correct answers in CI.

### Changed

- **`VizList` is now a `MutableSequence` rather than a `list` subclass.**
  `isinstance(dp, list)` is `False`. The previous inheritance was broken: the
  real `list` storage was never populated, so any consumer reading it saw an
  empty list.
- **`print(expr)` is sandboxed.** `#` still refers to the underlying data, but
  expressions evaluate with no builtins and no access to instance internals.
  The `#` substitution no longer corrupts hashes inside string literals.
- Packaging moved from `setup.py` plus `setup.cfg` (which disagreed on both the
  package name and the version) to a single `pyproject.toml` with a
  `hatchling` backend and a committed `uv.lock`.
- Minimum Python is now 3.10.

### Fixed

- **Render state was shared across every instance.** The `status` flag lived on
  the class, so one structure drawing itself suppressed access tracking on
  every other structure in the process. It is now a `ContextVar` with a depth
  counter, making it re-entrant and safe across threads and async tasks.
- **`a + b` mutated `a`.** `__add__` called `extend` on the underlying list, so
  concatenation modified the left operand in place. It now returns a new list.
- **`pop()` had unreachable code**: a `show_list` call after its `return`, so
  popping never redrew.
- **Values containing rich markup were swallowed.** A cell holding `[red]`
  was parsed as a style tag and vanished; values are now escaped.
- **`__hash__` forwarded to `list.__hash__`** (which is `None`), producing a
  confusing `TypeError`. `VizList` is now cleanly unhashable, like a list.
- `render_list` raised `UnboundLocalError` on the 2D path.
- The license file was named `LICENSE.txt ` with a trailing space, which broke
  metadata generation and therefore `pip install`.
- Three demos delegated the problem's core algorithm to the library instead of
  demonstrating it: the trie demo called the library's `insert`/`search` when
  implementing those *is* the exercise, the level-order demo called
  `VizTree.level_order()` instead of driving a queue, and the top-K demo called
  `nlargest` instead of maintaining a bounded heap. All three now write the
  algorithm. The level-order demo was additionally broken, using BST `search`
  on an unordered tree, so it silently highlighted only 3 of 5 nodes.
- `VizTrie.__len__` returned a cached count that went stale as soon as a caller
  set `is_word` directly; it now counts from the nodes.
- Removed a stale `README.txt` that had drifted from `README.md`.

## [0.2.3] - 2021

Initial published release: `VizList` with 1D and 2D table rendering.

[0.4.0]: https://github.com/algometrix/algoviz/releases/tag/v0.4.0
[0.3.0]: https://github.com/algometrix/algoviz/releases/tag/v0.3.0
[0.2.3]: https://github.com/algometrix/algoviz/releases/tag/v0.2.3
