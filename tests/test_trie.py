import pytest

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
        == Trie("abc") + Trie("foo")
        == Trie("foo") + Trie("abc")
        == Trie(*["abc", "foo"])
        == Trie().add(*["abc", "foo"])
        == Trie().add("abc", "foo")
        == Trie().add("abc").add("foo")
    )
    assert trie != object
    with pytest.raises(TypeError):
        trie += None

    assert Trie() + Trie() == Trie()
    assert Trie("a", "b", "c").pattern() == "[abc]"
    assert Trie("abs") + Trie("absolute") != Trie("absolute")

    trie1, trie2 = Trie(), Trie("abc")
    trie1 += trie2
    assert trie1.data["a"] is not trie2.data["a"]
    trie2.data["a"]["b"] = {"s": {"": {}}}
    assert trie1 != trie2
