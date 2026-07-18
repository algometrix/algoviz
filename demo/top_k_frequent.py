"""Top K Frequent Elements: counter plus heap (LeetCode 347)."""

from algoviz import VizCounter, VizHeap


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """Count every value, then let a max-heap surface the k largest."""
    counts = VizCounter(title_name="Frequencies")
    for num in nums:
        counts[num] += 1
    heap = VizHeap(counts.values(), title_name="Counts", max_heap=True)
    threshold = heap.nlargest(k)[-1]
    return [value for value, count in counts.items() if count >= threshold]


if __name__ == "__main__":
    print(f"Output : {top_k_frequent([1, 1, 1, 2, 2, 3], 2)}")
