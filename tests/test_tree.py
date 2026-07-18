"""Tests for `algoviz.viztree`."""

from __future__ import annotations

from typing import ClassVar

import pytest
from algoviz.core import VizConfig
from algoviz.viztree import TreeNode, VizTree

QUIET = VizConfig(auto_print=False, show_init=False)


@pytest.fixture
def quiet_config() -> VizConfig:
    """A config that never prints, so tests stay silent."""
    return QUIET


class TestLevelOrderRoundTrip:
    """Building from, and serializing back to, the LeetCode list shape."""

    def test_round_trips_with_none_padding(
        self, quiet_config: VizConfig
    ) -> None:
        """The exact LeetCode example round-trips unchanged."""
        values = [3, 9, 20, None, None, 15, 7]

        sut = VizTree.from_level_order(values, config=quiet_config)

        assert sut.to_level_order() == values

    def test_empty_list_is_an_empty_tree(self, quiet_config: VizConfig) -> None:
        """An empty or all-None source yields no root."""
        assert (
            VizTree.from_level_order([], config=quiet_config).root_node is None
        )
        assert (
            VizTree.from_level_order([None], config=quiet_config).root_node
            is None
        )

    def test_single_node_round_trips(self, quiet_config: VizConfig) -> None:
        """A one-element tree has no gaps to pad or trim."""
        sut = VizTree.from_level_order([5], config=quiet_config)

        assert sut.to_level_order() == [5]

    def test_wraps_an_existing_root_node(self, quiet_config: VizConfig) -> None:
        """A pasted-in TreeNode tree is accepted as-is."""
        root = TreeNode(1, TreeNode(2), TreeNode(3))

        sut = VizTree(root, config=quiet_config)

        assert sut.root_node is root
        assert sut.to_level_order() == [1, 2, 3]

    def test_trailing_none_gaps_are_trimmed(
        self, quiet_config: VizConfig
    ) -> None:
        """A right-leaning chain has no trailing Nones to keep."""
        sut = VizTree.from_level_order(
            [1, None, 2, None, 3], config=quiet_config
        )

        assert sut.to_level_order() == [1, None, 2, None, 3]


class TestTraversals:
    """inorder/preorder/postorder/level_order against known-correct output."""

    @pytest.fixture
    def sut(self, quiet_config: VizConfig) -> VizTree:
        """The LeetCode example tree: [3, 9, 20, None, None, 15, 7]."""
        return VizTree.from_level_order(
            [3, 9, 20, None, None, 15, 7], config=quiet_config
        )

    def test_inorder(self, sut: VizTree) -> None:
        """Left, root, right."""
        assert sut.inorder() == [9, 3, 15, 20, 7]

    def test_preorder(self, sut: VizTree) -> None:
        """Root, left, right."""
        assert sut.preorder() == [3, 9, 20, 15, 7]

    def test_postorder(self, sut: VizTree) -> None:
        """Left, right, root."""
        assert sut.postorder() == [9, 15, 7, 20, 3]

    def test_level_order(self, sut: VizTree) -> None:
        """Grouped by depth, shallowest first."""
        assert sut.level_order() == [[3], [9, 20], [15, 7]]

    def test_iter_matches_inorder(self, sut: VizTree) -> None:
        """Iterating the tree is the same as calling inorder()."""
        assert list(sut) == sut.inorder()

    def test_traversals_of_empty_tree_are_empty(
        self, quiet_config: VizConfig
    ) -> None:
        """No node means no output, not a crash."""
        sut = VizTree(config=quiet_config)

        assert sut.inorder() == []
        assert sut.preorder() == []
        assert sut.postorder() == []
        assert sut.level_order() == []
        assert list(sut) == []


class TestShape:
    """height and __len__."""

    def test_height_of_balanced_tree(self, quiet_config: VizConfig) -> None:
        """Longest root-to-leaf path, counted in nodes."""
        sut = VizTree.from_level_order(
            [3, 9, 20, None, None, 15, 7], config=quiet_config
        )

        assert sut.height() == 3

    def test_height_of_empty_tree_is_zero(
        self, quiet_config: VizConfig
    ) -> None:
        """An empty tree has no path at all."""
        assert VizTree(config=quiet_config).height() == 0

    def test_height_of_single_node_is_one(
        self, quiet_config: VizConfig
    ) -> None:
        """A lone root is a path of one node."""
        assert VizTree(TreeNode(1), config=quiet_config).height() == 1

    def test_len_counts_every_node(self, quiet_config: VizConfig) -> None:
        """Len counts nodes, not depth."""
        sut = VizTree.from_level_order(
            [3, 9, 20, None, None, 15, 7], config=quiet_config
        )

        assert len(sut) == 5

    def test_len_of_empty_tree_is_zero(self, quiet_config: VizConfig) -> None:
        """No nodes, no crash."""
        assert len(VizTree(config=quiet_config)) == 0


class TestBst:
    """BST insert and search."""

    def test_insert_builds_a_valid_bst(self, quiet_config: VizConfig) -> None:
        """Inorder traversal of a BST is always sorted."""
        sut = VizTree(config=quiet_config)
        for value in [5, 3, 8, 1, 4, 7, 9]:
            sut.insert(value)

        assert sut.inorder() == [1, 3, 4, 5, 7, 8, 9]

    def test_insert_into_empty_tree_creates_the_root(
        self, quiet_config: VizConfig
    ) -> None:
        """The first insert has no tree to descend into."""
        sut = VizTree(config=quiet_config)

        sut.insert(5)

        assert sut.root_node.val == 5

    def test_insert_duplicate_does_not_add_a_node(
        self, quiet_config: VizConfig
    ) -> None:
        """A value already present is left alone, not duplicated."""
        sut = VizTree(config=quiet_config)
        for value in [5, 3, 8]:
            sut.insert(value)

        sut.insert(5)

        assert len(sut) == 3

    def test_search_finds_an_existing_value(
        self, quiet_config: VizConfig
    ) -> None:
        """A present value is found and returns its node."""
        sut = VizTree(config=quiet_config)
        for value in [5, 3, 8, 1, 4]:
            sut.insert(value)

        found = sut.search(4)

        assert found is not None
        assert found.val == 4

    def test_search_misses_an_absent_value(
        self, quiet_config: VizConfig
    ) -> None:
        """A value never inserted is not found."""
        sut = VizTree(config=quiet_config)
        for value in [5, 3, 8]:
            sut.insert(value)

        assert sut.search(99) is None

    def test_search_on_empty_tree_returns_none(
        self, quiet_config: VizConfig
    ) -> None:
        """Nothing to search, no crash."""
        assert VizTree(config=quiet_config).search(1) is None


class TestVisit:
    """The user-driven animation hook."""

    def test_visit_highlights_the_node_in_get_color(
        self, quiet_config: VizConfig
    ) -> None:
        """Visiting a node marks it as read since the last render."""
        sut = VizTree(TreeNode(1), config=quiet_config)

        sut.visit(sut.root_node)

        assert id(sut.root_node) in sut.highlights.gets

    def test_visit_of_none_is_a_no_op(self, quiet_config: VizConfig) -> None:
        """A base-case None node can be visited unconditionally."""
        sut = VizTree(config=quiet_config)

        sut.visit(None)  # must not raise

        assert sut.highlights.gets == frozenset()


class TestFindOnUnorderedTrees:
    """`search` assumes BST ordering; `find` must not."""

    PLAIN: ClassVar = [3, 9, 20, None, None, 15, 7]

    def test_search_misses_values_on_a_plain_tree(self):
        """Pinning the footgun `find` exists to avoid."""
        tree = VizTree.from_level_order(self.PLAIN, config=QUIET)
        assert tree.search(9) is None, "BST search follows the wrong branch"
        assert tree.search(7) is None

    def test_find_locates_every_value_on_a_plain_tree(self):
        tree = VizTree.from_level_order(self.PLAIN, config=QUIET)
        for value in (3, 9, 20, 15, 7):
            found = tree.find(value)
            assert found is not None, f"find({value}) missed a present node"
            assert found.val == value

    def test_find_returns_none_for_an_absent_value(self):
        tree = VizTree.from_level_order(self.PLAIN, config=QUIET)
        assert tree.find(99) is None

    def test_find_on_an_empty_tree(self):
        assert VizTree.from_level_order([], config=QUIET).find(1) is None

    def test_find_returns_the_shallowest_leftmost_match(self):
        tree = VizTree.from_level_order([1, 1, 1], config=QUIET)
        assert tree.find(1) is tree.root_node

    def test_find_highlights_what_it_scanned(self):
        tree = VizTree.from_level_order(self.PLAIN, config=QUIET)
        tree.find(9)
        assert tree.highlights.gets, "the scanned path should be visible"

    def test_find_agrees_with_search_on_a_real_bst(self):
        tree = VizTree.from_level_order([5, 3, 8], config=QUIET)
        for value in (5, 3, 8):
            assert tree.find(value) is tree.search(value)
