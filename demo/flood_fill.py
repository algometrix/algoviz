"""Flood Fill: recolour a connected region (LeetCode 733)."""

from algoviz import VizGrid


def flood_fill(rows: list[list[int]], sr: int, sc: int, color: int) -> list:
    """Depth-first from the seed, repainting every cell of the same shade."""
    grid = VizGrid(rows, title_name="Flood Fill")
    original = grid[sr, sc]
    if original == color:
        return grid.data

    grid.mark_start(sr, sc)
    stack = [(sr, sc)]
    while stack:
        row, col = stack.pop()
        if grid[row, col] != original:
            continue
        grid[row, col] = color
        grid.mark_visited(row, col)
        stack.extend(grid.neighbors(row, col))
    return grid.data


if __name__ == "__main__":
    image = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]
    print(f"Output : {flood_fill(image, 1, 1, 2)}")
