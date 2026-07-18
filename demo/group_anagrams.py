"""Group Anagrams: bucket by sorted letters (LeetCode 49)."""

from algoviz import VizDict


def group_anagrams(words: list[str]) -> list[list[str]]:
    """Two words are anagrams exactly when their sorted letters match."""
    groups = VizDict(title_name="signature -> words")
    for word in words:
        signature = "".join(sorted(word))
        groups.setdefault(signature, []).append(word)
    return list(groups.values())


if __name__ == "__main__":
    print(f"Output : {group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat'])}")
