"""A binary tree that draws itself with `rich.tree.Tree`.

`TreeNode` mirrors LeetCode's own node (`.val`, `.left`, `.right`), and
`VizTree.from_level_order` accepts the level-order-with-`None`-gaps list
LeetCode problems are stated in, e.g. `[3, 9, 20, None, None, 15, 7]`.
That constructor is the reason this module exists: it is how tree
problems actually arrive.

Highlighting a node mid-algorithm is deliberately decoupled from the
built-in traversals. `inorder`/`preorder`/`postorder`/`level_order` are
plain, side-effect-free reads used to check an answer. `visit(node)` is
the animation hook: call it from your own recursion and each call
highlights that node in `get_color` and redraws, one frame per call.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator
from typing import Any

from rich.console import RenderableType
from rich.tree import Tree

from algoviz.core import VizBase, VizConfig, paint

__all__ = ["TreeNode", "VizTree"]

_EMPTY_LABEL = "None"


class TreeNode:
    """A binary tree node, LeetCode-shape compatible.

    Deliberately plain: `.val`, `.left`, `.right`, so code written
    against LeetCode's own `TreeNode` works against this one unchanged.
    """

    def __init__(
        self,
        val: Any = 0,
        left: TreeNode | None = None,
        right: TreeNode | None = None,
    ) -> None:
        """Create a node holding `val`, with optional `left`/`right`."""
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        """Show the node's value; children are omitted to stay finite."""
        return f"TreeNode({self.val!r})"


class VizTree(VizBase):
    """A binary tree rendered as a `rich.tree.Tree`.

    Structural writes (`insert`) highlight in `set_color`. `search`
    highlights the path walked in `get_color` but, like a plain read
    elsewhere in algoviz, does not redraw on its own -- call `show()`
    or `visit()` to see it. `visit(node)` is the explicit animation
    hook for a caller's own traversal.
    """

    def __init__(
        self,
        source: TreeNode | Iterable[Any] | None = None,
        title_name: str = "Tree",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> None:
        """Wrap `source`: a root node, a level-order list, or `None`."""
        super().__init__(
            title=title_name, config=config, parent=parent, **overrides
        )
        self._root = self._coerce(source)

        if self.config.show_init:
            self.show(f"{self.title} Init")

    @staticmethod
    def _coerce(source: TreeNode | Iterable[Any] | None) -> TreeNode | None:
        """Turn `source` into a root node, building one if needed."""
        if source is None or isinstance(source, TreeNode):
            return source
        return VizTree._build_level_order(list(source))

    @staticmethod
    def _build_level_order(values: list[Any]) -> TreeNode | None:
        """Build a tree from a LeetCode-style level-order list.

        Each `None` in `values` marks a missing child and, per the
        LeetCode convention, contributes no entries of its own -- only
        real nodes get a left/right slot consumed for them.
        """
        remaining = iter(values)
        root_val = next(remaining, None)
        if root_val is None:
            return None

        root = TreeNode(root_val)
        queue: deque[TreeNode] = deque([root])
        while queue:
            node = queue.popleft()
            left_val = next(remaining, None)
            if left_val is not None:
                node.left = TreeNode(left_val)
                queue.append(node.left)
            right_val = next(remaining, None)
            if right_val is not None:
                node.right = TreeNode(right_val)
                queue.append(node.right)
        return root

    @classmethod
    def from_level_order(
        cls,
        values: Iterable[Any],
        title_name: str = "Tree",
        config: VizConfig | None = None,
        parent: VizBase | None = None,
        **overrides: Any,
    ) -> VizTree:
        """Build a tree from a level-order list with `None` gaps."""
        return cls(
            list(values),
            title_name=title_name,
            config=config,
            parent=parent,
            **overrides,
        )

    def to_level_order(self) -> list[Any | None]:
        """This tree as a level-order list with `None` gaps.

        Trailing `None`s are trimmed, matching the convention problems
        state their expected output in.
        """
        if self._root is None:
            return []
        result: list[Any | None] = []
        queue: deque[TreeNode | None] = deque([self._root])
        while queue:
            node = queue.popleft()
            if node is None:
                result.append(None)
                continue
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        while result and result[-1] is None:
            result.pop()
        return result

    # -- BST operations ------------------------------------------------

    def insert(self, val: Any) -> None:
        """Insert `val` using BST ordering, then redraw.

        Duplicate values are left in place; nothing is inserted twice.
        """
        if self._root is None:
            self._root = TreeNode(val)
            self.highlights.mark_set(id(self._root))
            self._auto_show()
            return

        node = self._root
        while True:
            self.highlights.mark_get(id(node))
            if val < node.val:
                if node.left is None:
                    node.left = TreeNode(val)
                    self.highlights.mark_set(id(node.left))
                    break
                node = node.left
            elif val > node.val:
                if node.right is None:
                    node.right = TreeNode(val)
                    self.highlights.mark_set(id(node.right))
                    break
                node = node.right
            else:
                break
        self._auto_show()

    def search(self, val: Any) -> TreeNode | None:
        """Find `val` using BST ordering, highlighting the path walked."""
        node = self._root
        while node is not None:
            self.highlights.mark_get(id(node))
            if val == node.val:
                return node
            node = node.left if val < node.val else node.right
        return None

    def visit(self, node: TreeNode | None) -> None:
        """Mark `node` as the one currently being visited, then redraw.

        Call this at the top of your own recursive traversal to drive
        the animation one step at a time; a `None` node is a no-op so
        it is safe to call unconditionally at the base case.
        """
        if node is None:
            return
        self.highlights.mark_get(id(node))
        self._auto_show()

    # -- shape -----------------------------------------------------------

    def height(self) -> int:
        """Number of nodes on the longest root-to-leaf path.

        `0` for an empty tree, `1` for a single node.
        """
        return self._height(self._root)

    @staticmethod
    def _height(node: TreeNode | None) -> int:
        if node is None:
            return 0
        return 1 + max(VizTree._height(node.left), VizTree._height(node.right))

    def __len__(self) -> int:
        """Number of nodes in the tree."""
        return len(self.preorder())

    def __iter__(self) -> Iterator[Any]:
        """Iterate values in-order (left, root, right)."""
        return iter(self.inorder())

    # -- traversals ------------------------------------------------------

    def inorder(self) -> list[Any]:
        """Values in left-root-right order."""
        values: list[Any] = []
        self._inorder(self._root, values)
        return values

    @staticmethod
    def _inorder(node: TreeNode | None, out: list[Any]) -> None:
        if node is None:
            return
        VizTree._inorder(node.left, out)
        out.append(node.val)
        VizTree._inorder(node.right, out)

    def preorder(self) -> list[Any]:
        """Values in root-left-right order."""
        values: list[Any] = []
        self._preorder(self._root, values)
        return values

    @staticmethod
    def _preorder(node: TreeNode | None, out: list[Any]) -> None:
        if node is None:
            return
        out.append(node.val)
        VizTree._preorder(node.left, out)
        VizTree._preorder(node.right, out)

    def postorder(self) -> list[Any]:
        """Values in left-right-root order."""
        values: list[Any] = []
        self._postorder(self._root, values)
        return values

    @staticmethod
    def _postorder(node: TreeNode | None, out: list[Any]) -> None:
        if node is None:
            return
        VizTree._postorder(node.left, out)
        VizTree._postorder(node.right, out)
        out.append(node.val)

    def level_order(self) -> list[list[Any]]:
        """Values grouped by depth, shallowest level first."""
        if self._root is None:
            return []
        levels: list[list[Any]] = []
        queue: deque[TreeNode] = deque([self._root])
        while queue:
            level = [node.val for node in queue]
            levels.append(level)
            next_queue: deque[TreeNode] = deque()
            for node in queue:
                if node.left is not None:
                    next_queue.append(node.left)
                if node.right is not None:
                    next_queue.append(node.right)
            queue = next_queue
        return levels

    # -- viz plumbing ------------------------------------------------------

    @property
    def root_node(self) -> TreeNode | None:
        """The root `TreeNode`, or `None` when the tree is empty.

        Named `root_node` rather than `root`: `VizBase.root` already
        means "the outermost structure that owns drawing," and
        `_auto_show`/`clear_highlights` depend on that meaning. Shadowing
        it with the tree's root node would silently break redraws for
        any `VizTree` nested as a child of another structure.
        """
        return self._root

    def _eval_target(self) -> Any:
        return self._root

    def _renderable(self, title: str | None = None) -> RenderableType:
        tree = Tree(title or self.title)
        if self._root is None:
            tree.add(_EMPTY_LABEL)
        else:
            self._attach(tree, self._root, side=None)
        return tree

    def _attach(self, branch: Tree, node: TreeNode, side: str | None) -> None:
        style = self.highlights.style_for(id(node), self.config)
        label = paint(node.val, style)
        if side is not None:
            label = f"{side} {label}"
        child = branch.add(label)
        if node.left is not None:
            self._attach(child, node.left, side="L")
        if node.right is not None:
            self._attach(child, node.right, side="R")
