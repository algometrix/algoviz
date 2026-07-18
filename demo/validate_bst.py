"""Validate Binary Search Tree: bounds, not just parents (LeetCode 98)."""

from algoviz import VizTree


def is_valid_bst(values: list[int | None]) -> bool:
    """Each node must fall inside the range its ancestors allow."""
    tree = VizTree.from_level_order(values, title_name="Validate BST")

    def check(node, low: float, high: float) -> bool:
        if node is None:
            return True
        tree.visit(node)
        if not low < node.val < high:
            return False
        return check(node.left, low, node.val) and check(
            node.right, node.val, high
        )

    return check(tree.root_node, float("-inf"), float("inf"))


if __name__ == "__main__":
    print(f"Output : {is_valid_bst([5, 1, 4, None, None, 3, 6])}")
