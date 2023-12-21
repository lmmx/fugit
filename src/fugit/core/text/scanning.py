import re
from functools import cache

__all__ = ("compile_re",)


@cache
def compile_re(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.MULTILINE)
