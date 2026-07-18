"""Tests for the suspension, tracking, and rendering primitives."""

from __future__ import annotations

import dataclasses
import threading

import pytest
from algoviz.core import (
    HighlightTracker,
    VizConfig,
    paint,
    substitute_placeholder,
    suspend_tracking,
    tracking_suspended,
)


class TestSuspension:
    def test_not_suspended_by_default(self):
        assert tracking_suspended() is False

    def test_suspended_inside_block(self):
        with suspend_tracking():
            assert tracking_suspended() is True
        assert tracking_suspended() is False

    def test_nesting_is_reentrant(self):
        """The bug the old boolean flag had: inner exit re-enabled tracking."""
        with suspend_tracking():
            with suspend_tracking():
                assert tracking_suspended() is True
            # Still suspended: the outer block has not exited yet.
            assert tracking_suspended() is True
        assert tracking_suspended() is False

    def test_deep_nesting_unwinds_exactly(self):
        depth = 12
        managers = [suspend_tracking() for _ in range(depth)]
        for manager in managers:
            manager.__enter__()
        for index, manager in enumerate(reversed(managers)):
            assert tracking_suspended() is True
            manager.__exit__(None, None, None)
            still_open = depth - index - 1
            assert tracking_suspended() is (still_open > 0)

    def test_exception_restores_state(self):
        with pytest.raises(ValueError, match="boom"):
            with suspend_tracking():
                raise ValueError("boom")
        assert tracking_suspended() is False

    def test_isolated_across_threads(self):
        """A render on one thread must not blind tracking on another."""
        observed: list[bool] = []
        started = threading.Event()
        release = threading.Event()

        def hold_suspended():
            with suspend_tracking():
                started.set()
                release.wait(timeout=5)

        worker = threading.Thread(target=hold_suspended)
        worker.start()
        started.wait(timeout=5)
        observed.append(tracking_suspended())
        release.set()
        worker.join(timeout=5)

        assert observed == [False]


class TestHighlightTracker:
    def test_records_gets_and_sets(self):
        tracker = HighlightTracker()
        tracker.mark_get(1, 2)
        tracker.mark_set(3)
        assert tracker.gets == frozenset({1, 2})
        assert tracker.sets == frozenset({3})

    def test_ignores_marks_while_suspended(self):
        tracker = HighlightTracker()
        with suspend_tracking():
            tracker.mark_get(1)
            tracker.mark_set(2)
        assert tracker.gets == frozenset()
        assert tracker.sets == frozenset()

    def test_set_wins_over_get(self):
        config = VizConfig(get_color="blue", set_color="red")
        tracker = HighlightTracker()
        tracker.mark_get(0)
        tracker.mark_set(0)
        assert tracker.style_for(0, config) == "red"

    def test_untouched_key_has_no_style(self):
        tracker = HighlightTracker()
        assert tracker.style_for(9, VizConfig()) is None

    def test_clear_forgets_everything(self):
        tracker = HighlightTracker()
        tracker.mark_get(1)
        tracker.mark_set(2)
        tracker.clear()
        assert not tracker.gets
        assert not tracker.sets

    def test_non_integer_keys_work(self):
        """Dicts and grids key highlights by string and by tuple."""
        tracker = HighlightTracker()
        tracker.mark_get("word")
        tracker.mark_set((2, 3))
        assert tracker.style_for("word", VizConfig()) == "blue"
        assert tracker.style_for((2, 3), VizConfig()) == "red"


class TestVizConfig:
    def test_child_stops_self_printing(self):
        parent = VizConfig(auto_print=True, show_init=True, get_color="green")
        child = parent.child()
        assert child.auto_print is False
        assert child.show_init is False
        assert child.get_color == "green"

    def test_is_frozen(self):
        config = VizConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            config.get_color = "purple"  # type: ignore[misc]


class TestPaint:
    def test_plain_value_when_unstyled(self):
        assert paint(7, None) == "7"

    def test_wraps_in_style_tags(self):
        assert paint(7, "red") == "[red]7[/red]"

    def test_escapes_tag_shaped_values(self):
        """A value like '[red]' must not be eaten as a rich style tag."""
        assert paint("[red]", None) == r"\[red]"

    def test_leaves_non_tag_brackets_alone(self):
        """Rich only treats tag-shaped text as markup, so '[2]' is literal."""
        assert paint("[2]", None) == "[2]"

    def test_escaping_survives_a_style(self):
        assert paint("[red]", "blue") == r"[blue]\[red][/blue]"


class TestSubstitutePlaceholder:
    @pytest.mark.parametrize(
        ("expr", "expected"),
        [
            ("#[0]", "_[0]"),
            ("#[i] + #[j]", "_[i] + _[j]"),
            ("len(#)", "len(_)"),
            ("", ""),
            ("no placeholder", "no placeholder"),
        ],
    )
    def test_replaces_outside_strings(self, expr, expected):
        assert substitute_placeholder(expr) == expected

    @pytest.mark.parametrize(
        "expr",
        [
            "'a # b'",
            '"a # b"',
            "'#'",
        ],
    )
    def test_leaves_quoted_hashes_alone(self, expr):
        """A naive str.replace corrupted these; that is why this exists."""
        assert substitute_placeholder(expr) == expr

    def test_mixed_quoted_and_bare(self):
        assert substitute_placeholder("'# tag' + #[0]") == "'# tag' + _[0]"

    def test_respects_escaped_quotes(self):
        expr = r"'it\'s # here' + #[1]"
        assert substitute_placeholder(expr) == r"'it\'s # here' + _[1]"
