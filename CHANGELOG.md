# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Top-level exports: everything is importable from `algoviz` directly.
- 530 tests, 95% coverage, and 26 runnable demos in `demo/` that are executed
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
- Removed a stale `README.txt` that had drifted from `README.md`.

## [0.2.3] - 2021

Initial published release: `VizList` with 1D and 2D table rendering.

[0.3.0]: https://github.com/algometrix/algoviz/releases/tag/v0.3.0
[0.2.3]: https://github.com/algometrix/algoviz/releases/tag/v0.2.3
