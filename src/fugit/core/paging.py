from __future__ import annotations

from os import get_terminal_size

from pydantic import ConfigDict, ImportString, RootModel

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


class SystemPager(RootModel):
    model_config: ConfigDict = ConfigDict(validate_default=True)
    root: ImportString = "pydoc.pager"

    def show(self, content: str):
        assert isinstance(content, str)
        return self.root(content)
