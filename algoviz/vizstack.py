"""A LIFO stack that draws itself with the top of stack clearly marked.

`VizStack` backs the classic stack-shaped LeetCode problems: valid
parentheses, monotonic stack, next-greater-element, daily temperatures,
largest rectangle in histogram. What matters when teaching those is *which
element is on top*, so the render always marks it explicitly rather than
leaving the reader to infer it from list order.

The monotonic-stack family needs one thing more. Those algorithms keep the
stack ordered by a *magnitude* -- a temperature, a bar height -- and usually
store indices into some other array rather than the magnitudes themselves,
so a column of raw values shows `2, 3, 4` and hides the invariant entirely.
Passing `bar_of` maps each element to its magnitude and draws it as a bar,
which turns "temperatures decrease from the bottom up" into a staircase you
can see.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from typing import Any

from rich.console import RenderableType
from rich.table import Table

from algoviz.core import VizBase, VizConfig, glyph, paint

__all__ = ["VizStack"]

_TOP_LABEL = glyph("←", "<-") + " top"
_POPPED_LABEL = glyph("✗", "x") + " popped"

# Bars are drawn from full blocks plus a partial block for the remainder, so
# two magnitudes a few percent apart still differ on screen. Terminals that
# cannot encode the partials fall back to whole cells only, which rounds
# down rather than crashing -- see `glyph`.
_BAR_FULL = glyph("█", "#")
_BAR_PARTIALS = glyph("▏▎▍▌▋▊▉", "")


def _bar(magnitude: float, low: float, high: float, width: int) -> str:
    """Render `magnitude` as a bar of at most `width` cells.

    The bar measures `magnitude` against the span `low`..`high` rather
    than against zero. Monotonic-stack magnitudes are routinely clustered
    -- eight temperatures between 69 and 76 -- and a zero-anchored axis
    draws those as eight identical full bars, hiding the very ordering
    the picture exists to show. The trade is the usual one for a
    truncated axis: differences look larger than they are, which is why
    the magnitude is always printed beside the bar.

    Args:
        magnitude: The value to draw.
        low: Value drawn as the shortest bar.
        high: Value drawn as a full bar.
        width: Bar length in character cells when full.

    Returns:
        The bar text, left-aligned and padded to `width` cells.
    """
    span = high - low
    # A degenerate span means every magnitude is identical; a row of full
    # bars says "all the same" more honestly than a division by zero.
    filled = float(width) if span <= 0 else (magnitude - low) / span * width
    # Floor at one cell: the smallest magnitude is still a bar, not a
    # blank that reads as a missing value.
    filled = max(1.0, min(float(width), filled))

    whole = int(filled)
    bar = _BAR_FULL * whole
    if _BAR_PARTIALS and whole < width:
        eighths = int((filled - whole) * 8)
        if eighths:
            bar += _BAR_PARTIALS[eighths - 1]
    return bar.ljust(width)


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
        bar_of: Callable[[Any], float] | None = None,
        bar_label: str = "magnitude",
        bar_min: float | None = None,
        bar_max: float | None = None,
        bar_width: int = 12,
        **overrides: Any,
    ) -> None:
        """Wrap `iterable` as a stack, bottom-first, then draw it.

        Args:
            iterable: Initial contents, ordered bottom of stack first, so
                the last element becomes the top.
            title_name: Heading drawn above the table.
            config: Shared presentation settings.
            parent: Enclosing structure, when this stack is nested.
            bar_of: Maps an element to the magnitude it stands for. Given,
                a bar column is drawn; omitted, the stack renders exactly
                as before. A stack holding magnitudes directly wants
                `bar_of=lambda value: value`; one holding indices into
                some array wants `bar_of=lambda i: heights[i]`.
            bar_label: Heading for the bar column.
            bar_min: Magnitude drawn as the shortest bar.
            bar_max: Magnitude drawn as a full bar. Omitted, either bound
                is the most extreme magnitude seen so far. Those bounds
                only ever widen, so bars never re-scale under the reader
                more than once per new extreme -- but passing the source
                array's `min` and `max` fixes the scale from frame one and
                makes every frame directly comparable, which is what the
                demos do.
            bar_width: Bar length in character cells when full.
            **overrides: Individual `VizConfig` fields to override.

        Raises:
            TypeError: If `bar_of` is given but is not callable.
            ValueError: If `bar_width` is not positive.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        if bar_of is not None and not callable(bar_of):
            raise TypeError(f"bar_of must be callable, got {bar_of!r}")
        if bar_width < 1:
            raise ValueError(f"bar_width must be positive, got {bar_width}")

        self._data: list[Any] = list(iterable)
        self._departed: Any = None
        self._has_departed = False

        self._bar_of = bar_of
        self._bar_label = bar_label
        self._bar_min = bar_min
        self._bar_max = bar_max
        self._bar_width = bar_width
        # Running extremes for whichever bound was not pinned. They only
        # ever widen, so an unpinned scale settles instead of oscillating.
        self._seen_low: float | None = None
        self._seen_high: float | None = None

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
        if self._bar_of is None:
            for marker, value, style in reversed(rows):
                table.add_row(marker, paint(value, style))
            return table

        table.add_column(self._bar_label)
        magnitudes = [float(self._bar_of(value)) for _, value, _ in rows]
        cells = self._bar_cells(magnitudes)
        for (marker, value, style), cell in reversed(
            list(zip(rows, cells, strict=True))
        ):
            table.add_row(marker, paint(value, style), paint(cell, style))
        return table

    def _bar_cells(self, magnitudes: list[float]) -> list[str]:
        """A bar plus its number, one cell per magnitude.

        The numbers are right-aligned to the widest in *this* frame, so a
        two-digit and a three-digit reading still line their bars up.
        """
        self._widen_seen_range(magnitudes)
        low, high = self._bar_bounds()

        labels = [f"{magnitude:g}" for magnitude in magnitudes]
        width = max((len(label) for label in labels), default=0)
        return [
            f"{_bar(magnitude, low, high, self._bar_width)} {label:>{width}}"
            for magnitude, label in zip(magnitudes, labels, strict=True)
        ]

    def _widen_seen_range(self, magnitudes: list[float]) -> None:
        """Record `magnitudes` in the running extremes. Drawing writes here.

        Magnitudes are observed only while drawing, because `bar_of` is
        the one thing that knows how to read an element and the render
        path is its only caller. So the extremes track what has been
        *drawn*, not what has been pushed -- which is what the picture
        wants anyway, since a bar should not re-scale to accommodate a
        magnitude the reader never saw. A consequence worth knowing: a
        push and pop that both happen under `auto_print=False` never
        widen an unpinned scale, because no frame ever showed them.

        They only widen, never narrow, so an unpinned scale settles.
        """
        for magnitude in magnitudes:
            if self._seen_low is None or magnitude < self._seen_low:
                self._seen_low = magnitude
            if self._seen_high is None or magnitude > self._seen_high:
                self._seen_high = magnitude

    def _bar_bounds(self) -> tuple[float, float]:
        """The (low, high) bars are measured against: pinned, else seen."""
        low = self._bar_min if self._bar_min is not None else self._seen_low
        high = self._bar_max if self._bar_max is not None else self._seen_high
        # Either is None only on an empty stack, which draws no bars at
        # all, so what is returned then is never measured against.
        return (
            0.0 if low is None else float(low),
            0.0 if high is None else float(high),
        )

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
