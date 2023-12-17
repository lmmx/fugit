from typing import Annotated

from pydantic import AfterValidator, BaseModel, model_validator
from rich.console import Console

from ..core.io import fugit_console
from ..types import SignedInteger

__all__ = ("DisplayConfig",)


class DisplayConfig(BaseModel):
    """Put any display settings here"""

    quiet: bool = False
    plain: bool = False
    no_pager: bool = False
    file_limit: Annotated[str, AfterValidator(SignedInteger)] = "-0"

    @model_validator(mode="after")
    def configure_global_console(self) -> None:
        """Turn on rich colourful printing to stdout if `self.rich` is set to True."""
        color_system = None if self.plain else "auto"
        fugit_console.file_limit = self.file_limit
        fugit_console.console = Console(
            no_color=self.plain,
            quiet=self.quiet,
            color_system=color_system,
        )
        fugit_console.use_pager = not self.no_pager
