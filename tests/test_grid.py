"""Tests for VizGrid.

Coordinate-space bugs (off-by-ones at edges and corners) are the likeliest
place a matrix-traversal helper breaks, so `TestNeighbors` asserts exact
coordinate sets, not just counts, at all four corners plus an edge and the
centre.
"""

from __future__ import annotations

import pytest
from algoviz import core
from algoviz.core import VizConfig
from algoviz.vizgrid import Mark, VizGrid

QUIET = VizConfig(auto_print=False, show_init=False)


def make(grid, **kwargs):
    """A VizGrid that does not print, so tests stay readable."""
    return VizGrid(grid, config=QUIET, **kwargs)


class TestConstruction:
    def test_list_of_lists(self):
        grid = make([["1", "1", "0"], ["0", "1", "0"]])
        assert grid.shape == (2, 3)
        assert grid[0, 0] == "1"
        assert grid[1, 1] == "1"

    def test_list_of_strings(self):
        grid = make(["110", "010"])
        assert grid.shape == (2, 3)
        assert grid[0, 0] == "1"
        assert grid[1, 1] == "1"

    def test_list_of_lists_and_strings_are_equivalent(self):
        from_lists = make([["1", "1", "0"], ["0", "1", "0"]])
        from_strings = make(["110", "010"])
        assert from_lists.shape == from_strings.shape
        assert list(from_lists) == list(from_strings)

    def test_rows_and_cols_and_shape(self):
        grid = make(["12345", "67890", "abcde"])
        assert grid.rows == 3
        assert grid.cols == 5
        assert grid.shape == (3, 5)

    def test_iteration_yields_plain_rows(self):
        grid = make([[1, 2], [3, 4]])
        rows = list(grid)
        assert rows == [[1, 2], [3, 4]]
        assert all(isinstance(row, list) for row in rows)

    def test_len_is_row_count(self):
        assert len(make(["12", "34", "56"])) == 3

    def test_find(self):
        grid = make(["101", "010", "101"])
        assert set(grid.find("1")) == {
            (0, 0),
            (0, 2),
            (1, 1),
            (2, 0),
            (2, 2),
        }


class TestIndexing:
    def test_int_index_returns_row(self):
        grid = make([[1, 2, 3], [4, 5, 6]])
        assert grid[0] == [1, 2, 3]
        assert grid[1] == [4, 5, 6]

    def test_double_subscript_reads(self):
        grid = make([[1, 2], [3, 4]])
        assert grid[0][1] == 2
        assert grid[1][0] == 3

    def test_tuple_reads_and_writes(self):
        grid = make([[1, 2], [3, 4]])
        assert grid[0, 1] == 2
        grid[0, 1] = 99
        assert grid[0, 1] == 99
        assert grid[0] == [1, 99]

    def test_tuple_read_records_a_get(self):
        grid = make([[1, 2], [3, 4]])
        grid[1, 0]
        assert grid.highlights.gets == frozenset({(1, 0)})

    def test_tuple_write_records_a_set(self):
        grid = make([[1, 2], [3, 4]])
        grid[1, 0] = 9
        assert grid.highlights.sets == frozenset({(1, 0)})

    def test_out_of_bounds_negative_raises_index_error(self):
        grid = make([[1, 2], [3, 4]])
        with pytest.raises(IndexError, match=r"\(-1, 0\)"):
            grid[-1, 0]

    def test_out_of_bounds_past_end_raises_index_error(self):
        grid = make([[1, 2], [3, 4]])
        with pytest.raises(IndexError, match=r"\(0, 2\)"):
            grid[0, 2]

    def test_out_of_bounds_error_names_shape(self):
        grid = make([[1, 2], [3, 4]])
        with pytest.raises(IndexError, match=r"shape \(2, 2\)"):
            grid[5, 5]

    def test_out_of_bounds_write_raises_index_error(self):
        grid = make([[1, 2], [3, 4]])
        with pytest.raises(IndexError):
            grid[2, 2] = 1


class TestInBounds:
    def test_inside_grid(self):
        grid = make([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        assert grid.in_bounds(1, 1) is True

    def test_negative_is_out_of_bounds(self):
        grid = make([[0, 0], [0, 0]])
        assert grid.in_bounds(-1, 0) is False
        assert grid.in_bounds(0, -1) is False

    def test_past_end_is_out_of_bounds(self):
        grid = make([[0, 0], [0, 0]])
        assert grid.in_bounds(2, 0) is False
        assert grid.in_bounds(0, 2) is False


class TestNeighbors:
    """Exact coordinate sets at every corner, an edge, and the centre.

    Grid is 3 rows x 4 cols, so corners are (0,0), (0,3), (2,0), (2,3).
    """

    def _grid(self):
        return make(["0000", "0000", "0000"])

    def test_top_left_corner(self):
        grid = self._grid()
        assert set(grid.neighbors(0, 0)) == {(1, 0), (0, 1)}

    def test_top_right_corner(self):
        grid = self._grid()
        assert set(grid.neighbors(0, 3)) == {(1, 3), (0, 2)}

    def test_bottom_left_corner(self):
        grid = self._grid()
        assert set(grid.neighbors(2, 0)) == {(1, 0), (2, 1)}

    def test_bottom_right_corner(self):
        grid = self._grid()
        assert set(grid.neighbors(2, 3)) == {(1, 3), (2, 2)}

    def test_edge_non_corner(self):
        grid = self._grid()
        # (0, 1) sits on the top edge, not a corner.
        assert set(grid.neighbors(0, 1)) == {(1, 1), (0, 0), (0, 2)}

    def test_centre(self):
        grid = self._grid()
        # (1, 1) has all four orthogonal neighbours in bounds.
        assert set(grid.neighbors(1, 1)) == {
            (0, 1),
            (2, 1),
            (1, 0),
            (1, 2),
        }

    def test_diagonal_at_centre_yields_all_eight(self):
        grid = self._grid()
        assert set(grid.neighbors(1, 1, diagonal=True)) == {
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 0),
            (1, 2),
            (2, 0),
            (2, 1),
            (2, 2),
        }

    def test_diagonal_at_corner_yields_three(self):
        grid = self._grid()
        assert set(grid.neighbors(0, 0, diagonal=True)) == {
            (0, 1),
            (1, 0),
            (1, 1),
        }

    def test_orthogonal_vs_diagonal_counts(self):
        grid = self._grid()
        assert len(list(grid.neighbors(1, 1))) == 4
        assert len(list(grid.neighbors(1, 1, diagonal=True))) == 8
        assert len(list(grid.neighbors(0, 0))) == 2
        assert len(list(grid.neighbors(0, 0, diagonal=True))) == 3


class TestOverlayMarks:
    def test_mark_visited_then_style(self):
        grid = make([[0, 0], [0, 0]])
        grid.mark_visited(0, 0)
        assert grid._style_for_cell(0, 0) == grid._mark_colors[Mark.VISITED]

    def test_unmarked_cell_has_no_overlay_style(self):
        grid = make([[0, 0], [0, 0]])
        assert grid._style_for_cell(1, 1) is None

    def test_precedence_target_beats_everything(self):
        grid = make([[0, 0]])
        grid.mark_visited(0, 0)
        grid.mark_queued(0, 0)
        grid.mark_path(0, 0)
        grid.mark_start(0, 0)
        grid.mark_target(0, 0)
        assert grid._style_for_cell(0, 0) == grid._mark_colors[Mark.TARGET]

    def test_precedence_path_beats_queued_and_visited(self):
        grid = make([[0, 0]])
        grid.mark_visited(0, 0)
        grid.mark_queued(0, 0)
        grid.mark_path(0, 0)
        assert grid._style_for_cell(0, 0) == grid._mark_colors[Mark.PATH]

    def test_precedence_start_beats_path(self):
        grid = make([[0, 0]])
        grid.mark_path(0, 0)
        grid.mark_start(0, 0)
        assert grid._style_for_cell(0, 0) == grid._mark_colors[Mark.START]

    def test_overlay_beats_base_get_highlight(self):
        grid = make([[0, 0]])
        grid[0, 0]  # records a base "get" highlight
        grid.mark_visited(0, 0)
        assert grid._style_for_cell(0, 0) == grid._mark_colors[Mark.VISITED]

    def test_mark_out_of_bounds_raises(self):
        grid = make([[0, 0]])
        with pytest.raises(IndexError):
            grid.mark_visited(5, 5)

    def test_distinct_default_colors(self):
        grid = make([[0]])
        colors = list(grid._mark_colors.values())
        assert len(colors) == len(set(colors)), "marks must not collide"
        assert grid.config.get_color not in colors
        assert grid.config.set_color not in colors


class TestClearMarks:
    def test_clear_all(self):
        grid = make([[0, 0], [0, 0]])
        grid.mark_visited(0, 0)
        grid.mark_queued(1, 1)
        grid.clear_marks()
        assert grid._style_for_cell(0, 0) is None
        assert grid._style_for_cell(1, 1) is None

    def test_clear_one_kind_leaves_others(self):
        grid = make([[0, 0], [0, 0]])
        grid.mark_visited(0, 0)
        grid.mark_queued(1, 1)
        grid.clear_marks(Mark.VISITED)
        assert grid._style_for_cell(0, 0) is None
        assert grid._style_for_cell(1, 1) == grid._mark_colors[Mark.QUEUED]


class TestBatching:
    def _spy(self, grid):
        """Wrap grid.show to count calls, without mocking anything."""
        calls = []
        original = grid.show

        def spy_show(title=None):
            calls.append(title)
            original(title)

        grid.show = spy_show
        return calls

    def test_marks_outside_batch_draw_each_time(self):
        grid = VizGrid([[0, 0], [0, 0]], config=VizConfig(show_init=False))
        calls = self._spy(grid)
        grid.mark_visited(0, 0)
        grid.mark_visited(0, 1)
        grid.mark_visited(1, 0)
        assert len(calls) == 3

    def test_batch_draws_once(self):
        grid = VizGrid([[0, 0], [0, 0]], config=VizConfig(show_init=False))
        calls = self._spy(grid)
        with grid.batch():
            grid.mark_visited(0, 0)
            grid.mark_visited(0, 1)
            grid.mark_visited(1, 0)
        assert len(calls) == 1

    def test_nested_batch_does_not_draw_early(self):
        grid = VizGrid([[0, 0], [0, 0]], config=VizConfig(show_init=False))
        calls = self._spy(grid)
        with grid.batch():
            grid.mark_visited(0, 0)
            with grid.batch():
                grid.mark_visited(0, 1)
            # Inner batch exited; outer is still open, so no draw yet.
            assert len(calls) == 0
            grid.mark_visited(1, 0)
        assert len(calls) == 1

    def test_batch_respects_auto_print_false(self):
        grid = make([[0, 0], [0, 0]])  # QUIET: auto_print=False
        calls = self._spy(grid)
        with grid.batch():
            grid.mark_visited(0, 0)
        assert len(calls) == 0


class TestNumberOfIslandsEndToEnd:
    """A real BFS run using `neighbors` and `mark_visited`."""

    def test_three_islands(self):
        # Hand count: top-left blob, top-right single cell, bottom row
        # blob -- three disjoint islands of '1's.
        grid = make(
            [
                "11000",
                "11010",
                "00000",
                "01110",
            ]
        )
        seen = set()
        islands = 0
        for r in range(grid.rows):
            for c in range(grid.cols):
                if grid[r, c] != "1" or (r, c) in seen:
                    continue
                islands += 1
                queue = [(r, c)]
                seen.add((r, c))
                grid.mark_visited(r, c)
                while queue:
                    cr, cc = queue.pop()
                    for nr, nc in grid.neighbors(cr, cc):
                        if (nr, nc) in seen or grid[nr, nc] != "1":
                            continue
                        seen.add((nr, nc))
                        grid.mark_visited(nr, nc)
                        queue.append((nr, nc))
        assert islands == 3
        assert len(seen) == 8  # 4 + 1 + 3 cells across the three islands


class TestRendering:
    def test_renders_values_and_indices(self):
        grid = make(["12", "34"])
        with core.console.capture() as captured:
            core.console.print(grid._renderable())
        output = captured.get()
        for value in ("1", "2", "3", "4"):
            assert value in output

    def test_renders_title(self):
        grid = make(["1"], title_name="My Grid")
        with core.console.capture() as captured:
            core.console.print(grid._renderable())
        assert "My Grid" in captured.get()

    def test_cell_width_does_not_crash(self):
        grid = make(["11", "01"], cell_width=5)
        with core.console.capture() as captured:
            core.console.print(grid._renderable())
        assert captured.get()


class TestEquality:
    def test_equal_to_plain_list(self):
        assert make([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]

    def test_equal_to_another_vizgrid(self):
        assert make([[1, 2]]) == make([[1, 2]])

    def test_unhashable(self):
        with pytest.raises(TypeError):
            hash(make([[1]]))
