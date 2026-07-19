"""Subarray Sum Equals K: prefix sums in a map (LeetCode 560).

Not a two-pointer problem, and that is the point: negative numbers break
the sliding window, so this counts how many earlier prefix sums are
exactly `k` behind the current one.
"""

from algoviz import VizDict, VizList


def subarray_sum(nums: list[int], k: int) -> int:
    """Every earlier prefix that is `k` behind marks one valid subarray."""
    values = VizList(nums, title_name="Values")
    # One empty prefix, so a subarray starting at index 0 is counted.
    seen = VizDict({0: 1}, title_name="prefix sum -> count")

    running = 0
    count = 0
    for index in range(len(values)):
        values.set_pointer("i", index)
        running += values[index]
        count += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1

    values.clear_pointers()
    return count


if __name__ == "__main__":
    print(f"Output : {subarray_sum([1, 1, 1], 2)}")
