"""Tests for VizList.

The important ones are the protocol-parity tests (a VizList must behave like
the list it wrapped) and the regression tests at the bottom, which pin the
bugs that motivated the rewrite.
"""

from __future__ import annotations

import io

import pytest
from algoviz.core import VizConfig, suspend_tracking
from algoviz.vizlist import VizList
from rich.console import Console

QUIET = VizConfig(auto_print=False, show_init=False)


def make(values, **kwargs):
    """A VizList that does not print, so tests stay readable."""
    return VizList(values, config=QUIET, **kwargs)


def render(structure) -> str:
    """The text a structure draws, with styling stripped.

    Rendered on a wide console so titles and cells are not wrapped mid-word,
    which would make substring assertions fail for cosmetic reasons.
    """
    console = Console(file=io.StringIO(), width=200, no_color=True)
    console.print(structure._renderable())
    return console.file.getvalue()


class TestSequenceParity:
    """A VizList must be indistinguishable from the list it wrapped."""

    @pytest.mark.parametrize(
        "values",
        [[], [1], [1, 2, 3], [0] * 5, ["a", "b"]],
    )
    def test_equals_source_list(self, values):
        assert make(values) == values
        assert list(make(values)) == values
        assert len(make(values)) == len(values)

    def test_iteration_order(self):
        # C416: the comprehension exercises __iter__, which is the point.
        assert [v for v in make([3, 1, 2])] == [3, 1, 2]  # noqa: C416

    def test_reversed(self):
        assert list(reversed(make([1, 2, 3]))) == [3, 2, 1]

    def test_membership(self):
        viz = make([1, 2, 3])
        assert 2 in viz
        assert 9 not in viz

    def test_builtins_that_consume_sequences(self):
        viz = make([3, 1, 2])
        assert sum(viz) == 6
        assert max(viz) == 3
        assert min(viz) == 1
        assert sorted(viz) == [1, 2, 3]

    def test_negative_indexing(self):
        assert make([1, 2, 3])[-1] == 3

    def test_slicing(self):
        assert make([1, 2, 3, 4])[1:3] == [2, 3]

    def test_index_and_count(self):
        viz = make([1, 2, 2, 3])
        assert viz.index(2) == 1
        assert viz.count(2) == 2

    def test_append_extend_insert(self):
        viz = make([1])
        viz.append(2)
        viz.extend([3, 4])
        viz.insert(0, 0)
        assert viz == [0, 1, 2, 3, 4]

    def test_pop_and_remove(self):
        viz = make([1, 2, 3])
        assert viz.pop() == 3
        viz.remove(1)
        assert viz == [2]

    def test_del_item(self):
        viz = make([1, 2, 3])
        del viz[1]
        assert viz == [1, 3]

    def test_sort_and_reverse_in_place(self):
        viz = make([3, 1, 2])
        viz.sort()
        assert viz == [1, 2, 3]
        viz.reverse()
        assert viz == [3, 2, 1]

    def test_repr_matches_list(self):
        assert repr(make([1, 2])) == repr([1, 2])

    def test_unhashable_like_a_list(self):
        with pytest.raises(TypeError):
            hash(make([1]))


class TestHighlighting:
    def test_read_is_recorded(self):
        viz = make([1, 2, 3])
        viz[1]
        assert viz.highlights.gets == frozenset({1})

    def test_write_is_recorded(self):
        viz = make([1, 2, 3])
        viz[2] = 9
        assert viz.highlights.sets == frozenset({2})

    def test_negative_index_recorded_as_positive(self):
        viz = make([1, 2, 3])
        viz[-1]
        assert viz.highlights.gets == frozenset({2})

    def test_slice_read_records_every_index(self):
        viz = make([1, 2, 3, 4, 5])
        viz[1:4]
        assert viz.highlights.gets == frozenset({1, 2, 3})

    def test_open_ended_slice_records_to_the_end(self):
        viz = make([1, 2, 3, 4])
        viz[2:]
        assert viz.highlights.gets == frozenset({2, 3})

    def test_show_clears_highlights(self):
        viz = make([1, 2, 3])
        viz[0]
        viz[1] = 5
        viz.show()
        assert not viz.highlights.gets
        assert not viz.highlights.sets

    def test_reads_while_suspended_are_not_recorded(self):
        viz = make([1, 2, 3])
        with suspend_tracking():
            viz[0]
        assert not viz.highlights.gets

    def test_write_colour_beats_read_colour(self):
        viz = make([1, 2, 3], get_color="blue", set_color="red")
        viz[1]
        viz[1] = 7
        assert viz.highlights.style_for(1, viz.config) == "red"


class TestTwoDimensional:
    def test_detects_nesting(self):
        assert make([[1, 2], [3, 4]]).is_2d is True
        assert make([1, 2]).is_2d is False

    def test_rows_become_children(self):
        viz = make([[1, 2], [3, 4]])
        assert all(isinstance(row, VizList) for row in viz.data)
        assert all(row.parent is viz for row in viz.data)

    def test_nested_read_and_write(self):
        viz = make([[1, 2], [3, 4]])
        assert viz[0][1] == 2
        viz[1][0] = 9
        assert viz[1] == [9, 4]

    def test_child_write_marks_child_not_parent(self):
        viz = make([[1, 2], [3, 4]])
        viz[0][1] = 8
        assert viz[0].highlights.sets == frozenset({1})
        assert not viz.highlights.sets

    def test_clearing_reaches_children(self):
        viz = make([[1, 2], [3, 4]])
        viz[0][1] = 8
        viz.clear_highlights()
        assert not viz[0].highlights.sets

    def test_assigning_a_raw_row_adopts_it(self):
        viz = make([[1, 2], [3, 4]])
        viz[0] = [7, 8]
        assert isinstance(viz.data[0], VizList)
        assert viz.data[0].parent is viz

    def test_empty_list_is_not_2d(self):
        assert make([]).is_2d is False

    def test_strings_are_cells_not_rows(self):
        """A list of strings is 1D; strings are Sequences but not rows."""
        assert make(["ab", "cd"]).is_2d is False


def flat(structure) -> str:
    """Rendered text with runs of whitespace collapsed.

    rich wraps a table title to the table's own width, so a title can arrive
    split across lines. Collapsing lets a test assert on the text itself
    rather than on incidental layout.
    """
    return " ".join(render(structure).split())


class TestRendering:
    def test_renders_values(self):
        assert "42" in render(make([42]))

    def test_renders_title(self):
        assert "My Table" in flat(make([1], title_name="My Table"))

    def test_renders_2d_rows(self):
        output = render(make([[1, 2], [3, 4]]))
        for value in ("1", "2", "3", "4"):
            assert value in output

    def test_row_and_column_labels(self):
        viz = make(
            [[0, 0], [0, 0]],
            row_index=["a", "b"],
            column_index=["x", "y"],
        )
        output = render(viz)
        assert "x" in output
        assert "a" in output

    def test_empty_list_renders(self):
        assert render(make([])) is not None

    def test_rendering_does_not_record_accesses(self):
        """The original bug: drawing the table dirtied the next frame."""
        viz = make([1, 2, 3])
        viz.show()
        assert not viz.highlights.gets
        assert not viz.highlights.sets

    def test_nested_render_leaves_tracking_enabled_after(self):
        """Re-entrant suspension must restore tracking once, not early."""
        viz = make([[1, 2], [3, 4]])
        viz.show()
        viz[0][1]
        assert viz[0].highlights.gets == frozenset({1})


class TestPrint:
    def test_plain_message(self, capsys):
        make([1, 2]).print("hello")
        assert "hello" in capsys.readouterr().out

    def test_expression_against_data(self, capsys):
        make([10, 20, 30]).print("value:", "#[1]")
        assert "20" in capsys.readouterr().out

    def test_expression_with_arithmetic(self, capsys):
        make([10, 20]).print("sum:", "#[0] + #[1]")
        assert "30" in capsys.readouterr().out

    def test_expression_does_not_record_highlights(self, capsys):
        viz = make([1, 2, 3])
        viz.print("x", "#[0]")
        capsys.readouterr()
        assert not viz.highlights.gets

    def test_expression_has_no_builtins(self):
        """The sandbox must not hand out __import__ and friends."""
        with pytest.raises((NameError, TypeError)):
            make([1]).print("x", "__import__('os').getcwd()")

    def test_expression_cannot_reach_self(self):
        with pytest.raises(NameError):
            make([1]).print("x", "self.config")


class TestRegressions:
    """Each of these pins a bug that existed before the rewrite."""

    def test_add_does_not_mutate(self):
        """`__add__` used to call extend, so `a + b` mutated `a` in place."""
        viz = make([1, 2])
        result = viz + [3]  # noqa: RUF005 - `+` is under test
        assert result == [1, 2, 3]
        assert viz == [1, 2], "the original list must be untouched"

    def test_add_returns_a_plain_list(self):
        assert isinstance(make([1]) + [2], list)  # noqa: RUF005

    def test_radd_works(self):
        assert [0] + make([1]) == [0, 1]  # noqa: RUF005 - __radd__ is under test

    def test_pop_returns_the_value(self):
        """`pop` had unreachable code after its return statement."""
        viz = make([1, 2, 3])
        assert viz.pop(0) == 1
        assert viz == [2, 3]

    def test_values_containing_markup_survive(self):
        """Values like '[red]' used to be swallowed as rich style tags."""
        output = render(make(["[red]"]))
        assert "[red]" in output

    def test_sibling_structures_do_not_share_state(self):
        """The old class-level `status` dict was shared by every instance."""
        first = make([1, 2, 3])
        second = make([4, 5, 6])
        first.show()
        second[0]
        assert second.highlights.gets == frozenset({0}), (
            "one structure rendering must not blind another"
        )

    def test_real_storage_is_not_empty(self):
        """Subclassing list left list's own storage empty; parity broke."""
        viz = make([1, 2, 3])
        assert list(viz) == [1, 2, 3]
        assert viz.data == [1, 2, 3]


class TestPointers:
    """Two-pointer problems are about where the pointers are."""

    def test_set_and_read_back(self):
        viz = make([1, 2, 3])
        viz.set_pointer("low", 0)
        viz.set_pointer("high", 2)
        assert viz.pointers == {"low": 0, "high": 2}

    def test_moving_a_pointer_replaces_it(self):
        viz = make([1, 2, 3])
        viz.set_pointer("i", 0)
        viz.set_pointer("i", 2)
        assert viz.pointers == {"i": 2}

    def test_none_removes_a_pointer(self):
        viz = make([1, 2, 3])
        viz.set_pointer("i", 1)
        viz.set_pointer("i", None)
        assert viz.pointers == {}

    def test_removing_an_absent_pointer_is_harmless(self):
        viz = make([1, 2, 3])
        viz.set_pointer("nope", None)
        assert viz.pointers == {}

    def test_clear_pointers(self):
        viz = make([1, 2, 3])
        viz.set_pointer("i", 0)
        viz.set_pointer("j", 1)
        viz.clear_pointers()
        assert viz.pointers == {}

    def test_pointers_property_is_a_snapshot(self):
        viz = make([1, 2, 3])
        viz.set_pointer("i", 0)
        viz.pointers["i"] = 99
        assert viz.pointers == {"i": 0}

    def test_setting_a_pointer_is_not_a_read(self):
        """The caller's own subscript records reads; this must not."""
        viz = make([1, 2, 3])
        viz.set_pointer("i", 1)
        assert not viz.highlights.gets

    def test_out_of_range_is_stored_but_not_drawn(self):
        """Pointers legally run past the end as a loop terminates."""
        viz = make([1, 2, 3])
        viz.set_pointer("past", 3)
        assert viz.pointers == {"past": 3}
        assert "past" not in render(viz)

    def test_negative_index_is_not_drawn(self):
        viz = make([1, 2, 3])
        viz.set_pointer("before", -1)
        assert "before" not in render(viz)

    def test_rejects_a_non_integer(self):
        viz = make([1, 2, 3])
        with pytest.raises(TypeError, match="int"):
            viz.set_pointer("i", "1")

    def test_rejects_a_bool(self):
        """A bool is an int subclass, and True as an index is a bug."""
        viz = make([1, 2, 3])
        with pytest.raises(TypeError, match="int"):
            viz.set_pointer("i", True)

    def test_rejected_on_a_2d_list(self):
        viz = make([[1, 2], [3, 4]])
        with pytest.raises(NotImplementedError, match="2D"):
            viz.set_pointer("i", 0)

    def test_label_is_drawn_under_the_value(self):
        viz = make([10, 20, 30])
        viz.set_pointer("low", 1)
        assert "low" in render(viz)

    def test_several_pointers_on_one_index_are_merged(self):
        viz = make([1, 2, 3])
        viz.set_pointer("i", 1)
        viz.set_pointer("j", 1)
        assert "i,j" in flat(viz)

    def test_no_pointer_row_when_none_are_set(self):
        """An untouched list must render exactly as it did before."""
        before = render(make([1, 2, 3]))
        viz = make([1, 2, 3])
        viz.set_pointer("i", 0)
        viz.set_pointer("i", None)
        assert render(viz) == before

    def test_pointers_survive_a_redraw(self):
        """A label stays put until the pointer moves, unlike a highlight."""
        viz = make([1, 2, 3])
        viz.set_pointer("i", 1)
        viz.show()
        assert "i" in render(viz)
