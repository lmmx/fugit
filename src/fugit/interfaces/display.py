from typing import Annotated

from pydantic import AfterValidator, BaseModel, model_validator

from ..core.console import make_console
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
        fugit_console.file_limit = self.file_limit
        fugit_console.console = make_console(plain=self.plain, quiet=self.quiet)
        fugit_console.use_pager = not self.no_pager
