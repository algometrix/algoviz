"""A LIFO stack that draws itself with the top of stack clearly marked.

`VizStack` backs the classic stack-shaped LeetCode problems: valid
parentheses, monotonic stack, next-greater-element, daily temperatures,
largest rectangle in histogram. What matters when teaching those is *which
element is on top*, so the render always marks it explicitly rather than
leaving the reader to infer it from list order.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Any

from rich.console import RenderableType
from rich.table import Table

from algoviz.core import VizBase, VizConfig, paint

__all__ = ["VizStack"]

_TOP_LABEL = "← top"
_POPPED_LABEL = "✗ popped"


class VizStack(VizBase):
    """A LIFO stack rendered as a table, deepest element at the bottom.

    Pushes highlight the new top in `set_color`, a write. Pops and peeks
    highlight the top in `get_color`, since both merely reveal a value
    rather than change one. A popped element is held in `_departed` and
    still rendered -- coloured as `get_color` -- for the one frame that
    shows the pop, then it is gone: "still visible while it's leaving,
    gone the frame after" falls out of the same clear-on-show cycle every
    other structure uses, instead of a separate animation mechanism.
    """

    def __init__(
        self,
        iterable: Sequence[Any] = (),
        title_name: str = "Stack",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Wrap `iterable` as a stack, bottom-first, then draw it.

        Args:
            iterable: Initial contents, ordered bottom of stack first, so
                the last element becomes the top.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this stack is nested.
            **overrides: Individual `VizConfig` fields to override.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._data: list[Any] = list(iterable)
        self._departed: Any = None
        self._has_departed = False

        if self.config.show_init:
            self.show(f"{self.title} Init")

    # -- stack protocol ------------------------------------------------

    def push(self, value: Any) -> None:
        """Push `value` onto the top of the stack, then redraw."""
        self._departed = None
        self._has_departed = False
        self._data.append(value)
        self.highlights.mark_set(self._top_key())
        self._auto_show()

    def pop(self) -> Any:
        """Remove and return the top element, then redraw.

        The popped element is shown one last time, coloured as removed,
        before it disappears on the next render.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._data:
            raise IndexError("pop from an empty VizStack")
        key = self._top_key()
        value = self._data.pop()
        self._departed = value
        self._has_departed = True
        self.highlights.mark_set(key)
        self._auto_show()
        return value

    def peek(self) -> Any:
        """Return the top element without removing it.

        Raises:
            IndexError: If the stack is empty.
        """
        if not self._data:
            raise IndexError("peek at an empty VizStack")
        self.highlights.mark_get(self._top_key())
        return self._data[-1]

    top = peek

    def is_empty(self) -> bool:
        """True when the stack holds no elements."""
        return not self._data

    def clear(self) -> None:
        """Remove every element, then redraw."""
        self._data.clear()
        self._departed = None
        self._has_departed = False
        self.highlights.clear()
        self._auto_show()

    def _top_key(self) -> int:
        """The index of the current top element."""
        return len(self._data) - 1

    # -- Python protocol -------------------------------------------------

    def __len__(self) -> int:
        """Number of elements currently on the stack."""
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        """Iterate top-to-bottom, the order a stack is conceptually read."""
        return reversed(self._data)

    def __contains__(self, value: Any) -> bool:
        """True when `value` is present anywhere on the stack."""
        return value in self._data

    def __bool__(self) -> bool:
        """True when the stack holds at least one element."""
        return bool(self._data)

    def __repr__(self) -> str:
        """Same repr as the underlying list, top element last."""
        return repr(self._data)

    # -- viz plumbing ------------------------------------------------------

    @property
    def data(self) -> list[Any]:
        """The underlying list, bottom first. Reading it is not tracked."""
        return self._data

    def _eval_target(self) -> Any:
        return self._data

    def _renderable(self, title: str | None = None) -> RenderableType:
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        table.add_column(" ")
        table.add_column("value")

        rows = list(self._rows())
        for marker, value, style in reversed(rows):
            table.add_row(marker, paint(value, style))
        return table

    def _rows(self) -> Iterator[tuple[str, Any, str | None]]:
        """Bottom-to-top rows: (position marker, value, highlight style).

        A departed (just-popped) element is drawn above the real top and
        marked distinctly, so a frame never shows two rows both claiming
        to be "top" at once.
        """
        for index, value in enumerate(self._data):
            style = self.highlights.style_for(index, self.config)
            marker = _TOP_LABEL if index == self._top_key() else ""
            yield marker, value, style

        if self._has_departed:
            yield (_POPPED_LABEL, self._departed, self.config.get_color)

    def clear_highlights(self) -> None:
        """Clear highlights and forget the just-shown departed element."""
        super().clear_highlights()
        self._departed = None
        self._has_departed = False
