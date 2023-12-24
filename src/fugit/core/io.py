from __future__ import annotations

from collections.abc import Iterable
from functools import cache
from types import TracebackType

from .error_handlers import SuppressBrokenPipeError
from .paging import SystemPager, TerminalDimensions

__all__ = ("PagerContext", "FugitConsole", "fugit_console")


class PagerContext:
    _console: FugitConsole
    pager: SystemPager
    styles: bool
    enabled: bool

    def __init__(self, console: FugitConsole, styles: bool, enabled: bool):
        self._console = console
        self.pager = SystemPager()
        self.styles = styles
        self.enabled = enabled

    def __enter__(self) -> PagerContext:
        return self._console

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            buffer: list[str] = self._console.printer_queue[:]
            del self._console.printer_queue[:]
            segments: Iterable[str] = buffer
            with SuppressBrokenPipeError():
                content = self._console._render_buffer(segments)
                if self.enabled:
                    self.pager.show(content)
                else:
                    print(content)
        return


@cache
class FugitConsole:
    page_with_styles: bool
    use_pager: bool
    file_limit: int
    file_count: int = 0
    printer_queue: list[str] = []

    def __init__(
        self,
        page_with_styles: bool = True,  # TODO: remove, redundant
        plain: bool = True,
        quiet: bool = False,
        use_pager: bool = True,
        file_limit: int = 0,
    ):
        self.plain = plain
        self.quiet = quiet
        self.page_with_styles: bool = page_with_styles
        self.use_pager: bool = use_pager
        self.file_limit: int = file_limit

    def size(self) -> TerminalDimensions:
        return TerminalDimensions()

    def overflows_terminal(self) -> bool:
        terminal_height = self.size().height
        text_height = len(self.printer_queue)
        return terminal_height < text_height

    def pager(self, styles: bool = True, enabled: bool = True) -> PagerContext:
        active = self.use_pager and self.overflows_terminal()
        return PagerContext(self, styles=styles, enabled=active)

    def submit(self, *output: str) -> None:
        """
        Report output through the rich console, but don't style at all if console was set to
        plain (so no bold, italics, etc. either), and avoid broken pipe errors when
        piping to `head` etc.
        """
        if self.file_limit != 0:
            if self.file_count == self.file_limit:
                raise SystemExit(0)
            if self.file_limit < 0:
                raise NotImplementedError("Tail not implemented yet")
        self.printer_queue.extend(output)

    def print_all(self) -> None:
        """Print the queue"""
        with SuppressBrokenPipeError():
            self._render_buffer(*self.printer_queue)

    def _render_buffer(
        self,
        feed: list[str],
        sep: str = "",
    ) -> str:
        """Concatenate the buffer into a single string to send to the pager."""
        return sep.join(feed)


"""
Global `FugitConsole` instance modified by a model validator upon initialisation
of `fugit.interfaces.display.DisplayConfig` or its subclass, the main `DiffConfig` model.
"""
fugit_console = FugitConsole()
