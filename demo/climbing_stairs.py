"""Climbing Stairs: the smallest interesting DP (LeetCode 70)."""

from algoviz import VizList


def climb_stairs(n: int) -> int:
    """Each step is reachable from the one below it and the one below that."""
    dp = VizList([0] * (n + 1), title_name="Climbing Stairs")
    dp[0] = dp[1] = 1
    for step in range(2, n + 1):
        dp[step] = dp[step - 1] + dp[step - 2]
    return dp[n]


if __name__ == "__main__":
    print(f"Output : {climb_stairs(6)}")
