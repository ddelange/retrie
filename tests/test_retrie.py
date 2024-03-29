import pytest

from retrie.retrie import Blacklist, Replacer, Retrie, Whitelist


def test_retrie():
    retrie = Retrie()
    retrie.trie.add("abc", "foo", "abs")

    assert retrie.pattern() == "(?:ab[cs]|foo)"

    match = retrie.compile(word_boundary="").match("foobar")
    assert match.group(0) == "foo"

    match = retrie.compile(word_boundary="").match("afoobar")
    assert match is None

    match = retrie.compile(word_boundary="").search("afoobar")
    assert match.group(0) == "foo"

    match = retrie.compile(word_boundary="", re_flags=None).search("a fOObar")
    assert match is None

    match = retrie.compile(word_boundary=r"\b").search("a foobar")
    assert match is None

    match = retrie.compile(word_boundary=r"\b").search("a foo bar")
    assert match.group(0) == "foo"

    retrie.trie.add("absolute")

    match = retrie.compile(word_boundary=r"\b").search("abs ")
    assert match.group(0) == "abs"

    match = retrie.compile(word_boundary=r"\b").search("abso absolute")
    assert match.group(0) == "absolute"

    retrie.trie.add("abcy")

    match = retrie.compile(word_boundary=r"\b").search("abc")
    assert match.group(0) == "abc"

    match = retrie.compile(word_boundary="").search("abcyz")
    assert match.group(0) == "abcy"


def test_blacklist():
    blacklist = Blacklist(["abc", "foo", "abs"], match_substrings=False)
    assert not blacklist.is_blacklisted("a foobar")
    assert tuple(blacklist.filter(("good", "abc", "foobar"))) == ("good", "foobar")
    assert blacklist.cleanse_text(("good abc foobar")) == "good  foobar"

    blacklist = Blacklist(["abc", "foo", "abs"], match_substrings=True)
    assert blacklist.is_blacklisted("a foobar")
    assert tuple(blacklist.filter(("good", "abc", "foobar"))) == ("good",)
    assert blacklist.cleanse_text(("good abc foobar")) == "good  bar"


def test_whitelist():
    whitelist = Whitelist(["abc", "foo", "abs"], match_substrings=False)
    assert not whitelist.is_whitelisted("a foobar")
    assert tuple(whitelist.filter(("bad", "abc", "foobar"))) == ("abc",)
    assert whitelist.cleanse_text(("bad abc foobar")) == "abc"

    whitelist = Whitelist(["abc", "foo", "abs"], match_substrings=True)
    assert whitelist.is_whitelisted("a foobar")
    assert tuple(whitelist.filter(("bad", "abc", "foobar"))) == ("abc", "foobar")
    assert whitelist.cleanse_text(("bad abc foobar")) == "abcfoo"


def test_replacer():
    replacement_mapping = dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"]))

    replacer = Replacer(replacement_mapping, match_substrings=True)
    assert replacer.replace("ABS ...foo... foobar") == "new3 ...new2... new2bar"

    replacer = Replacer(replacement_mapping, match_substrings=False)
    assert replacer.replace("ABS ...foo... foobar") == "new3 ...new2... foobar"

    replacer = Replacer(replacement_mapping, match_substrings=False, re_flags=None)
    assert replacer.replace("ABS ...foo... foobar") == "ABS ...new2... foobar"

    replacer = Replacer(replacement_mapping, match_substrings=False, word_boundary=" ")
    assert replacer.replace(". ABS ...foo... foobar") == ". new3 ...foo... foobar"


def test__lower_keys():
    replacement_mapping = {"x": 0, "X": 1}

    with pytest.raises(ValueError, match="Ambiguous replacement_mapping") as excinfo:
        Replacer(replacement_mapping)  # re.IGNORECASE enabled by default
    assert (
        str(excinfo.value)
        == "Ambiguous replacement_mapping: converting keys to lowercase yields duplicate keys"
    )
