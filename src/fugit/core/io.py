from contextlib import contextmanager
from functools import cache

from rich.console import Console

from ..types import SignedInteger
from .console import make_console
from .error_handlers import SuppressBrokenPipeError

__all__ = ("FugitConsole", "fugit_console")


@cache
class FugitConsole:
    console: Console
    page_with_styles: bool
    use_pager: bool
    file_limit: SignedInteger
    file_count: int = 0

    def __init__(
        self,
        page_with_styles: bool = True,
        plain: bool = True,
        quiet: bool = False,
        use_pager: bool = True,
        file_limit: SignedInteger = SignedInteger("-0"),
    ):
        self.page_with_styles: bool = page_with_styles
        self.use_pager: bool = use_pager
        self.file_limit: SignedInteger = file_limit
        self.console = make_console(plain=plain, quiet=quiet)

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
            if self.file_limit != -0.0:
                if self.file_count == self.file_limit:
                    raise SystemExit(0)
                if not self.file_limit.is_positive:
                    raise NotImplementedError("Tail not implemented yet")
            self.console.print(output, end=end, style=style)


"""
Global `rich.console.Console` instance modified by a model validator upon initialisation
of `fugit.interfaces.display.DisplayConfig` or its subclass, the main `DiffConfig` model.
"""
fugit_console = FugitConsole()
