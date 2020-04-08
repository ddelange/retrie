from retrie.retrie import Blacklist, Replacer, Retrie, Whitelist


def test_Retrie():
    retrie = Retrie()
    for term in ["abc", "foo", "abs"]:
        retrie.trie.add(term)

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


def test_Blacklist():
    blacklist = Blacklist(["abc", "foo", "abs"], match_substrings=False)
    assert not blacklist.is_blacklisted("a foobar")
    assert tuple(blacklist.filter(("good", "abc", "foobar"))) == ("good", "foobar")
    assert blacklist.cleanse_text(("good abc foobar")) == "good  foobar"

    blacklist = Blacklist(["abc", "foo", "abs"], match_substrings=True)
    assert blacklist.is_blacklisted("a foobar")
    assert tuple(blacklist.filter(("good", "abc", "foobar"))) == ("good",)
    assert blacklist.cleanse_text(("good abc foobar")) == "good  bar"


def test_Whitelist():
    whitelist = Whitelist(["abc", "foo", "abs"], match_substrings=False)
    assert not whitelist.is_whitelisted("a foobar")
    assert tuple(whitelist.filter(("bad", "abc", "foobar"))) == ("abc",)
    assert whitelist.cleanse_text(("good abc foobar")) == "abc"

    whitelist = Whitelist(["abc", "foo", "abs"], match_substrings=True)
    assert whitelist.is_whitelisted("a foobar")
    assert tuple(whitelist.filter(("bad", "abc", "foobar"))) == ("abc", "foobar")
    assert whitelist.cleanse_text(("good abc foobar")) == "abcfoo"


def test_Replacer():
    replacer = Replacer(
        dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"])),
        match_substrings=True,
    )
    assert replacer.replace("ABS ...foo... foobar") == "new3 ...new2... new2bar"

    replacer = Replacer(
        dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"])),
        match_substrings=False,
    )
    assert replacer.replace("ABS ...foo... foobar") == "new3 ...new2... foobar"

    replacer = Replacer(
        dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"])),
        match_substrings=False,
        re_flags=None,
    )
    assert replacer.replace("ABS ...foo... foobar") == "ABS ...new2... foobar"

    replacer = Replacer(
        dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"])),
        match_substrings=False,
        word_boundary=" ",
    )
    assert replacer.replace(". ABS ...foo... foobar") == ". new3 ...foo... foobar"
