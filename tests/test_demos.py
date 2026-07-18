"""Runs every demo end to end.

Demos are the first thing a new user copies, so a broken one is worse than a
broken internal. Each is executed as a real subprocess and checked against
the answer the LeetCode problem actually has.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DEMO_DIR = REPO_ROOT / "demo"

# Demo file -> the line it must print. The expected values are the correct
# answers to the underlying problems, verified by hand.
EXPECTED = {
    # Arrays and dynamic programming
    "climbing_stairs.py": "Output : 13",
    "coin_change.py": "Output : 4",
    "count_palin.py": "Output : 4",
    "house_robber.py": "Output : 12",
    "jump.py": "Output : 2",
    "longest_common_subsequence.py": "Output : 3",
    # Stacks
    "daily_temperatures.py": "Output : [1, 1, 4, 2, 1, 1, 0, 0]",
    "min_stack.py": "Output : -3",
    "valid_parentheses.py": "Output : True",
    # Queues and deques
    "rotting_oranges.py": "Output : 4",
    "sliding_window_max.py": "Output : [3, 3, 5, 5, 6, 7]",
    # Heaps
    "kth_largest.py": "Output : 5",
    "top_k_frequent.py": "Output : [1, 2]",
    # Maps and sets
    "group_anagrams.py": "Output : [['eat', 'tea', 'ate'], ['tan', 'nat']]",
    "longest_consecutive.py": "Output : 4",
    "two_sum.py": "Output : [0, 1]",
    # Grids
    "flood_fill.py": "Output : [[2, 2, 2], [2, 2, 0], [2, 0, 1]]",
    "num_islands.py": "Output : 3",
    # Linked lists
    "linked_list_cycle.py": "Output : True",
    "reverse_linked_list.py": "Output : [5, 4, 3, 2, 1]",
    # Trees and tries
    "binary_tree_level_order.py": "Output : [[3], [9, 20], [15, 7]]",
    "implement_trie.py": "Output : [True, False, True]",
    "validate_bst.py": "Output : False",
    "word_break.py": "Output : True",
    # Union-find
    "number_of_provinces.py": "Output : 2",
    "redundant_connection.py": "Output : [2, 3]",
}


def run_demo(name: str) -> str:
    """Execute a demo in a subprocess and return its stdout."""
    result = subprocess.run(
        [sys.executable, str(DEMO_DIR / name)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
        check=False,
        # Overlay onto the real environment rather than replacing it.
        # A bare dict drops SYSTEMROOT, and without it Windows Python
        # cannot reach the OS random source and dies during startup with
        # "failed to get random numbers to initialize Python".
        env={**os.environ, "TERM": "dumb", "NO_COLOR": "1"},
    )
    assert result.returncode == 0, f"{name} failed:\n{result.stderr}"
    return result.stdout


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_demo_produces_the_right_answer(name):
    assert EXPECTED[name] in run_demo(name)


def test_every_demo_is_covered():
    """A new demo must be added here, or it never gets run."""
    on_disk = {path.name for path in DEMO_DIR.glob("*.py")}
    assert on_disk == set(EXPECTED), (
        f"untested demos: {sorted(on_disk - set(EXPECTED))}"
    )


# Tables draw with box borders, trees with branch glyphs. A demo that
# rendered nothing at all has none of these.
DRAWING_GLYPHS = ("│", "└", "├", "━", "─")


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_demo_actually_renders(name):
    """A demo that prints only its answer is not demonstrating anything."""
    output = run_demo(name)
    assert any(glyph in output for glyph in DRAWING_GLYPHS), (
        f"{name} drew nothing"
    )
