"""A FIFO queue and a double-ended queue that draw themselves horizontally.

`VizQueue` backs BFS: enqueue at the back, dequeue from the front. `VizDeque`
backs sliding-window-maximum and monotonic-deque problems, where both ends
move. Both render as a single horizontal row with the front on the left and
the back on the right, matching how a line of people (or a sliding window)
is usually drawn.

Both are backed by `collections.deque`, not `list`, so removing from the
front is O(1) instead of the O(n) a list shift would cost.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator
from typing import Any

from rich.console import RenderableType
from rich.table import Table

from algoviz.core import VizBase, VizConfig, paint

__all__ = ["VizDeque", "VizQueue"]


def _position_header(index: int, total: int, level: int | None) -> str:
    """The column header for a slot: its end label, position, and level.

    FRONT/BACK is only meaningful on the current end slots, `index` is
    always shown, and `level` (BFS depth) is shown only when the caller
    tracks levels at all -- passing `None` omits it entirely so a plain
    queue is not cluttered with an always-zero level.
    """
    is_front = index == 0
    is_back = index == total - 1
    labels: list[str] = []
    if is_front and is_back:
        labels.append("FRONT/BACK")
    elif is_front:
        labels.append("FRONT")
    elif is_back:
        labels.append("BACK")
    labels.append(str(index))
    if level:
        labels.append(f"L{level}")
    return "\n".join(labels)


class VizQueue(VizBase):
    """A FIFO queue rendered as one horizontal row, front on the left.

    Enqueues highlight the new back slot in `set_color`, a write. Dequeues
    and peeks highlight the front in `get_color`, since both only reveal a
    value. A dequeued element is held in `_departed` and still rendered,
    coloured `get_color`, for the one frame that shows the dequeue, then it
    is gone -- the same clear-on-show pattern `VizStack` uses for pops.

    `mark_level()` tags every element enqueued from that point on with the
    next BFS depth, and the render shows the depth in each column header
    once at least one level boundary has been marked. It is opt-in and
    invisible when unused, so a plain queue stays uncluttered.
    """

    def __init__(
        self,
        iterable: Iterable[Any] = (),
        title_name: str = "Queue",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Wrap `iterable` as a FIFO queue, front-first, then draw it.

        Args:
            iterable: Initial contents, ordered front of queue first.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this queue is nested.
            **overrides: Individual `VizConfig` fields to override.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._data: deque[Any] = deque(iterable)
        self._levels: deque[int] = deque(0 for _ in self._data)
        self._current_level = 0
        self._departed: Any = None
        self._departed_level = 0
        self._has_departed = False

        if self.config.show_init:
            self.show(f"{self.title} Init")

    # -- queue protocol ------------------------------------------------

    def enqueue(self, value: Any) -> None:
        """Add `value` to the back of the queue, then redraw."""
        self._departed = None
        self._has_departed = False
        self._data.append(value)
        self._levels.append(self._current_level)
        self.highlights.mark_set(self._back_key())
        self._auto_show()

    append = enqueue

    def dequeue(self) -> Any:
        """Remove and return the front element, then redraw.

        Raises:
            IndexError: If the queue is empty.
        """
        if not self._data:
            raise IndexError("dequeue from an empty VizQueue")
        value = self._data.popleft()
        self._departed_level = self._levels.popleft()
        self._departed = value
        self._has_departed = True
        self._auto_show()
        return value

    popleft = dequeue

    def peek(self) -> Any:
        """Return the front element without removing it.

        Raises:
            IndexError: If the queue is empty.
        """
        if not self._data:
            raise IndexError("peek at an empty VizQueue")
        self.highlights.mark_get(self._front_key())
        return self._data[0]

    def is_empty(self) -> bool:
        """True when the queue holds no elements."""
        return not self._data

    def clear(self) -> None:
        """Remove every element and reset BFS levels, then redraw."""
        self._data.clear()
        self._levels.clear()
        self._current_level = 0
        self._departed = None
        self._departed_level = 0
        self._has_departed = False
        self.highlights.clear()
        self._auto_show()

    def mark_level(self) -> int:
        """Advance the BFS level for elements enqueued from now on.

        Returns:
            The new level number.
        """
        self._current_level += 1
        return self._current_level

    def _front_key(self) -> int:
        """The index of the current front element."""
        return 0

    def _back_key(self) -> int:
        """The index of the current back element."""
        return len(self._data) - 1

    # -- Python protocol -------------------------------------------------

    def __len__(self) -> int:
        """Number of elements currently in the queue."""
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        """Iterate front-to-back, the order elements would be dequeued."""
        return iter(self._data)

    def __contains__(self, value: Any) -> bool:
        """True when `value` is present anywhere in the queue."""
        return value in self._data

    def __bool__(self) -> bool:
        """True when the queue holds at least one element."""
        return bool(self._data)

    def __repr__(self) -> str:
        """Same repr as a list, front element first."""
        return repr(list(self._data))

    # -- viz plumbing ------------------------------------------------------

    @property
    def data(self) -> deque[Any]:
        """The underlying deque, front first. Reading it is not tracked."""
        return self._data

    def _eval_target(self) -> Any:
        return self._data

    def _entries(self) -> list[tuple[Any, int, str | None]]:
        """Displayed (value, level, style) triples, front to back.

        The departed element -- if any -- is spliced in at the front, since
        a queue can only ever dequeue from the front.
        """
        entries: list[tuple[Any, int, str | None]] = []
        if self._has_departed:
            entries.append(
                (self._departed, self._departed_level, self.config.get_color)
            )
        for index, value in enumerate(self._data):
            style = self.highlights.style_for(index, self.config)
            entries.append((value, self._levels[index], style))
        return entries

    def _renderable(self, title: str | None = None) -> RenderableType:
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        entries = self._entries()
        total = len(entries)
        level = self._current_level if self._current_level else None
        for index, (_, entry_level, _) in enumerate(entries):
            shown_level = entry_level if level is not None else None
            table.add_column(_position_header(index, total, shown_level))
        if entries:
            table.add_row(*(paint(value, style) for value, _, style in entries))
        return table

    def clear_highlights(self) -> None:
        """Clear highlights and forget the just-shown departed element."""
        super().clear_highlights()
        self._departed = None
        self._departed_level = 0
        self._has_departed = False


class VizDeque(VizBase):
    """A double-ended queue rendered as one horizontal row.

    `append`/`pop` act on the back (right); `appendleft`/`popleft` act on
    the front (left) -- the same ends `collections.deque` itself uses.
    Appends highlight the new slot in `set_color`. Pops and peeks highlight
    in `get_color`. A popped element is held and still rendered, coloured
    `get_color`, at the end it left for one frame, then it is gone --
    mirroring `VizStack`'s and `VizQueue`'s clear-on-show pattern.
    """

    def __init__(
        self,
        iterable: Iterable[Any] = (),
        title_name: str = "Deque",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Wrap `iterable` as a double-ended queue, then draw it.

        Args:
            iterable: Initial contents, ordered left end first.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this deque is nested.
            **overrides: Individual `VizConfig` fields to override.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._data: deque[Any] = deque(iterable)
        self._departed: Any = None
        self._departed_side: str | None = None
        self._has_departed = False

        if self.config.show_init:
            self.show(f"{self.title} Init")

    # -- deque protocol ------------------------------------------------

    def append(self, value: Any) -> None:
        """Add `value` to the back, then redraw."""
        self._clear_departed()
        self._data.append(value)
        self.highlights.mark_set(self._back_key())
        self._auto_show()

    def appendleft(self, value: Any) -> None:
        """Add `value` to the front, then redraw."""
        self._clear_departed()
        self._data.appendleft(value)
        self.highlights.mark_set(self._front_key())
        self._auto_show()

    def pop(self) -> Any:
        """Remove and return the back element, then redraw.

        Raises:
            IndexError: If the deque is empty.
        """
        if not self._data:
            raise IndexError("pop from an empty VizDeque")
        value = self._data.pop()
        self._set_departed(value, "back")
        self._auto_show()
        return value

    def popleft(self) -> Any:
        """Remove and return the front element, then redraw.

        Raises:
            IndexError: If the deque is empty.
        """
        if not self._data:
            raise IndexError("popleft from an empty VizDeque")
        value = self._data.popleft()
        self._set_departed(value, "front")
        self._auto_show()
        return value

    def peek_left(self) -> Any:
        """Return the front element without removing it.

        Raises:
            IndexError: If the deque is empty.
        """
        if not self._data:
            raise IndexError("peek_left at an empty VizDeque")
        self.highlights.mark_get(self._front_key())
        return self._data[0]

    def peek_right(self) -> Any:
        """Return the back element without removing it.

        Raises:
            IndexError: If the deque is empty.
        """
        if not self._data:
            raise IndexError("peek_right at an empty VizDeque")
        self.highlights.mark_get(self._back_key())
        return self._data[-1]

    def is_empty(self) -> bool:
        """True when the deque holds no elements."""
        return not self._data

    def clear(self) -> None:
        """Remove every element, then redraw."""
        self._data.clear()
        self._clear_departed()
        self.highlights.clear()
        self._auto_show()

    def _clear_departed(self) -> None:
        """Forget any departed element from a previous pop."""
        self._departed = None
        self._departed_side = None
        self._has_departed = False

    def _set_departed(self, value: Any, side: str) -> None:
        """Record `value` as just-removed from `side`, for one frame."""
        self._departed = value
        self._departed_side = side
        self._has_departed = True

    def _front_key(self) -> int:
        """The index of the current front element."""
        return 0

    def _back_key(self) -> int:
        """The index of the current back element."""
        return len(self._data) - 1

    # -- Python protocol -------------------------------------------------

    def __len__(self) -> int:
        """Number of elements currently in the deque."""
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        """Iterate front-to-back."""
        return iter(self._data)

    def __contains__(self, value: Any) -> bool:
        """True when `value` is present anywhere in the deque."""
        return value in self._data

    def __bool__(self) -> bool:
        """True when the deque holds at least one element."""
        return bool(self._data)

    def __repr__(self) -> str:
        """Same repr as a list, front element first."""
        return repr(list(self._data))

    # -- viz plumbing ------------------------------------------------------

    @property
    def data(self) -> deque[Any]:
        """The underlying deque, front first. Reading it is not tracked."""
        return self._data

    def _eval_target(self) -> Any:
        return self._data

    def _entries(self) -> list[tuple[Any, str | None]]:
        """Displayed (value, style) pairs, front to back.

        The departed element -- if any -- is spliced back in at whichever
        end it left from, so it briefly reappears exactly where it was.
        """
        entries = [
            (value, self.highlights.style_for(index, self.config))
            for index, value in enumerate(self._data)
        ]
        if not self._has_departed:
            return entries
        departed_cell = (self._departed, self.config.get_color)
        if self._departed_side == "front":
            return [departed_cell, *entries]
        return [*entries, departed_cell]

    def _renderable(self, title: str | None = None) -> RenderableType:
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        entries = self._entries()
        total = len(entries)
        for index in range(total):
            table.add_column(_position_header(index, total, None))
        if entries:
            table.add_row(*(paint(value, style) for value, style in entries))
        return table

    def clear_highlights(self) -> None:
        """Clear highlights and forget the just-shown departed element."""
        super().clear_highlights()
        self._clear_departed()
