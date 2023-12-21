from typing import Annotated

from msgspec import Meta, Struct, field

from ..core import io
from ..core.io import FugitConsole

__all__ = ("DebugConfig", "DisplayConfig", "DiffConfig", "configure_global_console")


def desc(typ, description: str):
    """Annotate a `msgspec.Struct` field's type with a description"""
    return Annotated[typ, Meta(description=description)]


class DebugConfig(Struct):
    debug: desc(bool, "Run debug diagnostics") = False


class DisplayConfig(DebugConfig):
    quiet: desc(bool, "Print nothing at all") = False
    plain: desc(bool, "Don't apply any kind of text styling") = False
    no_pager: desc(bool, "Don't send output to the system pager") = False
    file_limit: desc(int, "Stop after a certain number of files match the filters") = 0


class RepoConfig(DisplayConfig):
    change_type: desc(list[str], "Filter diff hunk types") = field(default_factory=list)
    repo: desc(str, "The repo whose git diff is to be computed") = "."
    revision: desc(str, "The commit for comparison with the index") = "HEAD"
    pygit2: desc(bool, "Use the pygit2 backend rather than GitPython") = False


class DiffConfig(RepoConfig):
    """
    Configure input filtering and output display. Using "HEAD" as the `revision` will
    refer to the latest branch commit, while "HEAD~{$n}" (e.g. "HEAD~1") will indicate
    a specific number of commits before the latest.
    """


def configure_global_console(config: DiffConfig) -> None:
    """Turn on rich colourful printing to stdout if `config.plain` is set to False."""
    io.fugit_console = FugitConsole(
        plain=config.plain,
        quiet=config.quiet,
        use_pager=not config.no_pager,
        file_limit=config.file_limit,
    )
