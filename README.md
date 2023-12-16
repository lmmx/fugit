<div align="center">

# fugit

<img src="https://github.com/lmmx/fugit/raw/master/docs/assets/images/hero.png" alt="Fugit Logo" width=300></img>

[![PyPI](https://img.shields.io/pypi/v/fugit?logo=python&logoColor=%23cccccc)](https://pypi.org/project/fugit)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lmmx/fugit/master.svg)](https://results.pre-commit.ci/latest/github/lmmx/fugit/master)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/fugit.svg)](https://pypi.org/project/fugit)
[![license](https://img.shields.io/github/license/lmmx/fugit.svg)](https://github.com/lmmx/fugit/blob/main/LICENSE)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![Documentation](https://readthedocs.org/projects/fugit/badge/?version=latest)](https://fugit.readthedocs.io/en/latest/?version=latest)

### Git diff handling in Python

</div>

> _sed fugit interea fugit irreparabile tempus_

(“meanwhile, the irreplaceable time escapes”)

## Motivation

Accessing structured diffs in a Git repository remains challenging, even with tools like GitPython.
This issue is especially pronounced when dealing with large diff sets, such as those generated
during transitions between linters (e.g., from Black to Ruff). Currently, without a straightforward
programmatic solution, understanding the essence of these diffs requires cumbersome manual effort.

Before writing this library I explored fast parsing approaches (Pydantic's integration with Rust's regex
crate in particular) and reviewed GitPython internals, as well as its pitfalls.

_fugit_ simplifies access to git diffs, and will help you avoid the covert hazards in GitPython's API.

## Installation

```py
pip install fugit
```

## Usage

Use fugit on the command line as a replacement to `git diff`:

```sh
fugit
```

```
usage: fugit [-h] [--repo REPO] [--revision REVISION] [-c [CHANGE_TYPE ...]]
             [-q] [--version]

Configure input filtering and output display.

options:
  -h, --help            show this help message and exit
  --repo REPO           The repo whose git diff is to be computed.
                        (default: .)
  --revision REVISION   Specify the commit for comparison with the index. Use "HEAD" to
                        refer to the latest branch commit, or "HEAD~{$n}" (e.g. "HEAD~1")
                        to indicate a specific number of commits before the latest.
                        (default: HEAD)
  -c [CHANGE_TYPE ...], --change-type [CHANGE_TYPE ...]
                        Change types to filter diffs for.
                        (default: ['A', 'C', 'D', 'M', 'R', 'T', 'U', 'X', 'B'])
  -q, --quiet           (default: False)
  --version             show program's version number and exit
```

Or the Python interface:

```py
from fugit import diff

diff(repo="/path/to/your/repo", quiet=True)
```

## Development

- To set up pre-commit hooks (to keep the CI bot happy) run `pre-commit install-hooks` so all git
  commits trigger the pre-commit checks. I use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
  This runs `black`, `flake8`, `autopep8`, `pyupgrade`, etc.

- To set up a dev env, I first create a new conda environment and use it in PDM with `which python > .pdm-python`.
  To use `virtualenv` environment instead of conda, skip that. Run `pdm install` and a `.venv` will be created if no
  Python binary path is found in `.pdm-python`.

- To run tests, run `pdm run python -m pytest` and the PDM environment will be used to run the test suite.
