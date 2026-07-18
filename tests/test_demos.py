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


def run_demo(name: str, encoding: str = "utf-8") -> subprocess.CompletedProcess:
    """Execute a demo in a subprocess and return the completed process.

    Pins the child's output encoding and decodes with the same one, so the
    result does not depend on the machine's locale. Without that, a child
    writing a legacy codepage and a parent decoding UTF-8 disagree and the
    read fails on output that is perfectly valid.
    """
    return subprocess.run(
        [sys.executable, str(DEMO_DIR / name)],
        capture_output=True,
        cwd=REPO_ROOT,
        timeout=60,
        check=False,
        encoding=encoding,
        errors="replace",
        # Overlay onto the real environment rather than replacing it.
        # A bare dict drops SYSTEMROOT, and without it Windows Python
        # cannot reach the OS random source and dies during startup with
        # "failed to get random numbers to initialize Python".
        env={
            **os.environ,
            "TERM": "dumb",
            "NO_COLOR": "1",
            "PYTHONIOENCODING": encoding,
        },
    )


def demo_output(name: str) -> str:
    """Run a demo, require it to succeed, and return its stdout."""
    result = run_demo(name)
    assert result.returncode == 0, f"{name} failed:\n{result.stderr}"
    return result.stdout


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_demo_produces_the_right_answer(name):
    assert EXPECTED[name] in demo_output(name)


def test_every_demo_is_covered():
    """A new demo must be added here, or it never gets run."""
    on_disk = {path.name for path in DEMO_DIR.glob("*.py")}
    assert on_disk == set(EXPECTED), (
        f"untested demos: {sorted(on_disk - set(EXPECTED))}"
    )


# Tables draw with box borders, trees with branch glyphs. A demo that
# rendered nothing at all has none of these.
#
# Both alphabets are listed because rich degrades to ASCII borders on a
# terminal whose encoding cannot carry the box-drawing set, which is the
# default on Windows when stdout is a pipe. Checking only the Unicode
# forms would fail there against output that is perfectly correct.
DRAWING_GLYPHS = (
    "│",  # unicode table border
    "└",  # unicode tree branch
    "├",
    "━",
    "─",
    "|",  # ascii table border
    "+--",  # ascii tree branch
    "`--",
)


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_demo_actually_renders(name):
    """A demo that prints only its answer is not demonstrating anything."""
    output = demo_output(name)
    assert any(glyph in output for glyph in DRAWING_GLYPHS), (
        f"{name} drew nothing"
    )


@pytest.mark.parametrize(
    "name",
    ["valid_parentheses.py", "linked_list_cycle.py", "implement_trie.py"],
)
def test_demo_survives_a_legacy_codepage(name):
    """The markers must degrade, not crash, on a non-UTF-8 terminal.

    Windows defaults to cp1252 when stdout is a pipe. Writing a character
    it cannot encode aborts the interpreter, so a demo that renders fine
    interactively would die the moment its output was redirected. These
    three cover the stack, linked-list, and trie markers.
    """
    result = run_demo(name, encoding="cp1252")
    assert result.returncode == 0, (
        f"{name} crashed on a cp1252 terminal:\n{result.stderr}"
    )
    assert "Output :" in result.stdout
