from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from git import Repo
from line_profiler import profile
from pydantic import AfterValidator, TypeAdapter, ValidationError
from pygit2 import Repository

from ...interfaces import DiffConfig
from ..io import FugitConsole, fugit_console
from ..text.bases import SpannedText, Style
from ..text.palette import (
    BoldYellow_Text,
    GreenText,
    RedText,
    SimpleLine,
)
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


@profile
def process_diff(
    console: FugitConsole,
    diff_info: DiffInfoGP | DiffInfoPG2,
    diffs: list[str],
    config: DiffConfig,
) -> None:
    ...
    filtrated = diff_info.text
    if STORE_DIFFS:
        diffs.append(filtrated)
    header = diff_info.overview if config.plain else BoldYellow_Text(diff_info.overview)
    # This simulates the render process (`Console.render_str`)
    if config.plain:
        highlighted = filtrated.splitlines(keepends=True)
    else:
        highlighted = highlight_diff(filtrated)
    console.submit(header, *highlighted)
    console.file_count += 1
    return


highlight_patterns = {
    "hunk_context": (r"^@@.*", Style.W),  # applied first (whole line)
    "hunk_header": (r"^@@.*?@@ ", Style.b),  # applied second (only inside @ signs)
}


@profile
def highlight_diff(diff: str) -> list[SimpleLine, SpannedText]:
    """This replaces the highlighter applied by `Console.render_markup`."""
    diff_lines = []
    for line in diff.splitlines(keepends=True):
        match initial_char := line[0]:
            case "+":
                diff_lines.append(GreenText(line))
                continue
            case "-":
                diff_lines.append(RedText(line))
                continue
            case _:
                diff_line = SpannedText(line=line)
                match initial_char:
                    case "@":
                        diff_line.highlight_regex(list(highlight_patterns.values()))
                diff_lines.append(diff_line)
    return diff_lines


@dataclass
class ChangeTypeChecker:
    change_types: list[str]

    def check(self, diff: DiffInfoPG2) -> DiffInfoPG2 | None:
        return diff if (diff.change_type in self.change_types) else None


def load_diff_pygit2(config: DiffConfig) -> list[str]:
    """
    Note: You can either implement commit tree-based diffs (with no 'R' kwarg reversal
    weirdness) or get it from a string at runtime (more configurable so we do that).
    """
    repo = Repository(config.repo)
    tree = config.revision
    repo_diff_patch = repo.diff(tree, cached=True)
    diffs: list[str] = []
    with fugit_console.pager() as console:
        ct_checker = ChangeTypeChecker(change_types=config.change_type)
        ct_validator = AfterValidator(ct_checker.check)
        ct_gate = Annotated[DiffInfoPG2, ct_validator]
        ta = TypeAdapter(list[ct_gate | None])
        validated_diffs = ta.validate_python(repo_diff_patch, from_attributes=True)
        for diff_info in filter(None, validated_diffs):
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
    with fugit_console.pager() as console:
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
