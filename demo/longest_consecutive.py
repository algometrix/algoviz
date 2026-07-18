"""Longest Consecutive Sequence: a set, not a sort (LeetCode 128)."""

from algoviz import VizSet


def longest_consecutive(nums: list[int]) -> int:
    """Only count up from a number whose predecessor is absent."""
    pool = VizSet(nums, title_name="Pool")
    best = 0
    for num in pool.data:
        if num - 1 in pool:
            continue
        length = 1
        while num + length in pool:
            length += 1
        best = max(best, length)
    return best


if __name__ == "__main__":
    print(f"Output : {longest_consecutive([100, 4, 200, 1, 3, 2])}")
