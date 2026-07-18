"""Word Break: a trie plus a DP sweep (LeetCode 139)."""

from algoviz import VizList, VizTrie


def word_break(text: str, words: list[str]) -> bool:
    """A position is reachable when some word bridges it from an earlier one."""
    trie = VizTrie(words, title_name="Dictionary")
    dp = VizList([False] * (len(text) + 1), title_name="Reachable")
    dp[0] = True
    for end in range(1, len(text) + 1):
        for start in range(end):
            if dp[start] and trie.search(text[start:end]):
                dp[end] = True
                break
    return dp[-1]


if __name__ == "__main__":
    print(f"Output : {word_break('leetcode', ['leet', 'code'])}")
