from pydantic import BaseModel

__all__ = ("DebugConfig",)


class DebugConfig(BaseModel):
    """Put any debug settings here"""

    debug: bool = False
