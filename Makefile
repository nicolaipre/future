VENV=".venv"
ENV_FILE='.env'
SOURCE_FILES="future"
VERSION_FILE="${SOURCE_FILES}/__init__.py"
SEMVER_REGEX="([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?"
CHANGELOG_VERSION=$(shell grep -o -E ${SEMVER_REGEX} docs/release-notes.md | head -1)
SOURCE_VERSION=$(shell grep -o -E ${SEMVER_REGEX} ${VERSION_FILE} | head -1)

.PHONY: info

test:
	curl api.example.com:8000/whatever/9/asd

dev:
	poetry run uvicorn example:app --reload

prod:
	poetry run uvicorn example:app

info:
	@echo "Makefile for Future"

clean:
	rm -rf *.egg-info build dist .pytest_cache __pycache__

docs:
	poetry run mkdocs serve

install:
	python3 -m pip install --upgrade pip
	python3 -m pip install poetry
	poetry install
	#poetry shell

sync:
	@if [ "${CHANGELOG_VERSION}" != "${SOURCE_VERSION}" ]; then \
		echo "Version in changelog does not match version in future/__init__.py!"; \
		exit 1; \
	fi

lint:
	poetry run ruff format future
	poetry run ruff check --fix future

check:
	#make sync
	poetry run ruff format --check --diff ${SOURCE_FILES}
	poetry run ruff check ${SOURCE_FILES}
	poetry run mypy future
	poetry run mypy tests --disable-error-code no-untyped-def --disable-error-code no-untyped-call

coverage:
	poetry run coverage report --show-missing --skip-covered --fail-under=20

build:
	poetry run python -m build
	poetry run twine check dist/*
	#poetry run mkdocs build

publish:
	if [ ! -z "${GITHUB_ACTIONS}" ]; then
		git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
		git config --local user.name "GitHub Action"

		VERSION=`grep __version__ ${VERSION_FILE} | grep -o '[0-9][^"]*'`

		if [ "refs/tags/${VERSION}" != "${GITHUB_REF}" ] ; then
			echo "GitHub Ref '${GITHUB_REF}' did not match package version '${VERSION}'"
			exit 1
		fi
	fi

	# https://python-poetry.org/docs/repositories/#publishable-repositories
	# python3 setup/setup.py sdist bdist_wheel
	# python3 -m twine upload dist/* --non-interactive
	# python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/* --non-interactive --verbose
	poetry run twine upload dist/*
	poetry run mkdocs gh-deploy --force

test:
	@if [ -z ${GITHUB_ACTIONS} ]; then \
		make check; \
	fi;	

	# pytest . -p no:logging -p no:warnings
	poetry run coverage run -m pytest tests

	@if [ -z ${GITHUB_ACTIONS} ]; then \
		make coverage; \
	fi;

leave:
	exit
