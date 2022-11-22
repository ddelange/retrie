# retrie

[![build](https://img.shields.io/github/workflow/status/ddelange/retrie/GH/master?logo=github&cacheSeconds=86400)](https://github.com/ddelange/retrie/actions?query=branch%3Amaster)
[![codecov](https://img.shields.io/codecov/c/github/ddelange/retrie/master?logo=codecov&logoColor=white)](https://codecov.io/gh/ddelange/retrie)
[![pypi Version](https://img.shields.io/pypi/v/retrie.svg?logo=pypi&logoColor=white)](https://pypi.org/project/retrie/)
[![python](https://img.shields.io/pypi/pyversions/retrie.svg?logo=python&logoColor=white)](https://pypi.org/project/retrie/)
[![downloads](https://pepy.tech/badge/retrie)](https://pypistats.org/packages/retrie)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)


[retrie](https://github.com/ddelange/retrie) offers fast methods to match and replace (sequences of) strings based on efficient Trie-based regex unions.

#### Trie

Instead of matching against a simple regex union, which becomes slow for large sets of words, a more efficient regex pattern can be compiled using a [Trie](https://en.wikipedia.org/wiki/Trie) structure:

```py
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
```


## Installation

This pure-Python, OS independent package is available on [PyPI](https://pypi.org/project/retrie):

```sh
$ pip install retrie
```


## Usage

[![readthedocs](https://readthedocs.org/projects/retrie/badge/?version=latest)](https://retrie.readthedocs.io)

For documentation, see [retrie.readthedocs.io](https://retrie.readthedocs.io/en/stable/_code_reference/retrie.html).

The following objects are all subclasses of `retrie.retrie.Retrie`, which handles filling the Trie and compiling the corresponding regex pattern.


#### Blacklist

The `Blacklist` object can be used to filter out bad occurences in a text or a sequence of strings:
```py
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
```


#### Whitelist

Similar methods are available for the `Whitelist` object:
```py
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
```


#### Replacer

The `Replacer` object does a fast single-pass search & replace for occurrences of `replacement_mapping.keys()` with corresponding values.
```py
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
```


## Development

[![gitmoji](https://img.shields.io/badge/gitmoji-%20%F0%9F%98%9C%20%F0%9F%98%8D-ffdd67)](https://github.com/carloscuesta/gitmoji-cli)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Run `make help` for options like installing for development, linting and testing.
