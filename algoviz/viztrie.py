"""A prefix tree that draws itself with `rich.tree.Tree`.

Backs the word-search / autocomplete / word-break family of problems,
where the operation that matters visually is "which path down the trie
did the last insert or search take" -- so every mutating or searching
call records the path it walked, and the render highlights it in
`get_color`/`set_color` and marks end-of-word nodes with a bullet.

Trie problems are almost always asked to be implemented from scratch,
so `TrieNode` is public and `root_node` hands it out. A student can walk
and mutate the trie by hand, calling `visit()` to drive the animation one
node at a time -- the same shape `VizTree` and `VizLinkedList` use. The
built-in `insert`/`search`/`delete` are there for when the trie is a tool
in some larger problem, not the exercise itself.

Scale: keep it to roughly a dozen short words. The render is one line per
node, and a trie's node count grows with the total number of characters
rather than the number of words, so 20 words of 5 to 8 letters is already
about 62 nodes and overflows a normal terminal in a single frame. That is
far denser than the other structures here, where 20 values means 20 nodes
or fewer. Nothing breaks past that point, it just stops being legible, so
prefer a small illustrative word set over a realistic dictionary.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

from rich.console import RenderableType
from rich.tree import Tree

from algoviz.core import VizBase, VizConfig, paint

__all__ = ["TrieNode", "VizTrie"]

_WORD_MARK = "•"


class TrieNode:
    """One node of the trie: its children and whether a word ends here.

    Public, and deliberately plain, because implementing the walk over
    these nodes is the exercise. `children` maps a single character to
    the next node; `is_word` marks that a word ends here.
    """

    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        """Create a node with no children, not yet the end of a word."""
        self.children: dict[str, TrieNode] = {}
        self.is_word = False


class VizTrie(VizBase):
    """A prefix tree rendered as a `rich.tree.Tree`.

    `insert` and `delete` highlight the path they touch in `set_color`
    and redraw. `search` and `starts_with` highlight the path walked in
    `get_color` but, like a plain read elsewhere in algoviz, do not
    redraw on their own -- call `show()` to see it.
    """

    def __init__(
        self,
        source: Iterable[str] | None = None,
        title_name: str = "Trie",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Build a trie, optionally pre-populated with words from `source`."""
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._root = TrieNode()

        for word in source or ():
            self._insert_quietly(word)

        if self.config.show_init:
            self.show(f"{self.title} Init")

    def _insert_quietly(self, word: str) -> None:
        """Insert `word` without touching highlights or redrawing.

        Used only while the initial `source` is being loaded, so
        construction produces one "Init" frame instead of one per word.
        """
        if not word:
            raise ValueError("cannot insert an empty word")
        path = self._create_path(word)
        path[-1].is_word = True

    def _create_path(self, word: str) -> list[TrieNode]:
        """Create any missing nodes along `word`, returning the full path.

        The path always starts with the root, so it has `len(word) + 1`
        entries.
        """
        node = self._root
        path = [node]
        for char in word:
            node = node.children.setdefault(char, TrieNode())
            path.append(node)
        return path

    def _walk(self, prefix: str) -> list[TrieNode]:
        """Nodes visited while consuming `prefix`, starting with the root.

        Stops early -- the returned path is shorter than
        `len(prefix) + 1` -- the moment a character has no matching
        child.
        """
        path = [self._root]
        node = self._root
        for char in prefix:
            child = node.children.get(char)
            if child is None:
                break
            node = child
            path.append(node)
        return path

    # -- operations ------------------------------------------------------

    def insert(self, word: str) -> None:
        """Insert `word`, then redraw.

        Raises:
            ValueError: If `word` is empty.
        """
        if not word:
            raise ValueError("cannot insert an empty word")
        path = self._create_path(word)
        path[-1].is_word = True

        self.highlights.clear()
        self.highlights.mark_set(*(id(node) for node in path))
        self._auto_show()

    def search(self, word: str) -> bool:
        """True when `word` was inserted exactly, not just as a prefix."""
        path = self._walk(word)
        self.highlights.clear()
        self.highlights.mark_get(*(id(node) for node in path))
        return len(path) == len(word) + 1 and path[-1].is_word

    def starts_with(self, prefix: str) -> bool:
        """True when some inserted word begins with `prefix`."""
        path = self._walk(prefix)
        self.highlights.clear()
        self.highlights.mark_get(*(id(node) for node in path))
        return len(path) == len(prefix) + 1

    def delete(self, word: str) -> bool:
        """Remove `word`, then redraw.

        Prunes trailing nodes left with no children and no word ending
        there, so sibling words that share a prefix with `word` are
        unaffected.

        Returns:
            True when `word` was present and removed.
        """
        path = self._walk(word)
        if len(path) != len(word) + 1 or not path[-1].is_word:
            return False

        path[-1].is_word = False
        self._prune(path, word)

        self.highlights.clear()
        self.highlights.mark_set(*(id(node) for node in path))
        self._auto_show()
        return True

    def _prune(self, path: list[TrieNode], word: str) -> None:
        """Drop trailing nodes in `path` that no longer serve a purpose."""
        for depth in range(len(word), 0, -1):
            node = path[depth]
            if node.children or node.is_word:
                break
            parent = path[depth - 1]
            del parent.children[word[depth - 1]]

    def words(self) -> list[str]:
        """Every word currently stored, in sorted order."""
        found: list[str] = []
        self._collect(self._root, "", found)
        return sorted(found)

    def _collect(self, node: TrieNode, prefix: str, out: list[str]) -> None:
        if node.is_word:
            out.append(prefix)
        for char, child in node.children.items():
            self._collect(child, prefix + char, out)

    def __len__(self) -> int:
        """Number of words stored.

        Counted from the nodes rather than cached, so it stays correct
        when a caller sets `is_word` by hand while implementing their
        own insert.
        """
        return len(self.words())

    def __contains__(self, word: str) -> bool:
        """True when `word` was inserted exactly."""
        return self.search(word)

    def __iter__(self) -> Iterator[str]:
        """Iterate stored words in sorted order."""
        return iter(self.words())

    # -- driving your own traversal ----------------------------------------

    @property
    def root_node(self) -> TrieNode:
        """The root `TrieNode`, the starting point for your own walk.

        The root holds no character; a word's first letter is a key in
        `root_node.children`. Named `root_node` rather than `root`
        because `VizBase.root` already means "the outermost structure
        that owns drawing" and `_auto_show` depends on that meaning.
        """
        return self._root

    def visit(self, node: TrieNode | None, writing: bool = False) -> None:
        """Mark `node` as the one currently being visited, then redraw.

        Call this inside your own insert or search loop to animate it one
        node at a time. Visits accumulate, so the path you have walked so
        far stays lit until the next redraw clears it.

        Args:
            node: The node being visited. `None` is a no-op, so this is
                safe to call unconditionally when a child may be missing.
            writing: Highlight in `set_color` instead of `get_color`, for
                when the step creates or modifies a node rather than
                reading it.
        """
        if node is None:
            return
        if writing:
            self.highlights.mark_set(id(node))
        else:
            self.highlights.mark_get(id(node))
        self._auto_show()

    # -- viz plumbing ------------------------------------------------------

    def _eval_target(self) -> Any:
        return self.words()

    def _renderable(self, title: str | None = None) -> RenderableType:
        tree = Tree(title or self.title)
        self._attach(tree, self._root)
        return tree

    def _attach(self, branch: Tree, node: TrieNode) -> None:
        for char, child in sorted(node.children.items()):
            style = self.highlights.style_for(id(child), self.config)
            label = paint(char, style)
            if child.is_word:
                label += f" {_WORD_MARK}"
            self._attach(branch.add(label), child)
