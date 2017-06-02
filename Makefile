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

devel: devreq ## prepare development environment
	pip install -e .

devreq:
	pip install -r requirements_dev.txt

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

release: ## package and upload a release
	twine upload dist/*

dist: clean-build clean-pyc clean-test ## builds source and wheel package
	python setup.py sdist bdist_wheel
	ls -l dist

install: ## install the package to the active Python's site-packages
	pip install -U dist/*.whl

test: ## run tests quickly with the default Python
	cd tests && python -m coverage run -p --source=morelia,. --branch -m unittest discover .

coverage:  ## prepare coverage report
	python -m coverage combine tests
	python -m coverage report -m --skip-covered
	python -m coverage xml

htmlcov:  ## prepare coverage report
	python -m coverage combine tests
	python -m coverage html

lint: ## run static analysis with flake8
	flake8 morelia tests

docs: ## generate Sphinx HTML documentation
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

ci: dist devreq install test coverage lint docs ## run CI pipeline

tox:
	tox --skip-missing-interpreters

tox-ci: dist tox coverage lint docs ## run CI with tox testing every python version
