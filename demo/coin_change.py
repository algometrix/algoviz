"""Coin Change II: count the ways to make an amount (LeetCode 518)."""

from algoviz import VizList


def change(amount: int, coins: list[int]) -> int:
    """One coin at a time, so each combination is counted exactly once."""
    dp = VizList([0] * (amount + 1), title_name="Coin Change")
    dp[0] = 1
    for coin in coins:
        for value in range(coin, amount + 1):
            dp.print(f"coin={coin} | dp[{value}] += dp[{value - coin}]")
            dp[value] += dp[value - coin]
    return dp[-1]


if __name__ == "__main__":
    print(f"Output : {change(5, [1, 2, 5])}")
