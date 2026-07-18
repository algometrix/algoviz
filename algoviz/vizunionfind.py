"""A disjoint-set union that draws its forest and its grouped components.

`VizUnionFind` is its own structure, not a mapping or a set -- there is no
single natural container protocol for "which elements are connected to
which", so it exposes its own small API (`find`, `union`, `connected`,
`components`) directly on `VizBase` instead of forcing a fit onto
`MutableMapping`/`MutableSet` the way the other structures in this package
do.

Path compression and union-by-size are both implemented for real: `find`
flattens every pointer on the path to the root, and `union` always attaches
the smaller component under the larger one's root, not the other way round.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from typing import Any

from rich.console import Group, RenderableType
from rich.table import Table
from rich.tree import Tree

from algoviz.core import VizBase, VizConfig, paint

__all__ = ["VizUnionFind"]


class VizUnionFind(VizBase):
    """A disjoint-set union with path compression and union-by-size.

    Construct from a count (`VizUnionFind(5)` makes elements `0..4`) or
    from an iterable of hashable labels (`VizUnionFind(['a', 'b', 'c'])`).

    Every `find`/`union`/`connected` call redraws once, highlighting the
    elements it traversed (`get_color`) and, if path compression or a
    union changed a parent pointer, the elements it rewired (`set_color`).
    """

    def __init__(
        self,
        initial: int | Iterable[Hashable],
        title_name: str = "UnionFind",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Build from an element count or an iterable of element labels.

        Args:
            initial: An int `n` creates elements `0..n-1`; an iterable of
                hashable labels creates one element per item.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this union-find is nested.
            **overrides: Individual `VizConfig` fields to override.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        elements = range(initial) if isinstance(initial, int) else initial
        self._parent: dict[Hashable, Hashable] = {}
        self._size: dict[Hashable, int] = {}
        for element in elements:
            self._parent[element] = element
            self._size[element] = 1
        self._component_count = len(self._parent)

        if self.config.show_init:
            self.show(f"{self.title} Init")

    # -- union-find protocol -------------------------------------------------

    def find(self, x: Hashable) -> Hashable:
        """Return the root of `x`'s component, then redraw.

        Flattens every pointer on the path from `x` to its root (path
        compression), so repeated calls on the same chain get cheaper.

        Raises:
            KeyError: If `x` is not an element of this union-find.
        """
        self._check_known(x)
        root = self._compress_and_get_root(x)
        self._auto_show()
        return root

    def union(self, a: Hashable, b: Hashable) -> bool:
        """Union the components containing `a` and `b`, then redraw.

        The smaller component's root is attached under the larger one's
        (union-by-size), which keeps the resulting trees shallow.

        Returns:
            True if a union happened. False if `a` and `b` were already in
            the same component, in which case this is a no-op.

        Raises:
            KeyError: If `a` or `b` is not an element of this union-find.
        """
        self._check_known(a)
        self._check_known(b)
        root_a = self._find_root(a)
        root_b = self._find_root(b)
        self.highlights.mark_get(a, b)

        if root_a == root_b:
            self._auto_show()
            return False

        small, big = (
            (root_a, root_b)
            if self._size[root_a] < self._size[root_b]
            else (root_b, root_a)
        )
        self._parent[small] = big
        self._size[big] += self._size[small]
        self._component_count -= 1
        self.highlights.mark_set(small)
        self._auto_show()
        return True

    def connected(self, a: Hashable, b: Hashable) -> bool:
        """True iff `a` and `b` are in the same component, then redraw.

        Compresses the paths for both `a` and `b` (same as `find`), shown
        as a single redraw rather than two.

        Raises:
            KeyError: If `a` or `b` is not an element of this union-find.
        """
        self._check_known(a)
        self._check_known(b)
        root_a = self._compress_and_get_root(a)
        root_b = self._compress_and_get_root(b)
        self._auto_show()
        return root_a == root_b

    @property
    def component_count(self) -> int:
        """Number of disjoint components remaining."""
        return self._component_count

    def component_size(self, x: Hashable) -> int:
        """Size of the component containing `x`. A pure, untracked read.

        Raises:
            KeyError: If `x` is not an element of this union-find.
        """
        self._check_known(x)
        root = self._find_root(x)
        return self._size[root]

    def components(self) -> dict[Hashable, list[Hashable]]:
        """Map each root to the members of its component.

        A pure query: does not mutate parent pointers, record highlights,
        or redraw.
        """
        groups: dict[Hashable, list[Hashable]] = {}
        for element in self._parent:
            root = self._find_root(element)
            groups.setdefault(root, []).append(element)
        return groups

    # -- internal traversal ---------------------------------------------------

    def _check_known(self, x: Hashable) -> None:
        """Raise KeyError naming `x` if it was never added to this DSU."""
        if x not in self._parent:
            raise KeyError(f"{x!r} is not an element of this VizUnionFind")

    def _find_root(self, x: Hashable) -> Hashable:
        """Walk parent pointers to the root, without mutating anything."""
        node = x
        while self._parent[node] != node:
            node = self._parent[node]
        return node

    def _compress_and_get_root(self, x: Hashable) -> Hashable:
        """Find `x`'s root and flatten every pointer on the way to it."""
        path = [x]
        while self._parent[path[-1]] != path[-1]:
            path.append(self._parent[path[-1]])
        root = path[-1]

        self.highlights.mark_get(*path)
        changed = [node for node in path[:-1] if self._parent[node] != root]
        for node in changed:
            self._parent[node] = root
        if changed:
            self.highlights.mark_set(*changed)
        return root

    # -- Python protocol -------------------------------------------------------

    def __repr__(self) -> str:
        """A compact view of the current parent pointers."""
        return f"VizUnionFind({dict(self._parent)!r})"

    # -- viz plumbing ---------------------------------------------------------

    def _eval_target(self) -> Any:
        return self._parent

    def _renderable(self, title: str | None = None) -> RenderableType:
        # `show()` already suspends tracking for the whole render (see
        # `VizBase.show`), and everything below reads `self._parent`
        # directly (never `self.find`), so nothing here mutates a parent
        # pointer or records a highlight as a side effect of drawing.
        table = self._element_table(title)
        tree = self._component_tree()
        return Group(table, tree)

    def _element_table(self, title: str | None) -> Table:
        """A table of every element, its direct parent, and its root."""
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        table.add_column("element")
        table.add_column("parent")
        table.add_column("root")
        if not self._parent:
            table.caption = "(empty)"
            return table
        for element in self._parent:
            style = self.highlights.style_for(element, self.config)
            root = self._find_root(element)
            table.add_row(
                paint(element, style),
                paint(self._parent[element], None),
                paint(root, None),
            )
        return table

    def _component_tree(self) -> Tree:
        """A `root -> members` view of the current components."""
        tree = Tree("components")
        groups = self.components()
        # Sort by str(root): roots are `Hashable`, not necessarily mutually
        # comparable (e.g. an int label and a str label together would raise
        # TypeError under a direct sort).
        for root in sorted(groups, key=str):
            members = groups[root]
            branch = tree.add(f"{root} (size {len(members)})")
            for member in members:
                style = self.highlights.style_for(member, self.config)
                branch.add(paint(member, style))
        return tree
