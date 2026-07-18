"""Min Stack: constant-time minimum via a paired stack (LeetCode 155)."""

from algoviz import VizStack


class MinStack:
    """Keeps a second stack whose top is always the running minimum."""

    def __init__(self) -> None:
        """Create the value stack and its parallel minimum stack."""
        self._values = VizStack(title_name="Values")
        self._mins = VizStack(title_name="Minimums")

    def push(self, value: int) -> None:
        """Push a value, mirroring the new minimum onto the min stack."""
        self._values.push(value)
        smallest = value if not self._mins else min(value, self._mins.peek())
        self._mins.push(smallest)

    def pop(self) -> None:
        """Drop the top value and the minimum that went with it."""
        self._values.pop()
        self._mins.pop()

    def top(self) -> int:
        """The value most recently pushed."""
        return self._values.peek()

    def get_min(self) -> int:
        """The smallest value currently on the stack."""
        return self._mins.peek()


if __name__ == "__main__":
    stack = MinStack()
    for number in (-2, 0, -3):
        stack.push(number)
    lowest = stack.get_min()
    stack.pop()
    print(f"Output : {lowest}")
