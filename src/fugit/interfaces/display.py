from pydantic import BaseModel

from ..core import io
from ..core.io import FugitConsole

__all__ = ("DisplayConfig",)


class DisplayConfig(BaseModel):
    """Put any display settings here"""

    quiet: bool = False
    plain: bool = False
    no_pager: bool = False
    file_limit: int = 0


def configure_global_console(config: DisplayConfig) -> None:
    """Turn on rich colourful printing to stdout if `config.plain` is set to False."""
    io.fugit_console = FugitConsole(
        plain=config.plain,
        quiet=config.quiet,
        use_pager=not config.no_pager,
        file_limit=config.file_limit,
    )
