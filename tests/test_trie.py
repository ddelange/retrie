from retrie.trie import Trie


def test_Trie():
    trie = Trie()
    assert trie.pattern() == ""

    for term in ["abc", "foo", "abs"]:
        trie.add(term)
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
