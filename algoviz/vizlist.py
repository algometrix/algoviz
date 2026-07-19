"""A list that draws itself and highlights the cells you touch.

`VizList` is a `MutableSequence`, not a `list` subclass. The old version
inherited from `list` while keeping its real data in a separate attribute, so
`list`'s own storage was always empty and any C-level fast path that read it
saw the wrong thing. Delegating explicitly is slower by a hair and correct.
"""

from __future__ import annotations

from collections.abc import Iterator, MutableSequence, Sequence
from typing import Any

from rich.console import RenderableType
from rich.table import Table

from algoviz.core import VizBase, VizConfig, glyph, paint

__all__ = ["VizList"]

# Same marker VizLinkedList uses, with the same ASCII fallback for
# terminals whose encoding cannot carry an arrow.
_POINTER_MARK = glyph("\u2191", "^")


def _is_row(value: Any) -> bool:
    """True when `value` should become a nested row rather than a cell."""
    return isinstance(value, (Sequence, VizList)) and not isinstance(
        value, (str, bytes)
    )


class VizList(VizBase, MutableSequence):
    """A 1D or 2D list that renders as a table after every write.

    Reads are highlighted in `get_color`, writes in `set_color`. Both are
    cleared once drawn, so each frame shows only what that step touched.
    """

    def __init__(
        self,
        array: Sequence[Any],
        title_name: str = "Array",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        row_index: Sequence[Any] | None = None,
        column_index: Sequence[Any] | None = None,
        **overrides: Any,
    ) -> None:
        """Wrap `array`, detecting whether it is a 1D or 2D structure.

        Args:
            array: Values to wrap. A sequence of sequences renders as 2D.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this list is a nested row.
            row_index: Labels for rows, drawn in a leading column.
            column_index: Labels for columns, drawn in the header.
            **overrides: Individual `VizConfig` fields to override.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self.row_index = list(row_index) if row_index else None
        self.col_index = list(column_index) if column_index else None

        data = list(array)
        self.is_2d = bool(data) and _is_row(data[0])
        if self.is_2d:
            data = [
                self._adopt(row, position) for position, row in enumerate(data)
            ]
        self._data: list[Any] = data
        self._pointers: dict[str, int] = {}

        if self.config.show_init:
            self.show(f"{self.title} Init")

    def _adopt(self, row: Sequence[Any], position: int) -> VizList:
        """Wrap a raw row as a child VizList that renders inside this table."""
        if isinstance(row, VizList):
            row.parent = self
            return row
        label = [self.row_index[position]] if self.row_index else None
        return VizList(
            row,
            config=self.config.child(),
            parent=self,
            row_index=label,
        )

    # -- sequence protocol -------------------------------------------------

    def __len__(self) -> int:
        """Number of items."""
        return len(self._data)

    def __getitem__(self, key: int | slice) -> Any:
        """Read an item or slice, recording the indices touched."""
        result = self._data[key]
        if not self.is_2d:
            self.highlights.mark_get(*self._keys_for(key))
        return result

    def __setitem__(self, key: int | slice, value: Any) -> None:
        """Write an item or slice, then redraw."""
        if self.is_2d and isinstance(key, int) and _is_row(value):
            value = self._adopt(value, key)
        self._data[key] = value
        self.highlights.mark_set(*self._keys_for(key))
        self._auto_show()

    def __delitem__(self, key: int | slice) -> None:
        """Remove an item or slice, then redraw."""
        del self._data[key]
        self.highlights.clear()
        self._auto_show()

    def insert(self, index: int, value: Any) -> None:
        """Insert `value` before `index`, then redraw."""
        if self.is_2d and _is_row(value):
            value = self._adopt(value, index)
        self._data.insert(index, value)
        self.highlights.clear()
        self.highlights.mark_set(self._normalize(index))
        self._auto_show()

    def _normalize(self, index: int) -> int:
        """Turn a possibly-negative index into a positive one."""
        return index if index >= 0 else index + len(self._data)

    def _keys_for(self, key: int | slice) -> tuple[int, ...]:
        """The concrete indices a subscript touches."""
        if isinstance(key, slice):
            return tuple(range(*key.indices(len(self._data))))
        return (self._normalize(key),)

    # -- list conveniences MutableSequence does not provide ----------------

    def sort(self, **kwargs: Any) -> None:
        """Sort in place, then redraw."""
        self._data.sort(**kwargs)
        self.highlights.clear()
        self._auto_show()

    def copy(self) -> list[Any]:
        """A plain-list copy of the current contents."""
        return list(self._data)

    def __add__(self, other: Sequence[Any]) -> list[Any]:
        """Concatenate into a new plain list."""
        return self._data + list(other)

    def __radd__(self, other: Sequence[Any]) -> list[Any]:
        """Concatenate onto a sequence on the left."""
        return list(other) + self._data

    def __mul__(self, count: int) -> list[Any]:
        """Repeat into a new plain list."""
        return self._data * count

    __rmul__ = __mul__

    def __eq__(self, other: Any) -> bool:
        """Compare contents with another sequence."""
        if isinstance(other, VizList):
            return self._data == other._data
        return self._data == other

    def __ne__(self, other: Any) -> bool:
        """Inverse of equality."""
        return not self.__eq__(other)

    # A mutable sequence must not be hashable; the old version forwarded to
    # list.__hash__ (which is None) and raised a confusing TypeError.
    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        """Same repr as the underlying list."""
        return repr(self._data)

    def __str__(self) -> str:
        """Same str as the underlying list."""
        return str(self._data)

    # -- viz plumbing ------------------------------------------------------

    @property
    def data(self) -> list[Any]:
        """The underlying list. Reading it does not record a highlight."""
        return self._data

    def _eval_target(self) -> Any:
        return self._data

    def _children(self) -> Iterator[VizBase]:
        return (row for row in self._data if isinstance(row, VizBase))

    def _cells(self, label: Any = None) -> tuple[str, ...]:
        """Values as styled cells, with an optional leading label."""
        cells: list[str] = []
        if self.row_index:
            heading = str(self.row_index[0])
            if label is not None:
                heading = f"{heading} [{label}]"
            cells.append(paint(heading, None))
        for index, value in enumerate(self._data):
            style = self.highlights.style_for(index, self.config)
            cells.append(paint(value, style))
        return tuple(cells)

    def _column_labels(self) -> list[str]:
        width = (
            len(self._data[0]) if self.is_2d and self._data else len(self._data)
        )
        if not self.col_index:
            return [str(i) for i in range(width)]
        return [f"{name} [{i}]" for i, name in enumerate(self.col_index)]

    # -- named pointers ----------------------------------------------------

    def set_pointer(self, name: str, index: int | None) -> None:
        """Point the named pointer at `index`, then redraw.

        Two-pointer problems are about where the pointers are, so this
        draws a labelled row under the values and keeps it there until
        the pointer moves again. Passing `index=None` removes it.

        Pointers take an index rather than a value, which is what the
        algorithm already has in hand. That differs from
        `VizLinkedList.set_pointer`, which takes a node, because a list
        has positions where a chain only has nodes.

        An out-of-range index is stored but not drawn. Pointers legally
        run past the end as a loop terminates, and refusing that would
        force a guard into every caller for the sake of the picture.

        Raises:
            TypeError: If `index` is not an int.
            NotImplementedError: On a 2D list, where a single row of
                labels cannot say which row it refers to.
        """
        if self.is_2d:
            raise NotImplementedError(
                "pointers are not supported on a 2D list; set them on a row"
            )
        if index is None:
            self._pointers.pop(name, None)
            self._auto_show()
            return
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError(f"pointer index must be an int, got {index!r}")
        # Deliberately not marked as a read: the caller's own subscript
        # records that. Marking here would paint every pointer move as an
        # access even when the algorithm only compared indices.
        self._pointers[name] = index
        self._auto_show()

    def clear_pointers(self) -> None:
        """Remove every pointer, then redraw."""
        self._pointers.clear()
        self._auto_show()

    @property
    def pointers(self) -> dict[str, int]:
        """A snapshot of the current pointer names and their indices."""
        return dict(self._pointers)

    def _pointer_cells(self) -> tuple[str, ...]:
        """A row of pointer labels aligned under the values they mark."""
        names_at: dict[int, list[str]] = {}
        for name, index in sorted(self._pointers.items()):
            if 0 <= index < len(self._data):
                names_at.setdefault(index, []).append(name)

        cells: list[str] = [""] if self.row_index else []
        for index in range(len(self._data)):
            names = names_at.get(index)
            cells.append(f"{_POINTER_MARK}{','.join(names)}" if names else "")
        return tuple(cells)

    def _renderable(self, title: str | None = None) -> RenderableType:
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        if self.row_index:
            table.add_column(" ")
        for label in self._column_labels():
            table.add_column(label)

        if not self.is_2d:
            table.add_row(*self._cells())
            if self._pointers:
                table.add_row(*self._pointer_cells())
            return table

        for position, row in enumerate(self._data):
            if isinstance(row, VizList):
                table.add_row(*row._cells(label=position))
            else:
                table.add_row(paint(row, None))
        return table
