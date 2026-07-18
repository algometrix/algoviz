"""Number of Provinces: union-find over a connectivity matrix (LeetCode 547)."""

from algoviz import VizUnionFind


def find_circle_num(is_connected: list[list[int]]) -> int:
    """Union every connected pair; the components left are the provinces."""
    size = len(is_connected)
    uf = VizUnionFind(size, title_name="Provinces")
    for row in range(size):
        for col in range(row + 1, size):
            if is_connected[row][col]:
                uf.union(row, col)
    return uf.component_count


if __name__ == "__main__":
    matrix = [[1, 1, 0], [1, 1, 0], [0, 0, 1]]
    print(f"Output : {find_circle_num(matrix)}")
