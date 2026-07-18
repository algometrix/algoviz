"""Kth Largest Element: a bounded min-heap (LeetCode 215)."""

from algoviz import VizHeap


def find_kth_largest(nums: list[int], k: int) -> int:
    """Keep only the k best seen so far; the root is then the kth largest."""
    heap = VizHeap(title_name=f"{k} largest so far")
    for num in nums:
        heap.push(num)
        if len(heap) > k:
            heap.pop()
    return heap.peek()


if __name__ == "__main__":
    print(f"Output : {find_kth_largest([3, 2, 1, 5, 6, 4], 2)}")
