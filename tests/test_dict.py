"""Tests for `VizDict`, `VizCounter`, and `VizSet`."""

from __future__ import annotations

import collections

import pytest
from algoviz.core import VizConfig, console
from algoviz.vizdict import VizCounter, VizDict, VizSet

QUIET = VizConfig(sleep_time=0.0, show_init=False, auto_print=False)


class TestVizDictProtocol:
    """A `VizDict` must behave like the dict it wraps."""

    def test_matches_plain_dict_across_an_operation_sequence(self) -> None:
        """Get/set/delete/update/pop/setdefault/popitem stay in lockstep."""
        sut = VizDict(config=QUIET)
        reference: dict = {}

        for key, value in [("a", 1), ("b", 2), ("c", 3)]:
            sut[key] = value
            reference[key] = value

        assert sut["a"] == reference["a"]
        assert ("b" in sut) == ("b" in reference)
        assert ("z" in sut) == ("z" in reference)

        del sut["a"]
        del reference["a"]
        assert dict(sut) == reference

        assert sut.setdefault("b", 99) == reference.setdefault("b", 99)
        assert sut.setdefault("d", 4) == reference.setdefault("d", 4)
        assert dict(sut) == reference

        assert sut.pop("b") == reference.pop("b")
        assert sut.pop("missing", "fallback") == reference.pop(
            "missing", "fallback"
        )
        assert dict(sut) == reference

        sut.update({"e": 5}, f=6)
        reference.update({"e": 5}, f=6)
        assert dict(sut) == reference

        assert sut.popitem() == reference.popitem()
        assert len(sut) == len(reference)
        assert list(sut) == list(reference)
        assert list(sut.keys()) == list(reference.keys())
        assert list(sut.values()) == list(reference.values())
        assert list(sut.items()) == list(reference.items())

    def test_pop_missing_key_without_default_raises_key_error(self) -> None:
        sut = VizDict(config=QUIET)

        with pytest.raises(KeyError):
            sut.pop("missing")

    def test_popitem_on_empty_dict_raises_key_error(self) -> None:
        sut = VizDict(config=QUIET)

        with pytest.raises(KeyError):
            sut.popitem()

    def test_constructs_from_a_mapping(self) -> None:
        assert dict(VizDict({"a": 1, "b": 2}, config=QUIET)) == {
            "a": 1,
            "b": 2,
        }

    def test_constructs_from_an_iterable_of_pairs(self) -> None:
        sut = VizDict([("a", 1), ("b", 2)], config=QUIET)

        assert dict(sut) == {"a": 1, "b": 2}


class TestVizDictRendering:
    """Rendering draws without crashing, empty or populated."""

    def test_empty_dict_renders_a_caption_not_a_crash(self) -> None:
        sut = VizDict(config=QUIET)

        with console.capture() as capture:
            sut.show()

        assert "empty" in capture.get()

    def test_populated_dict_renders_its_entries(self) -> None:
        sut = VizDict({"a": 1, "b": 2}, config=QUIET)

        with console.capture() as capture:
            sut.show()

        output = capture.get()
        assert "a" in output
        assert "1" in output


class TestVizCounter:
    """Counter semantics: default-0 reads, tallying, `most_common`."""

    def test_reading_a_missing_key_returns_zero_not_key_error(self) -> None:
        sut = VizCounter(config=QUIET)

        assert sut["missing"] == 0

    def test_increment_on_a_missing_key_ends_at_one(self) -> None:
        sut = VizCounter(config=QUIET)

        sut["a"] += 1

        assert sut["a"] == 1

    def test_most_common_matches_collections_counter_including_ties(
        self,
    ) -> None:
        """Ties keep insertion order, same as `collections.Counter`."""
        items = ["a", "b", "a", "c", "b", "a"]
        sut = VizCounter(items, config=QUIET)
        reference = collections.Counter(items)

        assert sut.most_common() == reference.most_common()
        assert sut.most_common(2) == reference.most_common(2)

    def test_constructs_by_tallying_an_iterable_of_items(self) -> None:
        sut = VizCounter(["a", "a", "b"], config=QUIET)

        assert dict(sut) == {"a": 2, "b": 1}

    def test_constructs_from_precomputed_counts(self) -> None:
        sut = VizCounter({"a": 2, "b": 1}, config=QUIET)

        assert dict(sut) == {"a": 2, "b": 1}

    def test_empty_counter_renders_a_caption_not_a_crash(self) -> None:
        sut = VizCounter(config=QUIET)

        with console.capture() as capture:
            sut.show()

        assert "empty" in capture.get()

    def test_populated_counter_renders_its_counts(self) -> None:
        sut = VizCounter(["a", "a", "b"], config=QUIET)

        with console.capture() as capture:
            sut.show()

        output = capture.get()
        assert "a" in output
        assert "2" in output

    def test_show_sorted_by_count_ranks_highest_first(self) -> None:
        sut = VizCounter(["a", "b", "b", "b"], config=QUIET)

        with console.capture() as capture:
            sut.show(sorted_by_count=True)

        output = capture.get()
        assert output.index("b") < output.index("a")


class TestVizSet:
    """Membership-set semantics: add/discard/remove and set algebra."""

    def test_add_then_membership(self) -> None:
        sut = VizSet(config=QUIET)
        sut.add(1)
        sut.add(2)

        assert 1 in sut
        assert 3 not in sut
        assert len(sut) == 2

    def test_discard_of_a_missing_element_does_not_raise(self) -> None:
        sut = VizSet([1], config=QUIET)

        sut.discard(99)

        assert set(sut) == {1}

    def test_remove_of_a_missing_element_raises_key_error(self) -> None:
        sut = VizSet([1], config=QUIET)

        with pytest.raises(KeyError):
            sut.remove(99)

    def test_remove_of_an_existing_element(self) -> None:
        sut = VizSet([1, 2], config=QUIET)

        sut.remove(1)

        assert set(sut) == {2}

    def test_set_algebra_matches_plain_sets(self) -> None:
        sut = VizSet([1, 2, 3], config=QUIET)
        plain = {1, 2, 3}
        other = {2, 3, 4}

        assert sut | other == plain | other
        assert sut & other == plain & other
        assert sut - other == plain - other
        assert sut ^ other == plain ^ other

    def test_constructs_from_an_iterable_deduplicating_members(self) -> None:
        sut = VizSet([1, 1, 2], config=QUIET)

        assert set(sut) == {1, 2}

    def test_empty_set_renders_a_caption_not_a_crash(self) -> None:
        sut = VizSet(config=QUIET)

        with console.capture() as capture:
            sut.show()

        assert "empty" in capture.get()

    def test_populated_set_renders_its_members(self) -> None:
        sut = VizSet([1, 2, 3], config=QUIET)

        with console.capture() as capture:
            sut.show()

        assert "2" in capture.get()
