"""Implement Trie: build the walk yourself, node by node (LeetCode 208).

The point of this problem is writing the traversal, so nothing here calls
`VizTrie.insert` or `VizTrie.search`. Those exist for when a trie is a tool
inside some larger problem. Here the trie is the exercise, so this walks
`root_node.children` by hand and calls `visit()` at each step to light up
the node it is standing on.
"""

from algoviz import TrieNode, VizTrie


class Trie:
    """A prefix tree, implemented over the nodes algoviz renders."""

    def __init__(self) -> None:
        """Start with an empty trie and the visual attached to its root."""
        self.viz = VizTrie(title_name="Trie")
        self.root = self.viz.root_node

    def insert(self, word: str) -> None:
        """Walk down the word, creating each node that does not exist yet."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            self.viz.visit(node, writing=True)
        node.is_word = True
        self.viz.show(f"inserted {word!r}")

    def _walk(self, prefix: str) -> TrieNode | None:
        """The node `prefix` ends at, or None if it falls off the trie."""
        node = self.root
        for char in prefix:
            node = node.children.get(char)
            if node is None:
                return None
            self.viz.visit(node)
        return node

    def search(self, word: str) -> bool:
        """True only when the full word was inserted, not just its prefix."""
        node = self._walk(word)
        self.viz.show(f"search {word!r}")
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        """True when any inserted word begins with `prefix`."""
        node = self._walk(prefix)
        self.viz.show(f"starts_with {prefix!r}")
        return node is not None


if __name__ == "__main__":
    trie = Trie()
    trie.insert("apple")
    trie.insert("app")
    # 'app' is a real word, 'appl' is only a prefix: that is the distinction
    # the problem is testing, and the render shows why.
    results = [
        trie.search("apple"),
        trie.search("appl"),
        trie.starts_with("appl"),
    ]
    print(f"Output : {results}")
