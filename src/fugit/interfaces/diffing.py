from pydantic import BaseModel

from ..core import io
from ..core.io import FugitConsole

__all__ = ("DebugConfig", "DisplayConfig", "DiffConfig", "configure_global_console")


class DebugConfig(BaseModel):
    debug: bool = False


class DisplayConfig(DebugConfig):
    quiet: bool = False
    plain: bool = False
    no_pager: bool = False
    file_limit: int = 0


class RepoConfig(DisplayConfig):
    change_type: list[str] = list("ACDMRTUXB")
    repo: str = "."
    revision: str = "HEAD"
    pygit2: bool = False


class DiffConfig(RepoConfig):
    """
    Configure input filtering and output display.

      :param repo: The repo whose git diff is to be computed.
      :param revision: Specify the commit for comparison with the index. Use "HEAD" to
                       refer to the latest branch commit, or "HEAD~{$n}" (e.g. "HEAD~1")
                       to indicate a specific number of commits before the latest.
      :param change_type: Change types to filter diffs for.
    """


def configure_global_console(config: DiffConfig) -> None:
    """Turn on rich colourful printing to stdout if `config.plain` is set to False."""
    io.fugit_console = FugitConsole(
        plain=config.plain,
        quiet=config.quiet,
        use_pager=not config.no_pager,
        file_limit=config.file_limit,
    )
