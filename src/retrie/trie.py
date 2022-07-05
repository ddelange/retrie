import re
from typing import Dict, Optional, Text, Union

data_type = Dict[Text, Union[int, Dict]]


class Trie:
    """Create a Trie for a sequence of strings.

    The Trie can be exported to a Regex pattern, which should match much faster than a
    simple Regex union.

    """

    __slots__ = "data"

    def __init__(self):
        self.data = {}  # type: data_type

    def add(self, *word):
        """Add one or more words to the current Trie."""
        for word in word:
            ref = self.data
            for char in word:
                ref[char] = ref.get(char, {})
                ref = ref[char]
            ref[""] = 1

    def dump(self):  # type: (...) -> data_type
        """Dump the current trie as dictionary."""
        return self.data

    def pattern(self):  # type: (...) -> Text
        """Dump the current trie as regex string."""
        return self._pattern(self.dump()) or ""

    @classmethod
    def _pattern(cls, data):  # type: (...) -> Optional[Text]
        """Build regex string from Trie."""
        if not data or len(data) == 1 and "" in data:
            return None

        deeper = []
        current = []
        leaf_reached = False
        for char in sorted(data):
            if data[char] == 1:
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
