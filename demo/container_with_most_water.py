"""Container With Most Water: the cleanest two-pointer (LeetCode 11).

Start as wide as possible and move whichever side is shorter. Moving the
taller one can only ever lose area, which is why the greedy step is safe.
"""

from algoviz import VizList


def max_area(heights: list[int]) -> int:
    """Close in from both ends, always abandoning the shorter wall."""
    walls = VizList(heights, title_name="Heights")
    left, right = 0, len(walls) - 1
    best = 0

    while left < right:
        walls.set_pointer("left", left)
        walls.set_pointer("right", right)

        best = max(best, min(walls[left], walls[right]) * (right - left))
        if walls[left] < walls[right]:
            left += 1
        else:
            right -= 1

    walls.clear_pointers()
    return best


if __name__ == "__main__":
    print(f"Output : {max_area([1, 8, 6, 2, 5, 4, 8, 3, 7])}")
