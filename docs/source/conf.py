# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import inspect
import sys
from pathlib import Path

from sphinx.ext import apidoc

from retrie import __version__

current_dir = Path(__file__).parent.absolute()
base_dir = current_dir.parents[1]
code_dir = base_dir / "src"

sys.path.insert(0, str(code_dir))

readme_dest = current_dir / "README.md"
readme_src = base_dir / "README.md"

if readme_dest.exists():
    readme_dest.unlink()
readme_dest.symlink_to(readme_src)

# -- Project information -----------------------------------------------------

project = "retrie"
project_url = "https://github.com/ddelange/retrie"
author = "ddelange"
copyright = "2020, ddelange"  # noqa:A001

# The full version, including alpha/beta/rc tags
release = __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "recommonmark",
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.linkcode",
    "sphinx.ext.intersphinx",
]
autodoc_typehints = "description"

# recommonmark extension allows mixed filetypes
source_suffix = [".rst", ".md"]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]


# -- Options for sphinx.ext.autodoc ------------------------------------------


def run_apidoc(_):
    exclude = []

    argv = [
        "--doc-project",
        "Code Reference",
        "-M",
        "-f",
        "-d",
        "3",
        "--tocfile",
        "index",
        "-o",
        str(current_dir / "_code_reference"),
        str(code_dir),
    ] + exclude

    apidoc.main(argv)


def setup(app):
    app.connect("builder-inited", run_apidoc)


# -- Options for sphinx.ext.linkcode: [source] links -------------------------


def linkcode_resolve(  # noqa:CCR001
    domain,
    info,
    blob_url=f'{project_url.rstrip("/")}/blob',
    default_branch="master",  # branch used for untagged 'latest' builds on readthedocs
    tag_prefix="",  # could be for instance "v" depending on tagging convention
):
    """Determine a GitHub permalink (with line numbers) for a Python object. Adapted from https://github.com/numpy/numpy/blob/v1.19.4/doc/source/conf.py."""
    if domain != "py":
        return None

    modname = info["module"]
    fullname = info["fullname"]

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except Exception:
            return None

    # strip decorators, which would resolve to the source of the decorator
    # possibly an upstream bug in getsourcefile, bpo-1764286
    obj = inspect.unwrap(obj)

    try:
        sourcefile = inspect.getsourcefile(obj)
    except Exception:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except Exception:
        linespec = ""
    else:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"

    try:
        # editable install
        relsourcefile = Path(sourcefile).relative_to(base_dir)
    except ValueError as exc:
        # site-packages
        if "site-packages/" not in sourcefile:
            raise RuntimeError(
                "Expected a pip install -e, or install to site-packages"
            ) from exc

        relsourcefile = (code_dir / sourcefile.split("site-packages/")[-1]).relative_to(
            base_dir
        )

    if "dev" in release:
        # setuptools_scm (setup.py) appends a dev identifier to __version__ if there are
        # commits since last tag. For readthedocs, this is only the case when building
        # 'latest' that is newer than 'stable', for which the default_branch is assumed.
        return f"{blob_url}/{default_branch}/{relsourcefile}{linespec}"
    else:
        return f"{blob_url}/{tag_prefix}{release}/{relsourcefile}{linespec}"


# -- Options for sphinx.ext.intersphinx --------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
