from __future__ import annotations

from git import Repo
from pydantic import TypeAdapter, ValidationError
from pygit2 import Repository
from rich.text import Text

from ...interfaces import DiffConfig
from ..io import FugitConsole, fugit_console
from .gitpython import DiffInfoGP, count_match, get_diff
from .pygit2 import DiffInfoPG2

__all__ = ("diff", "load_diff", "highlight_diff", "process_diff")

STORE_DIFFS = False


def diff(**config) -> list[str]:
    """Narrow the input type to DiffConfig type for `load_diff`."""
    return load_diff(DiffConfig.model_validate(config))


def load_diff(config: DiffConfig) -> list[str]:
    # """Have to use GitPython as pygit2 cached diffs don't work"""
    # return load_diff_gitpython(config)
    """Try to get pygit2 cached diffs to work"""
    return load_diff_pygit2(config) if config.pygit2 else load_diff_gitpython(config)


def process_diff(
    console: FugitConsole,
    diff_info: DiffInfoGP | DiffInfoPG2,
    diffs: list[str],
    config: DiffConfig,
) -> None:
    ...
    if diff_info.change_type in config.change_type:
        filtrate = diff_info.text
        if STORE_DIFFS:
            diffs.append(filtrate)
        console.submit(Text(diff_info.overview, style="bold yellow underline"))
        # This simulates the render process (`Console.render_str`)
        console.submit(*highlight_diff(filtrate))
        console.file_count += 1


def load_diff_pygit2(config: DiffConfig) -> list[str]:
    """
    Note: You can either implement commit tree-based diffs (with no 'R' kwarg reversal
    weirdness) or get it from a string at runtime (more configurable so we do that).
    """
    repo = Repository(config.repo)
    tree = config.revision
    repo_diff_patch = repo.diff(tree, cached=True)
    diffs: list[str] = []
    with fugit_console.pager_available() as console:
        ta = TypeAdapter(list[DiffInfoPG2])
        for diff_info in ta.validate_python(repo_diff_patch, from_attributes=True):
            process_diff(
                console=console,
                diff_info=diff_info,
                diffs=diffs,
                config=config,
            )
            del diff_info
    return diffs


def load_diff_gitpython(config: DiffConfig) -> list[str]:
    """
    Note: You can either implement commit tree-based diffs (with no 'R' kwarg reversal
    weirdness) or get it from a string at runtime (more configurable so we do that).
    For reference, you would do it like this rather than ``config.revision``:

      >>> tree = repo.head.commit.tree
    """
    repo = Repo(config.repo, search_parent_directories=True)
    index = repo.index
    tree = config.revision
    file_diff_patch = get_diff(index, tree, create_patch=True)
    file_diff_info = get_diff(index, tree, create_patch=False)
    count_match(file_diff_patch, file_diff_info)
    diffs: list[str] = []
    with fugit_console.pager_available() as console:
        for patch, info in zip(file_diff_patch, file_diff_info):
            try:
                diff_info = DiffInfoGP.from_tree_pair(patch=patch, info=info)
            except ValidationError:
                raise  # TODO: make a nicer custom error and exit
            process_diff(
                console=console,
                diff_info=diff_info,
                diffs=diffs,
                config=config,
            )
            del diff_info
    return diffs


def highlight_diff(diff: str) -> list[Text]:
    """This replaces the highlighter applied by `Console.render_markup`."""
    # TODO express this as a Rich highlighter class
    highlight_patterns = {
        "removed": (r"^\+.*", "green"),
        "added": (r"^-.*", "red"),
        "hunk_context": (r"^@@.*", "bold white"),  # applied first (whole line)
        "hunk_header": (r"^@@.*?@@ ", "blue"),  # applied second (only inside @ signs)
    }
    diff_lines = []
    for line in diff.splitlines(keepends=True):
        diff_line = Text(line, style="white")
        for pattern, style in highlight_patterns.values():
            diff_line.highlight_regex(pattern, style=style)
        diff_lines.append(diff_line)
    return diff_lines
