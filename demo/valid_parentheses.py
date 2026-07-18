"""Valid Parentheses: the classic stack warm-up (LeetCode 20)."""

from algoviz import VizStack

PAIRS = {")": "(", "]": "[", "}": "{"}


def is_valid(text: str) -> bool:
    """Push every opener, and require the right opener on every closer."""
    stack = VizStack(title_name="Parens")
    for char in text:
        if char not in PAIRS:
            stack.push(char)
            continue
        if stack.is_empty() or stack.pop() != PAIRS[char]:
            return False
    return stack.is_empty()


if __name__ == "__main__":
    print(f"Output : {is_valid('([]{})')}")
