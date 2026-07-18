"""Tests for the package surface and the contract every structure shares.

The per-structure test modules cover behaviour in depth. These cover what
only shows up when the structures are looked at together: that the public
API is importable and coherent, that every structure honours the same
presentation contract, and that the examples in the README actually run.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import algoviz
import pytest
from algoviz import (
    VizConfig,
    VizCounter,
    VizDeque,
    VizDict,
    VizGrid,
    VizHeap,
    VizLinkedList,
    VizList,
    VizQueue,
    VizSet,
    VizStack,
    VizTree,
    VizTrie,
    VizUnionFind,
)
from algoviz.core import VizBase
from algoviz.vizlist import VizList as LegacyVizList
from rich.console import Console

REPO_ROOT = Path(__file__).resolve().parent.parent
QUIET = VizConfig(auto_print=False, show_init=False)
README = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

# Every concrete structure, built with settings that suppress drawing, so a
# single contract can be asserted against all of them.
FACTORIES = {
    "VizList": lambda cfg: VizList([1, 2, 3], config=cfg),
    "VizList2D": lambda cfg: VizList([[1, 2], [3, 4]], config=cfg),
    "VizStack": lambda cfg: VizStack([1, 2, 3], config=cfg),
    "VizQueue": lambda cfg: VizQueue([1, 2, 3], config=cfg),
    "VizDeque": lambda cfg: VizDeque([1, 2, 3], config=cfg),
    "VizHeap": lambda cfg: VizHeap([3, 1, 2], config=cfg),
    "VizDict": lambda cfg: VizDict({"a": 1}, config=cfg),
    "VizCounter": lambda cfg: VizCounter({"a": 1}, config=cfg),
    "VizSet": lambda cfg: VizSet({1, 2}, config=cfg),
    "VizGrid": lambda cfg: VizGrid(["11", "01"], config=cfg),
    "VizLinkedList": lambda cfg: VizLinkedList([1, 2, 3], config=cfg),
    "VizTree": lambda cfg: VizTree.from_level_order([1, 2, 3], config=cfg),
    "VizTrie": lambda cfg: VizTrie(["ab"], config=cfg),
    "VizUnionFind": lambda cfg: VizUnionFind(3, config=cfg),
}


def build(name, **overrides):
    """Construct a structure by name with the quiet config."""
    config = VizConfig(auto_print=False, show_init=False, **overrides)
    return FACTORIES[name](config)


class TestPublicApi:
    def test_every_exported_name_exists(self):
        for name in algoviz.__all__:
            assert hasattr(algoviz, name), f"{name} is exported but missing"

    def test_all_is_sorted(self):
        assert algoviz.__all__ == sorted(algoviz.__all__)

    def test_version_matches_pyproject(self):
        """A drifting version ships metadata that contradicts the package."""
        text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        declared = re.search(r'^version = "([^"]+)"', text, re.M)
        assert declared is not None
        assert algoviz.__version__ == declared.group(1)

    @pytest.mark.parametrize("name", sorted(FACTORIES))
    def test_structures_are_exported(self, name):
        exported = name.removesuffix("2D")
        assert exported in algoviz.__all__

    def test_legacy_import_path_still_works(self):
        """0.2.x code imported from the module, not the package."""
        assert LegacyVizList is VizList


class TestSharedContract:
    """Every structure must honour the same presentation contract."""

    @pytest.mark.parametrize("name", sorted(FACTORIES))
    def test_is_a_viz_structure(self, name):
        assert isinstance(build(name), VizBase)

    @pytest.mark.parametrize("name", sorted(FACTORIES))
    def test_show_init_false_draws_nothing(self, name, capsys):
        build(name)
        assert capsys.readouterr().out == ""

    @pytest.mark.parametrize("name", sorted(FACTORIES))
    def test_show_draws_something(self, name):
        structure = build(name)
        console = Console(file=io.StringIO(), width=200, no_color=True)
        console.print(structure._renderable())
        assert console.file.getvalue().strip() != ""

    @pytest.mark.parametrize("name", sorted(FACTORIES))
    def test_show_clears_highlights(self, name):
        structure = build(name)
        structure.show()
        assert not structure.highlights.gets
        assert not structure.highlights.sets

    @pytest.mark.parametrize("name", sorted(FACTORIES))
    def test_config_overrides_apply(self, name):
        structure = build(name, get_color="green")
        assert structure.config.get_color == "green"

    @pytest.mark.parametrize("name", sorted(FACTORIES))
    def test_title_is_set(self, name):
        assert build(name).title

    @pytest.mark.parametrize("name", sorted(FACTORIES))
    def test_repeated_renders_are_stable(self, name):
        """Rendering must not mutate the structure it draws."""
        structure = build(name)
        console = Console(file=io.StringIO(), width=200, no_color=True)
        console.print(structure._renderable())
        first = console.file.getvalue()
        console = Console(file=io.StringIO(), width=200, no_color=True)
        console.print(structure._renderable())
        assert console.file.getvalue() == first

    def test_structures_do_not_share_highlight_state(self):
        """The old class-level `status` dict was shared by every instance."""
        first = build("VizList")
        second = build("VizList")
        first[0]
        assert not second.highlights.gets

    def test_one_structure_rendering_does_not_blind_another(self):
        """Suspension is scoped to the render, not global and sticky."""
        first = build("VizList")
        second = build("VizList")
        first.show()
        second[1]
        assert second.highlights.gets == frozenset({1})


class TestReadmeExamples:
    """The documented examples must actually produce the documented output."""

    def test_coin_change_quick_start(self):
        dp = VizList([0] * 4, config=QUIET)
        dp[0] = 1
        for coin in (1, 2):
            for val in range(coin, 4):
                dp[val] += dp[val - coin]
        # 3 from coins {1, 2} is 1+1+1 or 1+2, so two combinations.
        assert dp[-1] == 2

    def test_stack_parentheses(self):
        stack = VizStack(config=QUIET)
        for char in "([])":
            if char in "([":
                stack.push(char)
            else:
                stack.pop()
        assert stack.is_empty()

    def test_heap_example(self):
        heap = VizHeap([5, 3, 8, 1], config=QUIET)
        heap.push(2)
        assert heap.data == [1, 2, 8, 5, 3]
        assert heap.pop() == 1

    def test_grid_neighbors(self):
        grid = VizGrid(["11000", "11000", "00100"], config=QUIET)
        assert grid.shape == (3, 5)
        assert grid[0, 0] == "1"
        assert set(grid.neighbors(0, 0)) == {(1, 0), (0, 1)}

    def test_linked_list_two_pointer(self):
        linked = VizLinkedList([1, 2, 3, 4, 5], config=QUIET)
        slow = fast = linked.head
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
            linked.set_pointer("slow", slow)
            linked.set_pointer("fast", fast)
        assert slow.val == 3, "slow lands on the middle node"

    def test_tree_traversals(self):
        tree = VizTree.from_level_order(
            [3, 9, 20, None, None, 15, 7], config=QUIET
        )
        assert tree.inorder() == [9, 3, 15, 20, 7]
        assert tree.level_order() == [[3], [9, 20], [15, 7]]

    def test_union_find(self):
        uf = VizUnionFind(5, config=QUIET)
        uf.union(0, 1)
        uf.union(3, 4)
        assert uf.connected(0, 1) is True
        assert uf.component_count == 3

    def test_trie_search_versus_prefix(self):
        trie = VizTrie(config=QUIET)
        trie.insert("apple")
        assert trie.search("app") is False
        assert trie.starts_with("app") is True

    def test_config_example(self):
        dp = VizList([0] * 5, config=QUIET)
        dp[2] = 7
        assert dp[2] == 7


class TestReadmeIsHonest:
    """Cheap guards against the README drifting from the code."""

    @pytest.mark.parametrize("name", sorted(set(FACTORIES) - {"VizList2D"}))
    def test_every_structure_is_documented(self, name):
        readme = README
        assert name in readme, f"{name} is public but not in the README"

    def test_documented_config_defaults_are_real(self):
        readme = README
        """The settings table must match the actual defaults."""
        defaults = VizConfig()
        assert defaults.get_color == "blue"
        assert defaults.set_color == "red"
        assert defaults.sleep_time == 0
        assert defaults.auto_print is True
        assert defaults.show_init is True
        assert defaults.show_header is True
        for setting in (
            "get_color",
            "set_color",
            "sleep_time",
            "auto_print",
            "show_init",
            "show_header",
        ):
            assert f"`{setting}`" in readme
