"""Submodule containing the :class:`Retrie` class, which handles filling the Trie and compiling the corresponding regex pattern, and its high-level wrappers.

The :class:`Blacklist` class can be used to filter out bad occurences in a text or a sequence of strings:
::

    from retrie.retrie import Blacklist

    # check out docstrings and methods
    help(Blacklist)

    blacklist = Blacklist(["abc", "foo", "abs"], match_substrings=False)
    blacklist.compiled
    # re.compile(r'(?<=\b)(?:ab[cs]|foo)(?=\b)', re.IGNORECASE|re.UNICODE)
    assert not blacklist.is_blacklisted("a foobar")
    assert tuple(blacklist.filter(("good", "abc", "foobar"))) == ("good", "foobar")
    assert blacklist.cleanse_text(("good abc foobar")) == "good  foobar"

    blacklist = Blacklist(["abc", "foo", "abs"], match_substrings=True)
    blacklist.compiled
    # re.compile(r'(?:ab[cs]|foo)', re.IGNORECASE|re.UNICODE)
    assert blacklist.is_blacklisted("a foobar")
    assert tuple(blacklist.filter(("good", "abc", "foobar"))) == ("good",)
    assert blacklist.cleanse_text(("good abc foobar")) == "good  bar"


Similar methods are available for the :class:`Whitelist` class:
::

    from retrie.retrie import Whitelist

    # check out docstrings and methods
    help(Whitelist)

    whitelist = Whitelist(["abc", "foo", "abs"], match_substrings=False)
    whitelist.compiled
    # re.compile(r'(?<=\b)(?:ab[cs]|foo)(?=\b)', re.IGNORECASE|re.UNICODE)
    assert not whitelist.is_whitelisted("a foobar")
    assert tuple(whitelist.filter(("bad", "abc", "foobar"))) == ("abc",)
    assert whitelist.cleanse_text(("bad abc foobar")) == "abc"

    whitelist = Whitelist(["abc", "foo", "abs"], match_substrings=True)
    whitelist.compiled
    # re.compile(r'(?:ab[cs]|foo)', re.IGNORECASE|re.UNICODE)
    assert whitelist.is_whitelisted("a foobar")
    assert tuple(whitelist.filter(("bad", "abc", "foobar"))) == ("abc", "foobar")
    assert whitelist.cleanse_text(("bad abc foobar")) == "abcfoo"

The :class:`Replacer` class does a fast single-pass search & replace for occurrences of ``replacement_mapping.keys()`` with corresponding values.
::

    from retrie.retrie import Replacer

    # check out docstrings and methods
    help(Replacer)

    replacement_mapping = dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"]))

    replacer = Replacer(replacement_mapping, match_substrings=True)
    replacer.compiled
    # re.compile(r'(?:ab[cs]|foo)', re.IGNORECASE|re.UNICODE)
    assert replacer.replace("ABS ...foo... foobar") == "new3 ...new2... new2bar"

    replacer = Replacer(replacement_mapping, match_substrings=False)
    replacer.compiled
    # re.compile(r'\b(?:ab[cs]|foo)\b', re.IGNORECASE|re.UNICODE)
    assert replacer.replace("ABS ...foo... foobar") == "new3 ...new2... foobar"

    replacer = Replacer(replacement_mapping, match_substrings=False, re_flags=None)
    replacer.compiled  # on py3, re.UNICODE is always enabled
    # re.compile(r'\b(?:ab[cs]|foo)\b')
    assert replacer.replace("ABS ...foo... foobar") == "ABS ...new2... foobar"

    replacer = Replacer(replacement_mapping, match_substrings=False, word_boundary=" ")
    replacer.compiled
    # re.compile(r'(?<= )(?:ab[cs]|foo)(?= )', re.IGNORECASE|re.UNICODE)
    assert replacer.replace(". ABS ...foo... foobar") == ". new3 ...foo... foobar"
"""
import re
from typing import (  # noqa:F401
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

DEFAULT_FLAGS = re.IGNORECASE | re.UNICODE  # on py3, re.UNICODE is always enabled
WORD_BOUNDARY = r"\b"


def _lower_keys(
    mapping,  # type: Mapping[Text, Any]
):  # type: (...) -> Dict[Text, Any]
    """Convert all keys of mapping to lowercase."""
    out = {k.lower(): v for k, v in mapping.items()}
    if len(out) < len(mapping):
        raise ValueError(
            "Ambiguous replacement_mapping: converting keys to lowercase yields duplicate keys"
        )
    return out


class Retrie:
    """Wrap a :class:`retrie.trie.Trie` to compile the corresponding regex pattern with word boundary and regex flags.

    Note:
        Although the Trie is case-sensitive, by default :obj:`re.IGNORECASE` is used for better performance. Pass ``re_flags=None`` to perform case-sensitive replacements.

    Args:
        word_boundary (str): Token to wrap the retrie to exclude certain matches.
        re_flags (re.RegexFlag): Flags passed to regex engine.
    """

    __slots__ = "trie", "word_boundary", "re_flags"

    def __init__(
        self,
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):  # type: (...) -> None
        """Initialize :class:`retrie.trie.Trie` and set config."""
        self.trie = trie.Trie()
        """The underlying :class:`retrie.trie.Trie`."""
        self.word_boundary = word_boundary or ""
        """The boundary token to wrap the :class:`retrie.trie.Trie` pattern in."""
        self.re_flags = self.parse_re_flags(re_flags)
        """Regex flags passed to :func:`re.compile`."""

    @classmethod
    def parse_re_flags(
        cls,
        re_flags,  # type: re_flag_type
    ):  # type: (...) -> int
        """Convert re_flags to integer.

        Args:
            re_flags (re.RegexFlag | int | None): The flags to cast to integer.
        """
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
        """Compile a :class:`re.Pattern` for the current Trie.

        Optionally the following args can be passed to temporarily override class attrs.

        Args:
            word_boundary (str): Token to wrap the retrie to exclude certain matches.
            re_flags (re.RegexFlag): Flags passed to regex engine.

        Returns:
            re.Pattern: Pattern capturing the Trie items enclosed by word_boundary.
        """
        word_boundary = self.word_boundary if word_boundary is None else word_boundary
        re_flags = self.re_flags if re_flags == -1 else re_flags

        if word_boundary == r"\b":
            # \b is non-capturing, so doesn't need to be wrapped
            lookbehind = lookahead = word_boundary
        else:
            lookbehind = "(?<=" + word_boundary + ")" if word_boundary else ""
            lookahead = "(?=" + word_boundary + ")" if word_boundary else ""

        return re.compile(
            lookbehind + self.pattern() + lookahead,
            flags=self.parse_re_flags(re_flags),
        )


class Checklist(Retrie):
    """Check and mutate strings against a Retrie.

    Note:
        Although the Trie is case-sensitive, by default :obj:`re.IGNORECASE` is used for better performance. Pass ``re_flags=None`` to perform case-sensitive replacements.

    Args:
        keys (Sequence): Strings to build the Retrie from.
        match_substrings (bool): Whether to override word_boundary with ``""``.
        word_boundary (str): Token to wrap the retrie to exclude certain matches.
        re_flags (re.RegexFlag): Flags passed to regex engine.
    """

    def __init__(
        self,
        keys,  # type: Sequence[Text]
        match_substrings=False,  # type: bool
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):  # type: (...) -> None
        """Initialize :class:`retrie.trie.Trie` and set config."""
        if match_substrings:
            word_boundary = ""

        Retrie.__init__(self, word_boundary=word_boundary, re_flags=re_flags)

        for key in keys:  # lazy exhaust in case keys is a huge generator
            self.trie.add(key)

    @cached_property
    def compiled(self):  # type: (...) -> Pattern[Text]
        """Compute and cache the compiled Pattern."""
        return self.compile()

    def is_listed(
        self, term  # type: Text
    ):  # type: (...) -> bool
        """Return True if Pattern is found in term.

        Args:
            term (str): The string to search.
        """
        return bool(self.compiled.search(term))

    def not_listed(
        self, term  # type: Text
    ):  # type: (...) -> bool
        """Return True if Pattern is not found in term.

        Args:
            term (str): The string to search.
        """
        return not self.is_listed(term)


class Blacklist(Checklist):
    """Mutate [sequences of] strings based on their match against blacklisted.

    Note:
        Although the Trie is case-sensitive, by default :obj:`re.IGNORECASE` is used for better performance. Pass ``re_flags=None`` to perform case-sensitive replacements.

    Args:
        blacklisted (Sequence): Strings to build the Retrie from.
        match_substrings (bool): Whether to override word_boundary with ``""``.
        word_boundary (str): Token to wrap the retrie to exclude certain matches.
        re_flags (re.RegexFlag): Flags passed to regex engine.
    """

    def __init__(
        self,
        blacklisted,  # type: Sequence[Text]
        match_substrings=False,  # type: bool
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):
        """Initialize :class:`retrie.trie.Trie` and set config."""
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
        """Return True if Pattern is found in term.

        Args:
            term (str): The string to search.
        """
        return self.is_listed(term)

    def filter(  # noqa:A003
        self,
        sequence,  # type: Sequence[Text]
    ):  # type: (...) -> Iterator[Text]
        """Construct an iterator from those elements of sequence not blacklisted.

        Args:
            sequence (Sequence): The sequence of strings to filter.
        """
        return filter(self.not_listed, sequence)

    def cleanse_text(
        self, term  # type: Text
    ):  # type: (...) -> Text
        """Return text, removing all blacklisted terms.

        Args:
            term (str): The string to search.
        """
        return self.compiled.sub("", term)


class Whitelist(Checklist):
    """Mutate [sequences of] strings based on their match against whitelisted.

    Note:
        Although the Trie is case-sensitive, by default :obj:`re.IGNORECASE` is used for better performance. Pass ``re_flags=None`` to perform case-sensitive replacements.

    Args:
        whitelisted (Sequence): Strings to build the Retrie from.
        match_substrings (bool): Whether to override word_boundary with ``""``.
        word_boundary (str): Token to wrap the retrie to exclude certain matches.
        re_flags (re.RegexFlag): Flags passed to regex engine.
    """

    def __init__(
        self,
        whitelisted,  # type: Sequence[Text]
        match_substrings=False,  # type: bool
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):
        """Initialize :class:`retrie.trie.Trie` and set config."""
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
        """Return True if Pattern is found in term.

        Args:
            term (str): The string to search.
        """
        return self.is_listed(term)

    def filter(  # noqa:A003
        self,
        sequence,  # type: Sequence[Text]
    ):  # type: (...) -> Iterator[Text]
        """Construct an iterator from whitelisted elements of sequence.

        Args:
            sequence (Sequence): The sequence of strings to filter.
        """
        return filter(self.is_listed, sequence)

    def cleanse_text(
        self, term  # type: Text
    ):  # type: (...) -> Text
        """Return text, only keeping whitelisted terms.

        Args:
            term (str): The string to search.
        """
        return "".join(self.compiled.findall(term))


class Replacer(Checklist):
    """Replace occurrences of ``replacement_mapping.keys()`` with corresponding values.

    Note:
        Although the Trie is case-sensitive, by default :obj:`re.IGNORECASE` is used for better performance. Pass ``re_flags=None`` to perform case-sensitive replacements.

    Args:
        replacement_mapping (Mapping): Mapping ``{old: new}`` to replace.
        match_substrings (bool): Whether to override word_boundary with ``""``.
        word_boundary (str): Token to wrap the retrie to exclude certain matches.
        re_flags (re.RegexFlag): Flags passed to regex engine.
    """

    __slots__ = "replacement_mapping"

    def __init__(
        self,
        replacement_mapping,  # type: Mapping[Text, Text]
        match_substrings=False,  # type: bool
        word_boundary=WORD_BOUNDARY,  # type: Text
        re_flags=DEFAULT_FLAGS,  # type: re_flag_type
    ):
        """Initialize :class:`retrie.trie.Trie` and set config."""
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
            count (int): Amount of occurences to replace. If 0 or omitted, replace all.

        Returns:
            str: String with matches replaced.
        """
        return self.compiled.sub(self._replace, text, count=count)
