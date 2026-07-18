"""Key/value and membership structures that draw themselves.

`VizDict`, `VizCounter`, and `VizSet` are `MutableMapping` / `MutableSet`,
not `dict` / `set` subclasses -- the same reasoning as `VizList` vs `list`
(see vizlist.py's module docstring): subclassing a builtin keeps the real
data in a separate attribute while the builtin's own C-level storage stays
empty, so any fast path that reads that storage directly sees the wrong
thing. Delegating explicitly to a plain `dict` underneath is correct at the
cost of a little speed, which does not matter for a visualization aid.

The `MutableMapping` and `MutableSet` ABCs provide several methods (`pop`,
`popitem`, `setdefault`, `update`, `clear`) as mixins built from the
abstract methods. Several of those mixins call the tracked methods more
than once per logical user action -- e.g. the default `clear()` for a set
calls `pop()` in a loop, which would redraw once per element instead of
once for the whole clear. Anywhere that would happen, this module
overrides the method so one user action produces exactly one highlight
pass and one redraw.
"""

from __future__ import annotations

from collections.abc import (
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSet,
)
from typing import Any

from rich.console import RenderableType
from rich.table import Table

from algoviz.core import VizBase, VizConfig, paint

__all__ = ["VizCounter", "VizDict", "VizSet"]

# Sentinel for `pop(key, default=...)`, distinct from any real value
# (including `None`, which is a legitimate default a caller might pass).
_UNSET: Any = object()


class VizDict(VizBase, MutableMapping):
    """A key/value map that renders as a two-column table after writes.

    Reads are highlighted in `get_color`, writes in `set_color`. Both are
    cleared once drawn. Insertion order is preserved, same as a plain dict.
    """

    def __init__(
        self,
        initial: Mapping[Hashable, Any]
        | Iterable[tuple[Hashable, Any]]
        | None = None,
        title_name: str = "Dict",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Build from `initial`: a mapping, an iterable of pairs, or None.

        Args:
            initial: Starting contents. A mapping is copied directly; an
                iterable of `(key, value)` pairs is consumed the same way
                `dict()` would. None starts empty.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this dict is nested.
            **overrides: Individual `VizConfig` fields to override.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._data: dict[Hashable, Any] = (
            dict(initial) if initial is not None else {}
        )

        if self.config.show_init:
            self.show(f"{self.title} Init")

    # -- mapping protocol ---------------------------------------------------

    def __getitem__(self, key: Hashable) -> Any:
        """Read `key`, recording it as a read.

        Raises:
            KeyError: If `key` is not present.
        """
        value = self._data[key]
        self.highlights.mark_get(key)
        return value

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Write `key`, then redraw."""
        self._data[key] = value
        self.highlights.mark_set(key)
        self._auto_show()

    def __delitem__(self, key: Hashable) -> None:
        """Remove `key`, then redraw.

        Raises:
            KeyError: If `key` is not present.
        """
        del self._data[key]
        self.highlights.clear()
        self._auto_show()

    def __iter__(self) -> Iterator[Hashable]:
        """Iterate keys in insertion order. Not tracked as a read."""
        return iter(self._data)

    def __len__(self) -> int:
        """Number of entries."""
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        """True when `key` is present, recording the check as a read."""
        self.highlights.mark_get(key)
        return key in self._data

    # -- atomic overrides (one highlight pass, one redraw) -------------------

    def pop(self, key: Hashable, default: Any = _UNSET) -> Any:
        """Remove `key` and return its value, then redraw once.

        Args:
            key: The key to remove.
            default: Returned instead of raising when `key` is absent.

        Raises:
            KeyError: If `key` is absent and no `default` was given.
        """
        if key not in self._data:
            if default is _UNSET:
                raise KeyError(key)
            return default
        value = self._data.pop(key)
        self.highlights.clear()
        self._auto_show()
        return value

    def popitem(self) -> tuple[Hashable, Any]:
        """Remove and return the most recently inserted `(key, value)` pair.

        Matches `dict.popitem`'s LIFO order.

        Raises:
            KeyError: If this structure is empty.
        """
        if not self._data:
            raise KeyError("popitem from an empty VizDict")
        key = next(reversed(self._data))
        value = self._data.pop(key)
        self.highlights.clear()
        self._auto_show()
        return key, value

    def setdefault(self, key: Hashable, default: Any = None) -> Any:
        """Return `key`'s value, inserting `default` if it is absent.

        An existing key is a pure read (no redraw, matching `__getitem__`).
        An inserted key is a write, redrawn once.
        """
        if key in self._data:
            self.highlights.mark_get(key)
            return self._data[key]
        self._data[key] = default
        self.highlights.mark_set(key)
        self._auto_show()
        return default

    def update(  # type: ignore[override]
        self,
        other: Mapping[Hashable, Any] | Iterable[tuple[Hashable, Any]] = (),
        /,
        **kwargs: Any,
    ) -> None:
        # The ignore is for the signature only. MutableMapping declares
        # `update` as five overloads that a single concrete signature cannot
        # match; every call those overloads accept works here at runtime.
        """Merge `other` and `kwargs` in as one action, then redraw once."""
        pairs = other.items() if isinstance(other, Mapping) else other
        for key, value in pairs:
            self._data[key] = value
            self.highlights.mark_set(key)
        for key, value in kwargs.items():
            self._data[key] = value
            self.highlights.mark_set(key)
        self._auto_show()

    def clear(self) -> None:
        """Remove every entry, then redraw once."""
        self._data.clear()
        self.highlights.clear()
        self._auto_show()

    # -- Python protocol -----------------------------------------------------

    def __eq__(self, other: Any) -> bool:
        """Compare contents with another mapping.

        Overridden rather than left to the `Mapping` mixin, whose default
        `__eq__` iterates through `self[key]` for every key -- which would
        record every key as read as a side effect of an equality check.
        """
        if isinstance(other, VizDict):
            return self._data == other._data
        return self._data == other

    def __ne__(self, other: Any) -> bool:
        """Inverse of equality."""
        return not self.__eq__(other)

    # A mutable mapping must not be hashable; defining __eq__ above already
    # makes Python drop the inherited hash, but this is explicit to match
    # VizList's convention rather than rely on that implicit behaviour.
    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        """Same repr as the underlying dict."""
        return repr(self._data)

    def __str__(self) -> str:
        """Same str as the underlying dict."""
        return str(self._data)

    # -- viz plumbing ---------------------------------------------------------

    @property
    def data(self) -> dict[Hashable, Any]:
        """The underlying dict. Reading it does not record a highlight."""
        return self._data

    def _eval_target(self) -> Any:
        return self._data

    def _renderable(self, title: str | None = None) -> RenderableType:
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        table.add_column("key")
        table.add_column("value")
        if not self._data:
            table.caption = "(empty)"
            return table
        for key, value in self._data.items():
            style = self.highlights.style_for(key, self.config)
            table.add_row(paint(key, None), paint(value, style))
        return table


class VizCounter(VizDict):
    """A frequency-map workhorse for counting problems.

    Built for group-anagrams, top-K-frequent, and sliding-window style
    problems. Behaves like `collections.Counter`: reading a key that was
    never set returns `0` instead of raising, so `counter[k] += 1` works
    the first time `k` is seen. That read is still recorded as a `get`,
    since the point is to visualize "checking this key's count".

    `initial` accepts two shapes, matching `collections.Counter`'s own
    constructor:

    * A mapping is treated as pre-computed counts, e.g.
      `VizCounter({'a': 2})`.
    * Any other iterable has its *elements* tallied one at a time, e.g.
      `VizCounter(['a', 'a', 'b'])` -> `{'a': 2, 'b': 1}`.

    This dual behaviour is what a LeetCode-style frequency counter needs:
    sometimes you already have counts, more often you have a sequence of
    items to tally.
    """

    def __init__(
        self,
        initial: Mapping[Hashable, int] | Iterable[Hashable] | None = None,
        title_name: str = "Counter",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Build from `initial`: pre-computed counts, or items to tally.

        Args:
            initial: A mapping is treated as pre-computed counts. Any other
                iterable has its elements tallied one at a time, matching
                `collections.Counter`'s own constructor. None starts empty.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this counter is nested.
            **overrides: Individual `VizConfig` fields to override.
        """
        self._sorted_by_count = False
        counts = self._tally(initial)
        super().__init__(
            counts,
            title_name=title_name,
            config=config,
            parent=parent,
            **overrides,
        )

    @staticmethod
    def _tally(
        initial: Mapping[Hashable, int] | Iterable[Hashable] | None,
    ) -> dict[Hashable, int]:
        """Build a counts dict from either pre-computed counts or items."""
        if initial is None:
            return {}
        if isinstance(initial, Mapping):
            return dict(initial)
        counts: dict[Hashable, int] = {}
        for item in initial:
            counts[item] = counts.get(item, 0) + 1
        return counts

    def __getitem__(self, key: Hashable) -> int:
        """Return the count for `key`, defaulting to 0 rather than raising."""
        value = self._data.get(key, 0)
        self.highlights.mark_get(key)
        return value

    def most_common(self, n: int | None = None) -> list[tuple[Hashable, int]]:
        """Return `(element, count)` pairs, highest count first.

        Matches `collections.Counter.most_common`: ties keep insertion
        order, because the sort below is stable and orders by count alone.
        """
        items = sorted(
            self._data.items(), key=lambda pair: pair[1], reverse=True
        )
        return items if n is None else items[:n]

    def show(
        self, title: str | None = None, sorted_by_count: bool = False
    ) -> None:
        """Draw this counter, optionally ranked by count.

        Args:
            title: Table title; defaults to `self.title`.
            sorted_by_count: When True, rows are ordered highest-count
                first instead of insertion order.
        """
        self._sorted_by_count = sorted_by_count
        super().show(title)

    def _renderable(self, title: str | None = None) -> RenderableType:
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        table.add_column("key")
        table.add_column("count")
        if not self._data:
            table.caption = "(empty)"
            return table
        items: Iterable[tuple[Hashable, int]] = self._data.items()
        if self._sorted_by_count:
            items = sorted(items, key=lambda pair: pair[1], reverse=True)
        for key, value in items:
            style = self.highlights.style_for(key, self.config)
            table.add_row(paint(key, None), paint(value, style))
        return table


class VizSet(VizBase, MutableSet):
    """A membership set that renders as a single-column table after writes.

    Backed by a dict keyed on the members (values unused), which gives O(1)
    membership and insertion-order iteration without needing a separate
    list to track order.
    """

    def __init__(
        self,
        initial: Iterable[Hashable] | None = None,
        title_name: str = "Set",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Build from `initial`, an iterable of members, or None.

        Args:
            initial: Starting members, or None to start empty.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this set is nested.
            **overrides: Individual `VizConfig` fields to override.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._members: dict[Hashable, None] = (
            dict.fromkeys(initial) if initial is not None else {}
        )

        if self.config.show_init:
            self.show(f"{self.title} Init")

    # -- set protocol ---------------------------------------------------------

    def __contains__(self, value: object) -> bool:
        """True when `value` is a member, recording the check as a read."""
        self.highlights.mark_get(value)
        return value in self._members

    def __iter__(self) -> Iterator[Hashable]:
        """Iterate members in insertion order. Not tracked as a read."""
        return iter(self._members)

    def __len__(self) -> int:
        """Number of members."""
        return len(self._members)

    def add(self, value: Hashable) -> None:
        """Add `value`, then redraw. A no-op re-add still redraws."""
        self._members[value] = None
        self.highlights.mark_set(value)
        self._auto_show()

    def discard(self, value: Hashable) -> None:
        """Remove `value` if present, then redraw. Never raises.

        Matching `VizList`/`VizDict`'s delete convention, the highlights
        are cleared rather than marking the removed value -- there is
        nothing left to point at once it is gone.
        """
        self._members.pop(value, None)
        self.highlights.clear()
        self._auto_show()

    def remove(self, value: Hashable) -> None:
        """Remove `value`, then redraw.

        Raises:
            KeyError: If `value` is not a member.
        """
        if value not in self._members:
            raise KeyError(value)
        del self._members[value]
        self.highlights.clear()
        self._auto_show()

    def clear(self) -> None:
        """Remove every member, then redraw once.

        Overrides the `MutableSet` mixin, whose default `clear()` calls
        `pop()` in a loop -- one redraw per element instead of one total.
        """
        self._members.clear()
        self.highlights.clear()
        self._auto_show()

    # -- set algebra ------------------------------------------------------
    #
    # These return plain `set` objects rather than a new `VizSet`. A
    # tracked, self-showing result would mean `a | b` pops up its own
    # table as a side effect of what is normally just a boolean check
    # ("is x in the union of these two sets?") -- surprising for a
    # seen-set workhorse. Pure algebra over a snapshot of the members is
    # simpler and matches how these operators are actually used.

    def __or__(self, other: Iterable[Hashable]) -> set[Hashable]:
        """Union with `other`, as a plain set."""
        return set(self._members) | set(other)

    def __and__(self, other: Iterable[Hashable]) -> set[Hashable]:
        """Intersection with `other`, as a plain set."""
        return set(self._members) & set(other)

    def __sub__(self, other: Iterable[Hashable]) -> set[Hashable]:
        """Difference with `other`, as a plain set."""
        return set(self._members) - set(other)

    def __xor__(self, other: Iterable[Hashable]) -> set[Hashable]:
        """Symmetric difference with `other`, as a plain set."""
        return set(self._members) ^ set(other)

    # -- Python protocol -----------------------------------------------------

    def __eq__(self, other: Any) -> bool:
        """Compare members with another set-like object."""
        if isinstance(other, VizSet):
            return self._members.keys() == other._members.keys()
        return set(self._members) == other

    def __ne__(self, other: Any) -> bool:
        """Inverse of equality."""
        return not self.__eq__(other)

    # A mutable set must not be hashable; see VizDict.__hash__ for why this
    # is explicit rather than left to the implicit effect of defining __eq__.
    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        """Same repr as the equivalent plain set."""
        return repr(set(self._members))

    def __str__(self) -> str:
        """Same str as the equivalent plain set."""
        return str(set(self._members))

    # -- viz plumbing ---------------------------------------------------------

    @property
    def data(self) -> set[Hashable]:
        """A plain-set snapshot of the members. Not tracked."""
        return set(self._members)

    def _eval_target(self) -> Any:
        return set(self._members)

    def _renderable(self, title: str | None = None) -> RenderableType:
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        table.add_column("member")
        if not self._members:
            table.caption = "(empty)"
            return table
        for value in self._members:
            style = self.highlights.style_for(value, self.config)
            table.add_row(paint(value, style))
        return table
