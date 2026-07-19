"""3Sum: sort, then two-pointer the remainder (LeetCode 15).

Fixing one number turns the problem into 2Sum on a sorted array, which a
pair of converging pointers solves without a hash map.
"""

from algoviz import VizList


def three_sum(nums: list[int]) -> list[list[int]]:
    """For each anchor, converge `left` and `right` on the missing pair."""
    values = VizList(sorted(nums), title_name="3Sum (sorted)")
    triples: list[list[int]] = []

    for anchor in range(len(values) - 2):
        if anchor > 0 and values[anchor] == values[anchor - 1]:
            continue  # skip a repeated anchor, or triples duplicate

        left, right = anchor + 1, len(values) - 1
        while left < right:
            values.set_pointer("anchor", anchor)
            values.set_pointer("left", left)
            values.set_pointer("right", right)

            total = values[anchor] + values[left] + values[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                triples.append([values[anchor], values[left], values[right]])
                left += 1
                while left < right and values[left] == values[left - 1]:
                    left += 1

    values.clear_pointers()
    return triples


if __name__ == "__main__":
    print(f"Output : {three_sum([-1, 0, 1, 2, -1, -4])}")
