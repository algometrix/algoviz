"""Shared primitives for every algoviz data structure.

Three concerns live here:

* Suspension -- while algoviz renders a structure it reads that structure's
  own data. Those reads must not be recorded as user accesses. Suspension is
  a property of the *dynamic extent* of a render, not of any one object, so
  it lives in a ContextVar with a depth counter. That makes it re-entrant
  (a parent rendering its children nests cleanly) and safe across threads
  and async tasks.
* Highlight tracking -- which keys were read and which were written since
  the last render.
* Rendering -- a single shared Console, and the config every structure takes.
"""

from __future__ import annotations

import contextvars
import time
from collections.abc import Hashable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import Any

from rich.console import Console, RenderableType
from rich.markup import escape

__all__ = [
    "HighlightTracker",
    "VizBase",
    "VizConfig",
    "console",
    "suspend_tracking",
    "tracking_suspended",
]

# One Console for the process. Creating one per render re-detects the terminal
# every time and drops colour when output is piped through a capture.
console = Console()

_suspend_depth: contextvars.ContextVar[int] = contextvars.ContextVar(
    "algoviz_suspend_depth", default=0
)


def tracking_suspended() -> bool:
    """True when accesses should not be recorded as user reads/writes."""
    return _suspend_depth.get() > 0


@contextmanager
def suspend_tracking() -> Iterator[None]:
    """Suspend access tracking for the duration of the block.

    Re-entrant: nesting increments a depth counter, so an inner block
    exiting does not re-enable tracking that an outer block turned off.
    This is the bug the old boolean `status['override_get']` flag had.
    """
    token = _suspend_depth.set(_suspend_depth.get() + 1)
    try:
        yield
    finally:
        _suspend_depth.reset(token)


@dataclass(frozen=True)
class VizConfig:
    """Presentation settings shared by every structure.

    Frozen so a config can be handed to child structures without one of them
    mutating what its siblings see.
    """

    get_color: str = "blue"
    set_color: str = "red"
    sleep_time: float = 0.0
    show_header: bool = True
    auto_print: bool = True
    show_init: bool = True

    def child(self) -> VizConfig:
        """Config for a nested structure: same look, but it never self-prints.

        Children are drawn as part of the parent's table, so a child that
        printed on its own would emit a second, half-rendered table.
        """
        return replace(self, auto_print=False, show_init=False)


class HighlightTracker:
    """Records which keys were read and written since the last render.

    Keys are whatever identifies a cell in the owning structure: an index for
    a list, a hashable key for a dict, a node id for a tree. Writes win over
    reads when a key is both, because the write is the more recent and more
    interesting event.
    """

    __slots__ = ("_gets", "_sets")

    def __init__(self) -> None:
        """Start with nothing recorded."""
        self._gets: set[Hashable] = set()
        self._sets: set[Hashable] = set()

    def mark_get(self, *keys: Hashable) -> None:
        """Record `keys` as read, unless tracking is suspended."""
        if tracking_suspended():
            return
        self._gets.update(keys)

    def mark_set(self, *keys: Hashable) -> None:
        """Record `keys` as written, unless tracking is suspended."""
        if tracking_suspended():
            return
        self._sets.update(keys)

    def clear(self) -> None:
        """Forget every recorded access."""
        self._gets.clear()
        self._sets.clear()

    @property
    def gets(self) -> frozenset[Hashable]:
        """Keys read since the last render."""
        return frozenset(self._gets)

    @property
    def sets(self) -> frozenset[Hashable]:
        """Keys written since the last render."""
        return frozenset(self._sets)

    def style_for(self, key: Hashable, config: VizConfig) -> str | None:
        """Colour for `key`, or None when it was neither read nor written."""
        if key in self._sets:
            return config.set_color
        if key in self._gets:
            return config.get_color
        return None


def paint(value: Any, style: str | None) -> str:
    """Render `value` as markup-safe text, optionally wrapped in a style.

    The escape matters: a list holding a string like "[2]" would otherwise be
    parsed by rich as a style tag and vanish from the output.
    """
    text = escape(str(value))
    if style is None:
        return text
    return f"[{style}]{text}[/{style}]"


class VizBase:
    """Common behaviour: config, highlight tracking, printing, rendering.

    Subclasses implement `_renderable()` and call `show()` when they want to
    draw. Everything about *when* to draw and how to keep tracking honest
    lives here so no subclass has to get it right again.
    """

    def __init__(
        self,
        title: str = "Structure",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Store presentation config, parent link, and a fresh tracker.

        Args:
            title: Heading drawn above the structure.
            config: Shared presentation settings; defaults are used if None.
            parent: Enclosing structure, when this one is nested.
            **overrides: Individual `VizConfig` fields to override.
        """
        base = config or VizConfig()
        self.config = replace(base, **overrides) if overrides else base
        self.title = title
        self.parent = parent
        self.highlights = HighlightTracker()

    # -- rendering ---------------------------------------------------------

    def _renderable(self, title: str | None = None) -> RenderableType:
        raise NotImplementedError

    @property
    def root(self) -> VizBase:
        """The outermost structure; the one that owns the drawing."""
        node: VizBase = self
        while node.parent is not None:
            node = node.parent
        return node

    def show(self, title: str | None = None) -> None:
        """Draw this structure and clear the highlights it just displayed."""
        with suspend_tracking():
            console.print(self._renderable(title or self.title))
            if self.config.sleep_time:
                time.sleep(self.config.sleep_time)
        self.clear_highlights()

    def _auto_show(self) -> None:
        """Draw from the root after a mutation, when auto-print is on."""
        root = self.root
        if root.config.auto_print:
            root.show()

    def clear_highlights(self) -> None:
        """Clear highlights on this structure and everything nested in it."""
        self.highlights.clear()
        for child in self._children():
            child.clear_highlights()

    def _children(self) -> Iterator[VizBase]:
        """Nested viz structures, so highlight clearing reaches them."""
        return iter(())

    # -- user-facing printing ---------------------------------------------

    def print(self, message: str = "", expr: str = "", end: str = "") -> None:
        """Print `message`, optionally followed by an evaluated expression.

        Inside `expr`, `#` stands for this structure's underlying data, so
        `obj.print('row', '#[3]')` prints the message and the value at index 3.

        The expression is evaluated with no builtins and with only the data in
        scope. It is still `eval`, so do not feed it untrusted input; prefer an
        f-string when you control the message anyway.
        """
        with suspend_tracking():
            if not expr:
                print(message, end)
                return
            rewritten = substitute_placeholder(expr)
            value = eval(
                rewritten, {"__builtins__": {}}, {"_": self._eval_target()}
            )
            print(message, value, end)

    def _eval_target(self) -> Any:
        """What `#` refers to inside `print(expr)`."""
        raise NotImplementedError


def substitute_placeholder(expr: str, name: str = "_") -> str:
    """Replace `#` with `name`, leaving `#` inside string literals alone.

    `#[0]` -> `_[0]`, but `"a # b"` is untouched. A plain str.replace would
    corrupt any expression containing a quoted hash, which is why this exists
    rather than the one-line replace it used to be.
    """
    out: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(expr):
        char = expr[index]
        if quote is not None:
            if char == "\\":
                out.append(expr[index : index + 2])
                index += 2
                continue
            if char == quote:
                quote = None
            out.append(char)
        elif char in ("'", '"'):
            quote = char
            out.append(char)
        elif char == "#":
            out.append(name)
        else:
            out.append(char)
        index += 1
    return "".join(out)
