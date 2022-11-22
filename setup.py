import io
import os.path as path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

requirements_path = path.join(here, "requirements", "prod.txt")

readme_path = path.join(here, "README.md")


def read_requirements(path):
    try:
        with io.open(path, mode="rt", encoding="utf-8") as fp:
            return list(
                filter(bool, [line.split("#")[0].strip() for line in fp])  # noqa:C407
            )
    except IndexError:
        raise RuntimeError("{} is broken".format(path))


def read_readme(path):
    with io.open(path, mode="rt", encoding="utf-8") as fp:
        return fp.read()


setup(
    name="retrie",
    description="Efficient Trie-based regex unions for blacklist/whitelist filtering and one-pass mapping-based string replacing",
    long_description=read_readme(readme_path),
    long_description_content_type="text/markdown",
    setup_requires=[
        "setuptools_scm<6; python_version=='2.7'",
        "setuptools_scm<7; python_version>'2.7'",
    ],
    install_requires=read_requirements(requirements_path),
    use_scm_version={
        "version_scheme": "guess-next-dev",
        "local_scheme": "dirty-tag",
        "write_to": "src/retrie/_repo_version.py",
        "write_to_template": 'version = "{version}"\n',
        "relative_to": __file__,
    },
    include_package_data=True,
    package_data={},
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    author="ddelange",
    author_email="ddelange@delange.dev",
    url="https://github.com/ddelange/retrie",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="pure-Python regex trie regex-trie blacklist whitelist re search replace",
    license="MIT",
)
