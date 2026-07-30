"""Tests for `VizStack`."""

from __future__ import annotations

import pytest
from algoviz.core import VizConfig, console
from algoviz.vizstack import VizStack

QUIET = VizConfig(sleep_time=0.0, show_init=False, auto_print=False)


@pytest.fixture
def sut() -> VizStack:
    """A stack seeded with a few elements, rendering suppressed."""
    return VizStack([1, 2, 3], config=QUIET)


class TestLifoOrder:
    """Push and pop follow last-in-first-out order."""

    def test_pop_returns_most_recently_pushed(self, sut: VizStack) -> None:
        """The most recent push is the first thing popped."""
        sut.push(4)

        assert sut.pop() == 4

    def test_pop_unwinds_in_reverse_push_order(self) -> None:
        """A run of pops returns pushes in reverse order."""
        sut = VizStack(config=QUIET)
        for value in (1, 2, 3):
            sut.push(value)

        assert [sut.pop(), sut.pop(), sut.pop()] == [3, 2, 1]

    def test_peek_does_not_remove(self, sut: VizStack) -> None:
        """Peeking leaves the stack's size and top unchanged."""
        before = len(sut)

        assert sut.peek() == 3
        assert sut.peek() == 3
        assert len(sut) == before

    def test_top_is_an_alias_for_peek(self, sut: VizStack) -> None:
        """`top` and `peek` return the same value."""
        assert sut.top() == sut.peek()


class TestEmptyStack:
    """An empty stack refuses to yield a value it does not have."""

    def test_pop_on_empty_raises_index_error(self) -> None:
        """Popping nothing raises, rather than returning None."""
        sut = VizStack(config=QUIET)

        with pytest.raises(IndexError):
            sut.pop()

    def test_peek_on_empty_raises_index_error(self) -> None:
        """Peeking nothing raises, rather than returning None."""
        sut = VizStack(config=QUIET)

        with pytest.raises(IndexError):
            sut.peek()

    def test_is_empty_true_for_fresh_stack(self) -> None:
        """A stack with no pushes reports itself empty."""
        assert VizStack(config=QUIET).is_empty()

    def test_is_empty_false_once_pushed(self, sut: VizStack) -> None:
        """A stack with elements does not report itself empty."""
        assert not sut.is_empty()

    def test_clear_empties_a_populated_stack(self, sut: VizStack) -> None:
        """Clearing removes every element."""
        sut.clear()

        assert sut.is_empty()
        assert len(sut) == 0


class TestProtocol:
    """Container protocol: len, iteration, membership, truthiness."""

    def test_len_matches_pushes(self, sut: VizStack) -> None:
        """Length reflects the number of elements currently pushed."""
        assert len(sut) == 3

    def test_iterates_top_to_bottom(self, sut: VizStack) -> None:
        """Iteration order is top-first, the order a stack reads."""
        assert list(sut) == [3, 2, 1]

    def test_contains_checks_membership_anywhere(self, sut: VizStack) -> None:
        """`in` finds a value regardless of its depth."""
        assert 1 in sut
        assert 99 not in sut

    def test_bool_false_when_empty(self) -> None:
        """An empty stack is falsy."""
        assert not VizStack(config=QUIET)

    def test_bool_true_when_populated(self, sut: VizStack) -> None:
        """A populated stack is truthy."""
        assert bool(sut)

    def test_data_property_exposes_underlying_list(self, sut: VizStack) -> None:
        """`data` returns the raw contents, bottom first."""
        assert sut.data == [1, 2, 3]

    def test_repr_matches_underlying_list(self, sut: VizStack) -> None:
        """Repr mirrors the plain-list repr."""
        assert repr(sut) == repr([1, 2, 3])


class TestRendering:
    """Rendering draws without crashing and marks only what moved."""

    def test_push_renders_top_marker_and_does_not_crash(self) -> None:
        """A push with auto-print on draws a table without raising."""
        sut = VizStack(config=VizConfig(sleep_time=0.0, show_init=False))

        with console.capture() as capture:
            sut.push("a")

        output = capture.get()
        assert "top" in output
        assert "a" in output

    def test_show_clears_highlights_after_drawing(self, sut: VizStack) -> None:
        """Once shown, a structure carries no leftover highlights."""
        sut.push(4)

        sut.show()

        assert not sut.highlights.gets
        assert not sut.highlights.sets

    def test_popped_element_still_appears_once_then_vanishes(self) -> None:
        """A pop shows the departed value for one frame, then drops it."""
        sut = VizStack(
            [1, 2], config=VizConfig(sleep_time=0.0, show_init=False)
        )

        with console.capture() as capture:
            sut.pop()
        first_frame = capture.get()

        with console.capture() as capture:
            sut.show()
        second_frame = capture.get()

        assert "2" in first_frame
        assert "2" not in second_frame

    def test_init_render_does_not_record_spurious_highlights(self) -> None:
        """Constructing and auto-showing leaves no dangling highlights."""
        sut = VizStack([1, 2, 3])

        assert not sut.highlights.gets
        assert not sut.highlights.sets


LOUD = VizConfig(sleep_time=0.0, show_init=False)
TEMPS = [73, 74, 75, 71, 69, 72, 76, 73]


def render(stack: VizStack) -> str:
    """The text of one frame of `stack`."""
    with console.capture() as capture:
        stack.show()
    return capture.get()


def bar_widths(frame: str) -> list[int]:
    """Filled cells per bar, top row first, ignoring partial blocks."""
    return [line.count("█") for line in frame.splitlines() if "█" in line]


class TestBars:
    """`bar_of` draws the magnitude an element stands for."""

    def test_no_bar_column_without_bar_of(self, sut: VizStack) -> None:
        """A stack given no mapping renders exactly as it always did."""
        assert "█" not in render(sut)

    def test_bar_label_heads_the_column(self) -> None:
        """The bar column carries the caller's heading."""
        sut = VizStack([1], config=LOUD, bar_of=lambda v: v, bar_label="height")

        assert "height" in render(sut)

    def test_magnitude_is_printed_beside_its_bar(self) -> None:
        """A bar is labelled with the number it represents."""
        sut = VizStack([2], config=LOUD, bar_of=lambda i: TEMPS[i])

        assert "75" in render(sut)

    def test_taller_magnitude_draws_a_longer_bar(self) -> None:
        """Bar length orders with magnitude, which is the whole point."""
        sut = VizStack(
            # Bottom-first, so this is temps 75, 71, 69: the staircase
            # daily_temperatures holds after day 4.
            [2, 3, 4],
            config=LOUD,
            bar_of=lambda i: TEMPS[i],
            bar_min=min(TEMPS),
            bar_max=max(TEMPS),
        )

        widths = bar_widths(render(sut))

        # Rendered top-first, so the warmest (bottom of stack) comes last.
        assert widths == sorted(widths)
        assert widths[0] < widths[-1]

    def test_element_may_be_its_own_magnitude(self) -> None:
        """A stack of values wants an identity mapping, not an index one."""
        sut = VizStack([1, 9], config=LOUD, bar_of=lambda value: value)

        top, bottom = bar_widths(render(sut))

        assert top > bottom

    def test_popped_element_keeps_its_bar_for_one_frame(self) -> None:
        """The departing element shows the magnitude that got it popped."""
        sut = VizStack([1, 9], config=LOUD, bar_of=lambda value: value)

        with console.capture() as capture:
            sut.pop()

        assert len(bar_widths(capture.get())) == 2

    def test_equal_magnitudes_do_not_divide_by_zero(self) -> None:
        """A degenerate span renders rather than raising."""
        sut = VizStack([5, 5, 5], config=LOUD, bar_of=lambda value: value)

        assert len(set(bar_widths(render(sut)))) == 1

    def test_smallest_magnitude_still_draws_a_bar(self) -> None:
        """The shortest bar is one cell, never a blank that reads as absent."""
        sut = VizStack([3, 8], config=LOUD, bar_of=lambda value: value)

        assert min(bar_widths(render(sut))) >= 1

    def test_pinned_scale_survives_a_pop(self) -> None:
        """With bounds pinned, a bar keeps its length as the stack drains."""
        sut = VizStack(
            [1, 5, 9], config=LOUD, bar_of=lambda v: v, bar_min=0, bar_max=10
        )
        before = bar_widths(render(sut))[-1]

        sut.pop()
        sut.clear_highlights()

        assert bar_widths(render(sut))[-1] == before

    def test_unpinned_scale_only_widens(self) -> None:
        """An unpinned bound remembers extremes that have left the stack."""
        sut = VizStack(config=LOUD, bar_of=lambda value: value)
        sut.push(100)
        sut.pop()
        sut.clear_highlights()
        sut.push(1)
        sut.push(50)

        top, bottom = bar_widths(render(sut))

        # 100 is gone but still sets the top of the scale, so 50 lands
        # mid-range instead of being redrawn as the new full bar.
        assert top > bottom
        assert top < 12

    def test_non_callable_bar_of_raises_type_error(self) -> None:
        """A non-callable mapping fails at construction, not at render."""
        with pytest.raises(TypeError):
            VizStack([1], config=QUIET, bar_of=[1, 2, 3])  # type: ignore[arg-type]

    def test_non_positive_bar_width_raises_value_error(self) -> None:
        """A zero-width bar column is a caller mistake, not a silent no-op."""
        with pytest.raises(ValueError):
            VizStack([1], config=QUIET, bar_of=lambda v: v, bar_width=0)
