"""Binary Tree Level Order Traversal: drive the BFS yourself (LeetCode 102).

The queue is the whole problem, so this builds and drains it by hand rather
than calling `VizTree.level_order()`. The library only holds the tree and
lights up whichever node the traversal is standing on.
"""

from collections import deque

from algoviz import VizTree


def level_order(values: list[int | None]) -> list[list[int]]:
    """Drain one full level per outer pass, so each pass is one row."""
    tree = VizTree.from_level_order(values, title_name="Level Order")
    if tree.root_node is None:
        return []

    result: list[list[int]] = []
    queue = deque([tree.root_node])
    while queue:
        # Snapshot the width first: the loop below appends the next level.
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            tree.visit(node)
            level.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        result.append(level)
    return result


if __name__ == "__main__":
    print(f"Output : {level_order([3, 9, 20, None, None, 15, 7])}")
