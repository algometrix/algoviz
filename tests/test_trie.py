"""Tests for `algoviz.viztrie`."""

from __future__ import annotations

import pytest
from algoviz.core import VizConfig
from algoviz.viztrie import VizTrie

QUIET = VizConfig(auto_print=False, show_init=False)


@pytest.fixture
def quiet_config() -> VizConfig:
    """A config that never prints, so tests stay silent."""
    return QUIET


class TestInsertAndLookup:
    """insert, search, starts_with, and the containers protocol."""

    def test_search_matches_only_a_full_word(
        self, quiet_config: VizConfig
    ) -> None:
        """search('app') is False when only 'apple' was inserted."""
        sut = VizTrie(config=quiet_config)
        sut.insert("apple")

        assert sut.search("apple") is True
        assert sut.search("app") is False

    def test_starts_with_matches_any_stored_prefix(
        self, quiet_config: VizConfig
    ) -> None:
        """starts_with is true for a prefix even without an exact word."""
        sut = VizTrie(config=quiet_config)
        sut.insert("apple")

        assert sut.starts_with("app") is True
        assert sut.starts_with("appl") is True
        assert sut.starts_with("b") is False

    def test_search_and_starts_with_disagree_on_a_bare_prefix(
        self, quiet_config: VizConfig
    ) -> None:
        """The classic distinguishing case between the two lookups."""
        sut = VizTrie(config=quiet_config)
        sut.insert("apple")

        assert sut.starts_with("app") is True
        assert sut.search("app") is False

    def test_search_on_empty_trie_is_false(
        self, quiet_config: VizConfig
    ) -> None:
        """Nothing stored, nothing found, no crash."""
        sut = VizTrie(config=quiet_config)

        assert sut.search("anything") is False
        assert sut.starts_with("a") is False

    def test_starts_with_empty_prefix_is_vacuously_true(
        self, quiet_config: VizConfig
    ) -> None:
        """Every word starts with the empty prefix."""
        sut = VizTrie(config=quiet_config)
        sut.insert("cat")

        assert sut.starts_with("") is True

    def test_insert_of_empty_word_raises(self, quiet_config: VizConfig) -> None:
        """There is no such thing as an empty word to store."""
        sut = VizTrie(config=quiet_config)

        with pytest.raises(ValueError):
            sut.insert("")

    def test_reinserting_a_word_does_not_grow_the_count(
        self, quiet_config: VizConfig
    ) -> None:
        """Inserting the same word twice stores it once."""
        sut = VizTrie(config=quiet_config)
        sut.insert("cat")

        sut.insert("cat")

        assert len(sut) == 1

    def test_contains_matches_search(self, quiet_config: VizConfig) -> None:
        """The `in` operator behaves like search."""
        sut = VizTrie(config=quiet_config)
        sut.insert("cat")

        assert "cat" in sut
        assert "ca" not in sut


class TestConstructionFromSource:
    """Bulk construction from an iterable of words."""

    def test_source_words_are_all_present(
        self, quiet_config: VizConfig
    ) -> None:
        """Every word passed to the constructor is queryable."""
        sut = VizTrie(["cat", "car", "dog"], config=quiet_config)

        assert sut.words() == ["car", "cat", "dog"]

    def test_len_counts_distinct_words(self, quiet_config: VizConfig) -> None:
        """Word count, not node count."""
        sut = VizTrie(["cat", "car", "dog"], config=quiet_config)

        assert len(sut) == 3

    def test_no_source_is_an_empty_trie(self, quiet_config: VizConfig) -> None:
        """No source, no crash, nothing stored."""
        sut = VizTrie(config=quiet_config)

        assert len(sut) == 0
        assert sut.words() == []


class TestDelete:
    """delete, and that it never breaks sibling words."""

    def test_delete_removes_the_word(self, quiet_config: VizConfig) -> None:
        """A deleted word is no longer found."""
        sut = VizTrie(["cat"], config=quiet_config)

        removed = sut.delete("cat")

        assert removed is True
        assert sut.search("cat") is False

    def test_delete_of_absent_word_returns_false(
        self, quiet_config: VizConfig
    ) -> None:
        """Deleting something never inserted changes nothing."""
        sut = VizTrie(["cat"], config=quiet_config)

        removed = sut.delete("dog")

        assert removed is False
        assert sut.search("cat") is True

    def test_delete_does_not_break_a_sibling_that_shares_a_prefix(
        self, quiet_config: VizConfig
    ) -> None:
        """Deleting 'car' must leave 'cat' fully intact."""
        sut = VizTrie(["cat", "car"], config=quiet_config)

        sut.delete("car")

        assert sut.search("cat") is True
        assert sut.search("car") is False
        assert sut.words() == ["cat"]

    def test_delete_does_not_break_a_word_that_is_its_prefix(
        self, quiet_config: VizConfig
    ) -> None:
        """Deleting 'apple' must leave the shorter word 'app' intact."""
        sut = VizTrie(["app", "apple"], config=quiet_config)

        sut.delete("apple")

        assert sut.search("app") is True
        assert sut.search("apple") is False

    def test_delete_prunes_nodes_with_no_remaining_purpose(
        self, quiet_config: VizConfig
    ) -> None:
        """Removing the only word along a branch drops that branch."""
        sut = VizTrie(["cat"], config=quiet_config)

        sut.delete("cat")

        assert sut.starts_with("c") is False
        assert len(sut) == 0

    def test_delete_does_not_prune_a_prefix_still_in_use(
        self, quiet_config: VizConfig
    ) -> None:
        """A prefix another word still needs survives pruning."""
        sut = VizTrie(["cat", "car"], config=quiet_config)

        sut.delete("cat")

        assert sut.starts_with("ca") is True
        assert sut.search("car") is True
