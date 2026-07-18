"""Longest Common Subsequence: the canonical 2D table (LeetCode 1143)."""

from algoviz import VizList


def lcs(first: str, second: str) -> int:
    """Match extends the diagonal; a mismatch takes the better neighbour."""
    grid = [[0] * (len(second) + 1) for _ in range(len(first) + 1)]
    dp = VizList(
        grid,
        title_name="LCS",
        row_index=["-", *first],
        column_index=["-", *second],
    )
    for row in range(1, len(first) + 1):
        for col in range(1, len(second) + 1):
            if first[row - 1] == second[col - 1]:
                dp[row][col] = dp[row - 1][col - 1] + 1
            else:
                dp[row][col] = max(dp[row - 1][col], dp[row][col - 1])
    return dp[-1][-1]


if __name__ == "__main__":
    print(f"Output : {lcs('abcde', 'ace')}")
