"""Daily Temperatures: a monotonic stack of indices (LeetCode 739).

The stack holds indices of days still waiting for something warmer. Its
invariant is that the temperatures those indices stand for *decrease* from
the bottom of the stack up -- but the stack stores indices, so a plain
column of values shows `2, 3, 4` and the invariant is invisible.

`bar_of` maps each stored index back to its temperature and draws it, so
every frame is a staircase narrowing toward the top. Watch what a warm day
does: each bar shorter than the incoming temperature pops off, one frame
each, until the staircase is restored and the new day is pushed on top.
That popping *is* how the invariant is maintained.

The answer array is drawn alongside, because the pop is where this
algorithm does its real work. A day leaves the stack exactly when its
answer becomes knowable, and the write that follows each pop is the whole
output being assembled one cell at a time. Watching only the stack shows
the bookkeeping and hides the result.
"""

from algoviz import VizList, VizStack

TEMPS = [73, 74, 75, 71, 69, 72, 76, 73]


def daily_temperatures(temps: list[int]) -> list[int]:
    """Hold indices still waiting for a warmer day, warmest at the bottom."""
    stack = VizStack(
        title_name="Waiting (indices)",
        bar_of=lambda index: temps[index],
        bar_label="temp",
        # Fixed from the start, so bars never re-scale mid-run and the
        # staircase in one frame is comparable with the next.
        bar_min=min(temps),
        bar_max=max(temps),
    )
    answer = VizList([0] * len(temps), title_name="Answer (days waited)")

    for index, temp in enumerate(temps):
        stack.print(f"\nday {index}, temp {temp}:")
        while stack and temps[stack.peek()] < temp:
            earlier = stack.pop()
            # The pop and this write are one event: the day leaves the
            # stack precisely because its answer is now known.
            answer[earlier] = index - earlier
        stack.push(index)

    return answer.data


if __name__ == "__main__":
    print(f"Output : {daily_temperatures(TEMPS)}")
