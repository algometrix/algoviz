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
