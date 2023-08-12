SHELL := /bin/bash

.PHONY: lint
## Run linting
lint:
	pre-commit run --all-files

.PHONY: test
## Run tests
test:
	python -m pytest tests/

.PHONY: showcov
## Open the test coverage overview using the default HTML viewer
showcov:
	xdg-open htmlcov/index.html || open htmlcov/index.html

.PHONY: install
## Install this repo, plus dev requirements, in editable mode
install:
	pip install -r requirements/ci.txt -r requirements/docs.txt -e .
	pre-commit install || true  # not installed on older python versions

.PHONY: builddocs
## Build documentation using Sphinx
builddocs:
	cd docs && make docs

.PHONY: showdocs
## Open the docs using the default HTML viewer
showdocs:
	xdg-open docs/_build/html/index.html || open docs/_build/html/index.html

.DEFAULT_GOAL := help
.PHONY: help
## Print Makefile documentation
help:
	@perl -0 -nle 'printf("\033[36m  %-15s\033[0m %s\n", "$$2", "$$1") while m/^##\s*([^\r\n]+)\n^([\w.-]+):[^=]/gm' $(MAKEFILE_LIST) | sort
