from pydantic import BaseModel, TypeAdapter
from pydantic.types import DirectoryPath

from .display import DisplayConfig

__all__ = ["FilterConfig", "DiffConfig"]


class FilterConfig(BaseModel):
    change_type: list[str] = list("ACDMRTUXB")


class RepoConfig(BaseModel):
    repo: DirectoryPath = "."
    revision: str = "HEAD"


class DiffConfig(DisplayConfig, FilterConfig, RepoConfig):
    """
    Configure input filtering and output display.

      :param repo: The repo whose git diff is to be computed.
      :param revision: Specify the commit for comparison with the index. Use "HEAD" to
                       refer tot he latest branch commit, or "HEAD~{$n}" (e.g. "HEAD~1")
                       to indicate a specific number of commits before the latest.
      :param change_type: Change types to filter diffs for.
    """


DiffConfig.adapt = TypeAdapter(DiffConfig).validate_python
