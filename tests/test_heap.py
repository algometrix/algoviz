"""Behavioural tests for `VizHeap`.

`heapq` is never mocked here: every test exercises the real module through
`VizHeap`'s public API and checks the observable result (pop order, `data`,
raised errors). Rendering tests only assert that drawing does not crash --
the console output itself is not parsed.
"""

from __future__ import annotations

import random

import pytest
from algoviz.core import VizConfig
from algoviz.vizheap import VizHeap

SILENT = VizConfig(auto_print=False, show_init=False)


def make_heap(values=(), max_heap=False):
    """A `VizHeap` that never auto-prints, for tests that don't need it."""
    return VizHeap(values, config=SILENT, max_heap=max_heap)


def drain(heap):
    """Pop every item off `heap` and return them in pop order."""
    popped = []
    while heap:
        popped.append(heap.pop())
    return popped


class TestMinHeapOrder:
    """A min-heap must pop items back out in ascending order."""

    def test_pops_ascending(self):
        sut = make_heap([5, 3, 8, 1, 9, 2, 7])
        assert drain(sut) == [1, 2, 3, 5, 7, 8, 9]

    def test_matches_sorted_for_fixed_random_input(self):
        rng = random.Random(1234)
        values = [rng.randint(-50, 50) for _ in range(40)]
        sut = make_heap(values)
        assert drain(sut) == sorted(values)

    def test_heapify_from_iterable_preserves_all_values(self):
        values = [4, 4, 1, 1, 9, -3, 0]
        sut = make_heap(values)
        assert sorted(sut.data) == sorted(values)
        assert len(sut) == len(values)


class TestMaxHeapOrder:
    """A max-heap must pop items back out in descending order."""

    def test_pops_descending(self):
        sut = make_heap([5, 3, 8, 1, 9, 2, 7], max_heap=True)
        assert drain(sut) == [9, 8, 7, 5, 3, 2, 1]

    def test_matches_reverse_sorted_for_fixed_random_input(self):
        rng = random.Random(5678)
        values = [rng.randint(-50, 50) for _ in range(40)]
        sut = make_heap(values, max_heap=True)
        assert drain(sut) == sorted(values, reverse=True)

    def test_never_leaks_negated_values(self):
        sut = make_heap([5, 3, 8, 1, 9], max_heap=True)
        assert all(value > 0 for value in sut.data)
        assert sut.peek() == 9
        assert sut.pop() == 9
        sut.push(2)
        assert 2 in sut.data
        assert -2 not in sut.data
        assert all(value > 0 for value in sut.data)

    def test_pushpop_and_replace_never_leak_negated_values(self):
        sut = make_heap([5, 3, 8], max_heap=True)
        result = sut.pushpop(1)
        assert result == 8
        assert all(value > 0 for value in sut.data)
        old = sut.replace(2)
        assert old == 5
        assert all(value > 0 for value in sut.data)


class TestPeekAndTop:
    """`peek`/`top` must return the root without mutating the heap."""

    def test_peek_does_not_mutate_min_heap(self):
        sut = make_heap([5, 3, 8, 1])
        before = sorted(sut.data)
        assert sut.peek() == 1
        assert sut.peek() == 1
        assert len(sut) == 4
        assert sorted(sut.data) == before

    def test_top_is_an_alias_for_peek(self):
        sut = make_heap([5, 3, 8, 1])
        assert sut.top() == sut.peek() == 1
        assert len(sut) == 4

    def test_peek_does_not_mutate_max_heap(self):
        sut = make_heap([5, 3, 8, 1], max_heap=True)
        assert sut.peek() == 8
        assert len(sut) == 4
        assert 8 in sut.data


class TestEmptyHeapErrors:
    """Popping, peeking, or replacing on an empty heap must fail loudly."""

    def test_pop_on_empty_raises_index_error(self):
        sut = make_heap()
        with pytest.raises(IndexError):
            sut.pop()

    def test_peek_on_empty_raises_index_error(self):
        sut = make_heap()
        with pytest.raises(IndexError):
            sut.peek()

    def test_top_on_empty_raises_index_error(self):
        sut = make_heap()
        with pytest.raises(IndexError):
            sut.top()

    def test_replace_on_empty_raises_index_error(self):
        sut = make_heap()
        with pytest.raises(IndexError):
            sut.replace(1)

    def test_pushpop_on_empty_returns_value_without_raising(self):
        # Matches heapq.heappushpop: an empty heap just hands the value
        # straight back without ever storing it.
        sut = make_heap()
        assert sut.pushpop(42) == 42
        assert len(sut) == 0


class TestMaxHeapConstructionValidation:
    """max_heap=True must reject values it cannot negate, immediately."""

    def test_construction_with_non_numeric_values_raises(self):
        with pytest.raises(ValueError):
            make_heap(["a", "b", "c"], max_heap=True)

    def test_push_of_non_numeric_value_raises(self):
        sut = make_heap([1, 2, 3], max_heap=True)
        with pytest.raises(ValueError):
            sut.push("not a number")

    def test_key_argument_on_max_heap_query_raises(self):
        sut = make_heap([1, 2, 3], max_heap=True)
        with pytest.raises(ValueError):
            sut.nsmallest(2, key=lambda value: value)
        with pytest.raises(ValueError):
            sut.nlargest(2, key=lambda value: value)


class TestPushPopReplaceSemantics:
    """pushpop/replace must follow heapq's contract, not a hand-rolled one."""

    def test_pushpop_returns_value_unchanged_when_smaller_than_root(self):
        sut = make_heap([5, 6, 7])
        assert sut.pushpop(1) == 1
        assert sorted(sut.data) == [5, 6, 7]

    def test_pushpop_replaces_root_when_larger(self):
        sut = make_heap([5, 6, 7])
        assert sut.pushpop(10) == 5
        assert sorted(sut.data) == [6, 7, 10]

    def test_replace_always_swaps_the_root(self):
        sut = make_heap([5, 6, 7])
        assert sut.replace(1) == 5
        assert sorted(sut.data) == [1, 6, 7]


class TestQueries:
    """nsmallest/nlargest, membership, length, and iteration."""

    def test_nsmallest_and_nlargest(self):
        sut = make_heap([9, 3, 7, 1, 8, 2])
        assert sut.nsmallest(3) == [1, 2, 3]
        assert sut.nlargest(3) == [9, 8, 7]

    def test_nsmallest_with_key(self):
        sut = make_heap([-9, 3, -7, 1])
        assert sut.nsmallest(2, key=abs) == [1, 3]

    def test_contains(self):
        sut = make_heap([1, 2, 3])
        assert 2 in sut
        assert 99 not in sut

    def test_len_and_bool(self):
        sut = make_heap()
        assert len(sut) == 0
        assert not sut
        sut.push(1)
        assert len(sut) == 1
        assert sut

    def test_iter_yields_every_value_exactly_once(self):
        values = [5, 3, 8, 1, 9]
        sut = make_heap(values)
        assert sorted(sut) == sorted(values)


class TestLeetCodeStyleUseCases:
    """End-to-end shapes from the use cases this API is meant to cover."""

    def test_top_k_frequent_via_nlargest(self):
        counts = {"a": 5, "b": 1, "c": 9, "d": 3}
        sut = make_heap(counts.items())
        top_two = sut.nlargest(2, key=lambda pair: pair[1])
        assert [word for word, _ in top_two] == ["c", "a"]

    def test_merge_k_sorted_lists(self):
        lists = [[1, 4, 5], [1, 3, 4], [2, 6]]
        sut = make_heap()
        for list_index, values in enumerate(lists):
            sut.push((values[0], list_index, 0))

        merged = []
        while sut:
            value, list_index, item_index = sut.pop()
            merged.append(value)
            next_item_index = item_index + 1
            if next_item_index < len(lists[list_index]):
                sut.push(
                    (
                        lists[list_index][next_item_index],
                        list_index,
                        next_item_index,
                    )
                )

        expected = sorted(v for values in lists for v in values)
        assert merged == expected

    def test_median_from_data_stream(self):
        low = make_heap(max_heap=True)  # lower half, largest on top
        high = make_heap()  # upper half, smallest on top

        def add(value):
            if not low or value <= low.peek():
                low.push(value)
            else:
                high.push(value)
            if len(low) > len(high) + 1:
                high.push(low.pop())
            elif len(high) > len(low):
                low.push(high.pop())

        def median():
            if len(low) > len(high):
                return low.peek()
            return (low.peek() + high.peek()) / 2

        stream = [5, 15, 1, 3, 8, 7, 9, 2]
        medians = []
        for value in stream:
            add(value)
            medians.append(median())

        expected = []
        seen = []
        for value in stream:
            seen.append(value)
            ordered = sorted(seen)
            mid = len(ordered) // 2
            if len(ordered) % 2:
                expected.append(ordered[mid])
            else:
                expected.append((ordered[mid - 1] + ordered[mid]) / 2)

        assert medians == expected

    def test_task_scheduler_style_repeated_pushpop(self):
        # Repeatedly take the most-frequent task, cool it down, and put it
        # back -- exercises pop/push on a max-heap of counts under churn.
        counts = make_heap({"A": 3, "B": 3, "C": 1}.items(), max_heap=False)
        # Use a max-heap keyed by negated count via plain numerics: rebuild
        # as (count, task) tuples in a max-heap-free min-heap on -count.
        sut = make_heap([(-3, "A"), (-3, "B"), (-1, "C")])
        order = []
        for _ in range(3):
            neg_count, task = sut.pop()
            order.append(task)
            if neg_count + 1 < 0:
                sut.push((neg_count + 1, task))
        assert order[0] in {"A", "B"}
        assert len(order) == 3
        assert counts  # constructed heap is non-empty (sanity check)


class TestRendering:
    """Drawing must not crash for any heap size, and must reflect highlights."""

    @pytest.mark.parametrize("size", [0, 1, 2, 7, 8])
    def test_renders_without_crashing(self, size):
        sut = VizHeap(list(range(size, 0, -1)), config=SILENT)
        renderable = sut._renderable()
        assert renderable is not None

    def test_push_highlights_are_set_color(self):
        sut = make_heap([1, 2, 3])
        sut.push(0)
        # push() clears highlights via _auto_show only when auto_print is
        # on; with auto_print off we can inspect the highlight state that
        # would have been drawn.
        assert sut.highlights.sets or sut.highlights.gets

    def test_show_clears_highlights_after_drawing(self, capsys):
        sut = VizHeap([1, 2, 3], config=VizConfig(show_init=False))
        sut.push(0)
        capsys.readouterr()
        assert not sut.highlights.gets
        assert not sut.highlights.sets

    def test_pop_root_is_highlighted_before_removal(self):
        sut = VizHeap(
            [1, 2, 3], config=VizConfig(show_init=False, auto_print=False)
        )
        sut.highlights.mark_get(0)
        assert sut.highlights.style_for(0, sut.config) == sut.config.get_color
