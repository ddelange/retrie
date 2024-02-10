"""Submodule containing code to build a regex pattern from a trie of strings.

Standalone usage:
::

    from retrie.trie import Trie

    trie = Trie()

    trie.add("abc", "foo", "abs")
    assert trie.pattern() == "(?:ab[cs]|foo)"  # equivalent to but faster than "(?:abc|abs|foo)"

    trie.add("absolute")
    assert trie.pattern() == "(?:ab(?:c|s(?:olute)?)|foo)"

    trie.add("abx")
    assert trie.pattern() == "(?:ab(?:[cx]|s(?:olute)?)|foo)"

    trie.add("abxy")
    assert trie.pattern() == "(?:ab(?:c|s(?:olute)?|xy?)|foo)"
"""
import re
from typing import Any, Dict, Optional, Text  # noqa:F401

data_type = Dict[Text, Dict]


class Trie:
    """Create a Trie for a sequence of strings.

    The Trie can be exported to a Regex pattern, which should match much faster than a
    simple Regex union.

    """

    __slots__ = "data"

    def __init__(
        self, *word  # type: Text
    ):
        """Initialize data dictionary."""
        self.data = {}  # type: data_type
        self.add(*word)

    def __eq__(
        self, other  # type: Any
    ):  # type: (...) -> bool
        """Compare two Trie objects."""
        if not isinstance(other, Trie):
            return False
        return self.data == other.data

    def add(
        self, *word  # type: Text
    ):  # type: (...) -> "Trie"
        """Add one or more words to the current Trie."""
        if len(word) == 1 and not isinstance(word[0], str):
            word = word[0]

        for word in word:
            ref = self.data
            for char in word:
                ref[char] = ref.get(char, {})
                ref = ref[char]
            ref[""] = {}
        return self

    def dump(self):  # type: (...) -> data_type
        """Dump the current trie as dictionary."""
        return self.data

    def pattern(self):  # type: (...) -> Text
        """Dump the current trie as regex string."""
        return self._pattern(self.dump()) or ""

    @classmethod
    def _pattern(  # noqa: CCR001
        cls, data  # type: Dict
    ):  # type: (...) -> Optional[Text]
        """Build regex string from Trie."""
        if not data or len(data) == 1 and "" in data:
            return None

        deeper = []
        current = []
        leaf_reached = False
        for char in sorted(data):
            if char == "":
                leaf_reached = True
                continue

            recurse = cls._pattern(data[char])
            if recurse is None:
                current.append(re.escape(char))
            else:
                deeper.append(re.escape(char) + recurse)

        final = list(deeper)

        if current:
            if len(current) == 1:
                final.append(current[0])
            else:
                final.append("[" + "".join(current) + "]")

        if len(final) == 1:
            result = final[0]
        else:
            result = "(?:" + "|".join(sorted(final)) + ")"

        if leaf_reached:
            if not deeper:
                result += "?"
            else:
                result = "(?:" + result + ")?"

        return result
