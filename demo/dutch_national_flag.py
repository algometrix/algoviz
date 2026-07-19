"""Sort Colors: the Dutch national flag partition (LeetCode 75).

One pass, three pointers, no counting. The invariant is the whole lesson:
everything left of `low` is 0, everything right of `high` is 2, and the
span between `mid` and `high` is the part still unexamined.
"""

from algoviz import VizList


def sort_colors(nums: list[int]) -> list[int]:
    """Sweep `mid` forward, swapping each value to the end it belongs at."""
    colors = VizList(nums, title_name="Sort Colors")
    low, mid, high = 0, 0, len(colors) - 1

    while mid <= high:
        colors.set_pointer("low", low)
        colors.set_pointer("mid", mid)
        colors.set_pointer("high", high)

        if colors[mid] == 0:
            colors[low], colors[mid] = colors[mid], colors[low]
            low += 1
            mid += 1
        elif colors[mid] == 2:
            # Do not advance mid: the value swapped in is still unseen.
            colors[mid], colors[high] = colors[high], colors[mid]
            high -= 1
        else:
            mid += 1

    colors.clear_pointers()
    return colors.data


if __name__ == "__main__":
    print(f"Output : {sort_colors([2, 0, 2, 1, 1, 0])}")
