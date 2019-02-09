.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

ci: dist install develop test docs

dist: clean ## builds source and wheel package
	poetry build
	ls -l dist

install:
	pip install -U dist/*.whl

develop:  ## create virtualenv and install dependencies
	poetry install

test: ## run tests quickly with the default Python
	poetry run pytest

test-all: clean tox docs ## test every Python version with tox

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts
	rm -fr .tox/

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/

tox:
	poetry run tox --skip-missing-interpreters

docs: ## generate Sphinx HTML documentation
	poetry run $(MAKE) -C docs clean
	poetry run $(MAKE) -C docs html

release: ## package and upload a release
	poetry publish
