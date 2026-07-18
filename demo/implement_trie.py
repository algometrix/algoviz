"""Implement Trie: prefix search over a word set (LeetCode 208)."""

from algoviz import VizTrie


def demo() -> bool:
    """Insert a few words, then show search and prefix search differ."""
    trie = VizTrie(title_name="Trie")
    for word in ("apple", "app", "apply", "bat"):
        trie.insert(word)
    trie.delete("apply")
    return trie.search("app") and trie.starts_with("ba")


if __name__ == "__main__":
    print(f"Output : {demo()}")
