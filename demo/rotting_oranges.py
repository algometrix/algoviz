"""Rotting Oranges: BFS measured in levels (LeetCode 994).

Every BFS level is one minute, so the last level is the answer.

The grid's values are `'0'`, `'1'`, and `'2'` -- empty, fresh, rotten --
which say nothing on their own. `cell_map` turns them into an empty slot, a
green orange, and a red one, so a frame shows rot spreading outward instead
of digits flipping.

That alone is not enough to teach the problem. The answer counts *minutes*,
and a grid coloured only by value draws minute 1 and minute 3 identically:
every rotten orange is the same red, so the quantity being counted is
nowhere on screen. So the oranges that rot *this* minute are marked queued
-- state the values genuinely do not carry, since a cell that just rotted
and one that rotted earlier are both `'2'` -- and the mark is cleared at the
top of the next minute. The yellow band is the BFS frontier, and watching it
sweep across the grid is watching the answer being counted.

`batch()` collapses the per-cell redraws into one frame per level, so
frames and minutes correspond exactly. Nothing marks cells *visited*: the
algorithm already records that by writing `'2'`, and a visited mark would
outrank the `cell_map` colour and repaint the rot it was showing.

So a frame carries four states at once. Yellow rotted this minute, red
rotted earlier, green is still fresh, and the cells left in the read
highlight are the ones this minute examined as neighbours and rejected --
the repeated work that makes BFS visit every cell but process each once.
"""

from algoviz import Mark, VizGrid, VizQueue

ORANGES = {
    "0": ("·", "grey37"),  # empty
    "1": ("●", "green"),  # fresh
    "2": ("●", "red"),  # rotten
}


def oranges_rotting(rows: list[list[str]]) -> int:
    """Every BFS level is one minute, so the last level is the answer."""
    grid = VizGrid(rows, title_name="Oranges", cell_map=ORANGES, cell_width=3)
    # Quiet, and shown once per minute below: a frame per enqueue would
    # bury the grid frame that the minute is actually about.
    queue = VizQueue(title_name="Rotting front", auto_print=False)
    fresh = 0
    for row in range(grid.rows):
        for col in range(grid.cols):
            if grid[row, col] == "2":
                queue.enqueue((row, col))
            elif grid[row, col] == "1":
                fresh += 1

    minutes = 0
    while queue and fresh:
        queue.mark_level()
        minutes += 1
        grid.print(f"\nminute {minutes}:")
        with grid.batch():
            # Last minute's frontier is this minute's history.
            grid.clear_marks(Mark.QUEUED)
            for _ in range(len(queue)):
                row, col = queue.dequeue()
                for nr, nc in grid.neighbors(row, col):
                    if grid[nr, nc] != "1":
                        continue
                    grid[nr, nc] = "2"
                    grid.mark_queued(nr, nc)
                    fresh -= 1
                    queue.enqueue((nr, nc))
        # The queue now holds exactly the cells drawn yellow above --
        # seeing the two together is what makes "the queue is the
        # frontier" concrete rather than a phrase to memorise.
        queue.show()
    return -1 if fresh else minutes


if __name__ == "__main__":
    board = [
        ["2", "1", "1"],
        ["1", "1", "0"],
        ["0", "1", "1"],
    ]
    print(f"Output : {oranges_rotting(board)}")
