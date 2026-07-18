"""Binary Tree Level Order Traversal: BFS by level (LeetCode 102)."""

from algoviz import VizTree


def level_order(values: list[int | None]) -> list[list[int]]:
    """Build from the level-order form problems are stated in, then walk it."""
    tree = VizTree.from_level_order(values, title_name="Level Order")
    for value in tree.inorder():
        tree.visit(tree.search(value))
    return tree.level_order()


if __name__ == "__main__":
    print(f"Output : {level_order([3, 9, 20, None, None, 15, 7])}")
