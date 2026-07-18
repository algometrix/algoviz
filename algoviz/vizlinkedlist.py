"""A singly linked list that draws itself as a horizontal chain.

`ListNode` mirrors the shape LeetCode hands out in every linked-list
problem (`.val`, `.next`), so a solution can be pasted in unmodified and
wrapped in a `VizLinkedList` for visualization. `VizLinkedList` itself
never rewrites a pasted algorithm's nodes; it only reads the chain.

Cycles are a first-class case rather than a bug to work around: every
traversal here (`to_list`, `__len__`, `__iter__`, rendering) walks the
chain with a visited-id set so a cyclic list can never hang the caller,
and the render marks the back-edge explicitly instead of silently
truncating it.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable, Iterator
from typing import Any

from rich.console import RenderableType
from rich.table import Table

from algoviz.core import VizBase, VizConfig, glyph, paint

__all__ = ["ListNode", "VizLinkedList"]

_CYCLE_MARK = glyph("↺", "@")  # back-edge marker: "-> ↺[index]"
_POINTER_MARK = glyph("↑", "^")  # pointer label marker: "↑ slow"


class ListNode:
    """A singly linked list node, LeetCode-shape compatible.

    Deliberately plain: just `.val` and `.next`, so code written against
    LeetCode's own `ListNode` works against this one without changes.
    """

    def __init__(self, val: Any = 0, next: ListNode | None = None) -> None:
        """Create a node holding `val`, linked to `next`."""
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        """Show the node's value; `.next` is omitted to stay finite."""
        return f"ListNode({self.val!r})"


class VizLinkedList(VizBase):
    """A singly linked list rendered as `1 -> 2 -> 3 -> None`.

    Reads happen through named pointers (`set_pointer`), which is how
    two-pointer and cycle-detection algorithms are visualized: each
    pointer's target is highlighted in `get_color` for one frame and
    labelled with an arrow underneath on every frame until it moves.
    Structural writes (`append`, `prepend`, `reverse`) highlight in
    `set_color` instead.
    """

    def __init__(
        self,
        source: ListNode | Iterable[Any] | None = None,
        title_name: str = "LinkedList",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Wrap `source`: a head node, an iterable of values, or `None`."""
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._head = self._coerce(source)
        self._pointers: dict[str, ListNode] = {}

        if self.config.show_init:
            self.show(f"{self.title} Init")

    @staticmethod
    def _coerce(source: ListNode | Iterable[Any] | None) -> ListNode | None:
        """Turn `source` into a head node, building a chain if needed."""
        if source is None or isinstance(source, ListNode):
            return source
        nodes = [ListNode(value) for value in source]
        for current, following in itertools.pairwise(nodes):
            current.next = following
        return nodes[0] if nodes else None

    @classmethod
    def from_list(
        cls,
        values: Iterable[Any],
        title_name: str = "LinkedList",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> VizLinkedList:
        """Build a chain of `ListNode`s from `values`."""
        return cls(
            list(values),
            title_name=title_name,
            config=config,
            parent=parent,
            **overrides,
        )

    # -- safe traversal ------------------------------------------------

    def _safe_nodes(self) -> tuple[list[ListNode], int | None]:
        """Nodes in traversal order, visiting each node at most once.

        Returns the node list and, when the chain loops back on itself,
        the index within that list where the cycle reconnects. Walking
        with a visited-id set (rather than following `.next` forever)
        is what keeps every public method below safe on a cyclic list.
        """
        nodes: list[ListNode] = []
        seen: dict[int, int] = {}
        node = self._head
        while node is not None:
            if id(node) in seen:
                return nodes, seen[id(node)]
            seen[id(node)] = len(nodes)
            nodes.append(node)
            node = node.next
        return nodes, None

    @property
    def has_cycle(self) -> bool:
        """True when the chain loops back into itself."""
        return self._safe_nodes()[1] is not None

    # -- sequence-ish protocol -------------------------------------------

    def to_list(self) -> list[Any]:
        """Values in traversal order, stopping before a cycle repeats."""
        return [node.val for node in self._safe_nodes()[0]]

    def __len__(self) -> int:
        """Number of distinct nodes reachable from the head."""
        return len(self._safe_nodes()[0])

    def __iter__(self) -> Iterator[Any]:
        """Iterate values head-to-tail, stopping before a cycle repeats."""
        return iter(self.to_list())

    def __contains__(self, value: Any) -> bool:
        """True when `value` appears anywhere in the chain."""
        return value in self.to_list()

    def __repr__(self) -> str:
        """Values in traversal order, formatted like a list literal."""
        return repr(self.to_list())

    # -- structural writes -------------------------------------------------

    def append(self, val: Any) -> None:
        """Add `val` as the new tail, then redraw.

        Raises:
            ValueError: If the list is cyclic, since it has no tail.
        """
        nodes, cycle_start = self._safe_nodes()
        if cycle_start is not None:
            raise ValueError("cannot append to a cyclic linked list")
        new_node = ListNode(val)
        if nodes:
            nodes[-1].next = new_node
        else:
            self._head = new_node
        self.highlights.mark_set(id(new_node))
        self._auto_show()

    def prepend(self, val: Any) -> None:
        """Insert `val` as the new head, then redraw."""
        self._head = ListNode(val, self._head)
        self.highlights.mark_set(id(self._head))
        self._auto_show()

    def reverse(self) -> None:
        """Reverse the chain in place, then redraw.

        Raises:
            ValueError: If the list is cyclic, since reversal would
                leave the back-edge pointing at a node that no longer
                precedes it.
        """
        _, cycle_start = self._safe_nodes()
        if cycle_start is not None:
            raise ValueError("cannot reverse a cyclic linked list")
        previous: ListNode | None = None
        current = self._head
        while current is not None:
            following = current.next
            current.next = previous
            previous = current
            current = following
        self._head = previous
        self.highlights.clear()
        if self._head is not None:
            self.highlights.mark_set(id(self._head))
        self._auto_show()

    # -- pointers ------------------------------------------------------

    def set_pointer(self, name: str, node: ListNode | None) -> None:
        """Point the named pointer at `node`, then redraw.

        The pointer's label is drawn under `node` on every frame until
        it moves again; passing `node=None` removes the pointer. The
        node itself is highlighted in `get_color` for this one frame,
        matching how a read is highlighted everywhere else in algoviz.
        """
        if node is None:
            self._pointers.pop(name, None)
        else:
            self._pointers[name] = node
            self.highlights.mark_get(id(node))
        self._auto_show()

    @property
    def pointers(self) -> dict[str, ListNode]:
        """A snapshot of the current pointer names and their nodes."""
        return dict(self._pointers)

    def _pointer_names_by_id(self) -> dict[int, list[str]]:
        """Pointer names grouped by the id of the node they target."""
        names_by_id: dict[int, list[str]] = {}
        for name, node in sorted(self._pointers.items()):
            names_by_id.setdefault(id(node), []).append(name)
        return names_by_id

    # -- viz plumbing ------------------------------------------------------

    @property
    def head(self) -> ListNode | None:
        """The first node in the chain, or `None` when empty."""
        return self._head

    @head.setter
    def head(self, node: ListNode | None) -> None:
        """Point the list at a new head, then redraw.

        Rewiring `.next` by hand and reassigning the head is exactly what
        reverse-a-list and reorder-a-list ask for, so this has to be
        writable. The redraw picks up whatever shape the chain now has,
        including one the caller has just turned into a cycle.
        """
        if node is not None and not isinstance(node, ListNode):
            raise TypeError(f"head must be a ListNode or None, got {node!r}")
        self._head = node
        self.highlights.clear()
        if node is not None:
            self.highlights.mark_set(id(node))
        self._auto_show()

    def nodes(self) -> list[ListNode]:
        """The nodes themselves, head-to-tail, stopping before a repeat.

        Handing back the real nodes is what lets a caller wire up a cycle
        (`lst.nodes()[-1].next = lst.nodes()[1]`) or hold a reference to
        walk with. Cycle-safe, so it terminates on a looped chain.
        """
        return list(self._safe_nodes()[0])

    @property
    def data(self) -> list[Any]:
        """Values in traversal order. Reading it is not tracked."""
        return self.to_list()

    def _eval_target(self) -> Any:
        return self.to_list()

    def _renderable(self, title: str | None = None) -> RenderableType:
        nodes, cycle_start = self._safe_nodes()
        has_none_tail = cycle_start is None
        width = len(nodes) + (1 if has_none_tail else 0)

        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        for index in range(width):
            table.add_column(str(index))

        names_by_id = self._pointer_names_by_id()
        value_cells: list[str] = []
        pointer_cells: list[str] = []
        for index, node in enumerate(nodes):
            style = self.highlights.style_for(id(node), self.config)
            cell = paint(node.val, style)
            if index < len(nodes) - 1:
                cell += " ->"
            elif cycle_start is not None:
                cell += f" -> {_CYCLE_MARK}[{cycle_start}]"
            value_cells.append(cell)

            names = names_by_id.get(id(node))
            pointer_cells.append(
                f"{_POINTER_MARK} {', '.join(names)}" if names else ""
            )

        if has_none_tail:
            value_cells.append("None")
            pointer_cells.append("")

        table.add_row(*value_cells)
        if any(pointer_cells):
            table.add_row(*pointer_cells)
        return table
