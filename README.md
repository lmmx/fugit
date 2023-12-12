# fugit

[![PyPI](https://img.shields.io/pypi/v/fugit?logo=python&logoColor=%23cccccc)](https://pypi.org/project/fugit)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lmmx/fugit/master.svg)](https://results.pre-commit.ci/latest/github/lmmx/fugit/master)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/fugit.svg)](https://pypi.org/project/fugit)

<!-- [![build status](https://github.com/lmmx/fugit/actions/workflows/master.yml/badge.svg)](https://github.com/lmmx/fugit/actions/workflows/master.yml) -->

Git diff handling in Python.

## Motivation

> _sed fugit interea fugit irreparabile tempus_ (“meanwhile, the irreplaceable time escapes”

Despite the existence of GitPython, it remains awkward to access structured diffs for a given repo.
This is particularly desirable for large diff sets, such as those created when migrating between
linters (such as Black to Ruff, as motivated this library). In such cases it's desirable to be able
to see clearly what the actual substance of the set of diffs is, but without programmatic means to
access this set simply it becomes a manual effort (with each reader re-duplicating others' efforts
or else just skipping the task and not making an informed decision).

Before writing this library I investigated fast parsing approaches (Pydantic with Rust's regex
crate in particular) and reviewed the internals of GitPython, as well as its API for accessing diffs.

The goal of this library is to make this specific facet of git easy to work with.

## Installation

```py
pip install fugit
```

## Usage

Expected interface:

```py
from fugit import diff

diff = diff(repo_path="/path/to/your/repo")
```

## Development

- To set up pre-commit hooks (to keep the CI bot happy) run `pre-commit install-hooks` so all git
  commits trigger the pre-commit checks. I use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
  This runs `black`, `flake8`, `autopep8`, `pyupgrade`, etc.

- To set up a dev env, I first create a new conda environment and use it in PDM with `which python > .pdm-python`.
  To use `virtualenv` environment instead of conda, skip that. Run `pdm install` and a `.venv` will be created if no
  Python binary path is found in `.pdm-python`.

- To run tests, run `pdm run python -m pytest` and the PDM environment will be used to run the test suite.
