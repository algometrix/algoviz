"""Reverse Linked List: pointer surgery, one node at a time (LeetCode 206)."""

from algoviz import VizLinkedList


def reverse_list(values: list[int]) -> list[int]:
    """Walk forward, flipping each node's next pointer behind you."""
    linked = VizLinkedList(values, title_name="Reverse")
    previous = None
    current = linked.head
    while current is not None:
        linked.set_pointer("current", current)
        following = current.next
        current.next = previous
        previous = current
        current = following
    linked.head = previous
    return linked.to_list()


if __name__ == "__main__":
    print(f"Output : {reverse_list([1, 2, 3, 4, 5])}")
