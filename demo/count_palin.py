"""Palindromic Substrings: expand a 2D table (LeetCode 647)."""

from algoviz import VizList


def count_substrings(text: str) -> int:
    """A span is a palindrome when its ends match and its inside is one."""
    size = len(text)
    grid = [[0] * size for _ in range(size)]
    dp = VizList(
        grid,
        title_name="DP Table",
        row_index=list(text),
        column_index=list(text),
    )
    total = 0
    for start in range(size - 1, -1, -1):
        for end in range(start, size):
            same_ends = text[start] == text[end]
            short_enough = (end - start + 1) < 3
            dp[start][end] = same_ends and (
                short_enough or bool(dp[start + 1][end - 1])
            )
            total += dp[start][end]
    return total


if __name__ == "__main__":
    print(f"Output : {count_substrings('aab')}")
