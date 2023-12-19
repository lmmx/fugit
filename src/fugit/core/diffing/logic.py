from __future__ import annotations

from git import Repo
from pydantic import (
    ValidationError,
)
from rich.text import Text

from ...interfaces import DiffConfig
from ..io import fugit_console
from .gitpython import DiffInfo, count_match, discard_diff_type, get_diff

__all__ = ("diff", "load_diff", "highlight_diff")


def diff(**config) -> list[str]:
    """Narrow the input type to DiffConfig type for `load_diff`."""
    return load_diff(DiffConfig.model_validate(config))


def load_diff(config: DiffConfig) -> list[str]:
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
                diff_info = DiffInfo.from_tree_pair(patch=patch, info=info)
            except ValidationError:
                raise  # TODO: make a nicer custom error and exit
            if discard_diff_type(diff_info=diff_info, config=config):
                continue
            filtrate = diff_info.text
            diffs.append(filtrate)
            console.print(diff_info.overview, style="bold yellow underline")
            # This simulates the render process (`Console.render_str`)
            rendered_filtrate = highlight_diff(filtrate)
            console.print(rendered_filtrate)
            console.file_count += 1
            del diff_info
    return diffs


def highlight_diff(diff: str) -> None:
    """This replaces the highlighter applied by `Console.render_markup`."""
    # TODO express this as a Rich highlighter class
    highlight_patterns = {
        "removed": (r"^\+.*", "green"),
        "added": (r"^-.*", "red"),
        "hunk_context": (r"^@@.*", "bold white"),  # applied first (whole line)
        "hunk_header": (r"^@@.*?@@ ", "blue"),  # applied second (only inside @ signs)
    }
    diff_lines = Text(style="white")
    for line in diff.splitlines(keepends=True):
        diff_line = Text(line)
        for pattern, style in highlight_patterns.values():
            diff_line.highlight_regex(pattern, style=style)
        diff_lines.append_text(diff_line)
    return diff_lines
