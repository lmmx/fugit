from __future__ import annotations

from enum import Enum

from msgspec import Struct

__all__ = ("Style", "Span", "SpannedText")


class Style(Enum):
    r = "red"
    g = "green"
    b = "blue"
    w = "white"
    W = "bold white"
    Y_ = "bold yellow underline"


class Span(Struct):
    start: int
    stop: int
    style: Style


class SpannedText(Struct):
    line: str
    style: Style = Style.w
    spans: list[Span] = []
