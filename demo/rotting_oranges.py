"""Rotting Oranges: BFS measured in levels (LeetCode 994)."""

from algoviz import VizGrid, VizQueue


def oranges_rotting(rows: list[list[str]]) -> int:
    """Every BFS level is one minute, so the last level is the answer."""
    grid = VizGrid(rows, title_name="Oranges")
    queue = VizQueue(title_name="Rotting front")
    fresh = 0
    for row in range(grid.rows):
        for col in range(grid.cols):
            if grid[row, col] == "2":
                queue.enqueue((row, col))
                grid.mark_start(row, col)
            elif grid[row, col] == "1":
                fresh += 1

    minutes = 0
    while queue and fresh:
        queue.mark_level()
        minutes += 1
        for _ in range(len(queue)):
            row, col = queue.dequeue()
            for nr, nc in grid.neighbors(row, col):
                if grid[nr, nc] != "1":
                    continue
                grid[nr, nc] = "2"
                grid.mark_visited(nr, nc)
                fresh -= 1
                queue.enqueue((nr, nc))
    return -1 if fresh else minutes


if __name__ == "__main__":
    board = [
        ["2", "1", "1"],
        ["1", "1", "0"],
        ["0", "1", "1"],
    ]
    print(f"Output : {oranges_rotting(board)}")
