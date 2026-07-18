"""Tests for `VizQueue` and `VizDeque`."""

from __future__ import annotations

import pytest
from algoviz.core import VizConfig, console
from algoviz.vizqueue import VizDeque, VizQueue

QUIET = VizConfig(sleep_time=0.0, show_init=False, auto_print=False)


@pytest.fixture
def sut() -> VizQueue:
    """A queue seeded with a few elements, rendering suppressed."""
    return VizQueue([1, 2, 3], config=QUIET)


@pytest.fixture
def dq() -> VizDeque:
    """A deque seeded with a few elements, rendering suppressed."""
    return VizDeque([1, 2, 3], config=QUIET)


class TestFifoOrder:
    """Enqueue and dequeue follow first-in-first-out order."""

    def test_dequeue_returns_oldest_first(self, sut: VizQueue) -> None:
        """The earliest-enqueued element is the first one out."""
        assert sut.dequeue() == 1

    def test_dequeue_drains_in_enqueue_order(self) -> None:
        """A run of dequeues returns enqueues in the order they arrived."""
        sut = VizQueue(config=QUIET)
        for value in (1, 2, 3):
            sut.enqueue(value)

        assert [sut.dequeue(), sut.dequeue(), sut.dequeue()] == [1, 2, 3]

    def test_peek_does_not_remove(self, sut: VizQueue) -> None:
        """Peeking leaves the queue's size and front unchanged."""
        before = len(sut)

        assert sut.peek() == 1
        assert sut.peek() == 1
        assert len(sut) == before

    def test_popleft_is_an_alias_for_dequeue(self) -> None:
        """`popleft` and `dequeue` behave identically."""
        sut = VizQueue([1, 2], config=QUIET)

        assert sut.popleft() == 1

    def test_append_is_an_alias_for_enqueue(self) -> None:
        """`append` and `enqueue` behave identically."""
        sut = VizQueue(config=QUIET)

        sut.append(1)

        assert sut.dequeue() == 1


class TestEmptyQueue:
    """An empty queue refuses to yield a value it does not have."""

    def test_dequeue_on_empty_raises_index_error(self) -> None:
        """Dequeuing nothing raises, rather than returning None."""
        sut = VizQueue(config=QUIET)

        with pytest.raises(IndexError):
            sut.dequeue()

    def test_peek_on_empty_raises_index_error(self) -> None:
        """Peeking nothing raises, rather than returning None."""
        sut = VizQueue(config=QUIET)

        with pytest.raises(IndexError):
            sut.peek()

    def test_is_empty_true_for_fresh_queue(self) -> None:
        """A queue with no enqueues reports itself empty."""
        assert VizQueue(config=QUIET).is_empty()

    def test_clear_empties_a_populated_queue(self, sut: VizQueue) -> None:
        """Clearing removes every element."""
        sut.clear()

        assert sut.is_empty()
        assert len(sut) == 0


class TestQueueProtocol:
    """Container protocol: len, iteration, membership, truthiness."""

    def test_len_matches_enqueues(self, sut: VizQueue) -> None:
        """Length reflects the number of elements currently queued."""
        assert len(sut) == 3

    def test_iterates_front_to_back(self, sut: VizQueue) -> None:
        """Iteration order matches dequeue order."""
        assert list(sut) == [1, 2, 3]

    def test_contains_checks_membership_anywhere(self, sut: VizQueue) -> None:
        """`in` finds a value regardless of its position."""
        assert 2 in sut
        assert 99 not in sut

    def test_bool_false_when_empty(self) -> None:
        """An empty queue is falsy."""
        assert not VizQueue(config=QUIET)

    def test_data_property_exposes_underlying_deque(
        self, sut: VizQueue
    ) -> None:
        """`data` returns the raw contents, front first."""
        assert list(sut.data) == [1, 2, 3]


class TestBfsLevels:
    """`mark_level` tags future enqueues without disturbing the past."""

    def test_mark_level_increments_and_returns_new_level(self) -> None:
        """Each call advances the level and reports the new number."""
        sut = VizQueue(config=QUIET)

        assert sut.mark_level() == 1
        assert sut.mark_level() == 2

    def test_elements_enqueued_before_a_mark_keep_their_level(self) -> None:
        """Marking a new level does not retroactively relevel old items."""
        sut = VizQueue(config=QUIET)
        sut.enqueue("root")
        sut.mark_level()
        sut.enqueue("child")

        assert list(sut._levels) == [0, 1]

    def test_clear_resets_the_level_counter(self) -> None:
        """Clearing forgets BFS depth along with the elements."""
        sut = VizQueue(config=QUIET)
        sut.mark_level()
        sut.mark_level()

        sut.clear()

        assert sut.mark_level() == 1


class TestQueueRendering:
    """Rendering draws without crashing and labels the ends."""

    def test_enqueue_renders_front_and_back_labels(self) -> None:
        """A render shows both FRONT and BACK for a multi-element queue."""
        sut = VizQueue([1], config=VizConfig(sleep_time=0.0, show_init=False))

        with console.capture() as capture:
            sut.enqueue(2)

        output = capture.get()
        assert "FRONT" in output
        assert "BACK" in output

    def test_show_clears_highlights_after_drawing(self, sut: VizQueue) -> None:
        """Once shown, a structure carries no leftover highlights."""
        sut.enqueue(4)

        sut.show()

        assert not sut.highlights.gets
        assert not sut.highlights.sets

    def test_dequeued_element_still_appears_once_then_vanishes(self) -> None:
        """A dequeue shows the departed value for one frame, then drops it."""
        sut = VizQueue(
            [1, 2], config=VizConfig(sleep_time=0.0, show_init=False)
        )

        with console.capture() as capture:
            sut.dequeue()
        first_frame = capture.get()

        with console.capture() as capture:
            sut.show()
        second_frame = capture.get()

        assert "1" in first_frame
        assert "1" not in second_frame

    def test_init_render_does_not_record_spurious_highlights(self) -> None:
        """Constructing and auto-showing leaves no dangling highlights."""
        sut = VizQueue([1, 2, 3])

        assert not sut.highlights.gets
        assert not sut.highlights.sets


class TestDequeBothEnds:
    """Both ends of a deque support push/pop independently."""

    def test_append_adds_to_the_back(self, dq: VizDeque) -> None:
        """`append` grows the back end."""
        dq.append(4)

        assert dq.pop() == 4

    def test_appendleft_adds_to_the_front(self, dq: VizDeque) -> None:
        """`appendleft` grows the front end."""
        dq.appendleft(0)

        assert dq.popleft() == 0

    def test_pop_removes_from_the_back(self, dq: VizDeque) -> None:
        """`pop` removes the most recently appended element."""
        assert dq.pop() == 3
        assert list(dq) == [1, 2]

    def test_popleft_removes_from_the_front(self, dq: VizDeque) -> None:
        """`popleft` removes the earliest element."""
        assert dq.popleft() == 1
        assert list(dq) == [2, 3]

    def test_peek_left_and_peek_right_do_not_remove(self, dq: VizDeque) -> None:
        """Peeking either end leaves the deque unchanged."""
        assert dq.peek_left() == 1
        assert dq.peek_right() == 3
        assert list(dq) == [1, 2, 3]


class TestEmptyDeque:
    """An empty deque refuses to yield a value it does not have."""

    def test_pop_on_empty_raises_index_error(self) -> None:
        """Popping the back of nothing raises."""
        with pytest.raises(IndexError):
            VizDeque(config=QUIET).pop()

    def test_popleft_on_empty_raises_index_error(self) -> None:
        """Popping the front of nothing raises."""
        with pytest.raises(IndexError):
            VizDeque(config=QUIET).popleft()

    def test_peek_left_on_empty_raises_index_error(self) -> None:
        """Peeking the front of nothing raises."""
        with pytest.raises(IndexError):
            VizDeque(config=QUIET).peek_left()

    def test_peek_right_on_empty_raises_index_error(self) -> None:
        """Peeking the back of nothing raises."""
        with pytest.raises(IndexError):
            VizDeque(config=QUIET).peek_right()

    def test_clear_empties_a_populated_deque(self, dq: VizDeque) -> None:
        """Clearing removes every element from both ends."""
        dq.clear()

        assert dq.is_empty()
        assert len(dq) == 0


class TestDequeProtocol:
    """Container protocol: len, iteration, membership, truthiness."""

    def test_len_matches_contents(self, dq: VizDeque) -> None:
        """Length reflects the number of elements currently held."""
        assert len(dq) == 3

    def test_iterates_front_to_back(self, dq: VizDeque) -> None:
        """Iteration order runs from the front end to the back end."""
        assert list(dq) == [1, 2, 3]

    def test_contains_checks_membership_anywhere(self, dq: VizDeque) -> None:
        """`in` finds a value regardless of its position."""
        assert 2 in dq
        assert 99 not in dq

    def test_bool_false_when_empty(self) -> None:
        """An empty deque is falsy."""
        assert not VizDeque(config=QUIET)

    def test_data_property_exposes_underlying_deque(self, dq: VizDeque) -> None:
        """`data` returns the raw contents, front first."""
        assert list(dq.data) == [1, 2, 3]


class TestDequeRendering:
    """Rendering draws without crashing and labels both ends."""

    def test_append_renders_front_and_back_labels(self) -> None:
        """A render shows both FRONT and BACK for a multi-element deque."""
        sut = VizDeque([1], config=VizConfig(sleep_time=0.0, show_init=False))

        with console.capture() as capture:
            sut.append(2)

        output = capture.get()
        assert "FRONT" in output
        assert "BACK" in output

    def test_popped_back_element_still_appears_once_then_vanishes(
        self,
    ) -> None:
        """A back pop shows the departed value for one frame, then drops it."""
        sut = VizDeque(
            [1, 2], config=VizConfig(sleep_time=0.0, show_init=False)
        )

        with console.capture() as capture:
            sut.pop()
        first_frame = capture.get()

        with console.capture() as capture:
            sut.show()
        second_frame = capture.get()

        assert "2" in first_frame
        assert "2" not in second_frame

    def test_show_clears_highlights_after_drawing(self, dq: VizDeque) -> None:
        """Once shown, a structure carries no leftover highlights."""
        dq.append(4)

        dq.show()

        assert not dq.highlights.gets
        assert not dq.highlights.sets

    def test_init_render_does_not_record_spurious_highlights(self) -> None:
        """Constructing and auto-showing leaves no dangling highlights."""
        sut = VizDeque([1, 2, 3])

        assert not sut.highlights.gets
        assert not sut.highlights.sets
