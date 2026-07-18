"""Top K Frequent Elements: a bounded heap of size k (LeetCode 347).

Counting is the easy half. The selection is the problem, so this keeps a
min-heap capped at k entries and evicts the weakest whenever it overflows,
rather than handing the whole job to `nlargest`.
"""

from algoviz import VizCounter, VizHeap


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """Keep only the k best pairs seen; whatever survives is the answer."""
    counts = VizCounter(title_name="Frequencies")
    for num in nums:
        counts[num] += 1

    # Pairs are (count, value), so the heap orders by frequency and the
    # root is always the weakest candidate still in the running.
    heap = VizHeap(title_name=f"{k} most frequent so far")
    for value, count in counts.items():
        heap.push((count, value))
        if len(heap) > k:
            heap.pop()

    return [value for _, value in sorted(heap, reverse=True)]


if __name__ == "__main__":
    print(f"Output : {top_k_frequent([1, 1, 1, 2, 2, 3], 2)}")
