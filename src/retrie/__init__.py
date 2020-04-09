try:
    from functools import cached_property  # type: ignore
except ImportError:  # pragma: no cover
    from cached_property import cached_property  # noqa:F401

# version based on .git/refs/tags - make a tag/release locally, or on GitHub (and pull)
from . import _repo_version  # noqa:ABS101

__version__ = _repo_version.version  # noqa:F401
