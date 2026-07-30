"""A 2D matrix that draws itself with a colour overlay for traversal state.

`VizGrid` backs the matrix-shaped LeetCode problems: number of islands,
rotting oranges, word search, flood fill, shortest path in a binary matrix,
spiral matrix. In those problems the cell *values* are usually static
terrain (`'1'`/`'0'`, `'.'`/`'#'`) and what actually matters, frame to
frame, is which cells the algorithm has visited, queued, walked as its
current path, or picked as start/target. That is a different shape of
signal than `VizList`'s read/write highlighting, so `VizGrid` adds a
persistent overlay on top of the base get/set highlighting instead of
replacing it.

The values themselves are the other half of the picture. `'0'`, `'1'`, and
`'2'` mean empty, fresh, and rotten to the problem but nothing at all to the
reader, who re-decodes them every frame. `cell_map` gives a value a glyph
and a colour, so the grid shows oranges rotting rather than digits changing.

`cell_map` is a dict where its sibling `VizStack.bar_of` is a function, and
the difference is not an accident. A grid's values are a small closed
alphabet -- `'0'`/`'1'`/`'2'`, land and water -- so a literal at the call
site *is* the legend, readable and reviewable in place. A monotonic stack's
elements are indices into an arbitrary array, an unbounded key space no
literal could cover, which is why that feature takes a callable. Take the
dict where the values enumerate; take the function where they do not.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any

from rich.console import RenderableType
from rich.table import Table

from algoviz.core import VizBase, VizConfig, glyph, paint

__all__ = ["Mark", "VizGrid"]

_ORTHOGONAL_DELTAS: tuple[tuple[int, int], ...] = (
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
)
_DIAGONAL_DELTAS: tuple[tuple[int, int], ...] = (
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
)


class Mark(Enum):
    """The overlay kinds a cell can carry, independent of its value.

    Modelled as an enum rather than magic strings so a typo like
    `"visted"` fails at call time instead of silently creating a new,
    never-cleared overlay kind.
    """

    VISITED = "visited"
    QUEUED = "queued"
    PATH = "path"
    START = "start"
    TARGET = "target"


# Highest-priority mark first. `_style_for_cell` walks this in order and
# returns the colour of the first kind present on the cell, so a cell that
# is both VISITED and on the PATH renders as PATH.
_PRECEDENCE: tuple[Mark, ...] = (
    Mark.TARGET,
    Mark.START,
    Mark.PATH,
    Mark.QUEUED,
    Mark.VISITED,
)


@dataclass(frozen=True)
class _CellStyle:
    """How one cell value is drawn: its colour, and its glyph if it has one.

    A value given only a colour keeps its own text, so `glyph` is None
    rather than a copy of that text -- "no glyph was asked for" and "the
    glyph happens to equal the value" are different facts, and only the
    first should let a later default take effect.
    """

    color: str
    glyph: str | None = None


def _is_glyph_pair(spec: Any) -> bool:
    """True when `spec` is a `(glyph, colour)` pair of strings."""
    return (
        isinstance(spec, tuple)
        and len(spec) == 2
        and all(isinstance(part, str) for part in spec)
    )


def _parse_cell_map(
    cell_map: dict[Any, str | tuple[str, str]] | None,
) -> dict[Any, _CellStyle]:
    """Normalize a `cell_map` into one `_CellStyle` per cell value.

    The union is input sugar and stops here, so nothing downstream has to
    ask which of the two forms an entry was written in.

    Glyphs are resolved against the output encoding once, here, rather
    than on every render: the keys are known now, and each one's own
    string is the natural fallback when its glyph cannot be encoded.

    Args:
        cell_map: Value to colour, or value to `(glyph, colour)`.

    Returns:
        One style per cell value, keyed by that value.

    Raises:
        TypeError: If an entry is neither a colour string nor a
            `(glyph, colour)` pair of strings.
    """
    styles: dict[Any, _CellStyle] = {}
    for value, spec in (cell_map or {}).items():
        if isinstance(spec, str):
            styles[value] = _CellStyle(color=spec)
        elif _is_glyph_pair(spec):
            mark, color = spec
            styles[value] = _CellStyle(
                color=color, glyph=glyph(mark, str(value))
            )
        else:
            raise TypeError(
                f"cell_map[{value!r}] must be a colour or a (glyph, colour) "
                f"pair, got {spec!r}"
            )
    return styles


class VizGrid(VizBase):
    """A 2D matrix rendered as a table with a persistent mark overlay.

    Unlike `VizList`, a `VizGrid`'s per-cell get/set highlighting (from
    `self.highlights`, cleared every frame like every other `VizBase`) is
    usually the less interesting signal. The interesting signal is the
    overlay: `mark_visited`, `mark_queued`, `mark_path`, `mark_start`, and
    `mark_target` record durable traversal state that survives across
    frames until `clear_marks` is called explicitly.

    Precedence when a cell carries more than one mark (highest first):
    `TARGET > START > PATH > QUEUED > VISITED`. A cell that is both
    visited and on the final path renders as PATH, for example. See
    `_PRECEDENCE`.

    Overlay marks also take precedence over the base read/write
    highlight: a cell that was merely read (`get_color`) but is also
    marked VISITED renders as VISITED, because the overlay is the whole
    point of this structure and a base highlight is incidental by
    comparison.

    A `cell_map` colour sits below both, so the full colour precedence is
    `overlay mark > read/write highlight > cell_map value`. The glyph is
    a separate channel and always comes from the value, never from a
    mark, so a visited land cell still looks like land. The corollary is
    worth stating: mark cells for state the *values do not already
    carry*. An algorithm that mutates values to record its progress --
    flood fill repainting a region, rotting oranges turning `'1'` into
    `'2'` -- says everything through `cell_map` already, and marking on
    top of that only overwrites the colour that was doing the work.

    Known limitation: `grid[r][c] = value` (double subscript) mutates the
    row list returned by `grid[r]` directly. That bypasses highlighting
    and does not trigger a redraw, because the intermediate `grid[r]`
    is a plain list with no tracking of its own. Use `grid[r, c] = value`
    instead, which is tracked and redraws.
    """

    def __init__(
        self,
        grid: Sequence[Any],
        title_name: str = "Grid",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        visited_color: str = "cyan",
        queued_color: str = "yellow",
        path_color: str = "magenta",
        start_color: str = "green",
        target_color: str = "bright_red",
        mark_colors: dict[Mark, str] | None = None,
        cell_map: dict[Any, str | tuple[str, str]] | None = None,
        cell_width: int | None = None,
        **overrides: Any,
    ) -> None:
        """Build a grid from a list of lists or a list of strings.

        Args:
            grid: The rows. Either a sequence of sequences (e.g.
                `[['1', '1'], ['0', '1']]`) or a sequence of strings
                (e.g. `['11', '01']`) -- both produce the same logical
                grid, since a string is itself a sequence of its
                characters.
            title_name: The table's title.
            config: Shared presentation settings. Defaults to
                `VizConfig()`.
            parent: The enclosing structure, if this grid is nested.
            visited_color: Default colour for `Mark.VISITED` cells.
            queued_color: Default colour for `Mark.QUEUED` cells.
            path_color: Default colour for `Mark.PATH` cells.
            start_color: Default colour for `Mark.START` cells.
            target_color: Default colour for `Mark.TARGET` cells.
            mark_colors: Optional overrides merged on top of the five
                `*_color` defaults above, keyed by `Mark`.
            cell_map: What a cell *value* looks like, keyed by that value.
                Each entry is either a colour, which tints the value as
                written (`{'1': 'green'}`), or a `(glyph, colour)` pair,
                which replaces the text too (`{'1': ('■', 'green')}`).
                Values absent from the map render exactly as they do
                without one, so a partial map is fine. A glyph the output
                encoding cannot carry falls back to the raw value rather
                than raising, the same bargain `glyph` makes elsewhere.
            cell_width: When set, every data column is rendered at this
                fixed width, so single-character terrain (`'1'`/`'0'`)
                reads as roughly square cells instead of being stretched
                to fit the header.
            **overrides: Field overrides applied to `config`, e.g.
                `auto_print=False`.
        """
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._data: list[list[Any]] = [list(row) for row in grid]
        self.cell_width = cell_width
        self._mark_colors: dict[Mark, str] = {
            Mark.VISITED: visited_color,
            Mark.QUEUED: queued_color,
            Mark.PATH: path_color,
            Mark.START: start_color,
            Mark.TARGET: target_color,
        }
        if mark_colors:
            self._mark_colors.update(mark_colors)
        self._marks: dict[Mark, set[tuple[int, int]]] = {
            kind: set() for kind in Mark
        }
        self._batch_depth = 0
        self._cell_styles = _parse_cell_map(cell_map)

        if self.config.show_init:
            self.show(f"{self.title} Init")

    # -- shape and iteration ------------------------------------------------

    @property
    def rows(self) -> int:
        """Number of rows in the grid."""
        return len(self._data)

    @property
    def cols(self) -> int:
        """Number of columns in the grid, or 0 when there are no rows."""
        return len(self._data[0]) if self._data else 0

    @property
    def shape(self) -> tuple[int, int]:
        """The grid's `(rows, cols)`."""
        return (self.rows, self.cols)

    @property
    def data(self) -> list[list[Any]]:
        """The underlying rows. Reading this does not record a highlight."""
        return self._data

    def __len__(self) -> int:
        """Number of rows, matching how `len()` on a raw 2D list behaves."""
        return self.rows

    def __iter__(self) -> Iterator[list[Any]]:
        """Iterate over rows, each a plain list, like a raw 2D list."""
        return iter(self._data)

    def find(self, value: Any) -> list[tuple[int, int]]:
        """Return every `(r, c)` coordinate whose cell equals `value`."""
        return [
            (r, c)
            for r, row in enumerate(self._data)
            for c, cell in enumerate(row)
            if cell == value
        ]

    # -- indexing -------------------------------------------------------

    def __getitem__(self, key: Any) -> Any:
        """Read a row, or a single cell via an `(r, c)` tuple.

        Args:
            key: An int to fetch that row (returned as a plain list,
                see the class docstring's known limitation), or an
                `(r, c)` tuple to fetch a single cell, which also
                records a highlighted read at that coordinate.

        Returns:
            The row when `key` is an int, or the cell value when `key`
            is an `(r, c)` tuple.

        Raises:
            IndexError: If `key` is an out-of-bounds `(r, c)` tuple.
        """
        if isinstance(key, tuple):
            r, c = key
            self._require_in_bounds(r, c)
            self.highlights.mark_get((r, c))
            return self._data[r][c]
        return self._data[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """Write a row, or a single cell via an `(r, c)` tuple, then redraw.

        Args:
            key: An int to replace that entire row with `value` (an
                iterable of cell values), or an `(r, c)` tuple to set a
                single cell to `value`.
            value: The new row contents, or the new cell value.

        Raises:
            IndexError: If `key` is an out-of-bounds `(r, c)` tuple.
        """
        if isinstance(key, tuple):
            r, c = key
            self._require_in_bounds(r, c)
            self._data[r][c] = value
            self.highlights.mark_set((r, c))
            self._auto_show()
            return
        self._data[key] = list(value)
        self._auto_show()

    def in_bounds(self, r: int, c: int) -> bool:
        """True when `(r, c)` is a real cell in this grid.

        Negative coordinates are out of bounds here, unlike Python's
        usual negative-index wraparound, because a coordinate pair is a
        grid position, not a list subscript.
        """
        return 0 <= r < self.rows and 0 <= c < self.cols

    def _require_in_bounds(self, r: int, c: int) -> None:
        """Raise `IndexError` unless `(r, c)` is inside the grid."""
        if self.in_bounds(r, c):
            return
        raise IndexError(
            f"({r}, {c}) is out of bounds for grid of shape {self.shape}"
        )

    def neighbors(
        self, r: int, c: int, diagonal: bool = False
    ) -> Iterator[tuple[int, int]]:
        """Yield in-bounds neighbour coordinates of `(r, c)`.

        Args:
            r: Row of the origin cell.
            c: Column of the origin cell.
            diagonal: When False (the default), yields up to 4
                orthogonal neighbours (up/down/left/right). When True,
                also yields up to 4 diagonal neighbours, for up to 8
                total. Neighbours that fall outside the grid -- at an
                edge or corner -- are skipped, never yielded as
                out-of-bounds coordinates.

        Yields:
            Each in-bounds neighbour as an `(r, c)` tuple.
        """
        deltas = _ORTHOGONAL_DELTAS
        if diagonal:
            deltas += _DIAGONAL_DELTAS
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc):
                yield nr, nc

    # -- overlay marks -------------------------------------------------

    def mark_visited(self, r: int, c: int) -> None:
        """Mark `(r, c)` as visited, then redraw (subject to batching)."""
        self._mark(Mark.VISITED, r, c)

    def mark_queued(self, r: int, c: int) -> None:
        """Mark `(r, c)` as queued, then redraw (subject to batching)."""
        self._mark(Mark.QUEUED, r, c)

    def mark_path(self, r: int, c: int) -> None:
        """Mark `(r, c)` as on the path, then redraw (subject to batching)."""
        self._mark(Mark.PATH, r, c)

    def mark_start(self, r: int, c: int) -> None:
        """Mark `(r, c)` as the start, then redraw (subject to batching)."""
        self._mark(Mark.START, r, c)

    def mark_target(self, r: int, c: int) -> None:
        """Mark `(r, c)` as the target, then redraw (subject to batching)."""
        self._mark(Mark.TARGET, r, c)

    def _mark(self, kind: Mark, r: int, c: int) -> None:
        """Record `(r, c)` under overlay `kind`, then redraw.

        Raises:
            IndexError: If `(r, c)` is outside the grid.
        """
        self._require_in_bounds(r, c)
        self._marks[kind].add((r, c))
        self._auto_show()

    def clear_marks(self, kind: Mark | None = None) -> None:
        """Clear overlay marks, then redraw (subject to batching).

        Unlike `self.highlights` (cleared automatically every frame),
        overlay marks are durable and only ever cleared on request --
        that persistence is what lets a render show the whole visited
        set of a BFS at once, not just the cells touched this step.

        Args:
            kind: The single overlay kind to clear (e.g. `Mark.VISITED`).
                When None (the default), every overlay kind is cleared.
        """
        kinds = self._marks if kind is None else {kind: self._marks[kind]}
        for cells in kinds.values():
            cells.clear()
        self._auto_show()

    def _style_for_cell(self, r: int, c: int) -> str | None:
        """The colour `(r, c)` renders in, or None for no colour.

        Precedence is stated once, on the class: overlay mark (in
        `_PRECEDENCE` order) > read/write highlight > `cell_map` value.
        """
        for kind in _PRECEDENCE:
            if (r, c) in self._marks[kind]:
                return self._mark_colors[kind]
        base = self.highlights.style_for((r, c), self.config)
        if base is not None:
            return base
        return self._color_for_value(self._data[r][c])

    def _color_for_value(self, value: Any) -> str | None:
        """The `cell_map` colour for `value`, or None when unmapped."""
        style = self._cell_styles.get(value)
        return style.color if style else None

    def _text_for_value(self, value: Any) -> Any:
        """The glyph `value` renders as, or the value itself when unmapped."""
        style = self._cell_styles.get(value)
        return style.glyph if style and style.glyph else value

    # -- batching --------------------------------------------------------

    @contextmanager
    def batch(self) -> Iterator[None]:
        """Suspend per-mutation redraws for the duration of the block.

        Mutations and highlight/mark bookkeeping still happen normally
        inside the block; only the automatic redraw after each one is
        suppressed. Exactly one redraw happens when the outermost
        `batch()` exits, still subject to the normal `auto_print` gate
        (a grid built with `auto_print=False` still never draws
        automatically, batched or not).

        This is local, redraw-only suspension scoped to this instance --
        a different concern from `algoviz.core.suspend_tracking`, which
        suspends *access recording* process-wide. `batch()` does not
        touch that mechanism.

        Nesting is supported via a depth counter, not a boolean: an
        inner `with grid.batch():` exiting must not trigger a draw while
        an outer `batch()` block is still open.

        Yields:
            None.
        """
        self._batch_depth += 1
        try:
            yield
        finally:
            self._batch_depth -= 1
            if self._batch_depth == 0:
                self._auto_show()

    def _auto_show(self) -> None:
        """Redraw from the root, unless a `batch()` block is still open."""
        if self._batch_depth > 0:
            return
        super()._auto_show()

    # -- viz plumbing ------------------------------------------------------

    def _eval_target(self) -> Any:
        """What `#` refers to inside `print(expr)`."""
        return self._data

    def _renderable(self, title: str | None = None) -> RenderableType:
        table = Table(
            title=title or self.title, show_header=self.config.show_header
        )
        table.add_column(" ")
        for c in range(self.cols):
            column_kwargs: dict[str, Any] = {"justify": "center"}
            if self.cell_width is not None:
                column_kwargs["width"] = self.cell_width
            table.add_column(str(c), **column_kwargs)

        for r, row in enumerate(self._data):
            cells = [paint(r, None)]
            for c, value in enumerate(row):
                text = self._text_for_value(value)
                cells.append(paint(text, self._style_for_cell(r, c)))
            table.add_row(*cells)
        return table

    def __repr__(self) -> str:
        """Same repr as the underlying list of rows."""
        return repr(self._data)

    def __str__(self) -> str:
        """Same str as the underlying list of rows."""
        return str(self._data)

    def __eq__(self, other: Any) -> bool:
        """Compare cell values with another `VizGrid` or a raw 2D list."""
        if isinstance(other, VizGrid):
            return self._data == other._data
        return self._data == other

    # A mutable container must not be hashable; defining __eq__ already
    # makes Python set __hash__ to None implicitly, this is just explicit.
    __hash__ = None  # type: ignore[assignment]
