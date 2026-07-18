"""Tests for `VizUnionFind`."""

from __future__ import annotations

import pytest
from algoviz.core import VizConfig, console
from algoviz.vizunionfind import VizUnionFind

QUIET = VizConfig(sleep_time=0.0, show_init=False, auto_print=False)


@pytest.fixture
def sut() -> VizUnionFind:
    """Five singleton elements, rendering suppressed."""
    return VizUnionFind(5, config=QUIET)


class TestConstruction:
    """Building from a count vs. from an iterable of labels."""

    def test_an_int_creates_zero_indexed_elements(
        self, sut: VizUnionFind
    ) -> None:
        assert set(sut._parent) == set(range(5))
        assert sut.component_count == 5

    def test_an_iterable_creates_labelled_elements(self) -> None:
        sut = VizUnionFind(["a", "b", "c"], config=QUIET)

        assert set(sut._parent) == {"a", "b", "c"}
        assert sut.component_count == 3


class TestUnionAndFind:
    """Union/find/connected and the component bookkeeping they drive."""

    def test_union_is_transitive(self, sut: VizUnionFind) -> None:
        sut.union(0, 1)
        sut.union(1, 2)

        assert sut.connected(0, 2)

    def test_component_count_decrements_once_per_successful_union(
        self, sut: VizUnionFind
    ) -> None:
        assert sut.component_count == 5

        assert sut.union(0, 1) is True
        assert sut.component_count == 4

        assert sut.union(1, 2) is True
        assert sut.component_count == 3

    def test_an_already_connected_union_is_a_no_op(
        self, sut: VizUnionFind
    ) -> None:
        sut.union(0, 1)

        assert sut.union(0, 1) is False
        assert sut.component_count == 4

    def test_component_size_reflects_unions(self, sut: VizUnionFind) -> None:
        sut.union(0, 1)
        sut.union(1, 2)

        assert sut.component_size(0) == 3
        assert sut.component_size(3) == 1

    def test_components_groups_elements_by_root(
        self, sut: VizUnionFind
    ) -> None:
        sut.union(0, 1)

        groups = sut.components()
        sizes = sorted(len(members) for members in groups.values())
        assert sizes == [1, 1, 1, 2]

        pair = next(m for m in groups.values() if len(m) == 2)
        assert sorted(pair) == [0, 1]


class TestPathCompression:
    """Path compression must actually flatten parent pointers."""

    def test_find_flattens_a_chain_at_least_three_deep(
        self, sut: VizUnionFind
    ) -> None:
        # `union`'s own union-by-size balancing never produces a chain
        # this deep on its own, so the chain is built by hand: 0 -> 1 ->
        # 2 -> 3 (root). That makes compression observable rather than
        # a trivial one-hop case.
        sut._parent[0] = 1
        sut._parent[1] = 2
        sut._parent[2] = 3

        root = sut.find(0)

        assert root == 3
        assert sut._parent[0] == 3
        assert sut._parent[1] == 3
        assert sut._parent[2] == 3


class TestUnknownElements:
    """Every lookup surface must reject elements it never saw."""

    def test_find_raises_key_error(self, sut: VizUnionFind) -> None:
        with pytest.raises(KeyError):
            sut.find("nope")

    def test_union_raises_key_error(self, sut: VizUnionFind) -> None:
        with pytest.raises(KeyError):
            sut.union("nope", 0)

    def test_connected_raises_key_error(self, sut: VizUnionFind) -> None:
        with pytest.raises(KeyError):
            sut.connected("nope", 0)

    def test_component_size_raises_key_error(self, sut: VizUnionFind) -> None:
        with pytest.raises(KeyError):
            sut.component_size("nope")


class TestRendering:
    """Rendering draws without crashing, empty or populated."""

    def test_empty_union_find_renders_without_crashing(self) -> None:
        sut = VizUnionFind(0, config=QUIET)

        with console.capture() as capture:
            sut.show()

        assert "empty" in capture.get()

    def test_populated_union_find_renders_elements_and_components(
        self, sut: VizUnionFind
    ) -> None:
        sut.union(0, 1)
        sut.union(2, 3)

        with console.capture() as capture:
            sut.show()

        output = capture.get()
        assert "components" in output
        assert "0" in output
