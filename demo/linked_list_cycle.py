"""Linked List Cycle: Floyd's tortoise and hare (LeetCode 141)."""

from algoviz import VizLinkedList


def has_cycle(values: list[int], tail_index: int | None) -> bool:
    """A faster pointer laps a slower one exactly when a loop exists."""
    linked = VizLinkedList(values, title_name="Cycle Check")
    if tail_index is not None:
        nodes = linked.nodes()
        nodes[-1].next = nodes[tail_index]

    slow = fast = linked.head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        linked.set_pointer("slow", slow)
        linked.set_pointer("fast", fast)
        if slow is fast:
            return True
    return False


if __name__ == "__main__":
    print(f"Output : {has_cycle([3, 2, 0, -4], 1)}")
