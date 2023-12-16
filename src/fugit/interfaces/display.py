from pydantic import BaseModel, model_validator

from ..core.io import fugit_console

__all__ = ("DisplayConfig",)


class DisplayConfig(BaseModel):
    """Put any display settings here"""

    quiet: bool = False
    rich: bool = True
    paged: bool = True

    @model_validator(mode="after")
    def configure_global_console(self) -> None:
        """Turn on rich colourful printing to stdout if `self.rich` is set to True."""
        fugit_console.no_color = self.rich
        fugit_console.quiet = self.quiet
        fugit_console.use_pager = self.paged
