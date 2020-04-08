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

assert trie.pattern() == ""

for term in ["abc", "foo", "abs"]:
    trie.add(term)
assert trie.pattern() == "(?:ab[cs]|foo)"  # equivalent to but faster than "(?:abc|abs|foo)"

trie.add("absolute")
assert trie.pattern() == "(?:ab(?:c|s(?:olute))|foo)"

trie.add("abx")
assert trie.pattern() == "(?:ab(?:[cx]|s(?:olute))|foo)"

trie.add("abxy")
assert trie.pattern() == "(?:ab(?:c|s(?:olute)|xy?)|foo)"
```


## Installation

This pure-Python, OS independent package is available on [PyPI](https://pypi.org/project/retrie):

```sh
$ pip install retrie
```


## Usage

The following objects are all subclasses of [`retrie.retrie.Retrie`](src/retrie/retrie.py), which handles filling the Trie and compiling the corresponding regex pattern.


#### Blacklist

The `Blacklist` object can be used to filter out bad occurences in a test or a sequenxce of strings:
```py
from retrie.retrie import Blacklist

blacklist = Blacklist(["abc", "foo", "abs"], match_substrings=False)
blacklist.compiled  # re.compile(r'(?<=\b)(?:ab[cs]|foo)(?=\b)', re.IGNORECASE|re.UNICODE)

assert not blacklist.is_blacklisted("a foobar")
assert tuple(blacklist.filter(("good", "abc", "foobar"))) == ("good", "foobar")
assert blacklist.cleanse_text(("good abc foobar")) == "good  foobar"

blacklist = Blacklist(["abc", "foo", "abs"], match_substrings=True)
blacklist.compiled  # re.compile(r'(?:ab[cs]|foo)', re.IGNORECASE|re.UNICODE)

assert blacklist.is_blacklisted("a foobar")
assert tuple(blacklist.filter(("good", "abc", "foobar"))) == ("good",)
assert blacklist.cleanse_text(("good abc foobar")) == "good  bar"
```


#### Whitelist

Similar methods are available for the `Whitelist` object:
```py
from retrie.retrie import Whitelist

whitelist = Whitelist(["abc", "foo", "abs"], match_substrings=False)
whitelist.compiled  # re.compile(r'(?<=\b)(?:ab[cs]|foo)(?=\b)', re.IGNORECASE|re.UNICODE)

assert not whitelist.is_whitelisted("a foobar")
assert tuple(whitelist.filter(("bad", "abc", "foobar"))) == ("abc",)
assert whitelist.cleanse_text(("good abc foobar")) == "abc"

whitelist = Whitelist(["abc", "foo", "abs"], match_substrings=True)
whitelist.compiled  # re.compile(r'(?:ab[cs]|foo)', re.IGNORECASE|re.UNICODE)

assert whitelist.is_whitelisted("a foobar")
assert tuple(whitelist.filter(("bad", "abc", "foobar"))) == ("abc", "foobar")
assert whitelist.cleanse_text(("good abc foobar")) == "abcfoo"
```


#### Replacer

The `Replacer` object can search & replace occurrences of `replacement_mapping.keys()` with corresponding values.
```py
from retrie.retrie import Replacer

replacer = Replacer(
    replacement_mapping=dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"])),
    match_substrings=True,
)
replacer.compiled  # re.compile(r'(?:ab[cs]|foo)', re.IGNORECASE|re.UNICODE)
assert replacer.replace("ABS ...foo... foobar") == "new3 ...new2... new2bar"

replacer = Replacer(
    replacement_mapping=dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"])),
    match_substrings=False,
)
assert replacer.replace("ABS ...foo... foobar") == "new3 ...new2... foobar"

replacer = Replacer(
    replacement_mapping=dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"])),
    match_substrings=False,
    re_flags=None,
)
assert replacer.replace("ABS ...foo... foobar") == "ABS ...new2... foobar"

replacer = Replacer(
    replacement_mapping=dict(zip(["abc", "foo", "abs"], ["new1", "new2", "new3"])),
    match_substrings=False,
    word_boundary=" ",
)
assert replacer.replace(". ABS ...foo... foobar") == ". new3 ...foo... foobar"
```


## Development

[![gitmoji](https://img.shields.io/badge/gitmoji-%20%F0%9F%98%9C%20%F0%9F%98%8D-ffdd67)](https://github.com/carloscuesta/gitmoji-cli)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Create a virtual environment.

```sh
python -m venv .venv
source .venv/bin/activate
```

Get ready to develop:

```sh
make install
```

This is equivalent to the following steps:

- Install pre-commit and other continous integration dependencies in order to make commits and run tests.
    ```sh
    pip install -r requirements/ci.txt
    pre-commit install
    ```

- With requirements installed, `make lint` and `make test` can now be run. There is also `make clean`, and `make all` which runs all three.

- To import the package in the python environment, install the package (`-e` for editable installation, upon import, python will read directly from the repository).
    ```sh
    pip install -e .
    ```
