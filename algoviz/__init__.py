"""AlgoViz: data structures that draw themselves as your algorithm runs.

Wrap a structure, run your algorithm unchanged, and watch each step render in
the terminal with the cells you touched highlighted.

    from algoviz import VizList

    dp = VizList([0] * 5, title_name="DP")
    dp[2] = 7  # prints a table with cell 2 highlighted

Every structure accepts the same presentation settings, either as keyword
overrides or as a shared `VizConfig`:

    from algoviz import VizConfig, VizStack

    quiet = VizConfig(auto_print=False, show_init=False)
    stack = VizStack([1, 2, 3], config=quiet)
    stack.show()  # draw only when you ask
"""

from algoviz.core import VizConfig
from algoviz.vizdict import VizCounter, VizDict, VizSet
from algoviz.vizgrid import Mark, VizGrid
from algoviz.vizheap import VizHeap
from algoviz.vizlinkedlist import ListNode, VizLinkedList
from algoviz.vizlist import VizList
from algoviz.vizqueue import VizDeque, VizQueue
from algoviz.vizstack import VizStack
from algoviz.viztree import TreeNode, VizTree
from algoviz.viztrie import TrieNode, VizTrie
from algoviz.vizunionfind import VizUnionFind

__version__ = "0.4.0"

__all__ = [
    "ListNode",
    "Mark",
    "TreeNode",
    "TrieNode",
    "VizConfig",
    "VizCounter",
    "VizDeque",
    "VizDict",
    "VizGrid",
    "VizHeap",
    "VizLinkedList",
    "VizList",
    "VizQueue",
    "VizSet",
    "VizStack",
    "VizTree",
    "VizTrie",
    "VizUnionFind",
    "__version__",
]
