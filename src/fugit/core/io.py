from contextlib import contextmanager

from rich.console import Console

from .error_handlers import SuppressBrokenPipeError

__all__ = ("FugitConsole", "fugit_console")


class FugitConsole:
    console: Console
    page_with_styles: bool
    use_pager: bool

    def __init__(
        self,
        page_with_styles: bool = True,
        plain: bool = True,
        quiet: bool = False,
        use_pager: bool = True,
    ):
        self.page_with_styles: bool = page_with_styles
        self.use_pager: bool = use_pager
        color_system = None if plain else "auto"
        self.console = Console(no_color=plain, quiet=quiet, color_system=color_system)

    @property
    def plain(self) -> bool:
        return self.console.color_system is None

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
        with SuppressBrokenPipeError():
            fugit_console.console.print(output, end=end, style=style)


"""
Global `rich.console.Console` instance modified by a model validator upon initialisation
of `fugit.interfaces.display.DisplayConfig` or its subclass, the main `DiffConfig` model.
"""
fugit_console = FugitConsole()
