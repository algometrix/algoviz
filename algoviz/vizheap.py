"""A heap that draws its backing array and its tree shape side by side.

`VizHeap` does not reimplement sift-up/sift-down. Every mutation delegates to
the stdlib `heapq` module, which is where heap correctness has to come from.
The only extra logic here is the min/max-heap trick (negate on the way in and
out) and the two-view rendering: a flat array table, exactly like `VizList`,
plus a `rich.tree.Tree` built from the same array using the `2i+1`/`2i+2`
child rule. Seeing both at once is the point -- the array is what `heapq`
actually stores, and the tree is why that array is a heap.
"""

from __future__ import annotations

import heapq
from collections.abc import Callable, Iterable, Iterator
from typing import Any

from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from algoviz.core import VizBase, VizConfig, paint

__all__ = ["VizHeap"]


class VizHeap(VizBase):
    """A min-heap or max-heap over a `heapq`-managed array.

    Reads of the root (`peek`, `top`, `pop`) are highlighted in `get_color`;
    the slot a pushed value lands in is highlighted in `set_color`. Both
    views -- the backing array and the tree -- show the same highlights, so
    a reader can watch one index light up in both places at once.

    Max-heap mode negates values on the way in and undoes the negation on
    the way out, the standard trick for building a max-heap on top of a
    min-heap-only library. That only works for values that support unary
    negation and stay orderable under it (plain numerics), so constructing
    or pushing anything else with `max_heap=True` fails immediately with a
    clear error instead of silently corrupting the heap order.
    """

    def __init__(
        self,
        iterable: Iterable[Any] = (),
        title_name: str = "Heap",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        max_heap: bool = False,
        **overrides: Any,
    ) -> None:
        """Build a heap from `iterable`, then draw its initial state.

        `max_heap=True` negates every value on the way in (and back out
        on every read), so `iterable` must hold plain orderable numerics
        in that mode -- anything else fails immediately with a clear
        error rather than corrupting heap order later.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._max_heap = max_heap
        self._heap: list[Any] = [self._encode(value) for value in iterable]
        heapq.heapify(self._heap)

        if self.config.show_init:
            self.show(f"{self.title} Init")

    # -- min/max-heap encoding ----------------------------------------------

    def _encode(self, value: Any) -> Any:
        """Turn a user-facing value into what the backing array stores."""
        if not self._max_heap:
            return value
        return self._negate(value)

    def _decode(self, stored: Any) -> Any:
        """Turn a stored array entry back into the value the user gave."""
        if not self._max_heap:
            return stored
        return self._negate(stored)

    @staticmethod
    def _negate(value: Any) -> Any:
        """Negate `value`, or fail clearly if it cannot be negated.

        Negation is its own inverse, so this one helper both encodes values
        going into a max-heap and decodes them coming back out.
        """
        try:
            return -value
        except TypeError as error:
            raise ValueError(
                "VizHeap(max_heap=True) only supports orderable numerics "
                f"that can be negated; got {value!r} of type "
                f"{type(value).__name__}. Use max_heap=False instead, or "
                "push plain numerics."
            ) from error

    def _locate(self, stored: Any) -> int | None:
        """Index of the exact object `stored` in the backing array.

        Identity, not equality, is what matters: `heapq` only ever moves
        object references around, so the reference just pushed is either
        still the exact object at its resting slot or it was popped back
        out again. Using `is` also makes duplicate *values* a non-issue --
        equal values are indistinguishable in a heap, so highlighting
        whichever slot holds this particular reference is always correct.
        """
        for index, item in enumerate(self._heap):
            if item is stored:
                return index
        return None

    # -- mutation ------------------------------------------------------------

    def push(self, value: Any) -> None:
        """Push `value` onto the heap, then redraw with its slot marked."""
        stored = self._encode(value)
        heapq.heappush(self._heap, stored)
        self.highlights.clear()
        index = self._locate(stored)
        if index is not None:
            self.highlights.mark_set(index)
        self._auto_show()

    def pop(self) -> Any:
        """Remove and return the root.

        Draws twice: once with the root highlighted as the thing about to
        be removed, once after removal showing the heap that `heapq`'s
        sift-down settled on.
        """
        if not self._heap:
            raise IndexError("pop from an empty VizHeap")
        self.highlights.clear()
        self.highlights.mark_get(0)
        self._auto_show()

        stored = heapq.heappop(self._heap)
        self.highlights.clear()
        self._auto_show()
        return self._decode(stored)

    def peek(self) -> Any:
        """Return the root without removing it, highlighting it in place."""
        if not self._heap:
            raise IndexError("peek from an empty VizHeap")
        self.highlights.clear()
        self.highlights.mark_get(0)
        self._auto_show()
        return self._decode(self._heap[0])

    def top(self) -> Any:
        """Alias for `peek`, matching common priority-queue vocabulary."""
        return self.peek()

    def pushpop(self, value: Any) -> Any:
        """Push `value`, then pop and return the new root, as one step.

        Delegates to `heapq.heappushpop`, which is cheaper than a separate
        push followed by a pop: when `value` is already the item that
        would be popped immediately, it is returned unchanged and never
        enters the heap at all.
        """
        stored = self._encode(value)
        self.highlights.clear()
        result = heapq.heappushpop(self._heap, stored)
        if result is not stored:
            index = self._locate(stored)
            if index is not None:
                self.highlights.mark_set(index)
        self._auto_show()
        return self._decode(result)

    def replace(self, value: Any) -> Any:
        """Pop and return the root, then push `value`, as one atomic step.

        Unlike `pushpop`, the current root is always discarded and `value`
        always enters the heap, even when `value` would itself have been
        the smallest/largest item.
        """
        if not self._heap:
            raise IndexError("replace on an empty VizHeap")
        self.highlights.clear()
        self.highlights.mark_get(0)
        self._auto_show()

        stored = self._encode(value)
        old = heapq.heapreplace(self._heap, stored)
        self.highlights.clear()
        index = self._locate(stored)
        if index is not None:
            self.highlights.mark_set(index)
        self._auto_show()
        return self._decode(old)

    # -- queries ---------------------------------------------------------

    def nsmallest(
        self, n: int, key: Callable[[Any], Any] | None = None
    ) -> list[Any]:
        """The `n` smallest logical values, regardless of heap mode."""
        self._check_key_supported(key)
        return heapq.nsmallest(n, self.data, key=key)

    def nlargest(
        self, n: int, key: Callable[[Any], Any] | None = None
    ) -> list[Any]:
        """The `n` largest logical values, regardless of heap mode."""
        self._check_key_supported(key)
        return heapq.nlargest(n, self.data, key=key)

    def _check_key_supported(self, key: Callable[[Any], Any] | None) -> None:
        """Reject a custom `key` on a max-heap before it produces garbage.

        A max-heap only works because it negates plain numerics; a `key`
        function pulls its own value out of each item, and negating *that*
        would only be meaningful if this method reached into the encoding
        itself, which it deliberately does not. Refusing the combination
        beats silently ignoring `max_heap` or silently ignoring `key`.
        """
        if self._max_heap and key is not None:
            raise ValueError(
                "VizHeap(max_heap=True) does not support a custom key for "
                "nsmallest/nlargest. Build a min-heap and negate the "
                "key's output yourself instead."
            )

    def __len__(self) -> int:
        """Number of items on the heap."""
        return len(self._heap)

    def __iter__(self) -> Iterator[Any]:
        """Iterate logical values in backing-array order (not sorted)."""
        return iter(self.data)

    def __bool__(self) -> bool:
        """True when the heap holds at least one item."""
        return bool(self._heap)

    def __contains__(self, value: Any) -> bool:
        """True when `value` is currently on the heap."""
        return value in self.data

    def __repr__(self) -> str:
        """Debug repr showing logical contents and heap mode."""
        return f"VizHeap({self.data!r}, max_heap={self._max_heap!r})"

    @property
    def data(self) -> list[Any]:
        """The logical contents in backing-array order.

        Negation from max-heap mode is undone. Reading this does not
        record a highlight.
        """
        return [self._decode(stored) for stored in self._heap]

    def _eval_target(self) -> Any:
        return self.data

    # -- rendering -----------------------------------------------------------

    def _renderable(self, title: str | None = None) -> RenderableType:
        heading = title or self.title
        decoded = self.data
        return Group(
            self._array_table(decoded, heading),
            Text(f"{heading} (tree)", style="bold"),
            self._tree(decoded),
        )

    def _array_table(self, decoded: list[Any], heading: str) -> Table:
        """The backing array as a table, indices over values."""
        table = Table(title=heading, show_header=self.config.show_header)
        for index in range(len(decoded)):
            table.add_column(str(index))
        cells = tuple(
            paint(value, self.highlights.style_for(index, self.config))
            for index, value in enumerate(decoded)
        )
        if cells:
            table.add_row(*cells)
        return table

    def _tree(self, decoded: list[Any]) -> Tree:
        """The same array as a tree, children at `2i+1` and `2i+2`."""
        if not decoded:
            return Tree(paint("(empty)", None))
        root = Tree(
            paint(decoded[0], self.highlights.style_for(0, self.config))
        )
        self._attach_children(root, decoded, 0)
        return root

    def _attach_children(
        self, node: Tree, decoded: list[Any], index: int
    ) -> None:
        """Recursively attach the heap-children of `index` to `node`."""
        for child_index in (2 * index + 1, 2 * index + 2):
            if child_index >= len(decoded):
                continue
            style = self.highlights.style_for(child_index, self.config)
            child = node.add(paint(decoded[child_index], style))
            self._attach_children(child, decoded, child_index)
