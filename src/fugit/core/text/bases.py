from __future__ import annotations

import re
from enum import Enum
from functools import cache

from pydantic import BaseModel, RootModel

__all__ = ("Style", "StyledModel", "Span", "compile_re", "TextLine", "SpannedText")


class Style(Enum):
    r = "red"
    g = "green"
    b = "blue"
    w = "white"
    W = "bold white"
    Y_ = "bold yellow underline"


class StyledModel(BaseModel, use_enum_values=True):
    """Allow declaration of style fields as `Style` enum values but evaluation as `str`."""


class Span(StyledModel):
    start: int
    stop: int
    style: Style


@cache
def compile_re(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.MULTILINE)


class TextLine(RootModel):
    root: str


class SpannedText(StyledModel):
    line: str
    style: Style = Style.w
    spans: list[Span] = []

    def highlight_regex(self, style_patterns: list[tuple[str, str]]) -> None:
        for pattern, style in style_patterns:
            for hit in compile_re(pattern).finditer(self.line):
                start, stop = hit.span()
                span = Span(start=start, stop=stop, style=style)
                self.spans.append(span)
        return
