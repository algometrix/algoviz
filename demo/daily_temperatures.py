"""Daily Temperatures: a monotonic stack of indices (LeetCode 739)."""

from algoviz import VizStack


def daily_temperatures(temps: list[int]) -> list[int]:
    """Hold indices still waiting for a warmer day, warmest at the bottom."""
    answer = [0] * len(temps)
    stack = VizStack(title_name="Waiting (indices)")
    for index, temp in enumerate(temps):
        while stack and temps[stack.peek()] < temp:
            earlier = stack.pop()
            answer[earlier] = index - earlier
        stack.push(index)
    return answer


if __name__ == "__main__":
    print(f"Output : {daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])}")
