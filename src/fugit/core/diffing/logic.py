from __future__ import annotations

import msgspec

# from git import Repo
# from pydantic import ValidationError
from pygit2 import Repository

from ...interfaces import DiffConfig
from ..io import FugitConsole, fugit_console
from ..text.bases import Span, SpannedText, Style
from ..text.palette import BLUE, BOLD, BOLD_YELLOW_US, GREEN, RED, RESET, WHITE
from ..text.scanning import compile_re

# from .gitpython import DiffInfoGP, count_match, get_diff
from .pygit2 import DiffInfoPG2

# from line_profiler import profile


__all__ = ("diff", "load_diff", "highlight_diff", "process_diff")

STORE_DIFFS = False
DiffInfoGP = None  # Not migrated


def diff(**config) -> list[str]:
    """Narrow the input type to DiffConfig type for `load_diff`."""
    return load_diff(msgspec.convert(config, type=DiffConfig))


def load_diff(config: DiffConfig) -> list[str]:
    # """Have to use GitPython as pygit2 cached diffs don't work"""
    # return load_diff_gitpython(config)
    """Try to get pygit2 cached diffs to work"""
    # FIXME Decommission GitPython until it is migrated to msgspec
    return load_diff_pygit2(config)  # if config.pygit2 else load_diff_gitpython(config)


# @profile
def process_diff(
    console: FugitConsole,
    diff_info: DiffInfoGP | DiffInfoPG2,
    diffs: list[str],
    config: DiffConfig,
) -> None:
    if config.change_type and (diff_info.change_type not in config.change_type):
        return
    filtrated = diff_info.text
    if STORE_DIFFS:
        diffs.append(filtrated)
    if config.plain:
        header = (diff_info.overview,)
    else:
        header = (BOLD_YELLOW_US, diff_info.overview, RESET)
    # This simulates the render process (`Console.render_str`)
    highlightable_lines = filtrated.splitlines(keepends=True)
    diff_line_count, highlighted_lines = highlight_diff(
        highlightable_lines,
        plain=config.plain,
    )
    console.submit(*header, *highlighted_lines)
    console.file_count += 1
    console.line_count += diff_line_count + 1
    return


highlight_patterns = {
    "hunk_context": (r"^@@.*", Style.W),  # applied first (whole line)
    "hunk_header": (r"^@@.*?@@ ", Style.b),  # applied second (only inside @ signs)
}


def highlight_regex(line: SpannedText, style_patterns: list[tuple[str, str]]) -> None:
    for pattern, style in style_patterns:
        for hit in compile_re(pattern).finditer(line.line):
            start, stop = hit.span()
            span = Span(start=start, stop=stop, style=style)
            line.spans.append(span)
    return


# @profile
def highlight_diff(
    source_lines: list[str],
    plain: bool = False,
) -> tuple[int, list[str]]:
    """This replaces the highlighter applied by `Console.render_markup`."""
    diff_line_texts = []
    diff_line_count = 0

    def store(texts: list[str]) -> None:
        nonlocal diff_line_count
        diff_line_texts.extend(texts)
        diff_line_count += 1

    for line in source_lines:
        match line[0]:
            case "d" | "i":
                continue  # diff or index
            case "+":
                if line[1] == "+":
                    continue
                store([line] if plain else [GREEN, line, RESET])
                continue
            case "-":
                if line[1] == "-":
                    continue
                store([line] if plain else [RED, line, RESET])
                continue
            case " ":
                store([line] if plain else [WHITE, line, RESET])
                continue
            case "@":
                # highlight_regex(diff_line, list(highlight_patterns.values()))
                hed_cutoff = line[2:].find("@@") + 4
                hed_span = line[:hed_cutoff]
                rest_span = line[hed_cutoff:]
                store([line] if plain else [BOLD, BLUE, hed_span, RESET, rest_span])
                continue
            case _:
                store([line])
    return diff_line_count, diff_line_texts


# @profile
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
        validated_diffs = msgspec.convert(
            list(repo_diff_patch),
            list[DiffInfoPG2],
            from_attributes=True,
        )
        for diff_info in filter(None, validated_diffs):
            process_diff(
                console=console,
                diff_info=diff_info,
                diffs=diffs,
                config=config,
            )
            del diff_info
    return diffs


# def load_diff_gitpython(config: DiffConfig) -> list[str]:
#     """
#     Note: You can either implement commit tree-based diffs (with no 'R' kwarg reversal
#     weirdness) or get it from a string at runtime (more configurable so we do that).
#     For reference, you would do it like this rather than ``config.revision``:
#
#       >>> tree = repo.head.commit.tree
#     """
#     repo = Repo(config.repo, search_parent_directories=True)
#     index = repo.index
#     tree = config.revision
#     file_diff_patch = get_diff(index, tree, create_patch=True)
#     file_diff_info = get_diff(index, tree, create_patch=False)
#     count_match(file_diff_patch, file_diff_info)
#     diffs: list[str] = []
#     with fugit_console.pager() as console:
#         for patch, info in zip(file_diff_patch, file_diff_info):
#             try:
#                 diff_info = DiffInfoGP.from_tree_pair(patch=patch, info=info)
#             except ValidationError:
#                 raise  # TODO: make a nicer custom error and exit
#             process_diff(
#                 console=console,
#                 diff_info=diff_info,
#                 diffs=diffs,
#                 config=config,
#             )
#             del diff_info
#     return diffs
