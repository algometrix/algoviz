"""Redundant Connection: the edge that closes a cycle (LeetCode 684)."""

from algoviz import VizUnionFind


def find_redundant_connection(edges: list[list[int]]) -> list[int]:
    """The first edge joining two already-connected nodes is the extra one."""
    uf = VizUnionFind(range(1, len(edges) + 1), title_name="Redundant Edge")
    for first, second in edges:
        if not uf.union(first, second):
            return [first, second]
    return []


if __name__ == "__main__":
    print(f"Output : {find_redundant_connection([[1, 2], [1, 3], [2, 3]])}")
