"""Flood Fill: recolour a connected region (LeetCode 733).

The problem is literally about colour, so `cell_map` gives each shade one.

No cell is marked, not even the seed. Repainting a cell *is* this
algorithm's progress and `cell_map` already shows it, while a mark outranks
the `cell_map` colour (see `VizGrid`'s precedence) -- so either a
`mark_visited` or a `mark_start` would paint over the very recolouring the
demo exists to display. The seed is visible instead as the first cell to
change shade.
"""

from algoviz import VizGrid

SHADES = {
    0: ("·", "grey37"),
    1: ("■", "cyan"),
    2: ("■", "magenta"),
}


def flood_fill(rows: list[list[int]], sr: int, sc: int, color: int) -> list:
    """Depth-first from the seed, repainting every cell of the same shade."""
    grid = VizGrid(rows, title_name="Flood Fill", cell_map=SHADES, cell_width=3)
    original = grid[sr, sc]
    if original == color:
        return grid.data

    stack = [(sr, sc)]
    while stack:
        row, col = stack.pop()
        if grid[row, col] != original:
            continue
        grid[row, col] = color
        stack.extend(grid.neighbors(row, col))
    return grid.data


if __name__ == "__main__":
    image = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]
    print(f"Output : {flood_fill(image, 1, 1, 2)}")
