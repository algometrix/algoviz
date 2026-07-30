"""Number of Islands: BFS over a grid overlay (LeetCode 200).

The terrain never changes here, so the two channels stay separate and both
stay readable: `cell_map` gives each value a permanent glyph and colour, and
the overlay marks record where BFS has been. A marked cell keeps its glyph,
so it still reads as land while showing that it has been counted.

The problem counts islands, so the frames have to distinguish them. One
visited colour cannot: finish two islands and you get one undifferentiated
cyan blob, which is the opposite of what is being counted. Each cell is
therefore marked *both* path and visited, and `PATH` outranks `VISITED`
(see `VizGrid`'s precedence), so the island being explored right now stands
out in magenta. Clearing just the path mark when the fill drains demotes
that whole island to cyan in one step -- it settles into the count, and the
next island lights up alone.
"""

from collections import deque

from algoviz import Mark, VizGrid

TERRAIN = {
    "0": ("·", "grey37"),  # water
    "1": ("■", "green"),  # land
}


def num_islands(rows: list[str]) -> int:
    """Flood-fill each unvisited land cell, counting one island per fill."""
    grid = VizGrid(rows, title_name="Islands", cell_map=TERRAIN, cell_width=3)
    seen: set[tuple[int, int]] = set()
    islands = 0
    for row in range(grid.rows):
        for col in range(grid.cols):
            if grid[row, col] != "1" or (row, col) in seen:
                continue
            islands += 1
            grid.print(f"\nisland {islands}:")
            seen.add((row, col))
            queue = deque([(row, col)])
            while queue:
                current = queue.popleft()
                grid.mark_visited(*current)
                grid.mark_path(*current)
                for neighbor in grid.neighbors(*current):
                    if grid[neighbor] == "1" and neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)
            # Island complete. Dropping the path mark settles it to
            # visited, leaving the next island the only magenta thing.
            grid.clear_marks(Mark.PATH)
    return islands


if __name__ == "__main__":
    print(f"Output : {num_islands(['11000', '11000', '00100', '00011'])}")
