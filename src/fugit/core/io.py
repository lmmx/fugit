from contextlib import contextmanager

from rich.console import Console

from .error_handlers import SuppressBrokenPipeError

__all__ = ("FugitConsole", "fugit_console")


class FugitConsole:
    console: Console
    use_pager: bool
    page_with_styles: bool

    def __init__(self, use_pager: bool = False, page_with_styles: bool = True):
        self.console: Console = Console()
        self.use_pager: bool = use_pager
        self.page_with_styles: bool = page_with_styles

    @contextmanager
    def pager_available(self):
        """Uses console pagination if `DisplayConfig` switched this setting on."""
        if self.use_pager:
            with self.console.pager(styles=self.page_with_styles):
                yield self
        else:
            yield self

    def print(self, output: str, end="", style=None) -> None:
        """
        Report output through the rich console, but don't style at all if rich was set to
        no_color (so no bold, italics, etc. either), and avoid broken pipe errors when
        piping to `head` etc.
        """
        with_style = style if fugit_console.no_color else None
        with SuppressBrokenPipeError():
            fugit_console.console.print(output, end=end, style=with_style)


"""
Global `rich.console.Console` instance modified by a model validator upon initialisation
of `fugit.interfaces.display.DisplayConfig` or its subclass, the main `DiffConfig` model.
"""
fugit_console = FugitConsole()
