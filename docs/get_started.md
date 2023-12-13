---
title: Get Started
icon: material/human-greeting
---

# Getting started

## 1. Installation

Fugit is available on PyPi:

```bash
pip install fugit
```


!!! info "Git dependency"

    You must have git installed to use fugit.


## 2. Usage

You can use fugit on the command line:

=== "Code"

    ```bash
    fugit -h
    ```

=== "Output"

    ```bash
    usage: fugit [-h] [--repo REPO] [--revision REVISION] [-c [CHANGE_TYPE ...]]
                 [--version]

    Configure input filtering and output display.

    options:
      -h, --help            show this help message and exit
      --repo REPO           The repo whose git diff is to be computed.
                            (default: .)
      --revision REVISION   Specify the commit for comparison with the index. Use "HEAD" to
                            refer tot he latest branch commit, or "HEAD~{$n}" (e.g. "HEAD~1")
                            to indicate a specific number of commits before the latest.
                            (default: HEAD)
      -c [CHANGE_TYPE ...], --change-type [CHANGE_TYPE ...]
                            Change types to filter diffs for.
                            (default: ['A', 'C', 'D', 'M', 'R', 'T', 'U', 'X', 'B'])
      --version             show program's version number and exit
    ```

When run, fugit does the following approach:

1. Uses GitPython to access the diff info
2. Parses as needed into Pydantic models

## 3. Local development

- To set up pre-commit hooks (to keep the CI bot happy) run `pre-commit install-hooks` so all git
  commits trigger the pre-commit checks. I use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
  This runs `black`, `flake8`, `autopep8`, `pyupgrade`, etc.

- To set up a dev env, I first create a new conda environment and use it in PDM with `which python > .pdm-python`.
  To use `virtualenv` environment instead of conda, skip that. Run `pdm install` and a `.venv` will be created if no
  Python binary path is found in `.pdm-python`.

- To run tests, run `pdm run python -m pytest` and the PDM environment will be used to run the test suite.

## 4. Acknowledgements

Fugit was developed by [@permutans](https://twitter.com/permutans).
