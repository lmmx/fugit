from pydantic import BaseModel, TypeAdapter

from .display import DisplayConfig

__all__ = ["FilterConfig", "DiffConfig"]


class FilterConfig(BaseModel):
    change_type: list[str] = list("ACDMRTUXB")


class DiffConfig(DisplayConfig, FilterConfig):
    """
    Configure input filtering and output display.

      :param change_type: Change types to filter diffs for.
    """


DiffConfig.adapt = TypeAdapter(DiffConfig).validate_python
