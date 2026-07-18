"""Two Sum: the hash-map one-pass (LeetCode 1)."""

from algoviz import VizDict


def two_sum(nums: list[int], target: int) -> list[int]:
    """Remember every value seen, then look up the partner each one needs."""
    seen = VizDict(title_name="value -> index")
    for index, num in enumerate(nums):
        need = target - num
        if need in seen:
            return [seen[need], index]
        seen[num] = index
    return []


if __name__ == "__main__":
    print(f"Output : {two_sum([2, 7, 11, 15], 9)}")
