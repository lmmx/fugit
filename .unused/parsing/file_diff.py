from __future__ import annotations

from typing import Final, Union

from parse import Parser
from pydantic import BaseModel, Field, model_validator

from .optional_specifier import parse_any_width_string

__all__ = (
    "compile",
    "Line",
    "FileHedLine",
    "IdxLine",
    "FileMarkerLine",
    "PreLine",
    "AftLine",
    "HunkHedLine",
    "DiffContent",
    "AddLine",
    "DelLine",
    "EqvLine",
    "FileDiff",
    "RepoDiff",
)


def compile(schema: str) -> Parser:
    """
    This is a drop-in replacement to the `parse.compile` function from the `parse_types`
    fork of that library.

    Always use this instead of `parse.compile` or templates with a "?" format specifier
    won't compile.
    """
    return Parser(schema, extra_types={"?": parse_any_width_string})


# --- Classes for line types


class Line(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def lift_from_string_literal(cls, val: str, /) -> Line:
        return {"text": val}


class FileHedLine(Line):
    """
    File Header: indicates the files being compared.

    Example:
    "diff --git a/pytensor/graph/basic.py b/pytensor/graph/basic.py"
    """

    template: Final[str] = "diff --git a/{src} b/{dst}"
    parser: Final[Parser] = compile(template)
    text: str = Field(pattern=parser._expression)


class IdxLine(Line):
    """
    Index Line: shows the blob (version) of each file before and after the
    change.

    Example:
    "index a11aa57bd..d86b19a12 100644"
    """

    template: Final[str] = "index {hash_a}..{hash_b} {file_mode}"
    parser: Final[Parser] = compile(template)
    text: str = Field(pattern=parser._expression)


class FileMarkerLine(Line):
    """
    a/b File Markers: These lines show the path to the file and its version ("a" for the
    original, "b" for the changed file). PreLine/AftLine are used for a/b respectively.

    Example (PreLine/AftLine):
    "--- a/pytensor/graph/basic.py"
    "+++ b/pytensor/graph/basic.py"
    """


class PreLine(FileMarkerLine):
    template: Final[str] = "--- {symbol}/{path}"
    parser: Final[Parser] = compile(template)
    text: str = Field(pattern=parser._expression)


class AftLine(FileMarkerLine):
    template: Final[str] = "+++ {symbol}/{path}"
    parser: Final[Parser] = compile(template)
    text: str = Field(pattern=parser._expression)


class HunkHedLine(Line):
    """
    Hunk Header: The line beginning with @@ shows the line numbers in the original and
    changed file. The format is @@ -[start line in a],[number of lines] +[start line in
    b],[number of lines] @@.

    Example:
    "@@ -62,6 +62,7 @@"
    """

    template: Final[str] = "@@ -{lineno_a},{line_count_a} +{lineno_b},{line_count_b}"
    parser: Final[Parser] = compile(template)
    text: str = Field(pattern=parser._expression)


class DiffContent(Line):
    """
    Diff Content: The actual content changes. Lines starting with a minus (-) are
    removed lines, lines starting with a plus (+) are added lines, and lines without a
    prefix are unchanged/context lines.

    Example (DelLine, AddLine, EqvLine):
    "-from collections.abc import Iterable"
    "+from collections.abc import Iterable, Sequence"
    " from collections.abc import Iterable as IterableType"
    """


class AddLine(DiffContent):
    template: Final[str] = "+{content:?}"
    parser: Final[Parser] = compile(template)
    text: str = Field(pattern=parser._expression)


class DelLine(DiffContent):
    template: Final[str] = "-{content:?}"
    parser: Final[Parser] = compile(template)
    text: str = Field(pattern=parser._expression)


class EqvLine(DiffContent):
    template: Final[str] = " {content:?}"
    parser: Final[Parser] = compile(template)
    text: str = Field(pattern=parser._expression)


HeaderLineTypes = Union[FileHedLine, IdxLine, PreLine, AftLine]
DiffLineTypes = Union[AddLine, DelLine, EqvLine]


class FileDiff(BaseModel):
    lines: list[HeaderLineTypes | HunkHedLine | DiffLineTypes]

    def split_files(self) -> RepoDiff:
        return RepoDiff(files=[self])


class RepoDiff(BaseModel):
    files: list[FileDiff]

    @classmethod
    def from_file_diff_lines(cls, file_diffs: list[str]) -> RepoDiff:
        file_records = [
            dict(lines=file_lines.splitlines()) for file_lines in file_diffs
        ]
        return cls(files=file_records)
