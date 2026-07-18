"""House Robber: skip-or-take DP (LeetCode 198)."""

from algoviz import VizList


def rob(houses: list[int]) -> int:
    """At each house, take it plus the best two back, or skip to the last."""
    dp = VizList([0] * (len(houses) + 1), title_name="House Robber")
    dp[1] = houses[0]
    for index in range(2, len(houses) + 1):
        dp[index] = max(dp[index - 1], dp[index - 2] + houses[index - 1])
    return dp[-1]


if __name__ == "__main__":
    print(f"Output : {rob([2, 7, 9, 3, 1])}")
