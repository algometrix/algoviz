"""Sliding Window Maximum: the monotonic deque (LeetCode 239)."""

from algoviz import VizDeque


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    """Keep indices in decreasing value order, so the front is the max."""
    window = VizDeque(title_name="Window (indices)")
    result = []
    for index, value in enumerate(nums):
        while window and nums[window.peek_right()] < value:
            window.pop()
        window.append(index)
        if window.peek_left() <= index - k:
            window.popleft()
        if index >= k - 1:
            result.append(nums[window.peek_left()])
    return result


if __name__ == "__main__":
    print(f"Output : {max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)}")
