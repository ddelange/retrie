from retrie.trie import Trie


def test_trie():
    trie = Trie()
    assert trie.pattern() == ""

    trie.add("abc", "foo", "abs")
    assert trie.pattern() == "(?:ab[cs]|foo)"

    trie.add("absolute")
    assert trie.pattern() == "(?:ab(?:c|s(?:olute)?)|foo)"

    trie.add("abx")
    assert trie.pattern() == "(?:ab(?:[cx]|s(?:olute)?)|foo)"

    trie.add("abxy")
    assert trie.pattern() == "(?:ab(?:c|s(?:olute)?|xy?)|foo)"

    trie.add("foe")
    assert trie.pattern() == "(?:ab(?:c|s(?:olute)?|xy?)|fo[eo])"

    trie.add("fo")
    assert trie.pattern() == "(?:ab(?:c|s(?:olute)?|xy?)|fo[eo]?)"

    trie = Trie()
    trie += Trie("abc")
    assert trie.pattern() == "abc"
    assert (
        trie + Trie().add("foo")
        == Trie("abc", "foo")
        == Trie(["abc", "foo"])
        == Trie().add(["abc", "foo"])
        == Trie().add("abc", "foo")
        == Trie().add("abc").add("foo")
    )
