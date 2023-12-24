from __future__ import annotations

from os import get_terminal_size

__all__ = ("TerminalDimensions", "SystemPager")


class TerminalDimensions:
    height: int
    width: int

    def __init__(self):
        try:
            size = get_terminal_size()
            self.height = size.lines
            self.width = size.columns
        except OSError:
            self.height = 25
            self.width = 80
        return


class SystemPager:
    def show(self, content: str):
        assert isinstance(content, str)
        return __import__("pydoc").pager(content)
