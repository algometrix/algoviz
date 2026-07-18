"""Jump Game II: fewest jumps to reach the last index (LeetCode 45)."""

from algoviz import VizList


def min_jumps(nums: list[int]) -> int:
    """Greedy sweep, widening the reachable window one jump at a time."""
    dp = VizList(nums, title_name="Jump Game")
    jumps = current_end = farthest = 0
    for index in range(len(dp) - 1):
        farthest = max(farthest, index + dp[index])
        if index != current_end:
            continue
        jumps += 1
        current_end = farthest
        dp.print(f"jump {jumps} reaches index {current_end}")
    return jumps


if __name__ == "__main__":
    print(f"Output : {min_jumps([2, 3, 1, 1, 4])}")
