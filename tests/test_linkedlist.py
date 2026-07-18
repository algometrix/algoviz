"""Tests for `algoviz.vizlinkedlist`."""

from __future__ import annotations

import pytest
from algoviz.core import VizConfig
from algoviz.vizlinkedlist import ListNode, VizLinkedList

QUIET = VizConfig(auto_print=False, show_init=False)


@pytest.fixture
def quiet_config() -> VizConfig:
    """A config that never prints, so tests stay silent."""
    return QUIET


def _cyclic_chain() -> tuple[ListNode, ListNode]:
    """Build `1 -> 2 -> 3 -> 4`, with `4` looping back to `2`.

    Returns the head and the node the cycle reconnects to, so tests can
    assert against it without re-deriving it.
    """
    head = ListNode(1)
    second = ListNode(2)
    third = ListNode(3)
    fourth = ListNode(4)
    head.next = second
    second.next = third
    third.next = fourth
    fourth.next = second
    return head, second


class TestRoundTrip:
    """Building from values and reading them back."""

    def test_from_list_round_trips_through_to_list(
        self, quiet_config: VizConfig
    ) -> None:
        """to_list undoes from_list for a plain, acyclic list."""
        sut = VizLinkedList.from_list([1, 2, 3], config=quiet_config)

        assert sut.to_list() == [1, 2, 3]

    def test_wraps_an_existing_head_node(self, quiet_config: VizConfig) -> None:
        """A pasted-in ListNode chain is accepted as-is."""
        head = ListNode(1, ListNode(2, ListNode(3)))

        sut = VizLinkedList(head, config=quiet_config)

        assert sut.to_list() == [1, 2, 3]
        assert sut.head is head

    def test_empty_source_is_an_empty_list(
        self, quiet_config: VizConfig
    ) -> None:
        """No source, or an empty iterable, both yield an empty chain."""
        assert VizLinkedList(config=quiet_config).to_list() == []
        assert VizLinkedList([], config=quiet_config).to_list() == []

    def test_len_and_iter_and_contains_match_to_list(
        self, quiet_config: VizConfig
    ) -> None:
        """The Python protocols agree with to_list on a plain chain."""
        sut = VizLinkedList.from_list([1, 2, 3], config=quiet_config)

        assert len(sut) == 3
        assert list(sut) == [1, 2, 3]
        assert 2 in sut
        assert 9 not in sut


class TestMutation:
    """append, prepend, and reverse."""

    def test_append_adds_to_the_tail(self, quiet_config: VizConfig) -> None:
        """Append grows the chain at the end, preserving order."""
        sut = VizLinkedList.from_list([1, 2], config=quiet_config)

        sut.append(3)

        assert sut.to_list() == [1, 2, 3]

    def test_append_on_empty_list_creates_the_head(
        self, quiet_config: VizConfig
    ) -> None:
        """Append on an empty list has no tail to chain onto."""
        sut = VizLinkedList(config=quiet_config)

        sut.append(1)

        assert sut.to_list() == [1]

    def test_prepend_adds_a_new_head(self, quiet_config: VizConfig) -> None:
        """Prepend grows the chain at the front."""
        sut = VizLinkedList.from_list([2, 3], config=quiet_config)

        sut.prepend(1)

        assert sut.to_list() == [1, 2, 3]

    def test_reverse_flips_order_and_updates_head(
        self, quiet_config: VizConfig
    ) -> None:
        """Reverse mutates in place and moves the head pointer."""
        sut = VizLinkedList.from_list([1, 2, 3, 4], config=quiet_config)

        sut.reverse()

        assert sut.to_list() == [4, 3, 2, 1]
        assert sut.head.val == 4

    def test_reverse_of_empty_list_stays_empty(
        self, quiet_config: VizConfig
    ) -> None:
        """Reversing nothing raises nothing and stays empty."""
        sut = VizLinkedList(config=quiet_config)

        sut.reverse()

        assert sut.to_list() == []
        assert sut.head is None

    def test_append_on_cyclic_list_raises(
        self, quiet_config: VizConfig
    ) -> None:
        """A cyclic list has no tail, so append is rejected."""
        head, _ = _cyclic_chain()
        sut = VizLinkedList(head, config=quiet_config)

        with pytest.raises(ValueError):
            sut.append(5)

    def test_reverse_of_cyclic_list_raises(
        self, quiet_config: VizConfig
    ) -> None:
        """Reversing a cycle would corrupt the back-edge, so it's rejected."""
        head, _ = _cyclic_chain()
        sut = VizLinkedList(head, config=quiet_config)

        with pytest.raises(ValueError):
            sut.reverse()


class TestCycleSafety:
    """A cyclic list must never hang len/iter/to_list/render."""

    def test_len_terminates_and_counts_distinct_nodes(
        self, quiet_config: VizConfig
    ) -> None:
        """Len counts each node in the cycle exactly once."""
        head, _ = _cyclic_chain()
        sut = VizLinkedList(head, config=quiet_config)

        assert len(sut) == 4

    def test_to_list_terminates_before_repeating(
        self, quiet_config: VizConfig
    ) -> None:
        """to_list stops the first time it would revisit a node."""
        head, _ = _cyclic_chain()
        sut = VizLinkedList(head, config=quiet_config)

        assert sut.to_list() == [1, 2, 3, 4]

    def test_iter_terminates(self, quiet_config: VizConfig) -> None:
        """Iterating a cyclic list finishes instead of looping forever."""
        head, _ = _cyclic_chain()
        sut = VizLinkedList(head, config=quiet_config)

        assert list(sut) == [1, 2, 3, 4]

    def test_has_cycle_detects_the_loop(self, quiet_config: VizConfig) -> None:
        """has_cycle is True exactly when the chain loops back."""
        head, _ = _cyclic_chain()
        cyclic = VizLinkedList(head, config=quiet_config)
        acyclic = VizLinkedList.from_list([1, 2, 3], config=quiet_config)

        assert cyclic.has_cycle is True
        assert acyclic.has_cycle is False

    def test_render_of_cyclic_list_terminates_and_marks_back_edge(
        self, quiet_config: VizConfig
    ) -> None:
        """Rendering a cycle finishes and the back-edge marker appears."""
        head, _ = _cyclic_chain()
        sut = VizLinkedList(head, config=quiet_config)

        renderable = sut._renderable()

        assert renderable is not None


class TestPointers:
    """Named pointers for two-pointer and cycle-detection algorithms."""

    def test_set_pointer_is_recorded(self, quiet_config: VizConfig) -> None:
        """A named pointer targets the given node."""
        sut = VizLinkedList.from_list([1, 2, 3], config=quiet_config)
        second = sut.head.next

        sut.set_pointer("slow", second)

        assert sut.pointers["slow"] is second

    def test_multiple_pointers_can_target_different_nodes(
        self, quiet_config: VizConfig
    ) -> None:
        """Slow and fast can point at different nodes simultaneously."""
        sut = VizLinkedList.from_list([1, 2, 3], config=quiet_config)

        sut.set_pointer("slow", sut.head)
        sut.set_pointer("fast", sut.head.next)

        assert sut.pointers["slow"] is sut.head
        assert sut.pointers["fast"] is sut.head.next

    def test_set_pointer_to_none_removes_it(
        self, quiet_config: VizConfig
    ) -> None:
        """Passing None clears a previously set pointer."""
        sut = VizLinkedList.from_list([1, 2, 3], config=quiet_config)
        sut.set_pointer("slow", sut.head)

        sut.set_pointer("slow", None)

        assert "slow" not in sut.pointers

    def test_pointer_into_a_cycle_is_recorded(
        self, quiet_config: VizConfig
    ) -> None:
        """A classic fast/slow cycle-detection setup can be represented."""
        head, cycle_node = _cyclic_chain()
        sut = VizLinkedList(head, config=quiet_config)

        sut.set_pointer("slow", cycle_node)
        sut.set_pointer("fast", cycle_node.next.next)

        assert sut.pointers["slow"] is cycle_node
        renderable = sut._renderable()
        assert renderable is not None


class TestHeadSetterAndNodes:
    """Rewiring pointers by hand is the whole point of these problems."""

    def test_head_can_be_reassigned(self):
        linked = VizLinkedList([1, 2, 3], config=QUIET)
        linked.head = linked.head.next
        assert linked.to_list() == [2, 3]

    def test_head_can_be_cleared(self):
        linked = VizLinkedList([1, 2], config=QUIET)
        linked.head = None
        assert linked.to_list() == []
        assert len(linked) == 0

    def test_head_rejects_a_non_node(self):
        linked = VizLinkedList([1], config=QUIET)
        with pytest.raises(TypeError, match="ListNode"):
            linked.head = 5

    def test_manual_reverse_round_trip(self):
        """The LeetCode 206 solution, done by hand against this API."""
        linked = VizLinkedList([1, 2, 3, 4, 5], config=QUIET)
        previous = None
        current = linked.head
        while current is not None:
            following = current.next
            current.next = previous
            previous = current
            current = following
        linked.head = previous
        assert linked.to_list() == [5, 4, 3, 2, 1]

    def test_nodes_returns_real_nodes(self):
        linked = VizLinkedList([1, 2, 3], config=QUIET)
        nodes = linked.nodes()
        assert [node.val for node in nodes] == [1, 2, 3]
        assert nodes[0] is linked.head

    def test_nodes_is_empty_for_an_empty_list(self):
        assert VizLinkedList([], config=QUIET).nodes() == []

    def test_nodes_terminates_on_a_cycle(self):
        linked = VizLinkedList([1, 2, 3], config=QUIET)
        nodes = linked.nodes()
        nodes[-1].next = nodes[1]
        assert len(linked.nodes()) == 3
        assert linked.has_cycle is True

    def test_nodes_snapshot_does_not_alias_internals(self):
        linked = VizLinkedList([1, 2], config=QUIET)
        linked.nodes().clear()
        assert len(linked) == 2
