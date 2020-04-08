import re
from typing import (
    Any,
    Dict,
    Iterator,
    Mapping,
    Match,
    Optional,
    Pattern,
    Sequence,
    Text,
)

from . import cached_property, trie  # noqa:ABS101

re_flag_type = Optional[int]

DEFAULT_FLAGS = re.IGNORECASE | re.UNICODE
WORD_BOUNDARY = r"\b"


def _lower_keys(
    mapping,  # type: Mapping[Text, Any]
):  # type: (...) -> Dict[Text, Any]
    """Convert all keys of mapping to lowercase."""
    return dict(zip((k.lower() for k in mapping), mapping.values()))


class Retrie:
    __slots__ = "trie", "word_boundary", "re_flags"

    def __init__(
        self,
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):  # type: (...) -> None
        """Initialize Trie and set regex config.

        Note:
            Although the Trie is case-sensitive, by defailt re.IGNORECASE is used.

        Args:
            word_boundary (str): Token to wrap the retrie to exclude certain matches.
            re_flags (re.RegexFlag): Flags passed to regex engine.
        """
        self.trie = trie.Trie()
        self.word_boundary = word_boundary or ""
        self.re_flags = self.parse_re_flags(re_flags)

    @classmethod
    def parse_re_flags(
        cls, re_flags,  # type: re_flag_type
    ):  # type: (...) -> int
        return int(re_flags) if re_flags else 0

    def pattern(self):  # type: (...) -> Text
        """Build regex pattern for the current Trie.

        Returns:
            str: Non-capturing regex representation.
        """
        return self.trie.pattern()

    def compile(  # noqa:A003
        self,
        word_boundary=None,  # type: Optional[Text]
        re_flags=-1,  # type: re_flag_type
    ):  # type: (...) -> Pattern[Text]
        """Compile re.Pattern for the current Trie.

        Optionally the following args can be passed to temporarily override class attrs.

        Args:
            word_boundary (str): Token to wrap the retrie to exclude certain matches.
            re_flags (re.RegexFlag): Flags passed to regex engine.

        Returns:
            re.Pattern: Pattern capturing the Trie items enclosed by word_boundary.
        """
        word_boundary = self.word_boundary if word_boundary is None else word_boundary
        re_flags = self.re_flags if re_flags == -1 else re_flags

        lookbehind = "(?<=" + word_boundary + ")" if word_boundary else ""
        lookahead = "(?=" + word_boundary + ")" if word_boundary else ""

        return re.compile(
            lookbehind + self.pattern() + lookahead,
            flags=self.parse_re_flags(re_flags),
        )


class Checklist(Retrie):
    def __init__(
        self,
        keys,  # type: Sequence[Text]
        match_substrings=False,  # type: bool
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):  # type: (...) -> None
        """Check and mutate strings against a Retrie.

        Note:
            Although the Trie is case-sensitive, by defailt re.IGNORECASE is used.

        Args:
            keys (Sequence): Strings to build the Retrie from.
            match_substrings (bool): Wether or not to override word_boundary with "".
            word_boundary (str): Token to wrap the retrie to exclude certain matches.
            re_flags (re.RegexFlag): Flags passed to regex engine.
        """
        if match_substrings:
            word_boundary = ""

        Retrie.__init__(self, word_boundary=word_boundary, re_flags=re_flags)

        for term in keys:
            self.trie.add(term)

    @cached_property
    def compiled(self):  # type: (...) -> Pattern[Text]
        """Compute and cache the compiled Pattern."""
        return self.compile()

    def is_listed(
        self, term  # type: Text
    ):  # type: (...) -> bool
        """Return True if Pattern is found in term."""
        return bool(self.compiled.search(term))

    def not_listed(
        self, term  # type: Text
    ):  # type: (...) -> bool
        """Return True if Pattern is not found in term."""
        return not self.is_listed(term)


class Blacklist(Checklist):
    def __init__(
        self,
        blacklisted,  # type: Sequence[Text]
        match_substrings=False,  # type: bool
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):
        """Mutate [sequences of] strings based on their match against blacklisted.

        Note:
            Although the Trie is case-sensitive, by defailt re.IGNORECASE is used.

        Args:
            blacklisted (Sequence): Strings to build the Retrie from.
            match_substrings (bool): Wether or not to override word_boundary with "".
            word_boundary (str): Token to wrap the retrie to exclude certain matches.
            re_flags (re.RegexFlag): Flags passed to regex engine.
        """
        Checklist.__init__(
            self,
            keys=blacklisted,
            match_substrings=match_substrings,
            word_boundary=word_boundary,
            re_flags=re_flags,
        )

    def is_blacklisted(
        self, term  # type: Text
    ):  # type: (...) -> bool
        """Return True if Pattern is found in term."""
        return self.is_listed(term)

    def filter(  # noqa:A003
        self, sequence,  # type: Sequence[Text]
    ):  # type: (...) -> Iterator[Text]
        """Construct an iterator from those elements of sequence not blacklisted."""
        return filter(self.not_listed, sequence)

    def cleanse_text(
        self, term  # type: Text
    ):  # type: (...) -> Text
        """Return text, removing all blacklisted terms."""
        return self.compiled.sub("", term)


class Whitelist(Checklist):
    def __init__(
        self,
        whitelisted,  # type: Sequence[Text]
        match_substrings=False,  # type: bool
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):
        """Mutate [sequences of] strings based on their match against whitelisted.

        Note:
            Although the Trie is case-sensitive, by defailt re.IGNORECASE is used.

        Args:
            whitelisted (Sequence): Strings to build the Retrie from.
            match_substrings (bool): Wether or not to override word_boundary with "".
            word_boundary (str): Token to wrap the retrie to exclude certain matches.
            re_flags (re.RegexFlag): Flags passed to regex engine.
        """
        Checklist.__init__(
            self,
            keys=whitelisted,
            match_substrings=match_substrings,
            word_boundary=word_boundary,
            re_flags=re_flags,
        )

    def is_whitelisted(
        self, term  # type: Text
    ):  # type: (...) -> bool
        """Return True if Pattern is found in term."""
        return self.is_listed(term)

    def filter(  # noqa:A003
        self, sequence,  # type: Sequence[Text]
    ):  # type: (...) -> Iterator[Text]
        """Construct an iterator from whitelisted elements of sequence."""
        return filter(self.is_listed, sequence)

    def cleanse_text(
        self, term  # type: Text
    ):  # type: (...) -> Text
        """Return text, only keeping whitelisted terms."""
        return "".join(self.compiled.findall(term))


class Replacer(Checklist):
    __slots__ = "replacement_mapping"

    def __init__(
        self,
        replacement_mapping,  # type: Mapping[Text, Text]
        match_substrings=False,  # type: bool
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):
        """Replace occurrences of replacement_mapping.keys() with corresponding values.

        Note:
            Although the Trie is case-sensitive, by defailt re.IGNORECASE is used.

        Args:
            replacement_mapping (Mapping): Mapping {old: new} to replace.
            match_substrings (bool): Wether or not to override word_boundary with "".
            word_boundary (str): Token to wrap the retrie to exclude certain matches.
            re_flags (re.RegexFlag): Flags passed to regex engine.
        """
        Checklist.__init__(
            self,
            keys=tuple(replacement_mapping.keys()),
            match_substrings=match_substrings,
            word_boundary=word_boundary,
            re_flags=re_flags,
        )

        self.replacement_mapping = (
            _lower_keys(replacement_mapping)
            if re.IGNORECASE & self.re_flags
            else replacement_mapping
        )

    def _replace(
        self, match  # type: Match[Text]
    ):  # type: (...) -> Text
        """Helper for dict lookup in re.sub."""
        key = (
            match.group(0).lower() if re.IGNORECASE & self.re_flags else match.group(0)
        )
        return self.replacement_mapping[key]

    def replace(
        self,
        text,  # type: Text
        count=0,  # type: int
    ):  # type: (...) -> Text
        """Replace occurrences of replacement_mapping.keys() with corresponding values.

        Args:
            text (str): String to search & replace.
            count (int): Amount of occurences to replace. If 0 or emitted, replace all.
        """
        return self.compiled.sub(self._replace, text, count=count)
