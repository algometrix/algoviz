"""Number of Islands: BFS over a grid overlay (LeetCode 200)."""

from collections import deque

from algoviz import VizGrid


def num_islands(rows: list[str]) -> int:
    """Flood-fill each unvisited land cell, counting one island per fill."""
    grid = VizGrid(rows, title_name="Islands")
    seen: set[tuple[int, int]] = set()
    islands = 0
    for row in range(grid.rows):
        for col in range(grid.cols):
            if grid[row, col] != "1" or (row, col) in seen:
                continue
            islands += 1
            seen.add((row, col))
            queue = deque([(row, col)])
            while queue:
                current = queue.popleft()
                grid.mark_visited(*current)
                for neighbor in grid.neighbors(*current):
                    if grid[neighbor] == "1" and neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)
    return islands


if __name__ == "__main__":
    print(f"Output : {num_islands(['11000', '11000', '00100', '00011'])}")
